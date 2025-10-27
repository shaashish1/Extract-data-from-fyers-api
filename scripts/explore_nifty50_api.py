#!/usr/bin/env python3
"""
Explore Fyers API for dynamic Nifty 50 constituents discovery
"""
import sys
from pathlib import Path
import json

# Add scripts directory to Python path
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from my_fyers_model import MyFyersModel

def explore_fyers_methods():
    """Explore available Fyers API methods"""
    fyers = MyFyersModel()
    
    print("🔍 Available Fyers API Methods:")
    print("=" * 50)
    
    # Get all methods
    methods = [method for method in dir(fyers.fyers_model) if not method.startswith('_')]
    
    for method in sorted(methods):
        print(f"  • {method}")
    
    return methods

def test_quotes_for_nifty_index():
    """Test getting Nifty 50 index data"""
    fyers = MyFyersModel()
    
    print(f"\n" + "=" * 50)
    print("🔍 Testing Nifty 50 Index Quote...")
    
    # Try different Nifty 50 symbols
    nifty_symbols = [
        'NSE:NIFTY50-INDEX',
        'NSE:NIFTY-INDEX', 
        'NSE:NIFTY',
        'NSE:NIFTY50',
        'NSE:NIFTYBANK-INDEX'
    ]
    
    for symbol in nifty_symbols:
        try:
            print(f"\n📊 Testing: {symbol}")
            data = {"symbols": symbol}
            response = fyers.fyers_model.quotes(data=data)
            
            if response and response.get('s') == 'ok':
                quote_data = response.get('d', [])
                if quote_data:
                    quote = quote_data[0]
                    ltp = quote.get('v', {}).get('lp', 'N/A')
                    print(f"✅ SUCCESS: LTP: {ltp}")
                    
                    # Check if there's any constituents data
                    print(f"📋 Full Response Keys: {list(quote.keys())}")
                    print(f"📋 Value Keys: {list(quote.get('v', {}).keys())}")
                else:
                    print(f"❌ No quote data")
            else:
                error_msg = response.get('message', 'Unknown error') if response else 'No response'
                print(f"❌ FAILED: {error_msg}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")

def test_symbol_search():
    """Test symbol search functionality"""
    fyers = MyFyersModel()
    
    print(f"\n" + "=" * 50)
    print("🔍 Testing Symbol Search...")
    
    # Try different search terms
    search_terms = ['NIFTY50', 'NIFTY', 'INDEX']
    
    for term in search_terms:
        try:
            print(f"\n🔍 Searching for: {term}")
            
            # Try different search methods
            search_methods = [
                ('search_scrips', {'search_term': term}),
                ('symbol_details', {'symbol': term}),
            ]
            
            for method_name, data in search_methods:
                try:
                    method = getattr(fyers.fyers_model, method_name, None)
                    if method:
                        print(f"  📡 Trying {method_name}...")
                        response = method(data=data)
                        
                        if response and response.get('s') == 'ok':
                            results = response.get('d', [])
                            print(f"  ✅ Found {len(results)} results")
                            
                            # Show first few results
                            for i, result in enumerate(results[:3]):
                                print(f"    {i+1}. {result}")
                        else:
                            print(f"  ❌ {method_name} failed: {response.get('message', 'Unknown') if response else 'No response'}")
                    else:
                        print(f"  ❌ Method {method_name} not available")
                except Exception as e:
                    print(f"  ❌ Exception in {method_name}: {e}")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_option_chain():
    """Test option chain - might contain underlying info"""
    fyers = MyFyersModel()
    
    print(f"\n" + "=" * 50)
    print("🔍 Testing Option Chain for Nifty...")
    
    try:
        data = {
            "symbol": "NSE:NIFTY50-INDEX",
            "expiry": "2025-10-31"  # Adjust date as needed
        }
        
        if hasattr(fyers.fyers_model, 'optionchain'):
            response = fyers.fyers_model.optionchain(data=data)
            
            if response and response.get('s') == 'ok':
                print("✅ Option chain data received")
                chain_data = response.get('d', {})
                print(f"📋 Option Chain Keys: {list(chain_data.keys())}")
                
                # Look for any underlying/constituent info
                if 'underlying' in chain_data:
                    print(f"📊 Underlying data: {chain_data['underlying']}")
            else:
                print(f"❌ Option chain failed: {response.get('message', 'Unknown') if response else 'No response'}")
        else:
            print("❌ Option chain method not available")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_historical_data_approach():
    """Test if we can get constituents through historical data of index"""
    fyers = MyFyersModel()
    
    print(f"\n" + "=" * 50)
    print("🔍 Testing Historical Data Approach...")
    
    try:
        # Get current date range
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        data = {
            "symbol": "NSE:NIFTY50-INDEX",
            "resolution": "D",
            "date_format": "1",
            "range_from": start_date.strftime("%Y-%m-%d"),
            "range_to": end_date.strftime("%Y-%m-%d"),
            "cont_flag": "1"
        }
        
        response = fyers.fyers_model.history(data=data)
        
        if response and response.get('s') == 'ok':
            print("✅ Historical data received")
            hist_data = response.get('d', {})
            print(f"📋 Historical Data Keys: {list(hist_data.keys())}")
            
            # Check for any constituent information
            if 'constituents' in hist_data:
                print(f"📊 Constituents found: {hist_data['constituents']}")
            else:
                print("❌ No constituent data in historical response")
        else:
            print(f"❌ Historical data failed: {response.get('message', 'Unknown') if response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def check_fyers_documentation():
    """Check what we can find in Fyers model attributes"""
    fyers = MyFyersModel()
    
    print(f"\n" + "=" * 50)
    print("🔍 Checking Fyers Model Documentation...")
    
    # Check for any method that might return index data
    interesting_methods = []
    
    for attr in dir(fyers.fyers_model):
        if not attr.startswith('_'):
            attr_lower = attr.lower()
            if any(term in attr_lower for term in ['index', 'constituent', 'symbol', 'search', 'master', 'scrip']):
                interesting_methods.append(attr)
    
    print(f"🎯 Potentially interesting methods:")
    for method in interesting_methods:
        print(f"  • {method}")
    
    return interesting_methods

if __name__ == "__main__":
    print("🔍 DYNAMIC NIFTY 50 CONSTITUENTS DISCOVERY")
    print("=" * 60)
    
    # Explore API
    methods = explore_fyers_methods()
    
    # Test various approaches
    test_quotes_for_nifty_index()
    test_symbol_search()
    test_option_chain() 
    test_historical_data_approach()
    interesting_methods = check_fyers_documentation()
    
    print(f"\n" + "=" * 60)
    print("📋 SUMMARY:")
    print(f"✅ Total API methods available: {len(methods)}")
    print(f"🎯 Potentially useful methods: {len(interesting_methods)}")
    print("🔍 Need to find official Nifty 50 constituents API or use external source")
    print("=" * 60)