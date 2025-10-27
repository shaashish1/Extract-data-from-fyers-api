"""
Real-time WebSocket data streaming with Parquet storage
Replaces run_websocket.py with Parquet-based real-time data collection
"""
import time
import threading
import pandas as pd
from datetime import datetime, timedelta
from my_fyers_model import client_id, MyFyersModel, get_access_token
from fyers_apiv3.FyersWebsocket import data_ws
from data_storage import get_parquet_manager
from constants import time_zone, option_symbols
from index_constituents import get_nifty50_symbols

# Initialize components
fy_model = MyFyersModel()
parquet_manager = get_parquet_manager()

# WebSocket configuration
access_token = f"{client_id}:{get_access_token()}"
# use SymbolUpdate to receive the full market data attributes
data_type = "SymbolUpdate"
live_data = {}

# Hold last created FyersDataSocket instance (used if the callback is invoked without args)
last_fyers_instance = None

# Buffer for collecting real-time data before saving
data_buffer = []
buffer_size = 100  # Save to file every 100 data points
last_save_time = datetime.now()
save_interval = timedelta(minutes=5)  # Save every 5 minutes regardless of buffer size

# Symbols to track - now using enhanced symbol discovery with complete coverage
try:
    # Import enhanced symbol discovery with complete coverage (preferred)
    from comprehensive_symbol_discovery import get_comprehensive_symbol_discovery
    enhanced_discovery = get_comprehensive_symbol_discovery()
    
    # Get optimized WebSocket symbol list (prioritized for streaming)
    print("🔄 Loading symbols using enhanced discovery with complete coverage...")
    symbols_to_track = enhanced_discovery.get_websocket_symbols(50)  # Top 50 for WebSocket
    
    print(f"📊 Tracking {len(symbols_to_track)} symbols using enhanced discovery")
    print(f"🎯 Symbol breakdown:")
    
    # Show breakdown of symbols
    nifty50_count = len([s for s in symbols_to_track if s in enhanced_discovery.get_symbols_for_category('nifty50')])
    bank_count = len([s for s in symbols_to_track if s in enhanced_discovery.get_symbols_for_category('bank_nifty')])
    etf_count = len([s for s in symbols_to_track if s in enhanced_discovery.get_symbols_for_category('etfs')])
    indices_count = len([s for s in symbols_to_track if s in enhanced_discovery.get_symbols_for_category('indices')])
    
    print(f"   • Nifty50: {nifty50_count} symbols")
    print(f"   • Bank Nifty: {bank_count} symbols")
    print(f"   • ETFs: {etf_count} symbols") 
    print(f"   • Indices: {indices_count} symbols")
    print(f"   📋 Sample symbols: {symbols_to_track[:5]}")
    
except ImportError:
    # Fallback to symbol discovery
    print("⚠️  Enhanced discovery not available, using fallback...")
    try:
        from symbol_discovery import SymbolDiscovery
        symbol_discovery = SymbolDiscovery()
        
        # Get symbols using the fallback approach
        print("🔄 Loading symbols using standard symbol discovery...")
        nifty50_symbols = symbol_discovery.get_nifty50_constituents()[:10]  # Top 10 for demo
        bank_symbols = symbol_discovery.get_banknifty_constituents()[:5]    # Top 5 banks
        etf_symbols = symbol_discovery.get_etf_symbols()[:3]                # Top 3 ETFs
        
        # Combine symbols for tracking
        symbols_to_track = nifty50_symbols + bank_symbols + etf_symbols
        
        print(f"📊 Tracking {len(symbols_to_track)} symbols using standard discovery")
        print(f"   • Nifty50 (top 10): {len(nifty50_symbols)} symbols")
        print(f"   • Bank Nifty (top 5): {len(bank_symbols)} symbols") 
        print(f"   • ETFs (top 3): {len(etf_symbols)} symbols")
        
    except ImportError:
        # Final fallback to hardcoded symbols
        print("⚠️  Symbol discovery not available, using hardcoded fallback...")
        symbols_to_track = get_nifty50_symbols()[:15]  # Top 15 Nifty50 stocks
        print(f"📊 Tracking {len(symbols_to_track)} hardcoded symbols")

except Exception as e:
    print(f"⚠️ Failed to load symbols using enhanced discovery, using fallback: {e}")
    # Fallback to a small set if all discovery methods fail
    symbols_to_track = [
        "NSE:RELIANCE-EQ",
        "NSE:TCS-EQ", 
        "NSE:HDFCBANK-EQ",
        "NSE:ICICIBANK-EQ",
        "NSE:INFY-EQ"
    ]
    print(f"📊 Using basic fallback symbols: {len(symbols_to_track)} symbols")

print(f"✅ WebSocket symbols loaded: {len(symbols_to_track)} total symbols")


