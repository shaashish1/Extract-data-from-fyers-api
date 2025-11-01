
# Add scripts directory to path for authentication
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from auth.my_fyers_model import MyFyersModel

"""
Created By: Aseem Singhal
Fyers API V3
"""

import datetime
from fyers_apiv3 import fyersModel

#generate trading session
client_id = open("client_id.txt",'r').read()
# Get access token from our authentication system
fyers_auth = MyFyersModel()
access_token = fyers_auth.get_access_token()nitialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")


# Fetch Market Depth
data = {
    "symbol":"NSE:NIFTY23SEPFUT",
    "ohlcv_flag":"1"
}
response = fyers.depth(data=data)
print(response)

symbol = data['symbol']

totalbuyqty = response['d'][symbol]['totalbuyqty']
print("Total Buy Qty: ", totalbuyqty)
totalsellqty = response['d'][symbol]['totalsellqty']
print("Total Sell Qty: ", totalsellqty)
top_5_bids = response['d'][symbol]['bids']
print("Top 5 Bids: ", top_5_bids)
top_5_asks = response['d'][symbol]['ask']
print("Top 5 Asks: ", top_5_asks)
upper_ckt = response['d'][symbol]['upper_ckt']
print("Upper Circuit: ", upper_ckt)
lower_ckt = response['d'][symbol]['lower_ckt']
print("Lower Circuit: ", lower_ckt)


# Fetch order details
orders = fyers.orderbook()
print(orders)

# Fetch position details
positions = fyers.positions()
print(positions)

# Fetch Tradebook details
tradebook = fyers.tradebook()
print(tradebook)

# Fetch Fund details
funds = fyers.funds()
print(funds)

# Fetch Holding details
holdings = fyers.holdings()
print(holdings)
