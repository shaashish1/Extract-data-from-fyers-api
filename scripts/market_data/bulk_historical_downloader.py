#!/usr/bin/env python3
"""
Bulk Historical Data Downloader for Fyers API
==============================================

Downloads 5 years of historical data for ALL discovered symbols across multiple timeframes.

Features:
- Downloads for all symbols from consolidated_symbols
- Multiple timeframes: 1m, 5m, 15m, 30m, 60m, 1D
- Organized by date/month folders
- Parallel processing (10 workers)
- Progress tracking with Rich
- Auto-retry failed downloads
- Resume capability
- Rate limiting (respects API limits)

Storage Structure:
data/parquet/{category}/{symbol}/{timeframe}/{YYYY}/{MM}/
└── {symbol}_{timeframe}_{YYYY}_{MM}.parquet

Usage:
    # Download all symbols, all timeframes
    python bulk_historical_downloader.py
    
    # Download specific category
    python bulk_historical_downloader.py --category nifty50
    
    # Download specific timeframe
    python bulk_historical_downloader.py --timeframe 1D
    
    # Resume previous download
    python bulk_historical_downloader.py --resume

Author: Fyers Trading Platform
Created: October 30, 2025
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, date
import pandas as pd
import time
import logging
import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
import threading
from concurrent.futures import ThreadPoolExecutor as _LocalExecutor

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for date/datetime objects"""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.auth.my_fyers_model import MyFyersModel
from scripts.core.rate_limit_manager import get_rate_limiter
from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.live import Live
from rich.panel import Panel
from rich import box

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bulk_download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

console = Console()

@dataclass
class DownloadTask:
    """Represents a single download task"""
    symbol: str
    category: str
    timeframe: str
    start_date: date
    end_date: date
    status: str = 'pending'  # pending, downloading, completed, failed
    error: Optional[str] = None
    retry_count: int = 0
    downloaded_months: int = 0
    total_months: int = 0

