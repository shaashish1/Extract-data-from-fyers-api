#!/usr/bin/env python3
"""
Direct Fyers Symbol Discovery Demo
Demonstrates the optimized approach: Direct Fyers API access without NSE downloads
"""
import time
from datetime import datetime
from fyers_direct_discovery import get_fyers_direct_discovery
from symbol_discovery import SymbolDiscovery
from nse_data_fetcher import get_nse_fetcher

def main():
    """Demonstrate the optimized direct Fyers approach"""
    print("🚀 Direct Fyers Symbol Discovery Optimization Demo")
    print("=" * 55)
    
    # Method 1: Direct Fyers Discovery (NEW OPTIMIZED APPROACH)
    print("\n🎯 Method 1: Direct Fyers Discovery (OPTIMIZED)")
    print("-" * 45)
    
    start_time = time.time()
    
    try:
        # Initialize direct discovery
        fyers_direct = get_fyers_direct_discovery()
        
        # Get symbols directly from Fyers with proven lists
        nifty50 = fyers_direct.get_nifty50_constituents()
        nifty100 = fyers_direct.get_nifty100_constituents()
        bank_nifty = fyers_direct.get_bank_nifty_constituents()
        indices = fyers_direct.get_major_indices()
        etfs = fyers_direct.get_popular_etfs()
        
        # Test option chain discovery
        print("\n⚡ Testing option chain discovery...")
        nifty_options = fyers_direct.discover_option_symbols('NSE:NIFTY50-INDEX', strike_count=5)
        
        direct_time = time.time() - start_time
        
        print(f"\n✅ Direct Fyers Results (in {direct_time:.2f}s):")
        print(f"   📊 Nifty50: {len(nifty50)} symbols")
        print(f"   📊 Nifty100: {len(nifty100)} symbols")
        print(f"   🏦 Bank Nifty: {len(bank_nifty)} symbols")
        print(f"   📈 Indices: {len(indices)} symbols")
        print(f"   💰 ETFs: {len(etfs)} symbols")
        print(f"   🎯 Nifty Options: {len(nifty_options)} symbols")
        
        total_direct = len(nifty50) + len(nifty100) + len(bank_nifty) + len(indices) + len(etfs) + len(nifty_options)
        print(f"   🎯 Total Symbols: {total_direct}")
        
        # Show sample symbols
        print(f"\n📋 Sample Nifty50 symbols:")
        for symbol in nifty50[:5]:
            print(f"      {symbol}")
        
        print(f"\n📋 Sample ETF symbols:")
        for symbol in etfs[:3]:
            print(f"      {symbol}")
        
        if nifty_options:
            print(f"\n📋 Sample Nifty Options:")
            for symbol in nifty_options[:3]:
                print(f"      {symbol}")
        
    except Exception as e:
        print(f"❌ Direct Fyers method failed: {e}")
        direct_time = None
        total_direct = 0
    
    # Method 2: NSE Download + Mapping (OLD APPROACH)
    print(f"\n📥 Method 2: NSE Download + Mapping (OLD)")
    print("-" * 40)
    
    start_time = time.time()
    
    try:
        # Initialize NSE fetcher
        nse_fetcher = get_nse_fetcher()
        
        # Fetch NSE data (downloads CSV files)
        print("📥 Downloading NSE data...")
        all_nse_data = nse_fetcher.fetch_all_nse_data(save_to_parquet=True)
        
        # Get symbols by category
        nse_nifty50 = nse_fetcher.get_fyers_symbols_by_category('indices', 'nifty50')
        nse_etfs = nse_fetcher.get_fyers_symbols_by_category('etfs')
        nse_derivatives = nse_fetcher.get_fyers_symbols_by_category('derivatives')
        
        nse_time = time.time() - start_time
        
        print(f"\n✅ NSE Download Results (in {nse_time:.2f}s):")
        print(f"   📊 Nifty50: {len(nse_nifty50)} symbols")
        print(f"   💰 ETFs: {len(nse_etfs)} symbols")
        print(f"   ⚡ Derivatives: {len(nse_derivatives)} symbols")
        
        total_nse = len(nse_nifty50) + len(nse_etfs) + len(nse_derivatives)
        print(f"   🎯 Total Symbols: {total_nse}")
        
        # Cleanup downloaded files
        nse_fetcher.cleanup_all_temp_files()
        
    except Exception as e:
        print(f"❌ NSE download method failed: {e}")
        nse_time = None
        total_nse = 0
    
    # Method 3: Unified Symbol Discovery (HYBRID OPTIMIZED)
    print(f"\n🔄 Method 3: Unified Symbol Discovery (HYBRID)")
    print("-" * 48)
    
    start_time = time.time()
    
    try:
        # Initialize unified discovery (uses direct Fyers with fallbacks)
        discovery = SymbolDiscovery()
        
        # Get symbols using the optimized hybrid approach
        unified_nifty50 = discovery.get_nifty50_constituents()
        unified_nifty100 = discovery.get_nifty100_constituents()
        unified_bank = discovery.get_banknifty_constituents()
        unified_etfs = discovery.get_etf_symbols()
        
        # Test option discovery
        unified_options = discovery.get_option_symbols('NSE:NIFTY50-INDEX', strike_count=5)
        
        unified_time = time.time() - start_time
        
        print(f"\n✅ Unified Discovery Results (in {unified_time:.2f}s):")
        print(f"   📊 Nifty50: {len(unified_nifty50)} symbols")
        print(f"   📊 Nifty100: {len(unified_nifty100)} symbols")
        print(f"   🏦 Bank Nifty: {len(unified_bank)} symbols")
        print(f"   💰 ETFs: {len(unified_etfs)} symbols")
        print(f"   🎯 Options: {len(unified_options)} symbols")
        
        total_unified = len(unified_nifty50) + len(unified_nifty100) + len(unified_bank) + len(unified_etfs) + len(unified_options)
        print(f"   🎯 Total Symbols: {total_unified}")
        
    except Exception as e:
        print(f"❌ Unified discovery method failed: {e}")
        unified_time = None
        total_unified = 0
    
    # Performance Comparison
    print(f"\n⚡ Performance Comparison")
    print("=" * 30)
    
    if direct_time is not None:
        print(f"✅ Direct Fyers:     {direct_time:.2f}s ({total_direct} symbols)")
    else:
        print(f"❌ Direct Fyers:     Failed")
    
    if nse_time is not None:
        print(f"📥 NSE Download:     {nse_time:.2f}s ({total_nse} symbols)")
    else:
        print(f"❌ NSE Download:     Failed")
    
    if unified_time is not None:
        print(f"🔄 Unified Hybrid:   {unified_time:.2f}s ({total_unified} symbols)")
    else:
        print(f"❌ Unified Hybrid:   Failed")
    
    # Performance benefits
    if direct_time and nse_time:
        improvement = ((nse_time - direct_time) / nse_time) * 100
        print(f"\n🚀 Performance Improvement:")
        print(f"   Direct Fyers is {improvement:.1f}% faster than NSE download")
        print(f"   Time saved: {nse_time - direct_time:.2f} seconds")
    
    # Benefits Summary
    print(f"\n🎯 Optimization Benefits")
    print("-" * 25)
    print("✅ No CSV/TXT file downloads")
    print("✅ No temporary file cleanup needed")
    print("✅ Direct API access to Fyers")
    print("✅ Faster symbol discovery")
    print("✅ Reduced network bandwidth")
    print("✅ Cleaner directory structure")
    print("✅ Better error handling with fallbacks")
    print("✅ Option chain discovery via Fyers API")
    
    # Recommendations
    print(f"\n💡 Recommendations")
    print("-" * 18)
    print("1. 🎯 Use Direct Fyers Discovery for production")
    print("2. 🔄 Keep NSE fetcher as backup for validation")
    print("3. 📊 Use Unified Discovery for automatic fallbacks")
    print("4. ⚡ Leverage option chain API for derivatives")
    print("5. 🗑️ Auto-cleanup enabled by default")
    
    print(f"\n✅ Direct Fyers Optimization Demo Completed!")


def test_quote_validation():
    """Test symbol validation using Fyers quotes"""
    print(f"\n🧪 Testing Symbol Validation via Fyers Quotes")
    print("-" * 45)
    
    fyers_direct = get_fyers_direct_discovery()
    
    # Test symbols
    test_symbols = [
        'NSE:RELIANCE-EQ',
        'NSE:TCS-EQ',
        'NSE:HDFCBANK-EQ',
        'NSE:INVALID-EQ',  # Invalid symbol for testing
        'NSE:NIFTY50-INDEX'
    ]
    
    print("Testing symbol validation...")
    for symbol in test_symbols:
        quote = fyers_direct.get_symbol_quote(symbol)
        if quote:
            name = quote.get('n', 'Unknown')
            ltp = quote.get('lp', 0)
            print(f"   ✅ {symbol}: {name} (LTP: ₹{ltp})")
        else:
            print(f"   ❌ {symbol}: Invalid or no data")


if __name__ == "__main__":
    # Run main demo
    main()
    
    # Test quote validation
    test_quotes = input("\n❓ Test symbol validation via quotes? (y/n): ").lower().strip() == 'y'
    if test_quotes:
        test_quote_validation()
    
    print("\n🎉 Optimization Demo Completed!")