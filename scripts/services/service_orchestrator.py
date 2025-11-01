#!/usr/bin/env python3
"""
Microservice Architecture for Parallel Historical Data Processing
==================================================================

Modular services for:
1. Symbol Loading Service - Loads and caches symbols
2. Data Download Service - Parallel downloads with progress tracking  
3. Backtesting Service - Tests strategies across symbols/timeframes

Features:
- Service-oriented architecture
- Independent, reusable components
- Real-time progress tracking with Rich
- Scale to 9K symbols × 6 timeframes × 100+ strategies
- Thread-safe operations
- Resilient error handling

Usage:
    from scripts.services.service_orchestrator import ServiceOrchestrator
    
    orchestrator = ServiceOrchestrator()
    orchestrator.run_full_pipeline()

Author: Fyers Trading Platform
Created: October 30, 2025
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
import pandas as pd
import time
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from queue import Queue, Empty
import threading
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TaskID
)
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich import box

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/services.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
console = Console()


class ServiceStatus(Enum):
    """Service status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class ServiceMetrics:
    """Metrics for a service"""
    service_name: str
    status: ServiceStatus
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    
    def get_progress_percentage(self) -> float:
        """Get completion percentage"""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100
    
    def get_elapsed_time(self) -> Optional[timedelta]:
        """Get elapsed time"""
        if not self.start_time:
            return None
        end = self.end_time if self.end_time else datetime.now()
        return end - self.start_time
    
    def get_eta(self) -> Optional[timedelta]:
        """Estimate time to completion"""
        if not self.start_time or self.completed_tasks == 0:
            return None
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        rate = self.completed_tasks / elapsed
        remaining = self.total_tasks - self.completed_tasks
        
        if rate > 0:
            eta_seconds = remaining / rate
            return timedelta(seconds=int(eta_seconds))
        return None