class DownloadStatus:
    """Thread-safe download status tracker"""
    
    def __init__(self, status_file: Path):
        self.status_file = status_file
        self.lock = threading.Lock()
        self.status = self._load_status()
    
    def _load_status(self) -> Dict:
        """Load status from file"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                # Corrupted status file: back it up and start fresh
                try:
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup = self.status_file.with_name(f"{self.status_file.stem}.bad-{ts}{self.status_file.suffix}")
                    os.replace(self.status_file, backup)
                    console.print(f"[yellow]⚠️  Corrupt status file moved to {backup}[/yellow]")
                except Exception:
                    pass
        return {
            'tasks': {},
            'statistics': {
                'total': 0,
                'completed': 0,
                'failed': 0,
                'pending': 0
            },
            'started_at': None,
            'updated_at': None
        }
    
    def _save_status(self):
        """Save status to file"""
        self.status['updated_at'] = datetime.now().isoformat()
        # Convert date objects to strings for JSON serialization
        status_copy = self.status.copy()
        for task_id, task_data in status_copy['tasks'].items():
            if isinstance(task_data.get('start_date'), date):
                task_data['start_date'] = task_data['start_date'].isoformat()
            if isinstance(task_data.get('end_date'), date):
                task_data['end_date'] = task_data['end_date'].isoformat()
        
        with open(self.status_file, 'w') as f:
            json.dump(status_copy, f, indent=2)
    
    def add_task(self, task: DownloadTask):
        """Add new task to status"""
        with self.lock:
            task_id = f"{task.symbol}_{task.timeframe}"
            task_dict = asdict(task)
            # Convert date objects to ISO strings
            task_dict['start_date'] = task.start_date.isoformat()
            task_dict['end_date'] = task.end_date.isoformat()
            self.status['tasks'][task_id] = task_dict
            self.status['statistics']['total'] += 1
            self.status['statistics']['pending'] += 1
            if not self.status['started_at']:
                self.status['started_at'] = datetime.now().isoformat()
            self._save_status()
    
    def update_task(self, task: DownloadTask):
        """Update task status"""
        with self.lock:
            task_id = f"{task.symbol}_{task.timeframe}"
            old_status = self.status['tasks'].get(task_id, {}).get('status', 'pending')
            
            task_dict = asdict(task)
            # Convert date objects to ISO strings
            task_dict['start_date'] = task.start_date.isoformat()
            task_dict['end_date'] = task.end_date.isoformat()
            self.status['tasks'][task_id] = task_dict
            
            # Update statistics
            if old_status != task.status:
                if old_status in self.status['statistics']:
                    self.status['statistics'][old_status] = max(0, self.status['statistics'].get(old_status, 0) - 1)
                if task.status in self.status['statistics']:
                    self.status['statistics'][task.status] = self.status['statistics'].get(task.status, 0) + 1
            
            self._save_status()
    
    def get_pending_tasks(self) -> List[DownloadTask]:
        """Get all pending tasks"""
        with self.lock:
            tasks = []
            for task_data in self.status['tasks'].values():
                if task_data['status'] in ['pending', 'failed']:
                    task = DownloadTask(**task_data)
                    # Convert string dates back to date objects
                    task.start_date = datetime.fromisoformat(task_data['start_date']).date()
                    task.end_date = datetime.fromisoformat(task_data['end_date']).date()
                    tasks.append(task)
            return tasks
    
    def get_statistics(self) -> Dict:
        """Get current statistics"""
        with self.lock:
            return self.status['statistics'].copy()


class BulkHistoricalDownloader:
    """
    Bulk historical data downloader with parallel processing and progress tracking
    """
    
    def __init__(self, max_workers: int = 10):
        self.fyers = MyFyersModel()
        self.rate_limiter = get_rate_limiter()
        self.max_workers = max_workers
        self.base_data_dir = Path('data/parquet')
        self.consolidated_symbols_dir = Path('data/consolidated_symbols')
        self.status_file = Path('logs/download_status.json')
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self.download_status = DownloadStatus(self.status_file)
        # Lightweight counters for richer summary
        self._counters = {
            'auth_errors': 0,
            'timeouts': 0,
            'no_data': 0,
            'records': 0,
        }
        
        # Timeframe configurations (Fyers resolution codes)
        self.timeframes = {
            '1m': '1',      # 1 minute
            '5m': '5',      # 5 minutes
            '15m': '15',    # 15 minutes
            '30m': '30',    # 30 minutes
            '60m': '60',    # 1 hour
            '1D': 'D',      # 1 day
        }
        
        # API request limits per timeframe
        self.request_limits = {
            '1m': 100,   # 100 days per request
            '5m': 100,
            '15m': 100,
            '30m': 100,
            '60m': 100,
            '1D': 366,   # 366 days per request
        }
        
        # Calculate 5 years date range
        self.end_date = date.today()
        self.start_date = self.end_date - timedelta(days=5*365)
        
        console.print(Panel.fit(
            f"[bold cyan]Bulk Historical Downloader[/bold cyan]\n"
            f"Date Range: {self.start_date} to {self.end_date}\n"
            f"Workers: {self.max_workers}\n"
            f"Timeframes: {', '.join(self.timeframes.keys())}",
            box=box.DOUBLE
        ))
    
    def load_symbols(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """Load symbols from consolidated_symbols directory"""
        symbols_by_category = {}
        
        # Read all symbol CSV files
        csv_files = list(self.consolidated_symbols_dir.glob('*_symbols.csv'))
        
        for csv_file in csv_files:
            cat_name = csv_file.stem.replace('_symbols', '')
            
            # Skip if specific category requested and this isn't it
            if category and cat_name != category:
                continue
            
            try:
                df = pd.read_csv(csv_file)
                if 'symbol' in df.columns:
                    symbols = df['symbol'].dropna().unique().tolist()
                    symbols_by_category[cat_name] = symbols
                    console.print(f"✅ Loaded {len(symbols)} symbols from [cyan]{cat_name}[/cyan]")
            except Exception as e:
                console.print(f"⚠️  Error loading {csv_file}: {e}")
        
        return symbols_by_category
    
    def create_download_tasks(
        self,
        symbols_by_category: Dict[str, List[str]],
        timeframes: Optional[List[str]] = None
    ) -> List[DownloadTask]:
        """Create download tasks for all symbols and timeframes"""
        tasks = []
        
        # Use all timeframes if none specified
        if not timeframes:
            timeframes = list(self.timeframes.keys())
        
        for category, symbols in symbols_by_category.items():
            for symbol in symbols:
                for tf in timeframes:
                    if tf not in self.timeframes:
                        console.print(f"⚠️  Unknown timeframe: {tf}, skipping")
                        continue
                    
                    # Calculate total months for this task
                    months = (self.end_date.year - self.start_date.year) * 12
                    months += self.end_date.month - self.start_date.month + 1
                    
                    task = DownloadTask(
                        symbol=symbol,
                        category=category,
                        timeframe=tf,
                        start_date=self.start_date,
                        end_date=self.end_date,
                        total_months=months
                    )
                    tasks.append(task)
        
        return tasks
    
    def download_symbol_data(
        self,
        symbol: str,
        category: str,
        timeframe: str,
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """Download data for a single symbol and timeframe"""
        resolution = self.timeframes[timeframe]
        request_limit = self.request_limits[timeframe]
        
        all_data = []
        current_start = start_date

        def _history_call_with_timeout(payload: dict, timeout_sec: int = 20):
            """Run a single history call with a watchdog timeout to avoid hangs."""
            with _LocalExecutor(max_workers=1) as ex:
                fut = ex.submit(self.fyers.get_fyre_model().history, payload)
                return fut.result(timeout=timeout_sec)
        
        while current_start < end_date:
            # Calculate chunk end date
            chunk_end = min(
                current_start + timedelta(days=request_limit),
                end_date
            )
            
            # Wait for rate limiter
            self.rate_limiter.wait_if_needed()
            
            try:
                # Make API request
                # Use epoch format for performance (date_format=0)
                # Compute epoch seconds for start/end of day
                start_dt = datetime.combine(current_start, datetime.min.time())
                end_dt = datetime.combine(chunk_end, datetime.max.time())

                range_from = int(start_dt.timestamp())
                range_to = int(end_dt.timestamp())

                # For intraday timeframes, prevent partial candle by trimming last minute
                if timeframe != '1D':
                    range_to = max(range_from, range_to - 60)

                # Derivatives typically need cont_flag=1; cash equities should be 0
                cont_flag = '1' if category.lower() in {"futures", "options", "derivatives", "fo"} else '0'

                data = {
                    "symbol": f"NSE:{symbol}-EQ",
                    "resolution": resolution,
                    "date_format": "0",
                    "range_from": str(range_from),
                    "range_to": str(range_to),
                    "cont_flag": cont_flag
                }
                
                # Use a watchdog timeout to prevent indefinite hangs
                try:
                    response = _history_call_with_timeout(data, timeout_sec=25)
                except Exception as te:
                    # Timeout or execution issue for this chunk
                    logger.error(f"Timeout/error on history call for {symbol} {timeframe} [{current_start} -> {chunk_end}]: {te}")
                    self._counters['timeouts'] += 1
                    current_start = chunk_end + timedelta(days=1)
                    continue
                
                # Fast-fail on authentication errors
                if isinstance(response, dict) and response.get('s') == 'error' and response.get('code') in (-16, -17):
                    self._counters['auth_errors'] += 1
                    raise RuntimeError(f"Authentication failed for history API (code {response.get('code')})")

                if response.get('s') == 'ok' and 'candles' in response:
                    df = pd.DataFrame(
                        response['candles'],
                        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                    )
                    all_data.append(df)
                
                # Update current_start for next iteration
                current_start = chunk_end + timedelta(days=1)
                
            except Exception as e:
                logger.error(f"Error downloading {symbol} {timeframe} from {current_start}: {e}")
                # Continue with next chunk even if one fails
                current_start = chunk_end + timedelta(days=1)
        
        # Combine all chunks
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df = combined_df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
            # Update counters
            try:
                self._counters['records'] += int(len(combined_df))
            except Exception:
                pass
            return combined_df
        
        return pd.DataFrame()
    
    def save_data_by_month(
        self,
        df: pd.DataFrame,
        symbol: str,
        category: str,
        timeframe: str
    ) -> int:
        """Save data organized by year and month"""
        if df.empty:
            return 0
        
        # Convert timestamp to datetime
        df['date'] = pd.to_datetime(df['timestamp'], unit='s')
        
        months_saved = 0
        
        # Group by year and month
        for (year, month), group_df in df.groupby([df['date'].dt.year, df['date'].dt.month]):
            # Create directory structure
            output_dir = self.base_data_dir / category / symbol / timeframe / str(year) / f"{month:02d}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create filename
            filename = f"{symbol}_{timeframe}_{year}_{month:02d}.parquet"
            output_path = output_dir / filename
            
            # Save only OHLCV columns
            save_df = group_df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()
            save_df.to_parquet(output_path, engine='pyarrow', compression='snappy', index=False)
            months_saved += 1
        
        return months_saved
    
    def process_download_task(self, task: DownloadTask) -> DownloadTask:
        """Process a single download task"""
        task.status = 'downloading'
        self.download_status.update_task(task)
        
        try:
            # Download data
            df = self.download_symbol_data(
                task.symbol,
                task.category,
                task.timeframe,
                task.start_date,
                task.end_date
            )
            
            if not df.empty:
                # Save data by month
                months_saved = self.save_data_by_month(
                    df,
                    task.symbol,
                    task.category,
                    task.timeframe
                )
                
                task.downloaded_months = months_saved
                task.status = 'completed'
                logger.info(f"✅ Completed {task.symbol} {task.timeframe}: {months_saved} months, {len(df)} records")
            else:
                task.status = 'completed'  # Mark as completed even if no data
                self._counters['no_data'] += 1
                logger.warning(f"⚠️  No data for {task.symbol} {task.timeframe}")
        
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.retry_count += 1
            logger.error(f"❌ Failed {task.symbol} {task.timeframe}: {e}")
        
        self.download_status.update_task(task)
        return task
    
    def run_bulk_download(
        self,
        category: Optional[str] = None,
        timeframe: Optional[str] = None,
        resume: bool = False,
        no_preflight: bool = False
    ):
        """Run bulk download with parallel processing"""
        
        # Preflight auth check to fail fast if token/client_id are invalid (unless disabled)
        if not no_preflight:
            check = self.fyers.preflight_auth_check()
            if not isinstance(check, dict) or check.get('s') != 'ok':
                msg = check.get('message') if isinstance(check, dict) else 'Unknown authentication error'
                console.print(f"[red]❌ Authentication check failed: {msg}[/red]")
                console.print("[yellow]Run: python auth/generate_token.py to refresh the token, then retry. Or use --no-preflight to attempt anyway.[/yellow]")
                return

        # Load tasks
        if resume:
            console.print("[yellow]📥 Resuming previous download...[/yellow]")
            tasks = self.download_status.get_pending_tasks()
            console.print(f"Found {len(tasks)} pending tasks")
        else:
            console.print("[cyan]📊 Loading symbols...[/cyan]")
            symbols_by_category = self.load_symbols(category)
            
            if not symbols_by_category:
                console.print("[red]❌ No symbols found![/red]")
                return
            
            # Create tasks
            timeframes_list = [timeframe] if timeframe else None
            tasks = self.create_download_tasks(symbols_by_category, timeframes_list)
            
            console.print(f"\n[green]✅ Created {len(tasks)} download tasks[/green]")
            
            # Add tasks to status tracker
            for task in tasks:
                self.download_status.add_task(task)
        
        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            main_task = progress.add_task(
                "[cyan]Downloading historical data...",
                total=len(tasks)
            )
            
            # Process tasks in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self.process_download_task, task): task
                    for task in tasks
                }
                
                for future in as_completed(futures):
                    task = future.result()
                    progress.advance(main_task)
                    
                    # Update progress description with current task
                    stats = self.download_status.get_statistics()
                    progress.update(
                        main_task,
                        description=f"[cyan]Completed: {stats['completed']}, Failed: {stats['failed']}, Pending: {stats['pending']}"
                    )
        
        # Display final statistics
        self.display_summary()
    
    def display_summary(self):
        """Display download summary"""
        stats = self.download_status.get_statistics()
        
        table = Table(title="Download Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green", justify="right")
        
        table.add_row("Total Tasks", str(stats['total']))
        table.add_row("Completed", str(stats['completed']))
        table.add_row("Failed", str(stats['failed']))
        table.add_row("Pending", str(stats['pending']))
        table.add_row("Records Downloaded", str(self._counters.get('records', 0)))
        table.add_row("No-Data Tasks", str(self._counters.get('no_data', 0)))
        table.add_row("Auth Errors", str(self._counters.get('auth_errors', 0)))
        table.add_row("Timeouts", str(self._counters.get('timeouts', 0)))
        
        success_rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        table.add_row("Success Rate", f"{success_rate:.1f}%")
        
        console.print("\n")
        console.print(table)
        
        if stats['failed'] > 0:
            console.print(f"\n[yellow]⚠️  {stats['failed']} tasks failed. Run with --resume to retry.[/yellow]")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Bulk Historical Data Downloader')
    parser.add_argument('--category', type=str, help='Download specific category only')
    parser.add_argument('--timeframe', type=str, choices=['1m', '5m', '15m', '30m', '60m', '1D'],
                       help='Download specific timeframe only')
    parser.add_argument('--workers', type=int, default=10, help='Number of parallel workers (default: 10)')
    parser.add_argument('--resume', action='store_true', help='Resume previous download')
    parser.add_argument('--no-preflight', action='store_true', help='Skip auth preflight and attempt download anyway')
    
    args = parser.parse_args()
    
    # Create downloader
    downloader = BulkHistoricalDownloader(max_workers=args.workers)
    
    # Run download
    downloader.run_bulk_download(
        category=args.category,
        timeframe=args.timeframe,
        resume=args.resume,
        no_preflight=args.no_preflight
    )


if __name__ == '__main__':
    main()
