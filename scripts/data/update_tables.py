"""
Update all data tables using Parquet storage (Fyers API only)
Fyers-only implementation without Yahoo Finance fallback for accurate real-time data
"""
import os
import time
import pandas as pd
from constants import *
from datetime import datetime, timedelta
from my_fyers_model import MyFyersModel
from data_storage import get_parquet_manager

# Initialize components
fy_model = MyFyersModel()
parquet_manager = get_parquet_manager()
today_date = datetime.today().strftime("%Y-%m-%d")

def get_symbols_to_update():
    """
    Get list of symbols that need updating based on available data files
    
    Returns:
        dict: Dictionary with symbol info and last dates
    """
    symbols_info = {}
    
    # Check all available data files
    available_data = parquet_manager.list_available_data()
    
    for category, files in available_data.items():
        for file_stem in files:
            if file_stem.endswith('_1D') or file_stem.endswith('_1d'):
                # Extract symbol name and timeframe
                parts = file_stem.split('_')
                if len(parts) >= 2:
                    symbol_name = '_'.join(parts[:-1])
                    timeframe = parts[-1]
                    
                    # Get last timestamp
                    last_timestamp = parquet_manager.get_last_timestamp(symbol_name, timeframe)
                    
                    if last_timestamp:
                        last_date = last_timestamp.strftime("%Y-%m-%d")
                        next_date = (last_timestamp + timedelta(days=1)).strftime("%Y-%m-%d")
                        
                        symbols_info[f"{symbol_name}_{timeframe}"] = {
                            'symbol_name': symbol_name,
                            'timeframe': timeframe,
                            'last_date': last_date,
                            'next_date': next_date,
                            'category': category
                        }
    
    return symbols_info

def get_fyers_symbol_mapping():
    """
    Map symbol names to Fyers API symbol format
    
    Returns:
        dict: Mapping of symbol names to Fyers symbols
    """
    symbol_mapping = {}
    
    # Add option symbols (indices)
    for name, fyers_symbol in option_symbols.items():
        symbol_mapping[name] = fyers_symbol
    
    # Add stock symbols
    for name, fyers_symbol in stocks_option_symbols.items():
        symbol_mapping[name] = fyers_symbol
    
    return symbol_mapping

def update_symbol_with_fyers(symbol_name, timeframe, start_date, end_date):
    """
    Update a symbol using Fyers API
    
    Args:
        symbol_name (str): Symbol name
        timeframe (str): Timeframe
        start_date (str): Start date
        end_date (str): End date
        
    Returns:
        bool: Success status
    """
    fyers_mapping = get_fyers_symbol_mapping()
    fyers_symbol = fyers_mapping.get(symbol_name)
    
    if not fyers_symbol:
        print(f"❌ No Fyers mapping found for {symbol_name}")
        return False
    
    try:
        print(f"📡 Fetching {symbol_name} from Fyers API...")
        
        # Convert timeframe for Fyers API
        if timeframe.upper() in ['1D', '1d']:
            resolution = 'D'
        elif timeframe == '1m':
            resolution = '1'
        elif timeframe == '5m':
            resolution = '5'
        elif timeframe == '15m':
            resolution = '15'
        elif timeframe == '1h':
            resolution = '60'
        else:
            resolution = 'D'  # Default to daily
        
        data = {
            "symbol": fyers_symbol,
            "resolution": resolution,
            "date_format": "1",
            "range_from": start_date,
            "range_to": end_date,
            "cont_flag": "1",
            "oi_flag": "1"
        }
        
        response = fy_model.get_history(data=data)
        
        if response.get('s') != 'ok':
            print(f"❌ Fyers API error: {response.get('message', 'Unknown error')}")
            return False
        
        candles = response.get('candles', [])
        if not candles:
            print(f"⚠️  No new data from Fyers for {symbol_name}")
            return True  # Not an error, just no new data
        
        # Convert to DataFrame
        df = pd.DataFrame(candles)
        df.columns = ["epoch", "open", "high", "low", "close", "volume"]
        
        # Convert timestamps
        df['timestamp'] = pd.to_datetime(df['epoch'], unit='s')
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(time_zone)
        df['timestamp'] = df['timestamp'].dt.tz_localize(None)
        
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df.drop_duplicates(inplace=True)
        
        # Save to Parquet
        parquet_manager.save_data(df, symbol_name, timeframe, mode='append')
        print(f"✅ Updated {symbol_name} with {len(df)} rows")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating {symbol_name} with Fyers: {e}")
        return False

