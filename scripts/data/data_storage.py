"""
Parquet file-based data storage module
Replaces MySQL database functionality with efficient Parquet file storage
"""
import os
import sys
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from datetime import datetime, timedelta

# Add core directory to path for constants import
script_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(script_dir, '..', 'core')
sys.path.insert(0, os.path.abspath(core_dir))

from constants import time_zone

class ParquetDataManager:
    """Manages data storage and retrieval using Parquet files"""
    
    def __init__(self, base_data_dir="data/parquet"):
        """
        Initialize Parquet data manager
        
        Args:
            base_data_dir (str): Base directory for storing parquet files
        """
        self.base_data_dir = Path(base_data_dir)
        self.base_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different data types
        self.indices_dir = self.base_data_dir / "indices"
        self.stocks_dir = self.base_data_dir / "stocks" 
        self.options_dir = self.base_data_dir / "options"
        
        for dir_path in [self.indices_dir, self.stocks_dir, self.options_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        # Directory for raw market update messages (SymbolUpdate)
        self.market_updates_dir = self.base_data_dir / "market_updates"
        self.market_updates_dir.mkdir(parents=True, exist_ok=True)
    
    def get_file_path(self, symbol, timeframe):
        """
        Get the file path for a given symbol and timeframe
        
        Args:
            symbol (str): Symbol name (e.g., 'nifty50', 'tatapower')
            timeframe (str): Timeframe (e.g., '1m', '5m', '1D')
            
        Returns:
            Path: Full path to the parquet file
        """
        # Determine which directory based on symbol type
        if any(idx in symbol.lower() for idx in ['nifty', 'bank', 'finnifty', 'indiavix']):
            data_dir = self.indices_dir
        elif symbol.lower().endswith('_option') or 'ce' in symbol.lower() or 'pe' in symbol.lower():
            data_dir = self.options_dir
        else:
            data_dir = self.stocks_dir
            
        filename = f"{symbol}_{timeframe}.parquet"
        return data_dir / filename

    def get_market_update_file(self, symbol: str):
        """
        Get the file path for raw market update (SymbolUpdate) storage
        """
        filename = f"{symbol}_market.parquet"
        return self.market_updates_dir / filename

    def load_market_updates(self, symbol: str, start_date=None, end_date=None):
        """
        Load market update parquet for a symbol. Returns a DataFrame.
        """
        file_path = self.get_market_update_file(symbol)
        if not file_path.exists():
            return pd.DataFrame()

        df = pd.read_parquet(file_path)

        if start_date or end_date:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            if start_date:
                df = df[df['timestamp'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['timestamp'] <= pd.to_datetime(end_date)]

        return df

    def load_latest_market_update(self, symbol: str):
        """
        Return the most recent market update row for a symbol as a dict, or None if not available.
        """
        df = self.load_market_updates(symbol)
        if df.empty:
            return None
        # Ensure timestamp is datetime and sort
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        row = df.iloc[-1]
        return row.to_dict()

    def save_market_update(self, df: pd.DataFrame, symbol: str, mode: str = 'append'):
        """
        Save raw market update DataFrame to Parquet. This method accepts an arbitrary
        set of columns (as supplied by the WebSocket SymbolUpdate) and persists them
        under data/parquet/market_updates/{symbol}_market.parquet.

        Args:
            df: DataFrame containing market update rows (must have a 'timestamp' column)
            symbol: filename-friendly symbol name (e.g., 'reliance')
            mode: 'append' or 'overwrite'
        """
        if df.empty:
            print(f"Warning: Empty market update DataFrame for {symbol}")
            return

        file_path = self.get_market_update_file(symbol)

        # Ensure timestamp exists and is datetime
        if 'timestamp' not in df.columns:
            df = df.copy()
            df['timestamp'] = pd.to_datetime(datetime.now())
        else:
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

        # If appending, merge with existing data and dedupe on timestamp
        if mode == 'append' and file_path.exists():
            try:
                existing = pd.read_parquet(file_path)
                combined = pd.concat([existing, df], ignore_index=True)
                combined = combined.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
                combined.to_parquet(file_path, index=False)
                print(f"✅ Appended {len(df)} rows to {file_path}")
            except Exception as e:
                print(f"❌ Failed appending market updates for {symbol}: {e}")
        else:
            try:
                df.to_parquet(file_path, index=False)
                print(f"✅ Saved {len(df)} rows to {file_path}")
            except Exception as e:
                print(f"❌ Failed saving market updates for {symbol}: {e}")
    
    def save_data(self, df, symbol, timeframe, mode='append'):
        """
        Save DataFrame to Parquet file
        
        Args:
            df (pd.DataFrame): Data to save
            symbol (str): Symbol name
            timeframe (str): Timeframe
            mode (str): 'append' or 'overwrite'
        """
        if df.empty:
            print(f"Warning: Empty DataFrame for {symbol}_{timeframe}")
            return
            
        file_path = self.get_file_path(symbol, timeframe)
        
        # Ensure proper column order and types
        expected_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in expected_columns):
            print(f"Warning: Missing expected columns for {symbol}_{timeframe}")
            print(f"Expected: {expected_columns}")
            print(f"Found: {list(df.columns)}")
            return
            
        # Standardize data types
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        # Remove duplicates and sort by timestamp
        df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
        
        if mode == 'append' and file_path.exists():
            # Load existing data and append
            existing_df = pd.read_parquet(file_path)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
            combined_df.to_parquet(file_path, index=False)
            print(f"✅ Appended {len(df)} rows to {file_path}")
        else:
            # Save new file or overwrite
            df.to_parquet(file_path, index=False)
            print(f"✅ Saved {len(df)} rows to {file_path}")
    
    def load_data(self, symbol, timeframe, start_date=None, end_date=None):
        """
        Load data from Parquet file
        
        Args:
            symbol (str): Symbol name
            timeframe (str): Timeframe
            start_date (str or datetime): Start date filter
            end_date (str or datetime): End date filter
            
        Returns:
            pd.DataFrame: Loaded data
        """
        file_path = self.get_file_path(symbol, timeframe)
        
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return pd.DataFrame()
            
        df = pd.read_parquet(file_path)
        
        # Apply date filters if provided
        if start_date or end_date:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            if start_date:
                df = df[df['timestamp'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['timestamp'] <= pd.to_datetime(end_date)]
                
        return df
    
    def get_last_timestamp(self, symbol, timeframe):
        """
        Get the last timestamp from a data file
        
        Args:
            symbol (str): Symbol name
            timeframe (str): Timeframe
            
        Returns:
            datetime or None: Last timestamp or None if file doesn't exist
        """
        file_path = self.get_file_path(symbol, timeframe)
        
        if not file_path.exists():
            return None
            
        try:
            # Read only the timestamp column for efficiency
            df = pd.read_parquet(file_path, columns=['timestamp'])
            if df.empty:
                return None
            return df['timestamp'].max()
        except Exception as e:
            print(f"Error reading last timestamp from {file_path}: {e}")
            return None
    
    def list_available_data(self):
        """
        List all available data files
        
        Returns:
            dict: Dictionary with data categories and their files
        """
        available_data = {
            'indices': [],
            'stocks': [],
            'options': []
        }
        
        for category, directory in [
            ('indices', self.indices_dir),
            ('stocks', self.stocks_dir), 
            ('options', self.options_dir)
        ]:
            if directory.exists():
                parquet_files = list(directory.glob("*.parquet"))
                available_data[category] = [f.stem for f in parquet_files]
                
        return available_data
    
    def get_data_info(self, symbol, timeframe):
        """
        Get information about a data file
        
        Args:
            symbol (str): Symbol name
            timeframe (str): Timeframe
            
        Returns:
            dict: Information about the data file
        """
        file_path = self.get_file_path(symbol, timeframe)
        
        if not file_path.exists():
            return {"exists": False}
            
        df = pd.read_parquet(file_path)
        
        return {
            "exists": True,
            "file_path": str(file_path),
            "total_rows": len(df),
            "start_date": df['timestamp'].min(),
            "end_date": df['timestamp'].max(),
            "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
        }

def get_parquet_manager():
    """Get a ParquetDataManager instance"""
    return ParquetDataManager()

# For backward compatibility - replace MySQL connection functions
def get_mysql_connection():
    """Deprecated: Use get_parquet_manager() instead"""
    raise NotImplementedError("MySQL support has been replaced with Parquet files. Use get_parquet_manager() instead.")

def get_mongo_connection():
    """Deprecated: Use get_parquet_manager() instead"""
    raise NotImplementedError("MongoDB support has been replaced with Parquet files. Use get_parquet_manager() instead.")

if __name__ == "__main__":
    # Test the ParquetDataManager
    manager = get_parquet_manager()
    print("📊 Parquet Data Manager initialized")
    print(f"📁 Base directory: {manager.base_data_dir}")
    
    # List available data
    available = manager.list_available_data()
    print("\n📋 Available data:")
    for category, files in available.items():
        print(f"  {category}: {len(files)} files")
        for file in files[:5]:  # Show first 5 files
            print(f"    - {file}")
        if len(files) > 5:
            print(f"    ... and {len(files) - 5} more")