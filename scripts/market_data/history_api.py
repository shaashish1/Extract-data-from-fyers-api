"""
Fyers History API Integration - Enhanced
==========================================

Get historical OHLCV data for symbols with intelligent storage.

Features:
- Multiple resolutions (1m to 1D)
- Auto-pagination for large datasets
- Month/date organized storage
- Batch downloading for multiple symbols
- Incremental updates

API Endpoint: https://api-t1.fyers.in/data/history
Data Limits:
- 1m to 240m: 100 days per request
- 1D: 366 days per request
- History from July 3, 2017

Author: Fyers Trading Platform
Created: October 28, 2025
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import time
import logging
from calendar import monthrange

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.auth.my_fyers_model import MyFyersModel
from scripts.core.rate_limit_manager import get_rate_limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FyersHistoryAPI:
    """
    Enhanced Fyers History API Wrapper
    
    Features:
    - Intelligent date range splitting
    - Month-wise data organization
    - Auto-retry with rate limiting
    - Comprehensive data storage
    """
    
    # Resolution limits (days per request)
    RESOLUTION_LIMITS = {
        '1': 100, '2': 100, '3': 100, '5': 100, '10': 100,
        '15': 100, '20': 100, '30': 100, '45': 100, '60': 100,
        '120': 100, '180': 100, '240': 100,
        '1D': 366, 'D': 366
    }
    
    # Available resolutions
    RESOLUTIONS = ['1', '2', '3', '5', '10', '15', '20', '30', '45', '60', '120', '180', '240', '1D', 'D']
    
    def __init__(self):
        """Initialize History API with rate limiting"""
        self.fyers = MyFyersModel()
        self.limiter = get_rate_limiter()
        logger.info("Fyers History API initialized with rate limiting")
    
    def get_history(self, symbol: str, resolution: str, 
                   from_date: str, to_date: str,
                   cont_flag: int = 0) -> Optional[pd.DataFrame]:
        """
        Get historical data for a symbol.
        
        Args:
            symbol: Symbol ticker (e.g., "NSE:SBIN-EQ")
            resolution: Candle resolution (1, 5, 15, 60, 1D, etc.)
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            cont_flag: 1 for continuous futures data
        
        Returns:
            DataFrame with OHLCV data or None
        """
        try:
            logger.info(f"Fetching {resolution} history for {symbol}: {from_date} to {to_date}")
            
            # Wait if needed to respect rate limits
            self.limiter.wait_if_needed()
            
            data = {
                "symbol": symbol,
                "resolution": resolution,
                "date_format": "1",  # Use date format (not epoch)
                "range_from": from_date,
                "range_to": to_date,
                "cont_flag": cont_flag
            }
            
            response = self.fyers.get_fyre_model().history(data=data)
            
            # Record request success/failure
            success = response and response.get('s') == 'ok'
            self.limiter.record_request(success)
            
            if success:
                candles = response.get('candles', [])
                
                if candles:
                    # Convert to DataFrame
                    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    
                    # Convert timestamp to datetime
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                    
                    logger.info(f"Fetched {len(df)} candles")
                    return df
                else:
                    logger.warning(f"No candles data for {symbol}")
                    return None
            else:
                logger.error(f"History API error: {response}")
                return None
                
        except RuntimeError as e:
            # Rate limit violation - stop execution
            logger.critical(f"RATE LIMIT VIOLATION: {e}")
            logger.critical("Stopping execution to prevent daily API block")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch history: {e}")
            return None
    
    def split_date_range(self, from_date: str, to_date: str, resolution: str) -> List[Tuple[str, str]]:
        """
        Split date range into API-compliant chunks.
        
        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            resolution: Candle resolution
        
        Returns:
            List of (from_date, to_date) tuples
        """
        max_days = self.RESOLUTION_LIMITS.get(resolution, 100)
        
        start = datetime.strptime(from_date, '%Y-%m-%d')
        end = datetime.strptime(to_date, '%Y-%m-%d')
        
        ranges = []
        current = start
        
        while current < end:
            chunk_end = min(current + timedelta(days=max_days - 1), end)
            ranges.append((
                current.strftime('%Y-%m-%d'),
                chunk_end.strftime('%Y-%m-%d')
            ))
            current = chunk_end + timedelta(days=1)
        
        return ranges
    
    def get_history_complete(self, symbol: str, resolution: str,
                            from_date: str, to_date: str,
                            rate_limit: float = 1.0) -> Optional[pd.DataFrame]:
        """
        Get complete historical data with auto-pagination.
        
        Args:
            symbol: Symbol ticker
            resolution: Candle resolution
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            rate_limit: Delay between requests (seconds)
        
        Returns:
            Complete DataFrame with all data
        """
        # Split date range
        ranges = self.split_date_range(from_date, to_date, resolution)
        
        logger.info(f"Fetching {len(ranges)} date range chunks for {symbol}")
        
        dfs = []
        for i, (start, end) in enumerate(ranges, 1):
            logger.info(f"Chunk {i}/{len(ranges)}: {start} to {end}")
            
            df = self.get_history(symbol, resolution, start, end)
            
            if df is not None and not df.empty:
                dfs.append(df)
            
            # Rate limiting
            if i < len(ranges):
                time.sleep(rate_limit)
        
        # Combine all chunks
        if dfs:
            combined = pd.concat(dfs, ignore_index=True)
            combined = combined.drop_duplicates(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)
            logger.info(f"Total candles: {len(combined)}")
            return combined
        else:
            logger.warning("No data retrieved")
            return None
    
    def get_history_by_month(self, symbol: str, resolution: str,
                            year: int, month: int) -> Optional[pd.DataFrame]:
        """
        Get historical data for a specific month.
        
        Args:
            symbol: Symbol ticker
            resolution: Candle resolution
            year: Year (e.g., 2025)
            month: Month (1-12)
        
        Returns:
            DataFrame with month's data
        """
        # Calculate month date range
        first_day = datetime(year, month, 1)
        last_day_num = monthrange(year, month)[1]
        last_day = datetime(year, month, last_day_num)
        
        from_date = first_day.strftime('%Y-%m-%d')
        to_date = last_day.strftime('%Y-%m-%d')
        
        # Don't fetch future months
        if first_day > datetime.now():
            logger.warning(f"Skipping future month: {year}-{month:02d}")
            return None
        
        return self.get_history_complete(symbol, resolution, from_date, to_date)
    
    def save_history_by_month(self, symbol: str, resolution: str,
                             from_year: int, from_month: int,
                             to_year: Optional[int] = None, to_month: Optional[int] = None):
        """
        Download and save historical data organized by month.
        
        Args:
            symbol: Symbol ticker
            resolution: Candle resolution
            from_year: Start year
            from_month: Start month
            to_year: End year (default: current year)
            to_month: End month (default: current month)
        """
        if to_year is None:
            to_year = datetime.now().year
        if to_month is None:
            to_month = datetime.now().month
        
        # Create base directory
        safe_symbol = symbol.replace(":", "_").replace("-", "_")
        base_dir = project_root / "data" / "history" / safe_symbol / resolution
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Iterate through months
        current = datetime(from_year, from_month, 1)
        end = datetime(to_year, to_month, 1)
        
        while current <= end:
            year = current.year
            month = current.month
            
            month_str = f"{year}_{month:02d}"
            filepath = base_dir / f"{month_str}.parquet"
            
            # Skip if already exists
            if filepath.exists():
                logger.info(f"Skipping {month_str} (already exists)")
            else:
                # Fetch month data
                df = self.get_history_by_month(symbol, resolution, year, month)
                
                if df is not None and not df.empty:
                    # Save to Parquet
                    df.to_parquet(filepath, index=False)
                    logger.info(f"Saved {len(df)} candles to {filepath}")
                else:
                    logger.warning(f"No data for {month_str}")
            
            # Move to next month
            if month == 12:
                current = datetime(year + 1, 1, 1)
            else:
                current = datetime(year, month + 1, 1)
            
            # Rate limiting
            time.sleep(1)
    
    def load_history_range(self, symbol: str, resolution: str,
                          from_date: str, to_date: str) -> Optional[pd.DataFrame]:
        """
        Load historical data from saved files.
        
        Args:
            symbol: Symbol ticker
            resolution: Candle resolution
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with data from files
        """
        safe_symbol = symbol.replace(":", "_").replace("-", "_")
        base_dir = project_root / "data" / "history" / safe_symbol / resolution
        
        if not base_dir.exists():
            logger.warning(f"No saved data for {symbol} {resolution}")
            return None
        
        # Parse dates
        start = datetime.strptime(from_date, '%Y-%m-%d')
        end = datetime.strptime(to_date, '%Y-%m-%d')
        
        # Load relevant month files
        dfs = []
        current = datetime(start.year, start.month, 1)
        end_month = datetime(end.year, end.month, 1)
        
        while current <= end_month:
            month_str = f"{current.year}_{current.month:02d}"
            filepath = base_dir / f"{month_str}.parquet"
            
            if filepath.exists():
                df = pd.read_parquet(filepath)
                dfs.append(df)
            
            # Next month
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)
        
        if dfs:
            combined = pd.concat(dfs, ignore_index=True)
            
            # Filter to date range
            combined['timestamp'] = pd.to_datetime(combined['timestamp'])
            mask = (combined['timestamp'] >= start) & (combined['timestamp'] <= end)
            filtered = combined[mask].sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"Loaded {len(filtered)} candles from saved files")
            return filtered
        else:
            logger.warning("No saved files found")
            return None


def demo_history_api():
    """Demo: Download historical data by month."""
    print("="*80)
    print("Fyers History API Demo")
    print("="*80)
    
    history_api = FyersHistoryAPI()
    
    # Test symbol
    symbol = "NSE:SBIN-EQ"
    resolution = "1D"
    
    # Download last 3 months
    print(f"\nDownloading {resolution} data for {symbol}...")
    print(f"Organizing by month...")
    
    # Get current date
    now = datetime.now()
    
    # Download last 3 months
    history_api.save_history_by_month(
        symbol=symbol,
        resolution=resolution,
        from_year=now.year,
        from_month=max(1, now.month - 2),  # 3 months ago
        to_year=now.year,
        to_month=now.month
    )
    
    print(f"\nData saved to: data/history/{symbol.replace(':', '_').replace('-', '_')}/{resolution}/")
    
    # Load and display sample
    print("\nLoading saved data...")
    df = history_api.load_history_range(
        symbol=symbol,
        resolution=resolution,
        from_date=(now - timedelta(days=30)).strftime('%Y-%m-%d'),
        to_date=now.strftime('%Y-%m-%d')
    )
    
    if df is not None:
        print(f"\nLast 10 candles:")
        print(df.tail(10).to_string(index=False))


if __name__ == "__main__":
    demo_history_api()
