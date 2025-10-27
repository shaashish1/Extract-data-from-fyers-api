"""
Test script to run Nifty 200 data extraction and display results
"""
import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from symbol_discovery import SymbolDiscovery
    from data_storage import get_parquet_manager
    from my_fyers_model import MyFyersModel
    from constants import option_symbols
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the correct directory and all dependencies are installed")
    sys.exit(1)

class Nifty200DataTest:
    def __init__(self):
        """Initialize the Nifty 200 data test"""
        self.symbol_discovery = SymbolDiscovery()
        self.data_manager = get_parquet_manager()
        self.nifty200_symbols = []
        
    def test_symbol_discovery(self):
        """Test the symbol discovery functionality"""
        print("🔍 Testing Nifty 200 Symbol Discovery...")
        print("=" * 60)
        
        try:
            # Get Nifty 200 symbols
            self.nifty200_symbols = self.symbol_discovery.get_nifty200_constituents()
            
            print(f"✅ Successfully discovered {len(self.nifty200_symbols)} Nifty 200 symbols")
            print(f"📊 Expected: 200 symbols")
            print(f"📈 Actual: {len(self.nifty200_symbols)} symbols")
            
            if len(self.nifty200_symbols) == 200:
                print("✅ Symbol count matches expected Nifty 200")
            else:
                print("⚠️  Symbol count doesn't match expected 200")
                
            return True
            
        except Exception as e:
            print(f"❌ Error in symbol discovery: {e}")
            return False
    
    def display_nifty200_symbols(self):
        """Display all Nifty 200 symbols in organized format"""
        print("\n📋 NIFTY 200 SYMBOLS LIST")
        print("=" * 60)
        
        if not self.nifty200_symbols:
            print("❌ No symbols found. Run test_symbol_discovery() first.")
            return
        
        # Organize symbols by sector/category
        sectors = {
            'Banking & Finance': [],
            'IT & Technology': [],
            'Pharmaceuticals': [],
            'Automobiles': [],
            'Energy & Power': [],
            'Metals & Mining': [],
            'FMCG': [],
            'Infrastructure': [],
            'Chemicals': [],
            'Others': []
        }
        
        # Categorize symbols (basic categorization based on common patterns)
        for symbol in self.nifty200_symbols:
            symbol_name = symbol.replace('NSE:', '').replace('-EQ', '')
            
            # Banking & Finance
            if any(keyword in symbol_name.upper() for keyword in ['BANK', 'HDFC', 'ICICI', 'AXIS', 'KOTAK', 'BAJFINANCE', 'SBIN', 'INDUSIND']):
                sectors['Banking & Finance'].append(symbol)
            # IT & Technology  
            elif any(keyword in symbol_name.upper() for keyword in ['TECH', 'INFY', 'TCS', 'WIPRO', 'HCLT', 'MINDTREE', 'LTTS']):
                sectors['IT & Technology'].append(symbol)
            # Pharmaceuticals
            elif any(keyword in symbol_name.upper() for keyword in ['PHARMA', 'CIPLA', 'DRREDDY', 'SUNPHARMA', 'BIOCON', 'LUPIN', 'CADILA']):
                sectors['Pharmaceuticals'].append(symbol)
            # Automobiles
            elif any(keyword in symbol_name.upper() for keyword in ['MARUTI', 'TATA', 'HERO', 'BAJAJ', 'ASHOK', 'EICHER', 'TVS']):
                sectors['Automobiles'].append(symbol)
            # Energy & Power
            elif any(keyword in symbol_name.upper() for keyword in ['POWER', 'COAL', 'OIL', 'GAS', 'ENERGY', 'RELIANCE', 'ONGC', 'IOC']):
                sectors['Energy & Power'].append(symbol)
            # Metals & Mining
            elif any(keyword in symbol_name.upper() for keyword in ['STEEL', 'METAL', 'HINDALCO', 'VEDL', 'ZINC', 'ALUMINIUM']):
                sectors['Metals & Mining'].append(symbol)
            # FMCG
            elif any(keyword in symbol_name.upper() for keyword in ['UNILEVER', 'ITC', 'NEST', 'BRITANNIA', 'DABUR', 'GODREJ']):
                sectors['FMCG'].append(symbol)
            # Infrastructure
            elif any(keyword in symbol_name.upper() for keyword in ['INFRA', 'CONSTRUCTION', 'CEMENT', 'L&T', 'UBL']):
                sectors['Infrastructure'].append(symbol)
            # Chemicals
            elif any(keyword in symbol_name.upper() for keyword in ['CHEM', 'ASIAN', 'UPL', 'SRF']):
                sectors['Chemicals'].append(symbol)
            else:
                sectors['Others'].append(symbol)
        
        # Display by sectors
        for sector, symbols in sectors.items():
            if symbols:
                print(f"\n🏢 {sector} ({len(symbols)} stocks):")
                print("-" * 40)
                for i, symbol in enumerate(symbols, 1):
                    clean_name = symbol.replace('NSE:', '').replace('-EQ', '')
                    print(f"  {i:2d}. {clean_name:<15} ({symbol})")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print("-" * 40)
        total_categorized = sum(len(symbols) for symbols in sectors.values())
        print(f"Total Symbols: {len(self.nifty200_symbols)}")
        print(f"Categorized: {total_categorized}")
        print(f"Sector Distribution:")
        for sector, symbols in sectors.items():
            if symbols:
                percentage = (len(symbols) / len(self.nifty200_symbols)) * 100
                print(f"  {sector}: {len(symbols)} ({percentage:.1f}%)")
    
    def test_data_availability(self):
        """Check what data is currently available for Nifty 200 stocks"""
        print("\n💾 CHECKING DATA AVAILABILITY")
        print("=" * 60)
        
        if not self.nifty200_symbols:
            print("❌ No symbols to check. Run test_symbol_discovery() first.")
            return
        
        available_data = {}
        missing_data = []
        
        # Check for each timeframe
        timeframes = ['1D', '1m', '5m', '15m', '1H']
        
        print("🔍 Scanning data directory...")
        
        for timeframe in timeframes:
            available_data[timeframe] = []
            
            for symbol in self.nifty200_symbols[:10]:  # Check first 10 for demo
                clean_symbol = symbol.replace('NSE:', '').replace('-EQ', '').lower()
                
                try:
                    # Check if data exists
                    data_info = self.data_manager.get_data_info(clean_symbol, timeframe)
                    if data_info and data_info.get('total_records', 0) > 0:
                        available_data[timeframe].append({
                            'symbol': clean_symbol,
                            'records': data_info.get('total_records', 0),
                            'date_range': f"{data_info.get('start_date', 'N/A')} to {data_info.get('end_date', 'N/A')}"
                        })
                except Exception as e:
                    missing_data.append(f"{clean_symbol}_{timeframe}")
        
        # Display results
        print(f"\n📈 DATA AVAILABILITY SUMMARY (Sample of first 10 stocks):")
        print("-" * 60)
        
        for timeframe in timeframes:
            count = len(available_data[timeframe])
            print(f"{timeframe:>4}: {count:2d}/10 stocks have data")
            
            if available_data[timeframe]:
                print(f"     Examples:")
                for item in available_data[timeframe][:3]:  # Show first 3
                    print(f"       {item['symbol']}: {item['records']} records ({item['date_range']})")
        
        if missing_data:
            print(f"\n⚠️  Some data missing for: {len(missing_data)} symbol-timeframe combinations")
    
    def test_fyers_connection(self):
        """Test connection to Fyers API"""
        print("\n🔌 TESTING FYERS API CONNECTION")
        print("=" * 60)
        
        try:
            # Initialize Fyers model
            fyers_model = MyFyersModel()
            
            # Test with a simple symbol
            test_symbol = "NSE:RELIANCE-EQ"
            print(f"🧪 Testing with symbol: {test_symbol}")
            
            # Try to get historical data for last 5 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)
            
            print(f"📅 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            print("⏳ Fetching sample data...")
            
            # This would test the actual API - uncomment if you want to test live
            # data = fyers_model.get_historical_data(
            #     symbol=test_symbol,
            #     resolution="D",
            #     start_date=start_date.strftime("%Y-%m-%d"),
            #     end_date=end_date.strftime("%Y-%m-%d")
            # )
            
            print("✅ Fyers API connection test skipped (uncomment to test live)")
            print("   Make sure auth/access_token.txt exists and is valid for live testing")
            
        except Exception as e:
            print(f"❌ Fyers API connection error: {e}")
    
    def run_full_test(self):
        """Run complete Nifty 200 test suite"""
        print("🚀 NIFTY 200 DATA EXTRACTION TEST")
        print("=" * 80)
        print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Test 1: Symbol Discovery
        if not self.test_symbol_discovery():
            print("❌ Symbol discovery failed. Stopping tests.")
            return
        
        # Test 2: Display Symbols
        self.display_nifty200_symbols()
        
        # Test 3: Data Availability
        self.test_data_availability()
        
        # Test 4: API Connection
        self.test_fyers_connection()
        
        print("\n" + "=" * 80)
        print("✅ NIFTY 200 TEST COMPLETED")
        print("=" * 80)
        print(f"📊 Total symbols discovered: {len(self.nifty200_symbols)}")
        print(f"📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save results
        self.save_test_results()
    
    def save_test_results(self):
        """Save test results to file"""
        try:
            test_dir = Path("scripts/test")
            test_dir.mkdir(exist_ok=True)
            
            results_file = test_dir / f"nifty200_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(results_file, 'w') as f:
                f.write(f"NIFTY 200 TEST RESULTS\n")
                f.write(f"=====================\n")
                f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Symbols: {len(self.nifty200_symbols)}\n\n")
                
                f.write("SYMBOLS LIST:\n")
                f.write("=============\n")
                for i, symbol in enumerate(self.nifty200_symbols, 1):
                    f.write(f"{i:3d}. {symbol}\n")
            
            print(f"💾 Test results saved to: {results_file}")
            
        except Exception as e:
            print(f"⚠️  Could not save test results: {e}")

def main():
    """Main function to run the test"""
    print("🎯 Starting Nifty 200 Data Test...")
    
    # Create test instance
    test = Nifty200DataTest()
    
    # Run full test suite
    test.run_full_test()

if __name__ == "__main__":
    main()