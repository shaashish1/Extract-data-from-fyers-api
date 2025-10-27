# Fyers API data extraction to Parquet files | fyers API V3 history data
import os
import time
import math
import pandas as pd
import datetime as dt
from constants import *
from datetime import datetime, date, timedelta
from my_fyers_model import MyFyersModel
from data_storage import get_parquet_manager

# Initialize components
fy_model = MyFyersModel()
parquet_manager = get_parquet_manager()
today_date = datetime.today().strftime("%Y-%m-%d")

# Configuration for data extraction
SYMBOL = 'NSE:TATAPOWER-EQ'  # Change this to extract different symbols
SYMBOL_NAME = 'tatapower'    # Used for file naming
TIMEFRAME = '1'              # 1 = 1 minute, 'D' = daily, etc.
TIMEFRAME_NAME = '1m'        # Used for file naming

# Date range for historical data
start_date = date(2017, 1, 1)
end_date = date(2017, 4, 10)

print(f"📊 Extracting data for {SYMBOL_NAME}")
print(f"📅 Date range: {start_date} to {end_date}")
print(f"⏱️  Timeframe: {TIMEFRAME_NAME}")

# Calculate number of API calls needed (100 days per call limit)
loop = math.ceil((date.today() - start_date).days / 100)
print(f"🔄 API calls needed: {loop}")

hist_data = pd.DataFrame()

def get_history_data(range_from, range_to, resolution, symbol):
    """
    Fetch historical data from Fyers API
    
    Args:
        range_from (date): Start date
        range_to (date): End date  
        resolution (str): Timeframe resolution
        symbol (str): Symbol to fetch
        
    Returns:
        pd.DataFrame: Historical data
    """
    try:
        data = {
            "symbol": symbol,
            "resolution": str(resolution),
            "date_format": "1",
            "range_from": range_from.strftime("%Y-%m-%d"),
            "range_to": range_to.strftime("%Y-%m-%d"),
            "cont_flag": "1",
            "oi_flag": "1"
        }
        
        print(f"📡 Fetching data: {range_from} to {range_to}")
        response = fy_model.get_history(data=data)
        
        if response.get('s') != 'ok':
            print(f"❌ API Error: {response.get('message', 'Unknown error')}")
            return pd.DataFrame()
            
        # Convert response to DataFrame
        candles = response.get('candles', [])
        if not candles:
            print(f"⚠️  No data received for {range_from} to {range_to}")
            return pd.DataFrame()
            
        df = pd.DataFrame(candles)
        df.columns = ["epoch", "open", "high", "low", "close", "volume"]

        # Convert epoch to timestamp with proper timezone handling
        df['timestamp'] = pd.to_datetime(df['epoch'], unit='s')
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(time_zone)
        df['timestamp'] = df['timestamp'].dt.tz_localize(None)
        
        # Select and order columns
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df.drop_duplicates(inplace=True)
        
        print(f"✅ Fetched {len(df)} rows")
        return df
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return pd.DataFrame()

def extract_historical_data():
    """Extract historical data and save to Parquet files"""
    global hist_data
    current_start = start_date
    current_end = end_date
    
    print("\n🚀 Starting historical data extraction...")
    
    for i in range(loop):
        print(f"\n📊 Progress: {i+1}/{loop}")
        
        # Fetch data for current date range
        batch_data = get_history_data(current_start, current_end, TIMEFRAME, SYMBOL)
        
        if not batch_data.empty:
            hist_data = pd.concat([hist_data, batch_data], axis=0, ignore_index=True)
            
        # Rate limiting - respect API limits
        time.sleep(1)
        
        # Move to next date range
        current_start = current_start + timedelta(days=100)
        current_end = current_end + timedelta(days=100)
        
        # Save intermediate data every 10 calls to prevent data loss
        if (i + 1) % 10 == 0 and not hist_data.empty:
            print(f"💾 Saving intermediate data ({len(hist_data)} rows)...")
            parquet_manager.save_data(hist_data, SYMBOL_NAME, TIMEFRAME_NAME, mode='append')
            hist_data = pd.DataFrame()  # Clear memory
    
    # Save any remaining data
    if not hist_data.empty:
        print(f"💾 Saving final batch ({len(hist_data)} rows)...")
        parquet_manager.save_data(hist_data, SYMBOL_NAME, TIMEFRAME_NAME, mode='append')

def update_data_incremental():
    """Update data incrementally from last available date"""
    print("\n🔄 Checking for incremental updates...")
    
    last_timestamp = parquet_manager.get_last_timestamp(SYMBOL_NAME, TIMEFRAME_NAME)
    
    if last_timestamp is None:
        print("📂 No existing data found. Running full extraction...")
        extract_historical_data()
        return
    
    # Calculate date range for update
    last_date = last_timestamp.date()
    update_start = last_date + timedelta(days=1)
    update_end = datetime.today().date()
    
    if update_start >= update_end:
        print("✅ Data is up to date!")
        return
        
    print(f"📅 Updating from {update_start} to {update_end}")
    
    # Fetch missing data
    missing_data = get_history_data(update_start, update_end, TIMEFRAME, SYMBOL)
    
    if not missing_data.empty:
        parquet_manager.save_data(missing_data, SYMBOL_NAME, TIMEFRAME_NAME, mode='append')
        print(f"✅ Added {len(missing_data)} new rows")
    else:
        print("ℹ️  No new data available")

def show_data_info():
    """Display information about the stored data"""
    info = parquet_manager.get_data_info(SYMBOL_NAME, TIMEFRAME_NAME)
    
    if info["exists"]:
        print(f"\n📊 Data Summary for {SYMBOL_NAME}_{TIMEFRAME_NAME}:")
        print(f"   📁 File: {info['file_path']}")
        print(f"   📈 Rows: {info['total_rows']:,}")
        print(f"   📅 Date range: {info['start_date']} to {info['end_date']}")
        print(f"   💾 Size: {info['file_size_mb']} MB")
    else:
        print(f"❌ No data found for {SYMBOL_NAME}_{TIMEFRAME_NAME}")

if __name__ == "__main__":
    print("🏗️  Fyers Data Extraction (Parquet Storage)")
    print("=" * 50)
    
    try:
        # Option 1: Extract historical data
        # extract_historical_data()
        
        # Option 2: Update incrementally (recommended for daily runs)
        update_data_incremental()
        
        # Show final data info
        show_data_info()
        
        print("\n🎉 Data extraction completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
        if not hist_data.empty:
            print("💾 Saving partial data...")
            parquet_manager.save_data(hist_data, SYMBOL_NAME, TIMEFRAME_NAME, mode='append')
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if not hist_data.empty:
            print("💾 Saving partial data...")
            parquet_manager.save_data(hist_data, SYMBOL_NAME, TIMEFRAME_NAME, mode='append')