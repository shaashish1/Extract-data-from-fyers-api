"""
Quick test to see what the Fyers API is returning for historical data
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from auth.my_fyers_model import MyFyersModel
from datetime import datetime, timedelta

# Initialize Fyers
fyers = MyFyersModel()
model = fyers.get_fyre_model()

# Test single API call for RELIANCE
symbol = "NSE:RELIANCE-EQ"
end_date = datetime.now()
start_date = end_date - timedelta(days=30)  # Just 30 days for testing

data = {
    "symbol": symbol,
    "resolution": "D",  # Daily
    "date_format": "1",  # YYYY-MM-DD
    "range_from": start_date.strftime("%Y-%m-%d"),
    "range_to": end_date.strftime("%Y-%m-%d"),
    "cont_flag": "1"
}

print(f"Testing API call for {symbol}")
print(f"Date range: {data['range_from']} to {data['range_to']}")
print(f"Request data: {data}")
print("\n" + "="*60)

response = model.history(data=data)

print(f"Response status: {response.get('s')}")
print(f"Response keys: {list(response.keys())}")
print(f"Full response: {response}")

if response.get('s') == 'ok' and 'candles' in response:
    print(f"\n✅ SUCCESS - Got {len(response['candles'])} candles")
    if len(response['candles']) > 0:
        print(f"First candle: {response['candles'][0]}")
        print(f"Last candle: {response['candles'][-1]}")
else:
    print(f"\n❌ FAILED - No candles data")
    if 'message' in response:
        print(f"API Message: {response['message']}")
