#!/usr/bin/env python3
"""
Test script to diagnose TATAMOTORS symbol issue
"""
import sys
from pathlib import Path

# Add scripts directory to Python path
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from my_fyers_model import MyFyersModel

def test_tatamotors_symbols():
    """Test different TATAMOTORS symbol formats"""
    fyers = MyFyersModel()
    
    # Test different possible symbol formats
    test_symbols = [
        'NSE:TATAMOTORS-EQ',
        'NSE:TATAMTRS-EQ', 
        'NSE:TATAMOTOR-EQ',
        'NSE:TATA-MOTORS-EQ',
        'NSE:TATAMOT-EQ',
        'NSE:TTMT-EQ'
    ]
    
    print("🧪 Testing TATA MOTORS symbol formats...")
    print("=" * 50)
    
    for symbol in test_symbols:
        print(f"\n🔍 Testing: {symbol}")
        try:
            data = {
                "symbol": symbol,
                "ohlcv_flag": "1"
            }
            
            response = fyers.fyers_model.depth(data=data)
            
            if response and response.get('s') == 'ok':
                symbol_data = response.get('d', {}).get(symbol, {})
                if symbol_data:
                    ltp = symbol_data.get('ltp', 'N/A')
                    volume = symbol_data.get('v', 'N/A')
                    print(f"✅ SUCCESS: LTP: ₹{ltp}, Volume: {volume}")
                else:
                    print(f"❌ No data returned for {symbol}")
            else:
                message = response.get('message', 'Unknown error') if response else 'No response'
                print(f"❌ FAILED: {message}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
    
    # Test with quotes API as well
    print(f"\n" + "=" * 50)
    print("🔍 Testing with quotes API...")
    
    for symbol in test_symbols[:3]:  # Test top 3 candidates
        print(f"\n📊 Quote test: {symbol}")
        try:
            data = {"symbols": symbol}
            response = fyers.fyers_model.quotes(data=data)
            
            if response and response.get('s') == 'ok':
                symbol_data = response.get('d', [])
                if symbol_data:
                    quote = symbol_data[0]
                    ltp = quote.get('v', {}).get('lp', 'N/A')
                    volume = quote.get('v', {}).get('volume', 'N/A')
                    print(f"✅ QUOTE SUCCESS: LTP: ₹{ltp}, Volume: {volume}")
                else:
                    print(f"❌ No quote data returned")
            else:
                message = response.get('message', 'Unknown error') if response else 'No response'
                print(f"❌ QUOTE FAILED: {message}")
                
        except Exception as e:
            print(f"❌ QUOTE EXCEPTION: {e}")

def test_market_depth_levels():
    """Test how many levels of market depth we can get"""
    fyers = MyFyersModel()
    
    print("\n" + "=" * 50)
    print("🔍 Testing market depth levels with RELIANCE...")
    
    try:
        data = {
            "symbol": "NSE:RELIANCE-EQ",
            "ohlcv_flag": "1"
        }
        
        response = fyers.fyers_model.depth(data=data)
        
        if response and response.get('s') == 'ok':
            symbol_data = response.get('d', {}).get('NSE:RELIANCE-EQ', {})
            
            bids = symbol_data.get('bids', [])
            asks = symbol_data.get('ask', [])
            
            print(f"📊 Bid levels available: {len(bids)}")
            print(f"📊 Ask levels available: {len(asks)}")
            
            print(f"\n🟢 BID LEVELS:")
            for i, bid in enumerate(bids):
                print(f"  Level {i+1}: Price: ₹{bid['price']}, Volume: {bid['volume']}, Orders: {bid['ord']}")
            
            print(f"\n🔴 ASK LEVELS:")
            for i, ask in enumerate(asks):
                print(f"  Level {i+1}: Price: ₹{ask['price']}, Volume: {ask['volume']}, Orders: {ask['ord']}")
                
        else:
            print(f"❌ Failed to get depth data")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_tatamotors_symbols()
    test_market_depth_levels()