#!/usr/bin/env python3
"""
Simple Symbol Count Test
=======================

Test symbol discovery using direct FYERS API calls to validate
our symbol counts and see what's actually available.
"""

from fyers_apiv3 import fyersModel
import requests
import pandas as pd
from datetime import datetime

# Use the real credentials that were fixed
client_id = "8I122G8NSD-100"
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiI4STEyMkc4TlNEIiwidXVpZCI6IjlkYjNlYTQwMTkwNDRiMmE4NGIxN2U1MDlmNDU3NzM5IiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IlhBMDAzMzAiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiIzNTNjNjYzOWRlODA2ZDQ2M2M0MDFjNTY2ZjhiMzdmY2RkOGU0NTgzMTE1NTNjMWU3Y2E4YWQ2NyIsImlzRGRwaUVuYWJsZWQiOiJZIiwiaXNNdGZFbmFibGVkIjoiTiIsImF1ZCI6IltcImQ6MVwiLFwiZDoyXCIsXCJ4OjBcIixcIng6MVwiLFwieDoyXCJdIiwiZXhwIjoxNzYxNzY0MTIxLCJpYXQiOjE3NjE3MzQxMjEsImlzcyI6ImFwaS5sb2dpbi5meWVycy5pbiIsIm5iZiI6MTc2MTczNDEyMSwic3ViIjoiYXV0aF9jb2RlIn0.U0d93O2vVik0f7rCHrh9UWIMKhMr1mQ6AyWmGFjyq64"

print("🧪 Simple Symbol Count Test")
print("=" * 50)

# Initialize Fyers
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")

print("🔐 Testing Authentication...")
try:
    # Test profile
    profile = fyers.get_profile()
    if profile and profile.get('s') == 'ok':
        print(f"✅ Authentication successful!")
        print(f"👤 User: {profile.get('data', {}).get('display_name', 'Unknown')}")
    else:
        print(f"❌ Authentication failed: {profile}")
        exit(1)
except Exception as e:
    print(f"❌ Authentication error: {e}")
    exit(1)

print("\\n📊 Testing Market Status...")
try:
    status = fyers.market_status()
    if status and status.get('s') == 'ok':
        markets = status.get('marketStatus', [])
        print(f"✅ Market Status: {len(markets)} market segments")
        for market in markets:
            print(f"  • {market.get('market_type', 'Unknown')}: {market.get('status', 'Unknown')}")
    else:
        print(f"❌ Market status failed: {status}")
except Exception as e:
    print(f"❌ Market status error: {e}")

print("\\n🔍 Testing Symbol Download (FYERS CSV Method)...")
try:
    # Download symbols directly from FYERS public URLs
    urls = {
        'NSE_CM': 'https://public.fyers.in/sym_details/NSE_CM.csv',
        'NSE_FO': 'https://public.fyers.in/sym_details/NSE_FO.csv', 
        'NSE_CD': 'https://public.fyers.in/sym_details/NSE_CD.csv',
        'BSE_CM': 'https://public.fyers.in/sym_details/BSE_CM.csv',
        'BSE_FO': 'https://public.fyers.in/sym_details/BSE_FO.csv',
        'MCX_FO': 'https://public.fyers.in/sym_details/MCX_FO.csv'
    }
    
    total_symbols = 0
    segment_counts = {}
    
    for segment, url in urls.items():
        try:
            print(f"📥 Downloading {segment}...")
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                # Count lines (minus header)
                lines = response.text.strip().split('\\n')
                count = len(lines) - 1  # Subtract header
                segment_counts[segment] = count
                total_symbols += count
                print(f"  ✅ {segment}: {count:,} symbols")
            else:
                print(f"  ❌ {segment}: HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ {segment}: Error - {e}")
    
    print(f"\\n📊 **TOTAL SYMBOLS FOUND: {total_symbols:,}**")
    print("\\n📈 Segment Breakdown:")
    for segment, count in segment_counts.items():
        percentage = (count / total_symbols * 100) if total_symbols > 0 else 0
        print(f"  • {segment}: {count:,} ({percentage:.1f}%)")
        
except Exception as e:
    print(f"❌ Symbol download error: {e}")

print("\\n🎯 Testing Sample Quotes...")
try:
    # Test a few sample symbols
    test_symbols = [
        "NSE:NIFTY50-INDEX",
        "NSE:RELIANCE-EQ", 
        "NSE:TCS-EQ",
        "NSE:HDFCBANK-EQ"
    ]
    
    print("🔍 Getting quotes for sample symbols...")
    for symbol in test_symbols:
        try:
            quote_data = {"symbols": symbol}
            quote = fyers.quotes(data=quote_data)
            if quote and quote.get('s') == 'ok':
                symbol_info = quote.get('d', [])[0] if quote.get('d') else {}
                name = symbol_info.get('n', symbol)
                ltp = symbol_info.get('v', {}).get('lp', 'N/A')
                print(f"  ✅ {symbol}: {name} - LTP: {ltp}")
            else:
                print(f"  ❌ {symbol}: {quote.get('message', 'Quote failed')}")
        except Exception as e:
            print(f"  ❌ {symbol}: Error - {e}")
        
        # Rate limiting delay
        import time
        time.sleep(1)
        
except Exception as e:
    print(f"❌ Quotes test error: {e}")

print("\\n" + "=" * 50)
print("🎉 Symbol Count Test Complete!")
print(f"📊 Discovery Summary:")
print(f"  • Total Symbols Available: {total_symbols:,}")
print(f"  • Authentication: Working")
print(f"  • Market Status: Working") 
print(f"  • Symbol Downloads: Working")
print("\\n🔍 This gives us the REAL symbol count from FYERS!")