class SymbolLoadingService:
    """
    Service 1: Symbol Loading and Management
    
    Features:
    - Load symbols from consolidated_symbols directory
    - Cache symbols in memory
    - Filter by category
    - Provide symbol metadata
    """
    
    def __init__(self):
        self.symbols_dir = Path('data/consolidated_symbols')
        self.symbol_cache: Dict[str, List[str]] = {}
        self.lock = threading.Lock()
        self.metrics = ServiceMetrics("SymbolLoadingService", ServiceStatus.IDLE)
        
    def load_symbols(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Load symbols from CSV files
        
        Args:
            category: Optional category filter (nifty50, all_equities, etc.)
        
        Returns:
            Dictionary mapping category to list of symbols
        """
        with self.lock:
            self.metrics.status = ServiceStatus.RUNNING
            self.metrics.start_time = datetime.now()
            
            try:
                if category:
                    # Load specific category
                    if category not in self.symbol_cache:
                        self.symbol_cache[category] = self._load_category(category)
                    return {category: self.symbol_cache[category]}
                else:
                    # Load all categories
                    csv_files = list(self.symbols_dir.glob('*_symbols.csv'))
                    self.metrics.total_tasks = len(csv_files)
                    
                    for csv_file in csv_files:
                        cat_name = csv_file.stem.replace('_symbols', '')
                        if cat_name not in self.symbol_cache:
                            self.symbol_cache[cat_name] = self._load_category(cat_name)
                        self.metrics.completed_tasks += 1
                    
                    self.metrics.status = ServiceStatus.COMPLETED
                    self.metrics.end_time = datetime.now()
                    return self.symbol_cache.copy()
            
            except Exception as e:
                self.metrics.status = ServiceStatus.FAILED
                self.metrics.errors.append(str(e))
                logger.error(f"Error loading symbols: {e}", exc_info=True)
                raise
    
    def _load_category(self, category: str) -> List[str]:
        """Load symbols for a specific category"""
        csv_file = self.symbols_dir / f"{category}_symbols.csv"
        
        if not csv_file.exists():
            raise FileNotFoundError(f"Category file not found: {csv_file}")
        
        df = pd.read_csv(csv_file)
        symbols = df['symbol'].tolist()
        logger.info(f"Loaded {len(symbols)} symbols for {category}")
        return symbols
    
    def get_symbol_count(self, category: Optional[str] = None) -> int:
        """Get total symbol count"""
        if category:
            return len(self.symbol_cache.get(category, []))
        return sum(len(symbols) for symbols in self.symbol_cache.values())
    
    def get_categories(self) -> List[str]:
        """Get list of available categories"""
        return list(self.symbol_cache.keys())
    
    def clear_cache(self):
        """Clear symbol cache"""
        with self.lock:
            self.symbol_cache.clear()
            self.metrics = ServiceMetrics("SymbolLoadingService", ServiceStatus.IDLE)


class DataDownloadService:
    """
    Service 2: Historical Data Download with Parallel Processing
    
    Features:
    - Parallel downloads (configurable workers)
    - Real-time progress tracking
    - Rate limiting
    - Auto-retry failed downloads
    - Resume capability
    """
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.metrics = ServiceMetrics("DataDownloadService", ServiceStatus.IDLE)
        self.download_queue: Queue = Queue()
        self.result_queue: Queue = Queue()
        self.lock = threading.Lock()
        
        # Import here to avoid circular dependency
        from scripts.market_data.bulk_historical_downloader import BulkHistoricalDownloader
        self.downloader = BulkHistoricalDownloader(max_workers=max_workers)
    
    def start_bulk_download(
        self,
        symbols: Dict[str, List[str]],
        timeframes: List[str],
        start_date: date,
        end_date: date,
        resume: bool = False
    ) -> ServiceMetrics:
        """
        Start bulk historical data download
        
        Args:
            symbols: Dictionary mapping category to list of symbols
            timeframes: List of timeframes to download
            start_date: Start date for historical data
            end_date: End date for historical data
            resume: Whether to resume previous download
        
        Returns:
            Service metrics with download statistics
        """
        self.metrics.status = ServiceStatus.RUNNING
        self.metrics.start_time = datetime.now()
        
        # Calculate total tasks
        total_tasks = sum(len(symbol_list) * len(timeframes) 
                         for symbol_list in symbols.values())
        self.metrics.total_tasks = total_tasks
        
        console.print(Panel(
            f"[bold cyan]Starting Bulk Download Service[/bold cyan]\n\n"
            f"[yellow]Categories:[/yellow] {len(symbols)}\n"
            f"[yellow]Total Symbols:[/yellow] {sum(len(s) for s in symbols.values())}\n"
            f"[yellow]Timeframes:[/yellow] {len(timeframes)}\n"
            f"[yellow]Total Tasks:[/yellow] {total_tasks:,}\n"
            f"[yellow]Workers:[/yellow] {self.max_workers}\n"
            f"[yellow]Date Range:[/yellow] {start_date} to {end_date}",
            title="Data Download Service",
            border_style="cyan"
        ))
        
        try:
            # Run bulk download using existing BulkHistoricalDownloader
            for category, symbol_list in symbols.items():
                for timeframe in timeframes:
                    result = self.downloader.run_bulk_download(
                        category=category,
                        timeframe=timeframe,
                        resume=resume
                    )
                    
                    # Update metrics
                    with self.lock:
                        self.metrics.completed_tasks += len(symbol_list)
            
            self.metrics.status = ServiceStatus.COMPLETED
            self.metrics.end_time = datetime.now()
            
            console.print(Panel(
                f"[bold green]✓ Download Complete![/bold green]\n\n"
                f"[yellow]Completed:[/yellow] {self.metrics.completed_tasks:,}\n"
                f"[yellow]Failed:[/yellow] {self.metrics.failed_tasks}\n"
                f"[yellow]Duration:[/yellow] {self.metrics.get_elapsed_time()}",
                title="Download Summary",
                border_style="green"
            ))
            
        except Exception as e:
            self.metrics.status = ServiceStatus.FAILED
            self.metrics.errors.append(str(e))
            logger.error(f"Download service failed: {e}", exc_info=True)
            raise
        
        return self.metrics


class BacktestingService:
    """
    Service 3: Strategy Backtesting with Parallel Execution
    
    Features:
    - Test 100+ strategies across all symbols/timeframes
    - Parallel strategy execution
    - Performance metrics calculation
    - Strategy ranking
    - Results aggregation
    """
    
    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        self.metrics = ServiceMetrics("BacktestingService", ServiceStatus.IDLE)
        self.results: List[Dict] = []
        self.lock = threading.Lock()
    
    def run_backtest(
        self,
        symbols: Dict[str, List[str]],
        timeframes: List[str],
        strategies: List[str]
    ) -> ServiceMetrics:
        """
        Run backtests across all combinations
        
        Args:
            symbols: Dictionary mapping category to list of symbols
            timeframes: List of timeframes
            strategies: List of strategy names
        
        Returns:
            Service metrics with backtest results
        """
        self.metrics.status = ServiceStatus.RUNNING
        self.metrics.start_time = datetime.now()
        
        # Calculate total tests
        total_symbols = sum(len(s) for s in symbols.values())
        total_tests = total_symbols * len(timeframes) * len(strategies)
        self.metrics.total_tasks = total_tests
        
        console.print(Panel(
            f"[bold magenta]Starting Backtesting Service[/bold magenta]\n\n"
            f"[yellow]Symbols:[/yellow] {total_symbols:,}\n"
            f"[yellow]Timeframes:[/yellow] {len(timeframes)}\n"
            f"[yellow]Strategies:[/yellow] {len(strategies)}\n"
            f"[yellow]Total Tests:[/yellow] {total_tests:,}\n"
            f"[yellow]Workers:[/yellow] {self.max_workers}",
            title="Backtesting Service",
            border_style="magenta"
        ))
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                
                task = progress.add_task(
                    f"[magenta]Backtesting {total_tests:,} combinations...",
                    total=total_tests
                )
                
                # TODO: Implement actual backtesting logic
                # For now, simulate progress
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = []
                    
                    for category, symbol_list in symbols.items():
                        for symbol in symbol_list:
                            for timeframe in timeframes:
                                for strategy in strategies:
                                    future = executor.submit(
                                        self._run_single_backtest,
                                        category, symbol, timeframe, strategy
                                    )
                                    futures.append(future)
                    
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                            with self.lock:
                                self.results.append(result)
                                self.metrics.completed_tasks += 1
                            progress.update(task, advance=1)
                        except Exception as e:
                            with self.lock:
                                self.metrics.failed_tasks += 1
                                self.metrics.errors.append(str(e))
                            progress.update(task, advance=1)
            
            self.metrics.status = ServiceStatus.COMPLETED
            self.metrics.end_time = datetime.now()
            
            console.print(Panel(
                f"[bold green]✓ Backtesting Complete![/bold green]\n\n"
                f"[yellow]Tests Completed:[/yellow] {self.metrics.completed_tasks:,}\n"
                f"[yellow]Tests Failed:[/yellow] {self.metrics.failed_tasks}\n"
                f"[yellow]Duration:[/yellow] {self.metrics.get_elapsed_time()}",
                title="Backtest Summary",
                border_style="green"
            ))
            
        except Exception as e:
            self.metrics.status = ServiceStatus.FAILED
            self.metrics.errors.append(str(e))
            logger.error(f"Backtesting service failed: {e}", exc_info=True)
            raise
        
        return self.metrics
    
    def _run_single_backtest(
        self,
        category: str,
        symbol: str,
        timeframe: str,
        strategy: str
    ) -> Dict:
        """
        Run a single backtest
        
        Returns:
            Dictionary with backtest results
        """
        # TODO: Implement actual backtesting logic
        # For now, return placeholder
        time.sleep(0.01)  # Simulate work
        
        return {
            'category': category,
            'symbol': symbol,
            'timeframe': timeframe,
            'strategy': strategy,
            'profit_loss': 0.0,
            'win_rate': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0
        }
    
    def get_ranked_strategies(self, top_n: int = 10) -> pd.DataFrame:
        """Get top performing strategies"""
        if not self.results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results)
        # Rank by profit_loss (or other metrics)
        df = df.sort_values('profit_loss', ascending=False)
        return df.head(top_n)


class ServiceOrchestrator:
    """
    Orchestrates all services to run the complete pipeline
    
    Features:
    - Coordinates symbol loading, download, and backtesting
    - Monitors all service metrics
    - Provides unified progress display
    - Handles service failures gracefully
    """
    
    def __init__(self, download_workers: int = 10, backtest_workers: int = 8):
        self.symbol_service = SymbolLoadingService()
        self.download_service = DataDownloadService(max_workers=download_workers)
        self.backtest_service = BacktestingService(max_workers=backtest_workers)
        self.lock = threading.Lock()
    
    def run_full_pipeline(
        self,
        download_data: bool = True,
        run_backtests: bool = False,
        category: Optional[str] = None,
        timeframes: Optional[List[str]] = None,
        strategies: Optional[List[str]] = None
    ):
        """
        Run the complete pipeline
        
        Args:
            download_data: Whether to download historical data
            run_backtests: Whether to run backtests
            category: Optional category filter
            timeframes: List of timeframes (default: all)
            strategies: List of strategies (default: basic set)
        """
        console.print(Panel(
            f"[bold yellow]═══ SERVICE ORCHESTRATOR ═══[/bold yellow]\n\n"
            f"Starting complete data processing pipeline...",
            border_style="yellow",
            title="Fyers Trading Platform"
        ))
        
        # Default timeframes
        if not timeframes:
            timeframes = ['1m', '5m', '15m', '30m', '60m', '1D']
        
        # Default strategies
        if not strategies:
            strategies = ['RSI_Strategy', 'MACD_Strategy', 'MA_Crossover']
        
        try:
            # Step 1: Load Symbols
            console.print("\n[bold cyan]Step 1/3: Loading Symbols...[/bold cyan]")
            symbols = self.symbol_service.load_symbols(category=category)
            total_symbols = sum(len(s) for s in symbols.values())
            console.print(f"[green]✓ Loaded {total_symbols:,} symbols across {len(symbols)} categories[/green]")
            
            # Step 2: Download Historical Data
            if download_data:
                console.print("\n[bold cyan]Step 2/3: Downloading Historical Data...[/bold cyan]")
                start_date = date.today() - timedelta(days=5*365)  # 5 years
                end_date = date.today()
                
                download_metrics = self.download_service.start_bulk_download(
                    symbols=symbols,
                    timeframes=timeframes,
                    start_date=start_date,
                    end_date=end_date,
                    resume=False
                )
                console.print(f"[green]✓ Download service completed[/green]")
            
            # Step 3: Run Backtests
            if run_backtests:
                console.print("\n[bold cyan]Step 3/3: Running Backtests...[/bold cyan]")
                backtest_metrics = self.backtest_service.run_backtest(
                    symbols=symbols,
                    timeframes=timeframes,
                    strategies=strategies
                )
                console.print(f"[green]✓ Backtesting service completed[/green]")
                
                # Show top strategies
                top_strategies = self.backtest_service.get_ranked_strategies(top_n=10)
                if not top_strategies.empty:
                    console.print("\n[bold]Top 10 Strategies:[/bold]")
                    console.print(top_strategies.to_string())
            
            # Final Summary
            console.print(Panel(
                f"[bold green]✓ Pipeline Complete![/bold green]\n\n"
                f"[yellow]Symbols Loaded:[/yellow] {total_symbols:,}\n"
                f"[yellow]Data Downloaded:[/yellow] {'Yes' if download_data else 'Skipped'}\n"
                f"[yellow]Backtests Run:[/yellow] {'Yes' if run_backtests else 'Skipped'}",
                title="Pipeline Summary",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"[bold red]✗ Pipeline failed: {e}[/bold red]")
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise


if __name__ == '__main__':
    """Example usage"""
    
    # Create orchestrator
    orchestrator = ServiceOrchestrator(download_workers=10, backtest_workers=8)
    
    # Run full pipeline (download only for now)
    orchestrator.run_full_pipeline(
        download_data=True,
        run_backtests=False,  # Set to True when backtesting engine is ready
        category='nifty50',  # Start with Nifty 50
        timeframes=['1D']  # Daily data first
    )
