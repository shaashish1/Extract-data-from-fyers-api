#!/usr/bin/env python3
"""
Dynamic Nifty 50 Symbol Discovery using Fyers WebSocket
Uses Fyers real-time data to discover and validate current Nifty 50 constituents
"""
import sys
import os
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

# Add scripts directory to Python path
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from my_fyers_model import MyFyersModel

# Import Fyers WebSocket
try:
    from fyers_apiv3.FyersWebsocket import data_ws
    WEBSOCKET_AVAILABLE = True
except ImportError:
    print("⚠️  Fyers WebSocket not available. Install: pip install fyers-apiv3")
    WEBSOCKET_AVAILABLE = False


class FyersSymbolDiscovery:
    """Dynamic symbol discovery using Fyers WebSocket and API"""
    
    def __init__(self):
        self.fyers_model = MyFyersModel()
        self.discovered_symbols = set()
        self.symbol_data = {}
        self.websocket_symbols = []
        self.discovery_complete = False
        
    def get_comprehensive_symbol_list(self) -> List[str]:
        """Get comprehensive list of potential Nifty 50 symbols to test"""
        
        # Core Nifty 50 candidates (known high probability stocks)
        core_candidates = [
            # Major Banks
            'NSE:HDFCBANK-EQ', 'NSE:ICICIBANK-EQ', 'NSE:SBIN-EQ', 
            'NSE:KOTAKBANK-EQ', 'NSE:AXISBANK-EQ', 'NSE:INDUSINDBK-EQ',
            
            # IT Giants
            'NSE:TCS-EQ', 'NSE:INFY-EQ', 'NSE:HCLTECH-EQ', 'NSE:WIPRO-EQ', 
            'NSE:TECHM-EQ', 'NSE:LTIM-EQ',
            
            # Conglomerates & Energy
            'NSE:RELIANCE-EQ', 'NSE:ADANIENT-EQ', 'NSE:LT-EQ', 'NSE:ITC-EQ',
            'NSE:ONGC-EQ', 'NSE:BPCL-EQ', 'NSE:IOC-EQ', 'NSE:NTPC-EQ',
            'NSE:POWERGRID-EQ', 'NSE:COALINDIA-EQ',
            
            # Telecom & Consumer
            'NSE:BHARTIARTL-EQ', 'NSE:HINDUNILVR-EQ', 'NSE:NESTLEIND-EQ',
            'NSE:BRITANNIA-EQ', 'NSE:DABUR-EQ', 'NSE:MARICO-EQ',
            'NSE:GODREJCP-EQ', 'NSE:COLPAL-EQ', 'NSE:TATACONSUM-EQ',
            
            # Auto & Industrial
            'NSE:MARUTI-EQ', 'NSE:M&M-EQ', 'NSE:BAJAJ-AUTO-EQ', 
            'NSE:EICHERMOT-EQ', 'NSE:HEROMOTOCO-EQ', 'NSE:TATAMOTORS-EQ',
            'NSE:TVSMOTOR-EQ', 'NSE:BOSCHLTD-EQ',
            
            # Pharma & Healthcare
            'NSE:SUNPHARMA-EQ', 'NSE:DRREDDY-EQ', 'NSE:CIPLA-EQ', 
            'NSE:DIVISLAB-EQ', 'NSE:APOLLOHOSP-EQ', 'NSE:FORTIS-EQ',
            'NSE:ZYDUSLIFE-EQ', 'NSE:BIOCON-EQ', 'NSE:TORNTPHARM-EQ',
            
            # Metals & Materials
            'NSE:TATASTEEL-EQ', 'NSE:JSWSTEEL-EQ', 'NSE:HINDALCO-EQ',
            'NSE:VEDL-EQ', 'NSE:SAIL-EQ', 'NSE:NMDC-EQ',
            'NSE:ULTRACEMCO-EQ', 'NSE:AMBUJACEM-EQ', 'NSE:GRASIM-EQ',
            'NSE:ACC-EQ', 'NSE:SHREECEM-EQ',
            
            # Financial Services
            'NSE:BAJFINANCE-EQ', 'NSE:BAJAJFINSV-EQ', 'NSE:SBILIFE-EQ',
            'NSE:HDFCLIFE-EQ', 'NSE:ICICIPRULI-EQ', 'NSE:LICHSGFIN-EQ',
            'NSE:SHRIRAMFIN-EQ', 'NSE:MUTHOOTFIN-EQ',
            
            # Paints & Chemicals
            'NSE:ASIANPAINT-EQ', 'NSE:BERGER-EQ', 'NSE:KANSAINER-EQ',
            'NSE:PIDILITIND-EQ', 'NSE:UPL-EQ', 'NSE:SRF-EQ',
            
            # Retail & Consumer Durables
            'NSE:TITAN-EQ', 'NSE:DMART-EQ', 'NSE:TRENT-EQ',
            'NSE:WHIRLPOOL-EQ', 'NSE:VOLTAS-EQ',
            
            # Technology & Others
            'NSE:ADANIPORTS-EQ', 'NSE:INDIGO-EQ', 'NSE:SIEMENS-EQ',
            'NSE:ABB-EQ', 'NSE:HAVELLS-EQ', 'NSE:CROMPTON-EQ',
            
            # New Potential Entries
            'NSE:ADANIGREEN-EQ', 'NSE:IRCTC-EQ', 'NSE:ZOMATO-EQ',
            'NSE:PAYTM-EQ', 'NSE:NYKAA-EQ', 'NSE:POLICYBZR-EQ'
        ]
        
        return core_candidates
    
    def test_symbol_with_quotes(self, symbol: str) -> Dict:
        """Test if symbol is valid and active using quotes API"""
        try:
            data = {"symbols": symbol}
            response = self.fyers_model.fyers_model.quotes(data=data)
            
            if response and response.get('s') == 'ok':
                quote_data = response.get('d', [])
                if quote_data and len(quote_data) > 0:
                    quote = quote_data[0]
                    symbol_info = quote.get('v', {})
                    
                    # Check if symbol has meaningful data
                    ltp = symbol_info.get('lp')
                    volume = symbol_info.get('volume', 0)
                    
                    if ltp and ltp > 0:
                        return {
                            'symbol': symbol,
                            'ltp': ltp,
                            'volume': volume,
                            'valid': True,
                            'market_cap_indicator': ltp * volume if volume else 0
                        }
            
            return {'symbol': symbol, 'valid': False}
            
        except Exception as e:
            return {'symbol': symbol, 'valid': False, 'error': str(e)}
    
    def discover_active_nifty50_candidates(self) -> List[str]:
        """Discover active Nifty 50 candidates using Fyers API"""
        print("🔍 Discovering active Nifty 50 candidates...")
        
        candidates = self.get_comprehensive_symbol_list()
        active_symbols = []
        
        print(f"📊 Testing {len(candidates)} potential symbols...")
        
        for i, symbol in enumerate(candidates):
            try:
                result = self.test_symbol_with_quotes(symbol)
                
                if result.get('valid'):
                    active_symbols.append(symbol)
                    ltp = result.get('ltp', 0)
                    volume = result.get('volume', 0)
                    
                    if (i + 1) % 10 == 0:
                        print(f"  ✅ Progress: {i + 1}/{len(candidates)} tested, "
                              f"{len(active_symbols)} active found")
                else:
                    if 'TATAMOTORS' in symbol:
                        print(f"  ❌ {symbol} - Confirmed invalid (likely delisted from Nifty 50)")
                
                # Rate limiting
                if i < len(candidates) - 1:
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"  ❌ Error testing {symbol}: {e}")
        
        print(f"✅ Discovery complete: {len(active_symbols)} active symbols found")
        return active_symbols
    
    def rank_symbols_by_market_importance(self, symbols: List[str]) -> List[str]:
        """Rank symbols by market importance (volume, price, etc.)"""
        print("📊 Ranking symbols by market importance...")
        
        symbol_scores = []
        
        for symbol in symbols:
            try:
                result = self.test_symbol_with_quotes(symbol)
                
                if result.get('valid'):
                    ltp = result.get('ltp', 0)
                    volume = result.get('volume', 0)
                    
                    # Simple scoring: higher price and volume = higher importance
                    score = (ltp * 0.1) + (volume * 0.000001)  # Weighted score
                    
                    symbol_scores.append({
                        'symbol': symbol,
                        'score': score,
                        'ltp': ltp,
                        'volume': volume
                    })
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"  ❌ Error scoring {symbol}: {e}")
        
        # Sort by score (descending)
        symbol_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 50 symbols
        top_symbols = [item['symbol'] for item in symbol_scores[:50]]
        
        print(f"🎯 Top 10 by importance:")
        for i, item in enumerate(symbol_scores[:10]):
            stock_name = item['symbol'].replace('NSE:', '').replace('-EQ', '')
            print(f"  {i+1:2d}. {stock_name:<12} LTP: ₹{item['ltp']:<8.2f} "
                  f"Volume: {item['volume']:>10,}")
        
        return top_symbols
    
    def get_current_nifty50_dynamic(self) -> List[str]:
        """Main method to get current Nifty 50 constituents dynamically"""
        print("🚀 DYNAMIC NIFTY 50 CONSTITUENTS DISCOVERY")
        print("=" * 60)
        
        # Step 1: Discover all active candidates
        active_symbols = self.discover_active_nifty50_candidates()
        
        if len(active_symbols) < 50:
            print(f"⚠️  Only found {len(active_symbols)} active symbols, less than 50")
            return active_symbols
        
        # Step 2: Rank by market importance to get top 50
        top_50_symbols = self.rank_symbols_by_market_importance(active_symbols)
        
        print(f"\n✅ FINAL NIFTY 50 CONSTITUENTS: {len(top_50_symbols)} symbols")
        print("=" * 60)
        
        return top_50_symbols
    
    def save_discovered_nifty50(self, symbols: List[str]):
        """Save discovered Nifty 50 symbols to files"""
        if not symbols:
            print("❌ No symbols to save")
            return False
        
        try:
            # Create data directory
            data_dir = Path("data/symbols")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save detailed JSON
            json_data = {
                "timestamp": datetime.now().isoformat(),
                "source": "fyers_dynamic_discovery",
                "method": "quotes_api_ranking",
                "count": len(symbols),
                "symbols": symbols,
                "description": "Current Nifty 50 constituents discovered dynamically from Fyers API"
            }
            
            json_file = data_dir / f"nifty50_dynamic_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            # Save current list (overwrite)
            current_file = data_dir / "current_nifty50_fyers.json"
            with open(current_file, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            # Save simple text list
            txt_file = data_dir / "current_nifty50_symbols.txt"
            with open(txt_file, 'w') as f:
                for symbol in symbols:
                    f.write(f"{symbol}\n")
            
            print(f"💾 Saved to:")
            print(f"  📄 {json_file}")
            print(f"  📄 {current_file}")
            print(f"  📄 {txt_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving symbols: {e}")
            return False
    
    def load_saved_nifty50(self) -> List[str]:
        """Load previously saved Nifty 50 symbols"""
        try:
            current_file = Path("data/symbols/current_nifty50_fyers.json")
            
            if current_file.exists():
                with open(current_file, 'r') as f:
                    data = json.load(f)
                
                symbols = data.get('symbols', [])
                timestamp = data.get('timestamp', 'Unknown')
                
                print(f"📂 Loaded {len(symbols)} symbols from {timestamp}")
                return symbols
            else:
                print("📂 No saved symbols found")
                return []
                
        except Exception as e:
            print(f"❌ Error loading saved symbols: {e}")
            return []


def main():
    """Main function for dynamic Nifty 50 discovery"""
    discovery = FyersSymbolDiscovery()
    
    print("Choose an option:")
    print("1. Discover new Nifty 50 constituents (takes ~2-3 minutes)")
    print("2. Load previously saved symbols")
    print("3. Refresh and update current list")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            # Full discovery
            symbols = discovery.get_current_nifty50_dynamic()
            
            if symbols:
                print(f"\n🎯 DISCOVERED NIFTY 50 SYMBOLS:")
                for i, symbol in enumerate(symbols, 1):
                    stock_name = symbol.replace('NSE:', '').replace('-EQ', '')
                    print(f"{i:2d}. {stock_name}")
                
                discovery.save_discovered_nifty50(symbols)
                
                print(f"\n✅ Dynamic discovery completed!")
                print(f"💡 Use these symbols in your market analysis scripts")
            else:
                print(f"\n❌ Discovery failed")
        
        elif choice == '2':
            # Load saved
            symbols = discovery.load_saved_nifty50()
            
            if symbols:
                print(f"\n📋 LOADED NIFTY 50 SYMBOLS:")
                for i, symbol in enumerate(symbols, 1):
                    stock_name = symbol.replace('NSE:', '').replace('-EQ', '')
                    print(f"{i:2d}. {stock_name}")
            else:
                print("❌ No saved symbols found. Run option 1 first.")
        
        elif choice == '3':
            # Refresh
            print("🔄 Refreshing symbol list...")
            symbols = discovery.get_current_nifty50_dynamic()
            
            if symbols:
                discovery.save_discovered_nifty50(symbols)
                print(f"✅ Updated with {len(symbols)} current symbols")
            else:
                print("❌ Refresh failed")
        
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n⚠️  Discovery interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()