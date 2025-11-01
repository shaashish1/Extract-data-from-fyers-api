#!/usr/bin/env python3
"""
NSE Symbol Matching Test
=========================

This script tests the actual NSE symbols available in FYERS data
and identifies which Nifty constituent symbols are missing or have
different names.
"""

import pandas as pd
import requests
from pathlib import Path

# Nifty symbol lists from the script
NIFTY_50_SYMBOLS = {
    'RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'BHARTIARTL', 'INFY', 'SBIN', 'LICI',
    'HINDUNILVR', 'ITC', 'LT', 'AXISBANK', 'KOTAKBANK', 'MARUTI', 'ASIANPAINT',
    'NESTLEIND', 'HCLTECH', 'ULTRACEMCO', 'BAJFINANCE', 'TITAN', 'SUNPHARMA', 'WIPRO',
    'ONGC', 'NTPC', 'POWERGRID', 'BAJAJFINSV', 'M&M', 'TATAMOTORS', 'TECHM', 'ADANIENT',
    'COALINDIA', 'JSWSTEEL', 'HINDALCO', 'TATASTEEL', 'ADANIPORTS', 'GRASIM', 'APOLLOHOSP',
    'BRITANNIA', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'HEROMOTOCO', 'CIPLA', 'BPCL',
    'SHRIRAMFIN', 'UPL', 'TRENT', 'INDIGO', 'BAJAJ-AUTO', 'LTIM'
}

print("🧪 NSE Symbol Matching Test")
print("=" * 60)

# Download NSE_CM data
print("📥 Downloading NSE_CM data from FYERS...")
url = 'https://public.fyers.in/sym_details/NSE_CM.csv'
response = requests.get(url, timeout=30)

if response.status_code == 200:
    # Parse CSV (no headers in FYERS CSV)
    from io import StringIO
    df = pd.read_csv(StringIO(response.text), header=None)
    
    print(f"✅ Downloaded {len(df)} NSE_CM symbols")
    print(f"📊 Columns in CSV: {len(df.columns)}")
    
    # Show first few rows to understand structure
    print("\n🔍 First 5 rows of data:")
    print(df.head())
    
    # Column 13 typically contains the base symbol
    if len(df.columns) >= 14:
        base_symbols = set(df.iloc[:, 13].dropna().unique())
        print(f"\n📋 Total unique base symbols (column 13): {len(base_symbols)}")
        
        # Test matching
        found_symbols = NIFTY_50_SYMBOLS & base_symbols
        missing_symbols = NIFTY_50_SYMBOLS - base_symbols
        
        print(f"\n✅ Nifty 50 symbols found: {len(found_symbols)}/50")
        print(f"❌ Nifty 50 symbols missing: {len(missing_symbols)}")
        
        if missing_symbols:
            print(f"\n🔍 Missing Nifty 50 symbols:")
            for symbol in sorted(missing_symbols):
                print(f"  • {symbol}")
                
                # Try to find similar symbols
                similar = [s for s in base_symbols if symbol.replace('-', '').replace('&', '') in str(s).upper()]
                if similar:
                    print(f"    Possible match: {similar}")
        
        # Show some base symbols for reference
        print(f"\n📋 Sample base symbols from FYERS:")
        for symbol in sorted(list(base_symbols))[:20]:
            print(f"  • {symbol}")
    
    # Also check column 9 (NSE symbol with exchange prefix)
    if len(df.columns) >= 10:
        nse_symbols = set(df.iloc[:, 9].dropna().unique())
        print(f"\n📋 Total unique NSE symbols (column 9): {len(nse_symbols)}")
        
        # Show sample NSE symbols
        print(f"\n📋 Sample NSE symbols from FYERS:")
        for symbol in sorted(list(nse_symbols))[:20]:
            print(f"  • {symbol}")
    
else:
    print(f"❌ Failed to download NSE_CM data: HTTP {response.status_code}")

print("\n" + "=" * 60)
print("🎯 Test Complete!")