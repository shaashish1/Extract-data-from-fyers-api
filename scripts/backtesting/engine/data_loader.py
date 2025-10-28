"""
Backtesting Data Loader
========================
Load historical OHLCV data from Parquet files for vectorbt backtesting.

Supports:
- Single symbol loading
- Multi-symbol batch loading  
- Multiple timeframes (1m, 5m, 15m, 1h, 1D)
- Date range filtering
- Symbol category filtering (Nifty50, BankNifty, etc.)

Created: October 28, 2025
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.data.data_storage import get_parquet_manager
from scripts.symbol_discovery.fyers_json_symbol_discovery import FyersJSONSymbolDiscovery

logger = logging.getLogger(__name__)


class BacktestDataLoader:
    """
    Load and prepare data for vectorbt backtesting.
    
    Features:
    - Automatic symbol discovery integration
    - Multi-symbol DataFrame preparation
    - Timeframe conversion support
    - Missing data handling
    - Date alignment across symbols
    """
    
    def __init__(self):
        """Initialize data loader with Parquet manager."""
        self.manager = get_parquet_manager()
        self.discovery = FyersJSONSymbolDiscovery()
        logger.info("Backtest Data Loader initialized")
    
    def load_symbol(
        self, 
        symbol: str, 
        timeframe: str = '1D',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Load single symbol data.
        
        Args:
            symbol: Symbol ticker (e.g., 'nifty50', 'reliance')
            timeframe: Data timeframe ('1m', '5m', '15m', '1h', '1D')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            columns: Columns to load (default: all OHLCV)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            logger.info(f"Loading {symbol} ({timeframe}) from {start_date or 'earliest'} to {end_date or 'latest'}")
            
            df = self.manager.load_data(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            
            if df.empty:
                logger.warning(f"No data found for {symbol} ({timeframe})")
                return pd.DataFrame()
            
            # Select columns if specified
            if columns:
                available_cols = [c for c in columns if c in df.columns]
                df = df[available_cols]
            
            # Ensure timestamp is index
            if 'timestamp' in df.columns:
                df = df.set_index('timestamp')
            
            logger.info(f"Loaded {len(df)} rows for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading {symbol}: {e}")
            return pd.DataFrame()
    
    def load_multiple_symbols(
        self,
        symbols: List[str],
        timeframe: str = '1D',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        column: str = 'close'
    ) -> pd.DataFrame:
        """
        Load multiple symbols into single DataFrame (vectorbt format).
        
        Args:
            symbols: List of symbol tickers
            timeframe: Data timeframe
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            column: Column to extract (default: 'close')
        
        Returns:
            DataFrame with columns = symbols, index = timestamp, values = prices
        """
        logger.info(f"Loading {len(symbols)} symbols for {timeframe} backtesting")
        
        data_dict = {}
        
        for symbol in symbols:
            df = self.load_symbol(symbol, timeframe, start_date, end_date)
            
            if not df.empty and column in df.columns:
                data_dict[symbol] = df[column]
            else:
                logger.warning(f"Skipping {symbol} - no {column} data")
        
        if not data_dict:
            logger.error("No data loaded for any symbol!")
            return pd.DataFrame()
        
        # Combine into single DataFrame
        combined_df = pd.DataFrame(data_dict)
        
        # Forward fill missing values (up to 5 periods)
        combined_df = combined_df.ffill(limit=5)
        
        # Drop rows with any remaining NaN
        initial_rows = len(combined_df)
        combined_df = combined_df.dropna()
        dropped = initial_rows - len(combined_df)
        
        if dropped > 0:
            logger.info(f"Dropped {dropped} rows with missing data")
        
        logger.info(f"Loaded {len(combined_df)} rows × {len(combined_df.columns)} symbols")
        return combined_df
    
    def load_nifty50_data(
        self,
        timeframe: str = '1D',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load Nifty50 constituent data.
        
        Args:
            timeframe: Data timeframe
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with all Nifty50 stocks (close prices)
        """
        logger.info("Loading Nifty50 constituents data")
        
        # Get Nifty50 symbols from discovery
        nifty50_symbols = self.discovery.get_nifty50_constituents()
        
        if not nifty50_symbols:
            logger.error("Failed to get Nifty50 constituents")
            return pd.DataFrame()
        
        # Extract symbol tickers (convert from full format if needed)
        tickers = []
        for symbol_info in nifty50_symbols:
            # Handle both dict and string formats
            if isinstance(symbol_info, dict):
                ticker = symbol_info.get('symbol', '').replace('NSE:', '').replace('-EQ', '')
            else:
                ticker = str(symbol_info).replace('NSE:', '').replace('-EQ', '')
            
            if ticker:
                tickers.append(ticker.lower())
        
        logger.info(f"Found {len(tickers)} Nifty50 symbols")
        
        # Load data for all symbols
        return self.load_multiple_symbols(
            symbols=tickers,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            column='close'
        )
    
    def load_index_data(
        self,
        index_name: str = 'nifty50',
        timeframe: str = '1D',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load index data (NIFTY50, BANKNIFTY, etc.).
        
        Args:
            index_name: Index name ('nifty50', 'niftybank', 'finnifty')
            timeframe: Data timeframe
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with index OHLCV data
        """
        return self.load_symbol(
            symbol=index_name.lower(),
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_available_data_summary(self) -> Dict:
        """
        Get summary of available data in storage.
        
        Returns:
            Dictionary with data availability info
        """
        logger.info("Scanning available data...")
        
        available_data = self.manager.list_available_data()
        
        summary = {
            'total_files': 0,
            'symbols': set(),
            'timeframes': set(),
            'categories': {'indices': 0, 'stocks': 0, 'options': 0}
        }
        
        # Parse the data structure
        for category, files in available_data.items():
            summary['categories'][category] = len(files)
            summary['total_files'] += len(files)
            
            for file_stem in files:
                # Parse format: symbol_timeframe (e.g., 'nifty50_1D')
                parts = file_stem.rsplit('_', 1)
                if len(parts) == 2:
                    symbol, timeframe = parts
                    summary['symbols'].add(symbol)
                    summary['timeframes'].add(timeframe)
                else:
                    summary['symbols'].add(file_stem)
        
        summary['symbols'] = sorted(list(summary['symbols']))
        summary['timeframes'] = sorted(list(summary['timeframes']))
        
        logger.info(f"Found {summary['total_files']} data files across {len(summary['symbols'])} symbols")
        
        return summary
    
    def prepare_for_vectorbt(
        self,
        symbols: Union[str, List[str]],
        timeframe: str = '1D',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ohlcv: bool = False
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Prepare data in vectorbt-ready format.
        
        Args:
            symbols: Single symbol or list of symbols
            timeframe: Data timeframe
            start_date: Start date
            end_date: End date
            ohlcv: If True, return dict with OHLCV DataFrames; else just close
        
        Returns:
            DataFrame (close prices) or Dict of DataFrames (OHLCV)
        """
        # Handle single symbol
        if isinstance(symbols, str):
            symbols = [symbols]
        
        if not ohlcv:
            # Just return close prices
            return self.load_multiple_symbols(
                symbols=symbols,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                column='close'
            )
        
        # Return full OHLCV
        logger.info("Preparing full OHLCV data for vectorbt")
        
        ohlcv_dict = {
            'open': {},
            'high': {},
            'low': {},
            'close': {},
            'volume': {}
        }
        
        for symbol in symbols:
            df = self.load_symbol(symbol, timeframe, start_date, end_date)
            
            if df.empty:
                continue
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in df.columns:
                    ohlcv_dict[col][symbol] = df[col]
        
        # Convert to DataFrames
        result = {}
        for col, data in ohlcv_dict.items():
            if data:
                result[col] = pd.DataFrame(data)
                # Align and fill missing data
                result[col] = result[col].ffill(limit=5).dropna()
        
        logger.info(f"Prepared OHLCV data: {len(result)} price types, {len(symbols)} symbols")
        return result


def demo_data_loader():
    """Demo: Load data for backtesting."""
    print("="*80)
    print("Backtest Data Loader Demo")
    print("="*80)
    
    loader = BacktestDataLoader()
    
    # Show available data
    print("\n📊 Available Data Summary:")
    print("-"*80)
    summary = loader.get_available_data_summary()
    print(f"Total files: {summary['total_files']}")
    print(f"Symbols: {', '.join(summary['symbols'][:10])}{'...' if len(summary['symbols']) > 10 else ''}")
    print(f"Timeframes: {', '.join(summary['timeframes'])}")
    print(f"Categories: {summary['categories']}")
    
    # Load single index
    print("\n📈 Loading NIFTY50 Index:")
    print("-"*80)
    nifty = loader.load_index_data('nifty50', '1D')
    if not nifty.empty:
        print(f"Loaded {len(nifty)} rows")
        print(f"Date range: {nifty.index[0]} to {nifty.index[-1]}")
        print(f"\nFirst 5 rows:")
        print(nifty.head())
    
    # Load multiple symbols
    print("\n📊 Loading Multiple Symbols:")
    print("-"*80)
    symbols = ['nifty50', 'niftybank', 'finnifty']
    multi_data = loader.load_multiple_symbols(symbols, '1D', column='close')
    if not multi_data.empty:
        print(f"Loaded {len(multi_data)} rows × {len(multi_data.columns)} symbols")
        print(f"\nFirst 5 rows:")
        print(multi_data.head())
    
    print("\n" + "="*80)
    print("✅ Data Loader Ready for Backtesting!")
    print("="*80)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    demo_data_loader()
