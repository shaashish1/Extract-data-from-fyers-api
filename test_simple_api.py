"""
Simple FYERS API test - quick timeout to avoid hanging
"""
import configparser
from fyers_apiv3.fyersModel import FyersModel
from datetime import datetime, timedelta

print("=" * 60)
print("SIMPLE FYERS API TEST")
print("=" * 60)

# Load credentials
config = configparser.ConfigParser()
config.read('auth/credentials.ini')
client_id = config['fyers']['client_id']

print(f"\n1. Client ID: {client_id}")

# Load token
with open('auth/access_token.txt', 'r') as f:
    access_token = f.read().strip()

print(f"2. Token length: {len(access_token)} characters")
print(f"3. Token preview: {access_token[:50]}...")

# Create FyersModel with 5 second timeout
print("\n4. Creating FyersModel instance...")
fyers = FyersModel(
    client_id=client_id, 
    token=access_token, 
    log_path="",
    is_async=False
)

print("5. FyersModel created successfully")

# Test 1: Get Profile (simplest API call)
print("\n" + "=" * 60)
print("TEST 1: Profile API")
print("=" * 60)
try:
    print("Calling fyers.get_profile()...")
    response = fyers.get_profile()
    print(f"Response: {response}")
    
    if response.get('s') == 'ok':
        print("✅ Profile API: SUCCESS")
        print(f"   Name: {response.get('data', {}).get('name', 'N/A')}")
        print(f"   Email: {response.get('data', {}).get('email_id', 'N/A')}")
    else:
        print(f"❌ Profile API: FAILED")
        print(f"   Error code: {response.get('code')}")
        print(f"   Message: {response.get('message')}")
except Exception as e:
    print(f"❌ Profile API: EXCEPTION - {e}")

# Test 2: Get Funds
print("\n" + "=" * 60)
print("TEST 2: Funds API")
print("=" * 60)
try:
    print("Calling fyers.funds()...")
    response = fyers.funds()
    print(f"Response: {response}")
    
    if response.get('s') == 'ok':
        print("✅ Funds API: SUCCESS")
    else:
        print(f"❌ Funds API: FAILED")
        print(f"   Error code: {response.get('code')}")
        print(f"   Message: {response.get('message')}")
except Exception as e:
    print(f"❌ Funds API: EXCEPTION - {e}")

# Test 3: Get Quotes (no market depth needed)
print("\n" + "=" * 60)
print("TEST 3: Quotes API")
print("=" * 60)
try:
    symbols = "NSE:SBIN-EQ"
    print(f"Calling fyers.quotes() for {symbols}...")
    response = fyers.quotes({"symbols": symbols})
    print(f"Response: {response}")
    
    if response.get('s') == 'ok':
        print("✅ Quotes API: SUCCESS")
    else:
        print(f"❌ Quotes API: FAILED")
        print(f"   Error code: {response.get('code')}")
        print(f"   Message: {response.get('message')}")
except Exception as e:
    print(f"❌ Quotes API: EXCEPTION - {e}")

# Test 4: History API (smallest possible request)
print("\n" + "=" * 60)
print("TEST 4: History API (1 day only)")
print("=" * 60)
try:
    # Yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    
    data = {
        "symbol": "NSE:SBIN-EQ",
        "resolution": "D",
        "date_format": "1",
        "range_from": date_str,
        "range_to": date_str,
        "cont_flag": "1"
    }
    
    print(f"Request: {data}")
    print("Calling fyers.history()...")
    response = fyers.history(data=data)
    print(f"Response: {response}")
    
    if response.get('s') == 'ok':
        print("✅ History API: SUCCESS")
        candles = response.get('candles', [])
        print(f"   Candles received: {len(candles)}")
    else:
        print(f"❌ History API: FAILED")
        print(f"   Error code: {response.get('code')}")
        print(f"   Message: {response.get('message')}")
except Exception as e:
    print(f"❌ History API: EXCEPTION - {e}")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
