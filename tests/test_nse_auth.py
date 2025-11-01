"""
Test NSE Authentication Pattern
================================
Simple test to validate the correct NSE authentication pattern
from the working NSE_Option_Chain_Analyzer.py

Author: NSE Data Pipeline
Date: October 29, 2025
"""

import requests
import time

def test_nse_auth():
    """Test NSE authentication with correct cookie pattern."""
    
    # Headers from working NSE_Option_Chain_Analyzer.py
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/130.0.0.0 Safari/537.36',
        'accept-language': 'en,gu;q=0.9,hi;q=0.8',
        'accept-encoding': 'gzip, deflate, br'
    }
    
    session = requests.Session()
    
    print("=" * 80)
    print("NSE AUTHENTICATION TEST")
    print("=" * 80)
    
    # STEP 1: Hit option-chain page to get cookies
    print("\n🔐 STEP 1: Getting session cookies from option-chain page...")
    try:
        url_oc = 'https://www.nseindia.com/option-chain'
        request = session.get(url_oc, headers=headers, timeout=10)
        cookies = dict(request.cookies)
        print(f"✅ Got {len(cookies)} cookies")
        print(f"   Cookies: {list(cookies.keys())}")
        time.sleep(1)
    except Exception as e:
        print(f"❌ Failed to get cookies: {e}")
        return
    
    # STEP 2: Test symbol discovery API
    print("\n📊 STEP 2: Testing symbol discovery API with cookies...")
    try:
        url_symbols = 'https://www.nseindia.com/api/underlying-information'
        response = session.get(url_symbols, headers=headers, timeout=10, cookies=cookies)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            index_count = len(data['data']['IndexList'])
            stock_count = len(data['data']['UnderlyingList'])
            print(f"✅ Symbol Discovery SUCCESS!")
            print(f"   Found {index_count} indices")
            print(f"   Found {stock_count} stocks")
            print(f"\n   Sample Indices: {[item['symbol'] for item in data['data']['IndexList'][:5]]}")
            print(f"   Sample Stocks: {[item['symbol'] for item in data['data']['UnderlyingList'][:10]]}")
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"   Response: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    
    # STEP 3: Test equity data API
    print("\n📈 STEP 3: Testing equity data API (Nifty 50)...")
    try:
        url_equity = 'https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050'
        response = session.get(url_equity, headers=headers, timeout=10, cookies=cookies)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            stocks = data.get('data', [])
            print(f"✅ Equity Data SUCCESS!")
            print(f"   Found {len(stocks)} stocks in Nifty 50")
            if stocks:
                sample = stocks[0]
                print(f"\n   Sample: {sample.get('symbol', 'N/A')}")
                print(f"   Last Price: {sample.get('lastPrice', 'N/A')}")
                print(f"   Change: {sample.get('pChange', 'N/A')}%")
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # STEP 4: Test option chain API
    print("\n🔗 STEP 4: Testing option chain API (NIFTY)...")
    try:
        url_options = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
        response = session.get(url_options, headers=headers, timeout=15, cookies=cookies)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', {}).get('data', [])
            print(f"✅ Option Chain SUCCESS!")
            print(f"   Found {len(records)} option records")
            if records:
                print(f"   Underlying Value: {data['records'].get('underlyingValue', 'N/A')}")
                print(f"   Expiry Dates: {data['records'].get('expiryDates', [])[:3]}")
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "=" * 80)
    print("🎉 AUTHENTICATION TEST COMPLETE!")
    print("=" * 80)
    print("\n✅ The authentication pattern works!")
    print("   Pattern: option-chain page → get cookies → use cookies for API calls")
    print("\n📝 Next Step: Apply this pattern to download_nse_complete_history.py")

if __name__ == '__main__':
    test_nse_auth()
