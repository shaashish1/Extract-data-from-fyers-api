#!/usr/bin/env python3
"""
NSE Symbol Management Demo Script
Demonstrates the new NSE data fetching and Fyers symbol mapping system
"""
import pandas as pd
import os
from datetime import datetime
from nse_data_fetcher import get_nse_fetcher
from symbol_discovery import SymbolDiscovery
from data_storage import get_parquet_manager

def main():
    """Main demonstration function"""
    print("🚀 NSE Symbol Management System Demo")
    print("=" * 50)
    
    # Initialize components
    nse_fetcher = get_nse_fetcher()
    symbol_discovery = SymbolDiscovery()
    parquet_manager = get_parquet_manager()
    
    # 1. Fetch fresh NSE data
    print("\n📥 1. Fetching NSE Symbol Data")
    print("-" * 30)
    
    try:
        all_data = nse_fetcher.fetch_all_nse_data(save_to_parquet=True)
        
        # Display summary
        total_symbols = 0
        for category, endpoints in all_data.items():
            if category != 'fetch_timestamp':
                for endpoint, data in endpoints.items():
                    if 'symbols' in data:
                        count = len(data['symbols'])
                        print(f"✅ {endpoint}: {count} symbols")
                        total_symbols += count
                    elif 'etfs' in data:
                        count = len(data['etfs'])
                        print(f"✅ {endpoint}: {count} ETFs")
                        total_symbols += count
                    elif 'derivatives' in data:
                        count = len(data['derivatives'])
                        print(f"✅ {endpoint}: {count} derivatives")
                        total_symbols += count
        
        print(f"\n📊 Total symbols fetched: {total_symbols}")
        
    except Exception as e:
        print(f"❌ Failed to fetch NSE data: {e}")
        print("🔄 Using existing cached data...")
    
    # 2. Test symbol discovery with NSE integration
    print("\n🔍 2. Testing Symbol Discovery with NSE Integration")
    print("-" * 50)
    
    # Test Nifty50 symbols
    nifty50_symbols = symbol_discovery.get_nifty50_constituents()
    print(f"📈 Nifty50 symbols: {len(nifty50_symbols)}")
    print(f"First 5: {nifty50_symbols[:5]}")
    
    # Test Nifty100 symbols
    nifty100_symbols = symbol_discovery.get_nifty100_constituents()
    print(f"📈 Nifty100 symbols: {len(nifty100_symbols)}")
    
    # Test Nifty200 symbols
    nifty200_symbols = symbol_discovery.get_nifty200_constituents()
    print(f"📈 Nifty200 symbols: {len(nifty200_symbols)}")
    
    # Test ETF symbols
    etf_symbols = symbol_discovery.get_nse_etf_symbols()
    print(f"💰 ETF symbols: {len(etf_symbols)}")
    if etf_symbols:
        print(f"First 3 ETFs: {etf_symbols[:3]}")
    
    # Test derivatives symbols
    derivative_symbols = symbol_discovery.get_nse_derivative_symbols()
    print(f"⚡ Derivative symbols: {len(derivative_symbols)}")
    if derivative_symbols:
        print(f"First 3 derivatives: {derivative_symbols[:3]}")
    
    # 3. Display symbol mappings
    print("\n🔄 3. NSE to Fyers Symbol Mapping Examples")
    print("-" * 45)
    
    # Examples of NSE to Fyers mapping
    mapping_examples = [
        ('RELIANCE', 'EQ'),
        ('HDFCBANK', 'EQ'),
        ('NIFTY50ETF', 'ETF'),
        ('GOLDSHARE', 'ETF'),
        ('NIFTY 50', 'INDEX'),
        ('BANKNIFTY', 'INDEX'),
        ('SENSEX', 'INDEX')
    ]
    
    for nse_symbol, instrument_type in mapping_examples:
        fyers_symbol = nse_fetcher.nse_to_fyers_symbol(nse_symbol, instrument_type)
        print(f"NSE: {nse_symbol:12} ({instrument_type:3}) → Fyers: {fyers_symbol}")
    
    # 4. Data storage verification
    print("\n💾 4. Verifying Parquet Storage")
    print("-" * 30)
    
    # Check NSE symbols directory
    nse_symbols_dir = nse_fetcher.nse_symbols_dir
    parquet_files = list(nse_symbols_dir.glob("*.parquet"))
    
    print(f"📁 NSE symbols directory: {nse_symbols_dir}")
    print(f"💾 Parquet files created: {len(parquet_files)}")
    
    for file_path in parquet_files:
        try:
            df = pd.read_parquet(file_path)
            print(f"   📄 {file_path.name}: {len(df)} records")
        except Exception as e:
            print(f"   ❌ {file_path.name}: Error reading - {e}")
    
    # 5. Symbol category breakdown
    print("\n📊 5. Symbol Category Breakdown")
    print("-" * 35)
    
    # Get symbols by category
    categories = ['indices', 'etfs', 'derivatives']
    for category in categories:
        try:
            symbols = nse_fetcher.get_fyers_symbols_by_category(category)
            print(f"{category.title():12}: {len(symbols)} symbols")
            
            # Show sample symbols
            if symbols:
                sample_size = min(3, len(symbols))
                print(f"   Sample: {symbols[:sample_size]}")
        except Exception as e:
            print(f"{category.title():12}: Error - {e}")
    
    # 6. Data freshness check
    print("\n🕒 6. Data Freshness Information")
    print("-" * 32)
    
    for file_path in parquet_files:
        try:
            df = pd.read_parquet(file_path)
            if 'last_updated' in df.columns and len(df) > 0:
                last_updated = df['last_updated'].iloc[0]
                print(f"{file_path.stem}: {last_updated}")
        except Exception as e:
            print(f"{file_path.stem}: Error checking timestamp - {e}")
    
    # 7. Cleanup old files
    print("\n🗑️ 7. Cleanup Old Temporary Files")
    print("-" * 35)
    
    nse_fetcher.cleanup_temp_files(older_than_hours=1)  # Clean files older than 1 hour
    
    print("\n✅ Demo completed successfully!")
    print("\n💡 Next Steps:")
    print("   • Run scripts/stocks_data.py with NSE symbols")
    print("   • Test real-time WebSocket with new symbol lists")
    print("   • Use symbol_discovery methods in data collection scripts")
    print("   • Set up periodic NSE data refresh (daily/weekly)")


def test_specific_endpoints():
    """Test specific NSE endpoints individually"""
    print("\n🧪 Testing Individual NSE Endpoints")
    print("-" * 38)
    
    nse_fetcher = get_nse_fetcher()
    
    # Test each endpoint
    endpoints_to_test = [
        ('nifty50', 'Index constituents'),
        ('nifty50_etf', 'Nifty50 ETFs'),
        ('gold_etf', 'Gold ETFs'),
        ('stock_options', 'Stock Options')
    ]
    
    for endpoint, description in endpoints_to_test:
        print(f"\n🔍 Testing {endpoint} ({description}):")
        try:
            df = nse_fetcher.fetch_nse_data(endpoint, save_csv=True)
            if df is not None:
                print(f"   ✅ Success: {len(df)} rows, {len(df.columns)} columns")
                print(f"   📋 Columns: {list(df.columns)[:5]}...")  # Show first 5 columns
            else:
                print(f"   ❌ Failed to fetch data")
        except Exception as e:
            print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    # Run main demo
    main()
    
    # Optionally test individual endpoints
    test_specific = input("\n❓ Test individual NSE endpoints? (y/n): ").lower().strip() == 'y'
    if test_specific:
        test_specific_endpoints()
    
    print("\n🎉 NSE Symbol Management Demo Completed!")