def symbol_to_filename(fyers_symbol):
    """
    Convert Fyers symbol to filename format
    
    Args:
        fyers_symbol (str): Fyers symbol format
        
    Returns:
        str: Filename-friendly symbol name
    """
    symbol_mapping = {
        "NSE:NIFTY50-INDEX": "nifty50",
        "NSE:NIFTYBANK-INDEX": "niftybank", 
        "NSE:FINNIFTY-INDEX": "finnifty",
        "NSE:INDIAVIX-INDEX": "indiavix",
        "NSE:TATAPOWER-EQ": "tatapower",
        "NSE:RELIANCE-EQ": "reliance",
        "NSE:INFY-EQ": "infy",
        "NSE:TCS-EQ": "tcs"
    }
    
    return symbol_mapping.get(fyers_symbol, fyers_symbol.replace("NSE:", "").replace("-EQ", "").replace("-INDEX", "").lower())

def save_buffer_to_parquet():
    """Save buffered SymbolUpdate messages to Parquet (raw market updates)."""
    global data_buffer, last_save_time

    if not data_buffer:
        return

    # Group data by symbol
    symbol_data = {}
    for data_point in data_buffer:
        symbol = data_point['symbol']
        if symbol not in symbol_data:
            symbol_data[symbol] = []
        symbol_data[symbol].append(data_point)

    # Save each symbol's raw market update
    for fyers_symbol, data_points in symbol_data.items():
        try:
            df = pd.DataFrame(data_points)

            # Ensure timestamp column exists and is datetime
            if 'last_traded_time' in df.columns and df['last_traded_time'].notna().any():
                # last_traded_time may be epoch millis or seconds; try to coerce
                try:
                    df['timestamp'] = pd.to_datetime(df['last_traded_time'], unit='ms', errors='coerce')
                    if df['timestamp'].isna().all():
                        df['timestamp'] = pd.to_datetime(df['last_traded_time'], unit='s', errors='coerce')
                except Exception:
                    df['timestamp'] = pd.to_datetime(df.get('timestamp', datetime.now()))
            else:
                df['timestamp'] = pd.to_datetime(df.get('timestamp', datetime.now()))

            # Convert filename and save using the new market update method
            symbol_name = symbol_to_filename(fyers_symbol)
            parquet_manager.save_market_update(df, symbol_name, mode='append')

            print(f"💾 Saved {len(df)} market update rows for {symbol_name}")

        except Exception as e:
            print(f"❌ Error saving market updates for {fyers_symbol}: {e}")

    # Clear buffer and update last save time
    data_buffer = []
    last_save_time = datetime.now()
    print(f"🔄 Buffer cleared at {last_save_time.strftime('%H:%M:%S')}")

def on_message(message):
    """
    Callback function to handle incoming WebSocket messages
    
    Parameters:
        message (dict or list): The received message from the WebSocket
    """
    global data_buffer, last_save_time
    
    try:
        # Handle both single message and list of messages
        messages = message if isinstance(message, list) else [message]
        
        for msg in messages:
            if isinstance(msg, dict) and 'symbol' in msg:
                # Build a normalized market-update record with requested attributes
                record = {}
                # Always include symbol
                record['symbol'] = msg.get('symbol')

                # List of desired fields to capture (best-effort using keys present in the message)
                desired = [
                    'ltp', 'prev_close_price', 'high_price', 'low_price', 'open_price',
                    'ch', 'chp', 'vol_traded_today', 'last_traded_time',
                    'bid_size', 'ask_size', 'ask_price', 'bid_price', 'last_traded_qty',
                    'tot_buy_qty', 'tot_sell_qty', 'avg_trade_price', 'type'
                ]

                for key in desired:
                    record[key] = msg.get(key)

                # Provide a fallback for some common alternate keys used by Fyers
                if record.get('last_traded_time') is None:
                    record['last_traded_time'] = msg.get('ltt') or msg.get('lt_time')
                if record.get('prev_close_price') is None:
                    record['prev_close_price'] = msg.get('pc') or msg.get('prev_close')
                if record.get('avg_trade_price') is None:
                    record['avg_trade_price'] = msg.get('avg_price') or msg.get('vwap')

                # Timestamp: prefer last_traded_time when present, otherwise now
                if record.get('last_traded_time') is not None:
                    record['timestamp'] = record['last_traded_time']
                else:
                    record['timestamp'] = datetime.now()

                # Store in live_data and buffer
                symbol = record['symbol']
                live_data[symbol] = record
                data_buffer.append(record.copy())

                # Print a short live line
                ltp = record.get('ltp', 'N/A')
                volume = record.get('vol_traded_today', 'N/A')
                symbol_name = symbol_to_filename(symbol)
                print(f"📊 {symbol_name}: LTP={ltp}, Volume={volume}")
        
        # Check if we should save buffer
        current_time = datetime.now()
        if (len(data_buffer) >= buffer_size or 
            current_time - last_save_time >= save_interval):
            save_buffer_to_parquet()
            
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        print(f"Message: {message}")

def on_error(message):
    """
    Callback function to handle WebSocket errors
    
    Parameters:
        message (dict): The error message received from the WebSocket
    """
    print(f"❌ WebSocket Error: {message}")

