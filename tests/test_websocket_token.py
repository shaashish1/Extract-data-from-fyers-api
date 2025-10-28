from fyers_apiv3.FyersWebsocket import data_ws
import os


def onmessage(message):
    print("Response:", message)


def onerror(message):
    print("Error:", message)


def onclose(message):
    print("Connection closed:", message)


def onopen():
    data_type = "SymbolUpdate"
    symbols = ['NSE:SBIN-EQ', 'NSE:ADANIENT-EQ']
    fyers.subscribe(symbols=symbols, data_type=data_type)
    fyers.keep_running()

# Read the latest access token from the correct file location

def get_access_token():
    # Get project root (parent of tests/ directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auth_file = os.path.join(project_root, 'auth', 'access_token.txt')
    
    if os.path.exists(auth_file):
        with open(auth_file, 'r') as f:
            return f.read().strip()
    raise FileNotFoundError(f"access_token.txt not found at {auth_file}")

raw_token = get_access_token()
access_token = "8I122G8NSD-100:" + raw_token

# Get project root for log directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(project_root, 'logs')

print(f"🔑 Using token (first 50 chars): {raw_token[:50]}...")
print(f"🔗 Full access_token format: 8I122G8NSD-100:{raw_token[:30]}...")
print(f"📏 Token length: {len(raw_token)}")
print("-" * 80)

fyers = data_ws.FyersDataSocket(
    access_token=access_token,
    log_path=log_dir,  # Store logs in project logs/ directory
    litemode=False,
    write_to_file=False,
    reconnect=True,
    on_connect=onopen,
    on_close=onclose,
    on_error=onerror,
    on_message=onmessage
)

fyers.connect()
