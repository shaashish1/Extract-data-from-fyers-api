#!/usr/bin/env python3
"""
Quick test to debug FYERS API history call
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.auth.my_fyers_model import MyFyersModel

# Initialize Fyers
print("Initializing Fyers API...")
fyers = MyFyersModel()
fyers_model = fyers.get_fyre_model()

# Test with a simple symbol
symbol = "NSE:RELIANCE-EQ"
print(f"\nTesting with symbol: {symbol}")

# Calculate dates (5 years back)
end_date = datetime.now()
start_date = end_date - timedelta(days=365)  # Just 1 year for testing

print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

# Prepare request
data = {
    "symbol": symbol,
    "resolution": "D",
    "date_format": "1",  # Using date format for clarity
    "range_from": start_date.strftime('%Y-%m-%d'),
    "range_to": end_date.strftime('%Y-%m-%d'),
    "cont_flag": "1"
}

print(f"\nRequest data:")
for key, value in data.items():
    print(f"  {key}: {value}")

print("\nCalling FYERS API...")
try:
    response = fyers_model.history(data=data)
    
    print(f"\nResponse status: {response.get('s', 'unknown')}")
    print(f"Response code: {response.get('code', 'unknown')}")
    print(f"Response message: {response.get('message', 'no message')}")
    
    if response.get('s') == 'ok':
        candles = response.get('candles', [])
        print(f"\nNumber of candles: {len(candles)}")
        
        if candles:
            print(f"\nFirst candle:")
            print(f"  {candles[0]}")
            print(f"\nLast candle:")
            print(f"  {candles[-1]}")
            
            # Convert first timestamp
            from datetime import datetime
            ts = candles[0][0]
            dt = datetime.fromtimestamp(ts)
            print(f"\nFirst candle date: {dt}")
    else:
        print(f"\n❌ API Error!")
        print(f"Full response: {response}")

except Exception as e:
    print(f"\n❌ Exception occurred: {e}")
    import traceback
    traceback.print_exc()