def on_close(message):
    """
    Callback function to handle WebSocket connection close events
    """
    print(f"🔌 WebSocket Connection Closed: {message}")
    
    # Save any remaining buffer data
    if data_buffer:
        print("💾 Saving remaining buffer data...")
        save_buffer_to_parquet()

def on_open(*args, **kwargs):
    """
    Callback function to subscribe to data type and symbols upon WebSocket connection
    
    Parameters:
        fyers: The FyersDataSocket instance
    """
    # Determine fyers instance: prefer first positional arg, else fallback to last_fyers_instance
    fyers = args[0] if args else globals().get('last_fyers_instance')
    print(f"🔌 WebSocket Connected!")
    print(f"📡 Subscribing to {len(symbols_to_track)} symbols...")

    for symbol in symbols_to_track:
        print(f"   📈 {symbol}")

    # Subscribe to the specified symbols and data type
    if fyers is not None:
        fyers.subscribe(symbols=symbols_to_track, data_type=data_type)
        # Keep the socket running to receive real-time data
        fyers.keep_running()
    else:
        print("⚠️  Unable to subscribe: FyersDataSocket instance not available in on_open callback")

def run_websocket():
    """Initialize and run the WebSocket connection"""
    try:
        print("🚀 Starting Fyers WebSocket (Parquet Storage)")
        print("=" * 50)
        
        # Create a Fyers DataSocket instance
        fyers = data_ws.FyersDataSocket(
            access_token=access_token,  # Access token in the format "appid:accesstoken"
            log_path="logs",  # Path to save logs
            litemode=False,  # Lite mode disabled for full data
            write_to_file=False,  # We'll handle file writing ourselves
            reconnect=True,  # Enable auto-reconnection
            on_connect=on_open,  # Callback function to subscribe to data upon connection
            on_close=on_close,  # Callback function to handle WebSocket close events
            on_error=on_error,  # Callback function to handle WebSocket errors
            on_message=on_message  # Callback function to handle incoming messages
        )
        # Save instance to module-level variable so callbacks that don't receive the instance can still use it
        try:
            globals()['last_fyers_instance'] = fyers
        except Exception:
            pass
        
        # Establish a connection to the Fyers WebSocket
        fyers.connect()
        
    except Exception as e:
        print(f"❌ Error starting WebSocket: {e}")

def show_live_summary():
    """Display summary of live data being collected"""
    while True:
        time.sleep(30)  # Show summary every 30 seconds
        
        if live_data:
            print(f"\n📊 Live Data Summary ({datetime.now().strftime('%H:%M:%S')}):")
            print("-" * 40)
            
            for symbol, data in live_data.items():
                symbol_name = symbol_to_filename(symbol)
                ltp = data.get('ltp', 'N/A')
                volume = data.get('vol_traded_today', 'N/A')
                change = data.get('ch', 'N/A')
                print(f"  {symbol_name:12}: LTP={ltp:>8} | Vol={volume:>10} | Chg={change:>6}")
            
            print(f"  Buffer size: {len(data_buffer)} points")
        else:
            # No live data available — attempt to show last saved snapshot from Parquet
            print("⏳ No live data available. Showing last saved snapshot (if any):")
            print("-" * 40)
            # Show only first 10 symbols to keep output compact
            for fyers_symbol in symbols_to_track[:10]:
                try:
                    symbol_name = symbol_to_filename(fyers_symbol)
                    latest = parquet_manager.load_latest_market_update(symbol_name)
                    if latest:
                        ts = latest.get('timestamp')
                        # format timestamp if it's a numpy/pandas datetime
                        try:
                            ts_str = pd.to_datetime(ts).strftime('%Y-%m-%d %H:%M:%S')
                        except Exception:
                            ts_str = str(ts)
                        ltp = latest.get('ltp', 'N/A')
                        ch = latest.get('ch', 'N/A')
                        chp = latest.get('chp', 'N/A')
                        vol = latest.get('vol_traded_today', latest.get('volume', 'N/A'))
                        print(f"  {symbol_name:12}: LTP={ltp:>8} | Vol={vol:>10} | Chg={ch:>6} ({chp}%) @ {ts_str}")
                    else:
                        print(f"  {symbol_name:12}: No snapshot available")
                except Exception as e:
                    print(f"  Error reading snapshot for {fyers_symbol}: {e}")

if __name__ == "__main__":
    try:
        # Start live summary in a separate thread
        summary_thread = threading.Thread(target=show_live_summary, daemon=True)
        summary_thread.start()
        
        # Run the main WebSocket loop
        while True:
            run_websocket()
            print("🔄 Reconnecting in 60 seconds...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n⚠️  WebSocket interrupted by user")
        
        # Save any remaining buffer data
        if data_buffer:
            print("💾 Saving final buffer data...")
            save_buffer_to_parquet()
            
        print("🔌 WebSocket connection closed")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        
        # Save any remaining buffer data
        if data_buffer:
            print("💾 Saving final buffer data...")
            save_buffer_to_parquet()