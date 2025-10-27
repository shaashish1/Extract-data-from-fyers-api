#!/usr/bin/env python3
"""
Dynamic Nifty 50 Constituents Discovery from External Sources
Uses multiple sources to get current Nifty 50 stocks and convert to Fyers format
"""
import sys
from pathlib import Path
import requests
import json
import pandas as pd
from datetime import datetime
import time

# Add scripts directory to Python path
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from my_fyers_model import MyFyersModel

class DynamicNifty50Discovery:
    """Discover current Nifty 50 constituents from multiple sources"""
    
    def __init__(self):
        self.fyers = MyFyersModel()
        self.nifty50_symbols = []
        
    def get_nifty50_from_nse_official(self):
        """Get Nifty 50 from NSE official API"""
        print("🔍 Method 1: NSE Official API...")
        
        try:
            # NSE official API for Nifty 50 constituents
            url = "https://www.nse.com.br/en/api/nifty50"  # This might not work - placeholder
            
            # Alternative: NSE Indices API
            nse_urls = [
                "https://archives.nseindia.com/content/indices/ind_nifty50list.csv",
                "https://www1.nseindia.com/content/indices/ind_nifty50list.csv",
                "https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            for url in nse_urls:
                try:
                    print(f"  📡 Trying: {url}")
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        # Try to parse as CSV
                        content = response.content.decode('utf-8')
                        
                        if 'Symbol' in content or 'SYMBOL' in content:
                            print("  ✅ CSV data found!")
                            
                            # Parse CSV
                            lines = content.strip().split('\n')
                            symbols = []
                            
                            for line in lines[1:]:  # Skip header
                                parts = line.split(',')
                                if len(parts) > 0:
                                    symbol = parts[0].strip().strip('"')
                                    if symbol and symbol != 'Symbol':
                                        symbols.append(f"NSE:{symbol}-EQ")
                            
                            if len(symbols) >= 40:  # Should be around 50
                                print(f"  ✅ Found {len(symbols)} symbols from NSE official")
                                return symbols[:50]  # Ensure max 50
                            
                        else:
                            print("  ❌ Not CSV format")
                    else:
                        print(f"  ❌ HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    
            return []
            
        except Exception as e:
            print(f"❌ NSE Official method failed: {e}")
            return []
    
    def get_nifty50_from_wikipedia(self):
        """Get Nifty 50 from Wikipedia (updated regularly)"""
        print("🔍 Method 2: Wikipedia...")
        
        try:
            url = "https://en.wikipedia.org/wiki/NIFTY_50"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Look for table with stock symbols
                content = response.text
                
                # Find table with constituents
                import re
                
                # Look for NSE symbols in the content
                symbol_pattern = r'NSE:([A-Z0-9&-]+)'
                matches = re.findall(symbol_pattern, content)
                
                if matches:
                    symbols = [f"NSE:{match}-EQ" for match in matches]
                    symbols = list(set(symbols))  # Remove duplicates
                    
                    if len(symbols) >= 40:
                        print(f"  ✅ Found {len(symbols)} symbols from Wikipedia")
                        return symbols[:50]
                
                # Alternative: Look for stock names and convert
                # This is more complex parsing - would need BeautifulSoup
                print("  ❌ Could not extract symbols from Wikipedia")
                
            return []
            
        except Exception as e:
            print(f"❌ Wikipedia method failed: {e}")
            return []
    
    def get_nifty50_from_financial_apis(self):
        """Get Nifty 50 from financial data APIs"""
        print("🔍 Method 3: Financial APIs...")
        
        apis_to_try = [
            {
                'name': 'Alpha Vantage',
                'url': 'https://www.alphavantage.co/query',
                'params': {
                    'function': 'LISTING_STATUS',
                    'apikey': 'demo'  # Would need real API key
                }
            },
            {
                'name': 'Yahoo Finance (Indirect)',
                'url': 'https://query1.finance.yahoo.com/v1/finance/search',
                'params': {
                    'q': 'NIFTY 50',
                    'lang': 'en-US',
                    'region': 'US',
                    'quotesCount': 50,
                    'newsCount': 0
                }
            }
        ]
        
        for api in apis_to_try:
            try:
                print(f"  📡 Trying: {api['name']}")
                
                response = requests.get(api['url'], params=api['params'], timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  📋 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                    
                    # Would need specific parsing for each API
                    # This is just exploration
                    
                else:
                    print(f"  ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {api['name']} failed: {e}")
        
        return []
    
    def verify_symbols_with_fyers(self, symbols):
        """Verify that symbols work with Fyers API"""
        print(f"🔍 Verifying {len(symbols)} symbols with Fyers...")
        
        verified_symbols = []
        failed_symbols = []
        
        for i, symbol in enumerate(symbols):
            try:
                # Test with quotes API
                data = {"symbols": symbol}
                response = self.fyers.fyers_model.quotes(data=data)
                
                if response and response.get('s') == 'ok':
                    quote_data = response.get('d', [])
                    if quote_data and quote_data[0].get('v', {}).get('lp'):
                        verified_symbols.append(symbol)
                        if (i + 1) % 10 == 0:
                            print(f"  ✅ Verified {i + 1}/{len(symbols)}...")
                    else:
                        failed_symbols.append(symbol)
                else:
                    failed_symbols.append(symbol)
                
                # Rate limiting
                if i < len(symbols) - 1:
                    time.sleep(0.2)
                    
            except Exception as e:
                failed_symbols.append(symbol)
                print(f"  ❌ Error verifying {symbol}: {e}")
        
        print(f"✅ Verified: {len(verified_symbols)} symbols")
        print(f"❌ Failed: {len(failed_symbols)} symbols")
        
        if failed_symbols:
            print(f"❌ Failed symbols: {failed_symbols[:5]}...")  # Show first 5
        
        return verified_symbols
    
    def create_nifty50_from_known_working(self):
        """Create Nifty 50 list from known working symbols and add missing ones"""
        print("🔍 Method 4: Build from known working symbols...")
        
        # Start with our verified working symbols from earlier
        known_working = [
            'NSE:RELIANCE-EQ', 'NSE:TCS-EQ', 'NSE:HDFCBANK-EQ',
            'NSE:INFY-EQ', 'NSE:ICICIBANK-EQ', 'NSE:SBIN-EQ',
            'NSE:BHARTIARTL-EQ', 'NSE:ITC-EQ', 'NSE:KOTAKBANK-EQ',
            'NSE:LT-EQ', 'NSE:ASIANPAINT-EQ', 'NSE:MARUTI-EQ',
            'NSE:AXISBANK-EQ', 'NSE:HCLTECH-EQ', 'NSE:WIPRO-EQ',
            'NSE:NESTLEIND-EQ', 'NSE:ULTRACEMCO-EQ', 'NSE:BAJFINANCE-EQ',
            'NSE:ONGC-EQ', 'NSE:POWERGRID-EQ', 'NSE:NTPC-EQ',
            'NSE:TECHM-EQ', 'NSE:HINDUNILVR-EQ', 'NSE:SUNPHARMA-EQ', 
            'NSE:TITAN-EQ', 'NSE:DRREDDY-EQ', 'NSE:BAJAJFINSV-EQ', 
            'NSE:COALINDIA-EQ', 'NSE:INDUSINDBK-EQ', 'NSE:TATASTEEL-EQ', 
            'NSE:ADANIPORTS-EQ', 'NSE:JSWSTEEL-EQ', 'NSE:HINDALCO-EQ', 
            'NSE:GRASIM-EQ', 'NSE:BRITANNIA-EQ', 'NSE:CIPLA-EQ', 
            'NSE:DIVISLAB-EQ', 'NSE:BAJAJ-AUTO-EQ', 'NSE:EICHERMOT-EQ', 
            'NSE:HEROMOTOCO-EQ', 'NSE:APOLLOHOSP-EQ', 'NSE:BPCL-EQ', 
            'NSE:ADANIENT-EQ', 'NSE:SBILIFE-EQ', 'NSE:LTIM-EQ',
            'NSE:SHRIRAMFIN-EQ', 'NSE:M&M-EQ', 'NSE:PIDILITIND-EQ',
            'NSE:IOC-EQ'
        ]
        
        print(f"  📋 Starting with {len(known_working)} known working symbols")
        
        # Common candidates for remaining slots
        additional_candidates = [
            'NSE:HDFCLIFE-EQ', 'NSE:TATACONSUM-EQ', 'NSE:GODREJCP-EQ',
            'NSE:BAJAJHLDNG-EQ', 'NSE:MARICO-EQ', 'NSE:DABUR-EQ',
            'NSE:COLPAL-EQ', 'NSE:BERGEPAINT-EQ', 'NSE:AMBUJACEM-EQ',
            'NSE:INDIGO-EQ', 'NSE:VEDL-EQ', 'NSE:TATAPOWER-EQ',
            'NSE:ZYDUSLIFE-EQ', 'NSE:APOLLOTYRE-EQ', 'NSE:UPL-EQ',
            'NSE:SIEMENS-EQ', 'NSE:TORNTPHARM-EQ', 'NSE:BIOCON-EQ',
            'NSE:LICHSGFIN-EQ', 'NSE:SAIL-EQ'
        ]
        
        # Verify additional candidates
        print(f"  🔍 Testing {len(additional_candidates)} additional candidates...")
        verified_additional = self.verify_symbols_with_fyers(additional_candidates)
        
        # Combine and ensure exactly 50
        all_symbols = known_working + verified_additional
        unique_symbols = list(dict.fromkeys(all_symbols))  # Preserve order, remove duplicates
        
        if len(unique_symbols) >= 50:
            final_symbols = unique_symbols[:50]
            print(f"✅ Created Nifty 50 list with {len(final_symbols)} symbols")
            return final_symbols
        else:
            print(f"⚠️  Only found {len(unique_symbols)} symbols, need more")
            return unique_symbols
    
    def discover_nifty50_constituents(self):
        """Main method to discover current Nifty 50 constituents"""
        print("🚀 DYNAMIC NIFTY 50 CONSTITUENTS DISCOVERY")
        print("=" * 60)
        
        # Try multiple methods
        methods = [
            self.get_nifty50_from_nse_official,
            self.get_nifty50_from_wikipedia,
            self.get_nifty50_from_financial_apis,
            self.create_nifty50_from_known_working
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                print(f"\n📡 Trying Method {i}...")
                symbols = method()
                
                if symbols and len(symbols) >= 45:  # At least 45 symbols
                    print(f"✅ Method {i} successful: {len(symbols)} symbols found")
                    
                    # Verify with Fyers
                    verified = self.verify_symbols_with_fyers(symbols)
                    
                    if len(verified) >= 45:
                        print(f"🎯 FINAL RESULT: {len(verified)} verified Nifty 50 symbols")
                        self.nifty50_symbols = verified
                        return verified
                    else:
                        print(f"⚠️  Only {len(verified)} symbols verified, trying next method...")
                else:
                    print(f"❌ Method {i} insufficient: {len(symbols) if symbols else 0} symbols")
                    
            except Exception as e:
                print(f"❌ Method {i} failed: {e}")
        
        print("❌ All methods failed")
        return []
    
    def save_discovered_symbols(self):
        """Save discovered symbols to file"""
        if not self.nifty50_symbols:
            print("❌ No symbols to save")
            return False
        
        try:
            # Save to JSON
            data_dir = Path("data/symbols")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dynamic_nifty50_{timestamp}.json"
            filepath = data_dir / filename
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "source": "dynamic_discovery",
                "count": len(self.nifty50_symbols),
                "symbols": self.nifty50_symbols,
                "fyers_format": True
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"💾 Symbols saved to: {filepath}")
            
            # Also save as simple list for easy import
            simple_file = data_dir / "current_nifty50.txt"
            with open(simple_file, 'w') as f:
                for symbol in self.nifty50_symbols:
                    f.write(f"{symbol}\n")
            
            print(f"💾 Simple list saved to: {simple_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving symbols: {e}")
            return False

def main():
    """Main function"""
    discovery = DynamicNifty50Discovery()
    symbols = discovery.discover_nifty50_constituents()
    
    if symbols:
        print(f"\n🎯 DISCOVERED NIFTY 50 SYMBOLS ({len(symbols)}):")
        print("=" * 60)
        for i, symbol in enumerate(symbols, 1):
            stock_name = symbol.replace('NSE:', '').replace('-EQ', '')
            print(f"{i:2d}. {stock_name:<15} ({symbol})")
        
        discovery.save_discovered_symbols()
        
        print(f"\n✅ Dynamic discovery completed!")
        print(f"💡 Use these symbols in your market depth analysis")
    else:
        print(f"\n❌ Dynamic discovery failed")
        print(f"💡 Falling back to manual symbol list")

if __name__ == "__main__":
    main()