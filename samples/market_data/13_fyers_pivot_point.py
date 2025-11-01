
# Add scripts directory to path for authentication
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from auth.my_fyers_model import MyFyersModel

"""
Created By: Aseem Singhal
Fyers API V3

"""

import datetime as dt
from fyers_apiv3 import fyersModel
import pandas as pd
import pytz

#generate trading session
client_id = open("client_id.txt",'r').read()
# Get access token from our authentication system
fyers_auth = MyFyersModel()
access_token = fyers_auth.get_access_token()nitialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

def fetchOHLC2(ticker,interval,duration):
    range_from = dt.date.today()-dt.timedelta(duration)
    range_to = dt.date.today()

    from_date_string = range_from.strftime("%Y-%m-%d")
    to_date_string = range_to.strftime("%Y-%m-%d")
    data = {
        "symbol":ticker,
        "resolution":interval,
        "date_format":"1",
        "range_from":from_date_string,
        "range_to":to_date_string,
        "cont_flag":"1"
    }

    response = fyers.history(data=data)['candles']

    # Create a DataFrame
    columns = ['Timestamp','Open','High','Low','Close','Volume']
    df = pd.DataFrame(response, columns=columns)

    # Convert Timestamp to datetime in UTC
    df['Timestamp2'] = pd.to_datetime(df['Timestamp'],unit='s').dt.tz_localize(pytz.utc)

    # Convert Timestamp to IST
    ist = pytz.timezone('Asia/Kolkata')
    df['Timestamp2'] = df['Timestamp2'].dt.tz_convert(ist)

    return (df)


def pivotpoints_today(ohlc_day):
    """returns pivot point and support/resistance levels"""
    high = round(ohlc_day["High"].iloc[-1],2)
    low = round(ohlc_day["Low"].iloc[-1],2)
    close = round(ohlc_day["Close"].iloc[-1],2)
    pivot = round((high + low + close)/3,2)
    r1 = round((2*pivot - low),2)
    r2 = round((pivot + (high - low)),2)
    r3 = round((high + 2*(pivot - low)),2)
    s1 = round((2*pivot - high),2)
    s2 = round((pivot - (high - low)),2)
    s3 = round((low - 2*(high - pivot)),2)
    return (pivot,r1,r2,r3,s1,s2,s3)


# Fetch OHLC data using the function
stock_df = fetchOHLC2("NSE:SBIN-EQ","30",100)
#print(stock_df)

stock_df['Timestamp2'] = pd.to_datetime(stock_df['Timestamp2'])
stock_df.drop(columns=['Timestamp'], inplace=True)
stock_df.set_index('Timestamp2', inplace=True)
print(stock_df)

daily_df = stock_df.resample('D').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
daily_df.dropna(inplace=True)
print(daily_df)

pivot,r1,r2,r3,s1,s2,s3 = pivotpoints_today(daily_df)
print("Pivot of today: ",pivot)
print("R1: ",r1)
print("S1: ",s1)




