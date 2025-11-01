import configparser
from fyers_apiv3 import fyersModel

# Read client_id dynamically from auth/credentials.ini
config = configparser.ConfigParser()
config.read("auth/credentials.ini")
client_id = config.get("fyers", "client_id")

# Read access_token dynamically from auth/access_token.txt
with open("auth/access_token.txt", "r", encoding="utf-8") as f:
	access_token = f.read().strip()

fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")
response = fyers.get_profile()
print(response)

