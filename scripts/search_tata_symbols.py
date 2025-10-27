#!/usr/bin/env python3
"""
Search for TATA Motors correct symbol using symbol search
"""
import sys
from pathlib import Path

# Add scripts directory to Python path
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from my_fyers_model import MyFyersModel

def search_tata_symbols():
    """Search for TATA related symbols"""
    fyers = MyFyersModel()
    
    print("🔍 Searching for TATA related symbols...")
    print("=" * 50)
    
    # Search patterns
    search_terms = ['TATA', 'MOTOR', 'AUTOMOTIVE']
    
    for term in search_terms:
        print(f"\n🔍 Searching for: {term}")
        try:
            data = {"symbol": term}
            response = fyers.fyers_model.symbol_details(data=data)
            
            if response and response.get('s') == 'ok':
                symbols = response.get('d', [])
                print(f"Found {len(symbols)} symbols")
                
                # Filter for TATA MOTORS related
                tata_motor_symbols = []
                for symbol in symbols:
                    symbol_name = symbol.get('symbol', '')
                    display_name = symbol.get('description', '')
                    
                    if 'TATA' in symbol_name.upper() and 'MOTOR' in symbol_name.upper():
                        tata_motor_symbols.append((symbol_name, display_name))
                    elif 'TATA' in display_name.upper() and 'MOTOR' in display_name.upper():
                        tata_motor_symbols.append((symbol_name, display_name))
                
                if tata_motor_symbols:
                    print("🚗 TATA Motors related symbols found:")
                    for sym, desc in tata_motor_symbols:
                        print(f"  • {sym} - {desc}")
                else:
                    print("❌ No TATA Motors symbols found")
            else:
                print(f"❌ Search failed: {response.get('message', 'Unknown error') if response else 'No response'}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def check_nifty50_composition():
    """Check current Nifty 50 composition from a reliable source"""
    print(f"\n" + "=" * 50)
    print("📋 Checking if TATA Motors is still in Nifty 50...")
    
    # TATA Motors might have been removed from Nifty 50
    # Let's check the current Nifty 50 without TATA Motors
    
    # Alternative symbols that might have replaced TATA Motors
    possible_replacements = [
        'NSE:ADANIENT-EQ',      # Adani Enterprises  
        'NSE:SHRIRAMFIN-EQ',    # Shriram Finance
        'NSE:LTIM-EQ',          # LTIMindtree
        'NSE:PIDILITIND-EQ',    # Pidilite Industries
        'NSE:APOLLOHOSP-EQ',    # Apollo Hospitals
        'NSE:SBILIFE-EQ',       # SBI Life
        'NSE:M&M-EQ',           # Mahindra & Mahindra
        'NSE:BAJAJ-AUTO-EQ'     # Bajaj Auto
    ]
    
    fyers = MyFyersModel()
    
    print("✅ Testing possible Nifty 50 replacements:")
    working_symbols = []
    
    for symbol in possible_replacements:
        try:
            data = {
                "symbol": symbol,
                "ohlcv_flag": "1"
            }
            
            response = fyers.fyers_model.depth(data=data)
            
            if response and response.get('s') == 'ok':
                symbol_data = response.get('d', {}).get(symbol, {})
                if symbol_data and symbol_data.get('ltp', 0) > 0:
                    ltp = symbol_data.get('ltp', 0)
                    volume = symbol_data.get('v', 0)
                    print(f"  ✅ {symbol}: LTP: ₹{ltp}, Volume: {volume:,}")
                    working_symbols.append(symbol)
                else:
                    print(f"  ❌ {symbol}: No data")
            else:
                print(f"  ❌ {symbol}: API error")
                
        except Exception as e:
            print(f"  ❌ {symbol}: Exception - {e}")
    
    return working_symbols

if __name__ == "__main__":
    search_tata_symbols()
    working_replacements = check_nifty50_composition()
    
    if working_replacements:
        print(f"\n🎯 Suggested replacement symbols for TATAMOTORS:")
        for symbol in working_replacements:
            print(f"  • {symbol}")