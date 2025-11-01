import configparser
from fyers_apiv3 import fyersModel

# Dynamic credentials
config = configparser.ConfigParser()
config.read("auth/credentials.ini")
client_id = config.get("fyers", "client_id")
with open("auth/access_token.txt", "r", encoding="utf-8") as f:
    access_token = f.read().strip()

fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(days=1)
thirty_days_ago = yesterday - timedelta(days=30)

data = {
    "symbol":"NSE:SBIN-EQ",
    "resolution":"D",
    "date_format":"0",
    "range_from": str(int(thirty_days_ago.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())),
    "range_to": str(int(yesterday.replace(hour=23, minute=59, second=0, microsecond=0).timestamp())),
    "cont_flag":"0"
}

response = fyers.history(data=data)
print(response)



