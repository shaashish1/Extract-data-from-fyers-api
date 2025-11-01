#!/usr/bin/env python3
"""
Test FYERS authentication with profile API
"""

import configparser
from fyers_apiv3.fyersModel import FyersModel

# Read config
config = configparser.ConfigParser()
config.read('auth/credentials.ini')
client_id = config['fyers']['client_id']

# Read token
with open('auth/access_token.txt', 'r') as f:
    access_token = f.read().strip()

print(f"Testing FYERS authentication...")
print(f"Client ID: {client_id}")

# Create FyersModel
fyers = FyersModel(client_id=client_id, token=access_token, log_path="", is_async=False)

# Try to get profile (this should work if token is valid)
print("\n1. Testing with get_profile()...")
try:
    profile = fyers.get_profile()
    print(f"✅ Profile API Response: {profile}")
except Exception as e:
    print(f"❌ Profile API Error: {e}")

# Try funds API
print("\n2. Testing with funds()...")
try:
    funds = fyers.funds()
    print(f"Response: {funds}")
    if funds and funds.get('s') == 'ok':
        print("✅ Funds API works!")
    else:
        print(f"❌ Funds API error: {funds}")
except Exception as e:
    print(f"❌ Funds API Exception: {e}")

# Try positions
print("\n3. Testing with positions()...")
try:
    positions = fyers.positions()
    print(f"Response: {positions}")
    if positions and positions.get('s') == 'ok':
        print("✅ Positions API works!")
    else:
        print(f"❌ Positions API error: {positions}")
except Exception as e:
    print(f"❌ Positions API Exception: {e}")

print("\n" + "="*60)
print("If profile/funds APIs work but history fails,")
print("it means the token is valid but data API access is restricted.")
print("="*60)
