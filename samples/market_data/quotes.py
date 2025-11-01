import configparser
from fyers_apiv3 import fyersModel

# Dynamic credentials
config = configparser.ConfigParser()
config.read("auth/credentials.ini")
client_id = config.get("fyers", "client_id")
with open("auth/access_token.txt", "r", encoding="utf-8") as f:
    access_token = f.read().strip()

fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")

data = {
    "symbols":"NSE:SBIN-EQ,NSE:IDEA-EQ"
}

response = fyers.quotes(data=data)
print(response)