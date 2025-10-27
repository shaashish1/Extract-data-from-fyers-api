#!/usr/bin/env python3
"""
Simple Market Depth Test - Single Symbol
========================================

Test script to verify market depth API with a single symbol.
This helps debug authentication and API connectivity issues.
"""

import os
import sys
from pathlib import Path

# Add scripts directory to Python path for imports
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.append(str(script_dir))

from my_fyers_model import MyFyersModel


def test_single_symbol_depth():
    """Test market depth for a single symbol"""
    print("🧪 SINGLE SYMBOL MARKET DEPTH TEST")
    print("=" * 50)
    
    try:
        # Initialize Fyers model
        print("🔗 Initializing Fyers connection...")
        fyers_model = MyFyersModel()
        print("✅ Fyers model initialized successfully")
        
        # Test with SBIN (as per your example)
        symbol = "NSE:SBIN-EQ"
        print(f"📊 Testing symbol: {symbol}")
        
        data = {
            "symbol": symbol,
            "ohlcv_flag": "1"
        }
        
        print("📡 Fetching market depth...")
        response = fyers_model.fyers_model.depth(data=data)
        
        print("\n📋 Raw Response:")
        print("-" * 50)
        print(response)
        
        if response and response.get('s') == 'ok':
            print("\n✅ SUCCESS: Market depth data received!")
            
            symbol_data = response.get('d', {}).get(symbol, {})
            if symbol_data:
                print(f"\n📊 Key Data for {symbol}:")
                print(f"  💰 LTP: ₹{symbol_data.get('ltp', 0)}")
                print(f"  📈 Change: {symbol_data.get('ch', 0)} ({symbol_data.get('chp', 0)}%)")
                print(f"  📊 Volume: {symbol_data.get('v', 0):,}")
                print(f"  🔄 Total Buy Qty: {symbol_data.get('totalbuyqty', 0):,}")
                print(f"  🔄 Total Sell Qty: {symbol_data.get('totalsellqty', 0):,}")
                
                bids = symbol_data.get('bids', [])
                asks = symbol_data.get('ask', [])
                
                print(f"\n📋 Market Depth:")
                print(f"  🟢 Bid Levels: {len(bids)}")
                print(f"  🔴 Ask Levels: {len(asks)}")
                
                if bids:
                    print(f"  🎯 Best Bid: ₹{bids[0]['price']} (Vol: {bids[0]['volume']:,})")
                if asks:
                    print(f"  🎯 Best Ask: ₹{asks[0]['price']} (Vol: {asks[0]['volume']:,})")
                    
        else:
            print("❌ FAILED: No valid data received")
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_single_symbol_depth()