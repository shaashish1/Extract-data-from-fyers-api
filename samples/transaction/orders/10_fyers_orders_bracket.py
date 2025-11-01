
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

def placeOrderBracket(inst ,t_type,qty,order_type,slPrice, targetPrice, price=0, price_stop=0,):
    exch = inst[:3]
    symb = inst[4:]
    dt = datetime.datetime.now()
    print(dt.hour,":",dt.minute,":",dt.second ," => ",t_type," ",symb," ",qty," ",order_type," @ price =  ",price)
    if(order_type=="MARKET"):
        type1 = 2
        price = 0
        price_stop = 0
    elif(order_type=="LIMIT"):
        type1 = 1
        price_stop = 0
    elif(order_type=="SL-LIMIT"):
        type1 = 4

    if(t_type=="BUY"):
        side1=1
    elif(t_type=="SELL"):
        side1=-1

    data =  {
        "symbol":inst,
        "qty":qty,
        "type":type1,
        "side":side1,
        "productType":"BO",
        "limitPrice":price,
        "stopPrice":price_stop,
        "validity":"DAY",
        "stopLoss": slPrice,
        "takeProfit" : targetPrice
    }

    try:
        orderid = fyers.place_order(data)
        print(dt.hour,":",dt.minute,":",dt.second ," => ", symb , orderid)
        return orderid
    except Exception as e:
        print(dt.hour,":",dt.minute,":",dt.second ," => ", symb , "Failed : {} ".format(e))


placeOrderBracket("NSE:SBIN-EQ" ,'BUY',1,"MARKET", 10,5)
