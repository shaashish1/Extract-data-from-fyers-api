import configparser
from fyers_apiv3 import fyersModel

# Read client_id from auth/credentials.ini
config = configparser.ConfigParser()
config.read("auth/credentials.ini")
client_id = config.get("fyers", "client_id")

# Read access_token from auth/access_token.txt
with open("auth/access_token.txt", "r") as f:
    access_token = f.read().strip()

print(f"Client ID: {client_id}")
print(f"Token length: {len(access_token)}")

# Initialize the FyersModel instance - MUST use is_async=False for synchronous calls
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")

# Make a request to get the funds information
print("\nCalling funds() API...")
response = fyers.funds()
print(f"\nResponse: {response}")

if response.get('s') == 'ok':
    print("\n✅ SUCCESS - Funds retrieved")
    print(f"Fund details: {response.get('fund_limit', [])}")
else:
    print(f"\n❌ FAILED - Error code: {response.get('code')}, Message: {response.get('message')}")