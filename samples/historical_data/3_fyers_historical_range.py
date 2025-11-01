
# Add scripts directory to path for authentication
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from auth.my_fyers_model import MyFyersModel

"""
Created By: Aseem Singhal
Fyers API V3

"""

import pandas as pd
from fyers_apiv3 import fyersModel
import pytz


#generate trading session
client_id = open("client_id.txt",'r').read()
# Get access token from our authentication system
fyers_auth = MyFyersModel()
access_token = fyers_auth.get_access_token()nitialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="C:/Users/aseem/Downloads/")

def fetchOHLC(ticker,interval,range_from, range_to):
    data = {
        "symbol":ticker,
        "resolution":interval,
        "date_format":"1",
        "range_from":range_from,
        "range_to":range_to,
        "cont_flag":"1"
    }

    '''
    1 minute : “1”
    2 minute : “2"
    3 minute : "3"
    5 minute : "5"
    10 minute : "10"
    15 minute : "15"
    20 minute : "20"
    30 minute : "30"
    60 minute : "60"
    120 minute : "120"
    240 minute : "240"
    Daily : "D"
    range format: yyyy-mm-dd
    '''
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

# Fetch OHLC data using the function
response_df = fetchOHLC("NSE:NIFTY23SEP20000CE","5","2023-08-18", "2023-08-29")

# Print the DataFrame
print(response_df)

# Save data to a CSV file
response_df.to_csv('output.csv', index=False)



