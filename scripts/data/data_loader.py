#!/usr/bin/env python3
"""
Historical Data Loader
======================

Utility to load historical data from organized Parquet files.

Features:
- Load data by symbol and timeframe
- Date range filtering
- Efficient querying from month-organized files
- List available symbols
- Data validation

Usage:
    from scripts.data.data_loader import HistoricalDataLoader
    
    loader = HistoricalDataLoader()
    df = loader.load_symbol('nifty50', 'RELIANCE', '1D')

Author: Fyers Trading Platform
Created: October 30, 2025
"""

from pathlib import Path
import pandas as pd
from datetime import datetime, date
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class HistoricalDataLoader:
    """
    Utility to load historical data from Parquet files organized by month
    """
    
    def __init__(self, base_path: str = 'data/parquet'):
        self.base_path = Path(base_path)
        
        if not self.base_path.exists():
            logger.warning(f"Data directory not found: {self.base_path}")
    
    def load_symbol(
        self,
        category: str,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Load data for a symbol
        
        Args:
            category: Symbol category (nifty50, etfs, all_equities, etc.)
            symbol: Symbol name (RELIANCE, TCS, etc.)
            timeframe: Timeframe (1m, 5m, 15m, 30m, 60m, 1D)
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume, date
        """
        symbol_path = self.base_path / category / symbol / timeframe
        
        if not symbol_path.exists():
            raise FileNotFoundError(f"No data found for {category}/{symbol}/{timeframe}")
        
        all_data = []
        
        # Get all Parquet files
        parquet_files = list(symbol_path.rglob('*.parquet'))
        
        if not parquet_files:
            logger.warning(f"No Parquet files found in {symbol_path}")
            return pd.DataFrame()
        
        # Load each file
        for file in parquet_files:
            try:
                df = pd.read_parquet(file)
                all_data.append(df)
            except Exception as e:
                logger.error(f"Error loading {file}: {e}")
        
        if not all_data:
            return pd.DataFrame()
        
        # Combine all data
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
        
        # Add date column
        combined['date'] = pd.to_datetime(combined['timestamp'], unit='s')
        
        # Filter by date range if specified
        if start_date:
            combined = combined[combined['date'] >= start_date]
        if end_date:
            combined = combined[combined['date'] <= end_date]
        
        # Reset index
        combined = combined.reset_index(drop=True)
        
        return combined
    
    def load_date_range(
        self,
        category: str,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Load data for a specific date range (optimized for month-based storage)
        
        Args:
            category: Symbol category
            symbol: Symbol name
            timeframe: Timeframe
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with data in the specified date range
        """
        base_path = self.base_path / category / symbol / timeframe
        
        if not base_path.exists():
            raise FileNotFoundError(f"No data found for {category}/{symbol}/{timeframe}")
        
        all_data = []
        
        # Iterate through years and months in the range
        current_date = start_date.replace(day=1)
        end_month = end_date.replace(day=1)
        
        while current_date <= end_month:
            year = current_date.year
            month = current_date.month
            
            file_path = base_path / str(year) / f"{month:02d}" / f"{symbol}_{timeframe}_{year}_{month:02d}.parquet"
            
            if file_path.exists():
                try:
                    df = pd.read_parquet(file_path)
                    all_data.append(df)
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")
            
            # Move to next month
            if month == 12:
                current_date = current_date.replace(year=year + 1, month=1)
            else:
                current_date = current_date.replace(month=month + 1)
        
        if not all_data:
            return pd.DataFrame()
        
        # Combine all data
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
        combined['date'] = pd.to_datetime(combined['timestamp'], unit='s')
        
        # Filter to exact date range
        combined = combined[
            (combined['date'] >= start_date) & 
            (combined['date'] <= end_date)
        ]
        
        return combined.reset_index(drop=True)
    
    def load_multiple_symbols(
        self,
        category: str,
        symbols: List[str],
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        Load data for multiple symbols
        
        Args:
            category: Symbol category
            symbols: List of symbol names
            timeframe: Timeframe
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        data_dict = {}
        
        for symbol in symbols:
            try:
                df = self.load_symbol(category, symbol, timeframe, start_date, end_date)
                if not df.empty:
                    data_dict[symbol] = df
            except FileNotFoundError:
                logger.warning(f"No data found for {symbol}")
            except Exception as e:
                logger.error(f"Error loading {symbol}: {e}")
        
        return data_dict
    
    def get_available_symbols(self, category: str) -> List[str]:
        """
        Get list of available symbols in a category
        
        Args:
            category: Category name
        
        Returns:
            List of symbol names
        """
        category_path = self.base_path / category
        
        if not category_path.exists():
            return []
        
        symbols = [d.name for d in category_path.iterdir() if d.is_dir()]
        return sorted(symbols)
    
    def get_available_categories(self) -> List[str]:
        """
        Get list of available categories
        
        Returns:
            List of category names
        """
        if not self.base_path.exists():
            return []
        
        categories = [d.name for d in self.base_path.iterdir() if d.is_dir()]
        return sorted(categories)
    
    def get_available_timeframes(self, category: str, symbol: str) -> List[str]:
        """
        Get list of available timeframes for a symbol
        
        Args:
            category: Category name
            symbol: Symbol name
        
        Returns:
            List of timeframe codes
        """
        symbol_path = self.base_path / category / symbol
        
        if not symbol_path.exists():
            return []
        
        timeframes = [d.name for d in symbol_path.iterdir() if d.is_dir()]
        return sorted(timeframes)
    
    def get_date_range(self, category: str, symbol: str, timeframe: str) -> Optional[Tuple[datetime, datetime]]:
        """
        Get the available date range for a symbol
        
        Args:
            category: Category name
            symbol: Symbol name
            timeframe: Timeframe
        
        Returns:
            Tuple of (start_date, end_date) or None if no data
        """
        try:
            df = self.load_symbol(category, symbol, timeframe)
            if df.empty:
                return None
            
            start_date = df['date'].min()
            end_date = df['date'].max()
            return (start_date, end_date)
        except Exception as e:
            logger.error(f"Error getting date range: {e}")
            return None
    
    def validate_data(self, category: str, symbol: str, timeframe: str) -> dict:
        """
        Validate data quality for a symbol
        
        Args:
            category: Category name
            symbol: Symbol name
            timeframe: Timeframe
        
        Returns:
            Dictionary with validation results
        """
        try:
            df = self.load_symbol(category, symbol, timeframe)
            
            if df.empty:
                return {'valid': False, 'error': 'No data found'}
            
            # Check for required columns
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                return {
                    'valid': False,
                    'error': f'Missing columns: {missing_cols}'
                }
            
            # Check for null values
            null_counts = df[required_cols].isnull().sum()
            has_nulls = null_counts.sum() > 0
            
            # Check for duplicates
            duplicate_count = df['timestamp'].duplicated().sum()
            
            # Check for data consistency
            invalid_ohlc = (
                (df['high'] < df['low']) |
                (df['high'] < df['open']) |
                (df['high'] < df['close']) |
                (df['low'] > df['open']) |
                (df['low'] > df['close'])
            ).sum()
            
            date_range = self.get_date_range(category, symbol, timeframe)
            
            return {
                'valid': not has_nulls and duplicate_count == 0 and invalid_ohlc == 0,
                'record_count': len(df),
                'null_values': null_counts.to_dict(),
                'duplicate_timestamps': int(duplicate_count),
                'invalid_ohlc_count': int(invalid_ohlc),
                'date_range': date_range,
                'warnings': []
            }
        
        except Exception as e:
            return {'valid': False, 'error': str(e)}


def get_data_loader(base_path: str = 'data/parquet') -> HistoricalDataLoader:
    """
    Factory function to get a HistoricalDataLoader instance
    
    Args:
        base_path: Base path for Parquet data
    
    Returns:
        HistoricalDataLoader instance
    """
    return HistoricalDataLoader(base_path)


if __name__ == '__main__':
    """Example usage"""
    
    loader = HistoricalDataLoader()
    
    # Get available categories
    categories = loader.get_available_categories()
    print(f"Available categories: {categories}")
    
    if categories:
        # Get symbols in first category
        symbols = loader.get_available_symbols(categories[0])
        print(f"\nSymbols in {categories[0]}: {len(symbols)}")
        
        if symbols:
            # Get timeframes for first symbol
            timeframes = loader.get_available_timeframes(categories[0], symbols[0])
            print(f"Timeframes for {symbols[0]}: {timeframes}")
            
            if timeframes:
                # Load data
                try:
                    df = loader.load_symbol(categories[0], symbols[0], timeframes[0])
                    print(f"\nLoaded {len(df)} records for {symbols[0]} {timeframes[0]}")
                    print(df.head())
                    
                    # Validate data
                    validation = loader.validate_data(categories[0], symbols[0], timeframes[0])
                    print(f"\nValidation: {validation}")
                except Exception as e:
                    print(f"Error: {e}")
