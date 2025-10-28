"""
Quick WebSocket Live Test
Tests WebSocket streaming for a few seconds
"""
import sys
import os
import time
import threading

# Add project root to path (parent directory of tests/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_websocket_live():
    """Test live WebSocket connection"""
    print("\n" + "="*80)
    print("LIVE WEBSOCKET TEST")
    print("="*80)
    
    try:
        from fyers_apiv3.FyersWebsocket import data_ws
        from scripts.core.index_constituents import get_nifty50_symbols
        
        # Get token from auth directory (one level up from tests/)
        auth_file = os.path.join(project_root, 'auth', 'access_token.txt')
        with open(auth_file, 'r', encoding='utf-8') as f:
            token = f.read().strip()
        
        client_id = "8I122G8NSD-100"
        access_token = f"{client_id}:{token}"
        
        # Track received messages
        message_count = {'count': 0, 'symbols': set()}
        
        def onmessage(message):
            message_count['count'] += 1
            if isinstance(message, dict):
                if message.get('type') == 'sub':
                    print(f"[OK] Subscription: {message.get('message')}")
                elif message.get('symbol'):
                    symbol = message['symbol']
                    message_count['symbols'].add(symbol)
                    if message_count['count'] <= 5:
                        ltp = message.get('ltp', 0)
                        print(f"[DATA] {symbol}: Rs.{ltp}")
        
        def onerror(message):
            print(f"[ERROR] {message}")
        
        def onclose(message):
            print(f"[CLOSE] Connection closed")
        
        def onopen():
            print("[OK] WebSocket connected!")
            symbols = get_nifty50_symbols()[:5]  # Test with 5 symbols
            print(f"[SUB] Subscribing to {len(symbols)} symbols...")
            fyers.subscribe(symbols=symbols, data_type="SymbolUpdate")
            fyers.keep_running()
        
        # Create WebSocket
        log_dir = os.path.join(project_root, 'logs')
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
        
        print("Starting WebSocket connection...")
        print("Test will run for 10 seconds...")
        
        # Run in background thread
        ws_thread = threading.Thread(target=fyers.connect, daemon=True)
        ws_thread.start()
        
        # Wait 10 seconds
        time.sleep(10)
        
        # Summary
        print("\n" + "="*80)
        print("TEST RESULTS")
        print("="*80)
        print(f"Total messages received: {message_count['count']}")
        print(f"Unique symbols: {len(message_count['symbols'])}")
        if message_count['symbols']:
            print(f"Symbols: {', '.join(list(message_count['symbols'])[:10])}")
        
        if message_count['count'] > 0:
            print("\n[OK] WebSocket streaming is WORKING!")
            return True
        else:
            print("\n[WARNING] No messages received - may be outside market hours")
            return False
        
    except Exception as e:
        print(f"\n[ERROR] WebSocket test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_websocket_live()
    sys.exit(0 if success else 1)
