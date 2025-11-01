"""
Test FYERS authentication with correct client_id format.
The token is generated for user XA00330, and we need to use the APP_ID-APP_TYPE format.
"""
from fyers_apiv3.fyersModel import FyersModel
import configparser

# Read credentials
config = configparser.ConfigParser()
config.read('auth/credentials.ini')

# Read token
with open('auth/access_token.txt', 'r') as f:
    access_token = f.read().strip()

print("=" * 80)
print("TESTING FYERS API WITH DIFFERENT CLIENT_ID FORMATS")
print("=" * 80)

# Get both client_id values from credentials
app_client_id = config['FYERS_CREDENTIALS']['client_id']  # 8I122G8NSD-100
user_name = config['FYERS_CREDENTIALS']['user_name']      # XA00330

print(f"\n📋 Available credentials:")
print(f"   app_client_id (APP_ID-APP_TYPE): {app_client_id}")
print(f"   user_name (FYERS username): {user_name}")
print(f"   Token length: {len(access_token)} characters")

# Test 1: Using APP_ID-APP_TYPE format (8I122G8NSD-100)
print(f"\n{'='*80}")
print("TEST 1: Using APP_ID-APP_TYPE format (8I122G8NSD-100)")
print(f"{'='*80}")
try:
    fyers1 = FyersModel(client_id=app_client_id, token=access_token, log_path="", is_async=False)
    
    # Try history API
    data = {
        "symbol": "NSE:SBIN-EQ",
        "resolution": "D",
        "date_format": "1",
        "range_from": "2025-09-29",
        "range_to": "2025-10-29",
        "cont_flag": "1"
    }
    response = fyers1.history(data=data)
    
    if response.get('s') == 'ok':
        print(f"✅ SUCCESS with APP_ID-APP_TYPE format!")
        print(f"   Candles received: {len(response.get('candles', []))}")
        if response.get('candles'):
            print(f"   Sample data: {response['candles'][0]}")
    else:
        print(f"❌ FAILED with APP_ID-APP_TYPE format")
        print(f"   Error: {response}")
        
except Exception as e:
    print(f"❌ EXCEPTION with APP_ID-APP_TYPE format: {e}")

# Test 2: Using username format (XA00330)
print(f"\n{'='*80}")
print("TEST 2: Using username format (XA00330)")
print(f"{'='*80}")
try:
    # Try with just username
    fyers2 = FyersModel(client_id=user_name, token=access_token, log_path="", is_async=False)
    
    data = {
        "symbol": "NSE:SBIN-EQ",
        "resolution": "D",
        "date_format": "1",
        "range_from": "2025-09-29",
        "range_to": "2025-10-29",
        "cont_flag": "1"
    }
    response = fyers2.history(data=data)
    
    if response.get('s') == 'ok':
        print(f"✅ SUCCESS with username format!")
        print(f"   Candles received: {len(response.get('candles', []))}")
        if response.get('candles'):
            print(f"   Sample data: {response['candles'][0]}")
    else:
        print(f"❌ FAILED with username format")
        print(f"   Error: {response}")
        
except Exception as e:
    print(f"❌ EXCEPTION with username format: {e}")

# Test 3: Try profile API to see if it gives more info
print(f"\n{'='*80}")
print("TEST 3: Profile API (to check authentication)")
print(f"{'='*80}")
try:
    fyers3 = FyersModel(client_id=app_client_id, token=access_token, log_path="", is_async=False)
    profile = fyers3.get_profile()
    print(f"Profile response: {profile}")
except Exception as e:
    print(f"Exception: {e}")

print(f"\n{'='*80}")
print("RECOMMENDATION:")
print(f"{'='*80}")
print("Based on test results, update my_fyers_model.py to use the correct client_id format.")