def update_all_symbols():
    """Update all symbols using Fyers API only (no fallback)"""
    symbols_to_update = get_symbols_to_update()
    
    if not symbols_to_update:
        print("📂 No existing data files found to update")
        return
    
    print(f"🔄 Found {len(symbols_to_update)} symbols to check for updates")
    
    updated_count = 0
    failed_count = 0
    skipped_count = 0
    
    for table_name, info in symbols_to_update.items():
        symbol_name = info['symbol_name']
        timeframe = info['timeframe']
        next_date = info['next_date']
        
        print(f"\n📊 Checking {table_name}...")
        print(f"   Last date: {info['last_date']}")
        print(f"   Next date: {next_date}")
        
        if next_date >= today_date:
            print(f"   ✅ Already up to date")
            skipped_count += 1
            continue
        
        # Only use Fyers API - no fallback to ensure real-time data quality
        success = update_symbol_with_fyers(symbol_name, timeframe, next_date, today_date)
        
        if success:
            updated_count += 1
            print(f"   ✅ Successfully updated with Fyers API")
        else:
            failed_count += 1
            print(f"   ❌ Failed to update (Fyers API only - no fallback)")
            print(f"   💡 Recommendation: Check symbol mapping in constants.py")
            
        # Rate limiting to respect API limits
        time.sleep(1)
    
    print(f"\n📊 Update Summary:")
    print(f"   ✅ Successfully updated: {updated_count}")
    print(f"   ⏭️  Already up to date: {skipped_count}")
    print(f"   ❌ Failed to update: {failed_count}")
    print(f"   📝 Total processed: {len(symbols_to_update)}")
    
    if failed_count > 0:
        print(f"\n💡 Failed updates are likely due to:")
        print(f"   - Symbol not mapped in constants.py")
        print(f"   - Symbol not available in Fyers API")
        print(f"   - API rate limiting (try again later)")
        print(f"   - Weekend/market closed (normal for real-time data)")

def update_symbol_with_yahoo(symbol_name, timeframe, start_date, end_date):
    """
    Deprecated: Yahoo Finance fallback removed
    Yahoo Finance provides delayed data which is not suitable for real-time analysis
    """
    print(f"❌ Yahoo Finance fallback has been removed")
    print(f"   Reason: Yahoo data is delayed and not suitable for real-time trading")
    print(f"   Using Fyers API only for accurate market data")
    return False

def show_data_summary():
    """Show summary of all available data"""
    available_data = parquet_manager.list_available_data()
    
    print("\n📊 Data Summary:")
    total_files = 0
    
    for category, files in available_data.items():
        print(f"\n📁 {category.title()}:")
        for file_stem in files:
            if '_' in file_stem:
                symbol_name, timeframe = file_stem.rsplit('_', 1)
                info = parquet_manager.get_data_info(symbol_name, timeframe)
                
                if info['exists']:
                    print(f"   📈 {file_stem}: {info['total_rows']:,} rows | "
                          f"{info['start_date']} to {info['end_date']} | "
                          f"{info['file_size_mb']} MB")
                    total_files += 1
    
    print(f"\n📋 Total files: {total_files}")

if __name__ == "__main__":
    print("🔄 Daily Data Update (Parquet Storage)")
    print("=" * 50)
    
    try:
        # Update all symbols
        update_all_symbols()
        
        # Show summary
        show_data_summary()
        
        print("\n🎉 Daily update completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Update interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during update: {e}")