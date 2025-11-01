#!/usr/bin/env python3
"""
Direct test of FYERS API without MyFyersModel wrapper
"""

import configparser
from datetime import datetime, timedelta
from fyers_apiv3.fyersModel import FyersModel

# Read config
config = configparser.ConfigParser()
config.read('auth/credentials.ini')
client_id = config['fyers']['client_id']

# Read token directly
with open('auth/access_token.txt', 'r') as f:
    access_token = f.read().strip()

print(f"Client ID: {client_id}")
print(f"Token (first 50 chars): {access_token[:50]}...")
print(f"Token length: {len(access_token)}")

# Create FyersModel directly
fyers = FyersModel(client_id=client_id, token=access_token, log_path="", is_async=False)

# Test with FYERS documentation example symbol
symbol = "NSE:SBIN-EQ"  # State Bank of India
print(f"\nTesting with symbol: {symbol}")

# Calculate dates - go back in time properly
end_date = datetime.now() - timedelta(days=1)  # Yesterday to avoid partial candles
start_date = end_date - timedelta(days=30)  # Just 30 days for testing

print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

# Prepare request
data = {
    "symbol": symbol,
    "resolution": "D",
    "date_format": "1",
    "range_from": start_date.strftime('%Y-%m-%d'),
    "range_to": end_date.strftime('%Y-%m-%d'),
    "cont_flag": "1"
}

print(f"\nRequest:")
for key, value in data.items():
    print(f"  {key}: {value}")

print("\nCalling FYERS API...")
response = fyers.history(data=data)

print(f"\nResponse status: {response.get('s', 'unknown')}")
print(f"Response code: {response.get('code', 'unknown')}")
print(f"Response message: {response.get('message', 'no message')}")

if response.get('s') == 'ok':
    candles = response.get('candles', [])
    print(f"\n✅ SUCCESS! Number of candles: {len(candles)}")
    
    if candles:
        print(f"\nFirst candle: {candles[0]}")
        print(f"Last candle: {candles[-1]}")
        
        # Convert timestamp
        ts = candles[0][0]
        dt = datetime.fromtimestamp(ts)
        print(f"\nFirst candle date: {dt}")
else:
    print(f"\n❌ API Error!")
    print(f"Full response: {response}")
