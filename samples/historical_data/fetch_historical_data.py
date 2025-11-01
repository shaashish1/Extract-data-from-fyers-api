
# Add scripts directory to path for authentication
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from auth.my_fyers_model import MyFyersModel

"""
Fetch historical data for all stocks and store in database
This script fetches 3 months of 5-minute candle data for all configured stocks
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_fetcher import FyersDataFetcher
from modules.database import Database
import config


def main():
    """Main function to fetch and store historical data"""
    
    print("="*80)
    print("PTIP - HISTORICAL DATA FETCHING")
    print("="*80)
    print(f"\nStart Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load access token
    token_file = "fyers_access_token.txt"
    if not os.path.exists(token_file):
        print(f"\n❌ Error: {token_file} not found!")
        print("Please run authenticate_fyers.py first to generate access token.")
        return
    
    with open(token_file, 'r') as f:
        access_token = f.read().strip()
    
    print(f"\n✅ Access token loaded")
    
    # Initialize components
    fetcher = FyersDataFetcher()
    db = Database()
    
    # Authenticate
    print("\n🔐 Authenticating with Fyers API...")
    if not fetcher.authenticate(access_token):
        print("❌ Authentication failed!")
        return
    
    print("✅ Authentication successful!")
    
    # Define date range (3 months of data)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3 months
    
    print(f"\n📅 Date Range:")
    print(f"   From: {start_date.strftime('%Y-%m-%d')}")
    print(f"   To: {end_date.strftime('%Y-%m-%d')}")
    print(f"   Duration: 90 days (~3 months)")
    
    # Get stocks from config
    stocks = config.DEFAULT_STOCKS
    
    print(f"\n📊 Stocks to fetch: {len(stocks)}")
    for i, stock in enumerate(stocks, 1):
        print(f"   {i}. {stock}")
    
    print(f"\n⚙️  Configuration:")
    print(f"   Resolution: 5-minute candles")
    print(f"   Expected candles per day: ~75 (market hours)")
    print(f"   Expected total candles per stock: ~5,000-6,000")
    
    # Confirm before proceeding
    print("\n" + "="*80)
    response = input("Proceed with data fetching? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Data fetching cancelled by user.")
        return
    
    print("\n" + "="*80)
    print("STARTING DATA FETCH")
    print("="*80)
    
    # Track statistics
    total_records = 0
    successful_stocks = 0
    failed_stocks = []
    
    # Fetch data for each stock
    for i, symbol in enumerate(stocks, 1):
        print(f"\n[{i}/{len(stocks)}] Processing {symbol}...")
        print("-" * 60)
        
        try:
            # Add stock to database
            stock_name = symbol.split(':')[1].replace('-EQ', '')
            exchange = symbol.split(':')[0]
            db.add_stock(symbol, stock_name, exchange)
            print(f"✅ Stock added to database: {stock_name}")
            
            # Fetch historical data
            print(f"📊 Fetching data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
            
            df = fetcher.fetch_historical_data(
                symbol=symbol,
                from_date=start_date,
                to_date=end_date,
                resolution='5'  # 5-minute candles
            )
            
            if df.empty:
                print(f"⚠️  No data fetched for {symbol}")
                failed_stocks.append(symbol)
                continue
            
            print(f"✅ Fetched {len(df)} records")
            
            # Store in database
            print(f"💾 Storing data in database...")
            if db.insert_price_data(df, symbol):
                print(f"✅ Data stored successfully")
                total_records += len(df)
                successful_stocks += 1
                
                # Show sample data
                print(f"\n📋 Sample data (first 3 records):")
                print(df.head(3).to_string(index=False))
                
                # Show date range
                print(f"\n📅 Data range:")
                print(f"   First record: {df['timestamp'].min()}")
                print(f"   Last record: {df['timestamp'].max()}")
                print(f"   Total days: {(df['timestamp'].max() - df['timestamp'].min()).days}")
            else:
                print(f"❌ Failed to store data for {symbol}")
                failed_stocks.append(symbol)
        
        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")
            failed_stocks.append(symbol)
            import traceback
            traceback.print_exc()
        
        # Add delay between stocks to respect rate limits
        if i < len(stocks):
            print(f"\n⏳ Waiting 2 seconds before next stock...")
            import time
            time.sleep(2)
    
    # Summary
    print("\n" + "="*80)
    print("DATA FETCH COMPLETE")
    print("="*80)
    
    print(f"\n📊 Summary:")
    print(f"   Total stocks processed: {len(stocks)}")
    print(f"   Successful: {successful_stocks}")
    print(f"   Failed: {len(failed_stocks)}")
    print(f"   Total records stored: {total_records:,}")
    
    if failed_stocks:
        print(f"\n⚠️  Failed stocks:")
        for stock in failed_stocks:
            print(f"   - {stock}")
    
    # Verify data in database
    print(f"\n🔍 Verifying data in database...")
    all_stocks = db.get_all_stocks()
    print(f"✅ Total stocks in database: {len(all_stocks)}")
    
    for stock in all_stocks:
        symbol = stock[1]  # symbol is at index 1
        df = db.get_price_data(symbol)
        print(f"   {symbol}: {len(df):,} records")
    
    print(f"\n✅ End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Close database
    db.close()
    
    print("\n🎉 Historical data fetching completed!")
    
    # Recommendations
    if successful_stocks == len(stocks):
        print("\n✅ All stocks fetched successfully!")
        print("\n📋 Next Steps:")
        print("   1. Run tests to verify data quality")
        print("   2. Test indicator calculations on real data")
        print("   3. Generate trading signals")
        print("   4. Proceed to Week 2: Strategy testing")
    else:
        print("\n⚠️  Some stocks failed to fetch.")
        print("   Please check the errors above and retry for failed stocks.")


if __name__ == "__main__":
    main()

