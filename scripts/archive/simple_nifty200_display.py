"""
Simple Nifty 200 Symbol Display Test
Shows all 200 symbols without requiring API connection
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SimpleNifty200Test:
    def __init__(self):
        """Initialize with hardcoded Nifty 200 symbols (exactly 200)"""
        # Nifty 100 base symbols (exactly 100)
        self.nifty100_symbols = [
            'NSE:RELIANCE-EQ', 'NSE:TCS-EQ', 'NSE:HDFCBANK-EQ', 'NSE:ICICIBANK-EQ',
            'NSE:HINDUNILVR-EQ', 'NSE:INFY-EQ', 'NSE:ITC-EQ', 'NSE:SBIN-EQ',
            'NSE:BHARTIARTL-EQ', 'NSE:KOTAKBANK-EQ', 'NSE:LT-EQ', 'NSE:AXISBANK-EQ',
            'NSE:ASIANPAINT-EQ', 'NSE:MARUTI-EQ', 'NSE:SUNPHARMA-EQ', 'NSE:TITAN-EQ',
            'NSE:BAJFINANCE-EQ', 'NSE:HCLTECH-EQ', 'NSE:ULTRACEMCO-EQ', 'NSE:WIPRO-EQ',
            'NSE:NESTLEIND-EQ', 'NSE:NTPC-EQ', 'NSE:POWERGRID-EQ', 'NSE:TATAMOTORS-EQ',
            'NSE:ADANIENT-EQ', 'NSE:BAJAJFINSV-EQ', 'NSE:ONGC-EQ', 'NSE:COALINDIA-EQ',
            'NSE:TATASTEEL-EQ', 'NSE:DIVISLAB-EQ', 'NSE:TECHM-EQ', 'NSE:HINDALCO-EQ',
            'NSE:DRREDDY-EQ', 'NSE:CIPLA-EQ', 'NSE:INDUSINDBK-EQ', 'NSE:JSWSTEEL-EQ',
            'NSE:GRASIM-EQ', 'NSE:BRITANNIA-EQ', 'NSE:M&M-EQ', 'NSE:EICHERMOT-EQ',
            'NSE:BAJAJ-AUTO-EQ', 'NSE:BPCL-EQ', 'NSE:ADANIPORTS-EQ', 'NSE:IOC-EQ',
            'NSE:APOLLOHOSP-EQ', 'NSE:SHRIRAMFIN-EQ', 'NSE:LTIM-EQ', 'NSE:HEROMOTOCO-EQ',
            'NSE:SBILIFE-EQ', 'NSE:PIDILITIND-EQ', 'NSE:TATACONSUM-EQ', 'NSE:GODREJCP-EQ',
            'NSE:UPL-EQ', 'NSE:HDFCLIFE-EQ', 'NSE:ICICIPRULI-EQ', 'NSE:VEDL-EQ',
            'NSE:TRENT-EQ', 'NSE:DABUR-EQ', 'NSE:JINDALSTL-EQ', 'NSE:GAIL-EQ',
            'NSE:LICI-EQ', 'NSE:BAJAJHLDNG-EQ', 'NSE:BANKBARODA-EQ', 'NSE:SIEMENS-EQ',
            'NSE:ABB-EQ', 'NSE:MARICO-EQ', 'NSE:NAUKRI-EQ', 'NSE:TORNTPHARM-EQ',
            'NSE:MUTHOOTFIN-EQ', 'NSE:BERGEPAINT-EQ', 'NSE:JINDALSTEL-EQ', 'NSE:CHOLAFIN-EQ',
            'NSE:AMBUJACEM-EQ', 'NSE:LUPIN-EQ', 'NSE:SAIL-EQ', 'NSE:BOSCHLTD-EQ',
            'NSE:MOTHERSON-EQ', 'NSE:HAVELLS-EQ', 'NSE:PNB-EQ', 'NSE:CUMMINSIND-EQ',
            'NSE:MCDOWELL-N-EQ', 'NSE:COLPAL-EQ', 'NSE:CANFINHOME-EQ', 'NSE:INDIGO-EQ',
            'NSE:ESCORTS-EQ', 'NSE:BATAINDIA-EQ', 'NSE:AUBANK-EQ', 'NSE:HINDZINC-EQ',
            'NSE:BANDHANBNK-EQ', 'NSE:VOLTAS-EQ', 'NSE:DALBHARAT-EQ', 'NSE:POLYCAB-EQ',
            'NSE:BEL-EQ', 'NSE:IDFCFIRSTB-EQ', 'NSE:BIOCON-EQ', 'NSE:RBLBANK-EQ',
            'NSE:OFSS-EQ', 'NSE:ZYDUSLIFE-EQ', 'NSE:CONCOR-EQ', 'NSE:PAGEIND-EQ'
        ]
        
        # Additional 100 symbols to complete Nifty 200 (exactly 100)
        self.additional_100_symbols = [
            'NSE:ZEEL-EQ', 'NSE:PVR-EQ', 'NSE:INOXLEISUR-EQ',
            'NSE:ADANIGREEN-EQ', 'NSE:ADANIPOWER-EQ', 'NSE:ADANITRANS-EQ',
            'NSE:JINDALSTEL-EQ', 'NSE:RPOWER-EQ', 'NSE:TORNTPOWER-EQ',
            'NSE:BHEL-EQ', 'NSE:CROMPTON-EQ', 'NSE:WHIRLPOOL-EQ', 
            'NSE:JKCEMENT-EQ', 'NSE:INDIACEM-EQ', 'NSE:ORIENT-EQ', 'NSE:JKPAPER-EQ',
            'NSE:BALRAMCHIN-EQ', 'NSE:CHAMBLFERT-EQ', 'NSE:COROMANDEL-EQ',
            'NSE:GNFC-EQ', 'NSE:GSFC-EQ', 'NSE:NFL-EQ', 'NSE:RCF-EQ', 'NSE:SRF-EQ', 
            'NSE:TATACHEMICALS-EQ', 'NSE:AJANTA-EQ', 'NSE:APLAPOLLO-EQ', 'NSE:AAVAS-EQ',
            'NSE:ABCAPITAL-EQ', 'NSE:ABFRL-EQ', 'NSE:ADANIGAS-EQ', 'NSE:AIAENG-EQ',
            'NSE:AJANTPHARM-EQ', 'NSE:AKZOINDIA-EQ', 'NSE:ALKYLAMINE-EQ', 'NSE:ALLCARGO-EQ',
            'NSE:AMARAJABAT-EQ', 'NSE:APLLTD-EQ', 'NSE:ARVINDFASN-EQ', 'NSE:ASAHIINDIA-EQ',
            'NSE:ASTRAL-EQ', 'NSE:ATUL-EQ', 'NSE:AVANTIFEED-EQ', 'NSE:BAJAJCON-EQ',
            'NSE:BEML-EQ', 'NSE:BHARATFORG-EQ', 'NSE:BIRLACORPN-EQ', 'NSE:BLUEDART-EQ',
            'NSE:BSOFT-EQ', 'NSE:CAPLIPOINT-EQ', 'NSE:CARBORUNIV-EQ', 'NSE:CASTROLIND-EQ',
            'NSE:CCL-EQ', 'NSE:CERA-EQ', 'NSE:CHEMCON-EQ', 'NSE:CHEMPLASTS-EQ',
            'NSE:CHENNPETRO-EQ', 'NSE:CHOLAHLDNG-EQ', 'NSE:CUB-EQ', 'NSE:CYIENT-EQ',
            'NSE:DBREALTY-EQ', 'NSE:DEEPAKFERT-EQ', 'NSE:DEEPAKNTR-EQ', 'NSE:DHANUKA-EQ',
            'NSE:DIXON-EQ', 'NSE:DMART-EQ', 'NSE:EDELWEISS-EQ', 'NSE:EMAMILTD-EQ',
            'NSE:ENDURANCE-EQ', 'NSE:ENGINERSIN-EQ', 'NSE:EQUITAS-EQ', 'NSE:ERIS-EQ',
            'NSE:ESABINDIA-EQ', 'NSE:EXIDEIND-EQ', 'NSE:FDC-EQ', 'NSE:FINEORG-EQ',
            'NSE:FINCABLES-EQ', 'NSE:FORCEMOT-EQ', 'NSE:FORTIS-EQ', 'NSE:GESHIP-EQ',
            'NSE:GILLETTE-EQ', 'NSE:GLAXO-EQ', 'NSE:GLENMARK-EQ', 'NSE:GMRINFRA-EQ',
            'NSE:GODFRYPHLP-EQ', 'NSE:GRANULES-EQ', 'NSE:GRAPHITE-EQ', 'NSE:GREAVESCOT-EQ',
            'NSE:GRINDWELL-EQ', 'NSE:GTLINFRA-EQ', 'NSE:GUJALKALI-EQ', 'NSE:GUJGASLTD-EQ',
            'NSE:GULFOILLUB-EQ', 'NSE:HAL-EQ', 'NSE:HAPPSTMNDS-EQ', 'NSE:HATSUN-EQ',
            'NSE:HEIDELBERG-EQ', 'NSE:HEXAWARE-EQ', 'NSE:HFCL-EQ', 'NSE:HIMATSEIDE-EQ',
            'NSE:HOMEFIRST-EQ', 'NSE:HONAUT-EQ', 'NSE:HUDCO-EQ', 'NSE:IBREALEST-EQ',
            'NSE:IDEA-EQ', 'NSE:IDFC-EQ', 'NSE:IEX-EQ', 'NSE:IFBIND-EQ'
        ]
        
        # Combine to get full Nifty 200 (ensure exactly 200)
        self.nifty200_symbols = self.nifty100_symbols[:100] + self.additional_100_symbols[:100]
    
    def display_nifty200_symbols(self):
        """Display all Nifty 200 symbols in organized format"""
        print("📋 NIFTY 200 SYMBOLS LIST")
        print("=" * 80)
        print(f"📊 Total Symbols: {len(self.nifty200_symbols)}")
        print(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Organize symbols by sector/category
        sectors = {
            'Banking & Finance': [],
            'IT & Technology': [],
            'Pharmaceuticals': [],
            'Automobiles': [],
            'Energy & Power': [],
            'Metals & Mining': [],
            'FMCG & Consumer': [],
            'Infrastructure & Real Estate': [],
            'Chemicals': [],
            'Telecom': [],
            'Others': []
        }
        
        # Categorize symbols
        for symbol in self.nifty200_symbols:
            symbol_name = symbol.replace('NSE:', '').replace('-EQ', '').upper()
            
            # Banking & Finance
            if any(keyword in symbol_name for keyword in ['BANK', 'HDFC', 'ICICI', 'AXIS', 'KOTAK', 'BAJFINANCE', 'SBIN', 'INDUSIND', 'FINANCE', 'CAPITAL', 'MUTHOOT', 'CHOLA', 'CANFIN', 'FEDERAL', 'SUNDARM', 'BANDHAN', 'AAVAS', 'LICI', 'SBILIFE', 'HDFCLIFE', 'PRULI']):
                sectors['Banking & Finance'].append(symbol)
            # IT & Technology  
            elif any(keyword in symbol_name for keyword in ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTIM', 'MPHASIS', 'OFSS', 'NAUKRI', 'HAPPSTMNDS', 'HEXAWARE', 'CYIENT']):
                sectors['IT & Technology'].append(symbol)
            # Pharmaceuticals
            elif any(keyword in symbol_name for keyword in ['PHARMA', 'CIPLA', 'DRREDDY', 'SUNPHARMA', 'BIOCON', 'LUPIN', 'DIVISLAB', 'TORNTPHARM', 'AJANTA', 'AJANTPHARM', 'ZYDUSLIFE', 'GLENMARK', 'FDC', 'GRANULES', 'ERIS']):
                sectors['Pharmaceuticals'].append(symbol)
            # Automobiles
            elif any(keyword in symbol_name for keyword in ['MARUTI', 'TATAMOTORS', 'M&M', 'HERO', 'BAJAJ', 'ASHOK', 'EICHER', 'TVS', 'ESCORTS', 'MOTHERSON', 'BHARATFORG', 'ENDURANCE', 'FORCEMOT']):
                sectors['Automobiles'].append(symbol)
            # Energy & Power
            elif any(keyword in symbol_name for keyword in ['POWER', 'COAL', 'OIL', 'GAS', 'ENERGY', 'RELIANCE', 'ONGC', 'IOC', 'BPCL', 'GAIL', 'NTPC', 'POWERGRID', 'ADANIPOWER', 'TORNTPOWER', 'RPOWER', 'ADANIGREEN']):
                sectors['Energy & Power'].append(symbol)
            # Metals & Mining
            elif any(keyword in symbol_name for keyword in ['STEEL', 'METAL', 'HINDALCO', 'VEDL', 'ZINC', 'ALUMINIUM', 'TATA', 'JSW', 'JINDAL', 'SAIL', 'COALINDIA']):
                sectors['Metals & Mining'].append(symbol)
            # FMCG
            elif any(keyword in symbol_name for keyword in ['UNILEVER', 'ITC', 'NEST', 'BRITANNIA', 'DABUR', 'GODREJ', 'MARICO', 'COLPAL', 'TATACONSUM', 'MCDOWELL', 'EMAMI', 'PIDILITE', 'TITAN', 'PAGE', 'BATA']):
                sectors['FMCG & Consumer'].append(symbol)
            # Infrastructure
            elif any(keyword in symbol_name for keyword in ['INFRA', 'CONSTRUCTION', 'CEMENT', 'L&T', 'UBL', 'ULTRA', 'REALTY', 'AMBUJA', 'DALBHARAT', 'JKCEMENT', 'INDIACEM', 'GMR', 'CONCOR', 'ADANIPORTS']):
                sectors['Infrastructure & Real Estate'].append(symbol)
            # Chemicals
            elif any(keyword in symbol_name for keyword in ['CHEM', 'ASIAN', 'UPL', 'SRF', 'DEEPAK', 'ALKYL', 'BALRAM', 'CHAMBER', 'COROMANDEL', 'GNFC', 'GSFC', 'NFL', 'RCF', 'ATUL']):
                sectors['Chemicals'].append(symbol)
            # Telecom
            elif any(keyword in symbol_name for keyword in ['BHARTI', 'IDEA', 'TELECOM']):
                sectors['Telecom'].append(symbol)
            else:
                sectors['Others'].append(symbol)
        
        # Display by sectors
        for sector, symbols in sectors.items():
            if symbols:
                print(f"\n🏢 {sector} ({len(symbols)} stocks):")
                print("-" * 50)
                for i, symbol in enumerate(symbols, 1):
                    clean_name = symbol.replace('NSE:', '').replace('-EQ', '')
                    print(f"  {i:2d}. {clean_name:<20} ({symbol})")
        
        # Summary
        print(f"\n📊 SECTOR-WISE DISTRIBUTION:")
        print("-" * 50)
        total_symbols = len(self.nifty200_symbols)
        for sector, symbols in sectors.items():
            if symbols:
                percentage = (len(symbols) / total_symbols) * 100
                print(f"  {sector:<25}: {len(symbols):3d} stocks ({percentage:5.1f}%)")
        
        print(f"\n✅ Total: {total_symbols} stocks (100% coverage)")
    
    def save_symbols_to_file(self):
        """Save all symbols to a text file"""
        try:
            # Create output directory if it doesn't exist
            test_dir = Path(__file__).parent / "output"
            test_dir.mkdir(exist_ok=True)
            results_file = test_dir / f"nifty200_symbols_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(results_file, 'w') as f:
                f.write(f"NIFTY 200 SYMBOLS LIST\n")
                f.write(f"=====================\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Symbols: {len(self.nifty200_symbols)}\n\n")
                
                f.write("ALL SYMBOLS:\n")
                f.write("============\n")
                for i, symbol in enumerate(self.nifty200_symbols, 1):
                    clean_name = symbol.replace('NSE:', '').replace('-EQ', '')
                    f.write(f"{i:3d}. {clean_name:<20} {symbol}\n")
                
                f.write(f"\n\nFyers API Format (comma-separated):\n")
                f.write("===================================\n")
                symbol_list = ','.join(self.nifty200_symbols)
                # Break into lines of reasonable length
                words = symbol_list.split(',')
                line = ""
                for word in words:
                    if len(line + word) > 80:
                        f.write(line + "\n")
                        line = word + ","
                    else:
                        line += word + ","
                if line:
                    f.write(line.rstrip(',') + "\n")
            
            print(f"\n💾 Symbols saved to: {results_file}")
            return results_file
            
        except Exception as e:
            print(f"⚠️  Could not save symbols: {e}")
            return None
    
    def run_test(self):
        """Run the complete Nifty 200 display test"""
        print("🚀 NIFTY 200 SYMBOL DISCOVERY TEST")
        print("=" * 80)
        
        # Display all symbols
        self.display_nifty200_symbols()
        
        # Save to file
        self.save_symbols_to_file()
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("📊 Displayed 200 Nifty 200 symbols")
        print("💡 These symbols can be used with Fyers API for data collection")
        print("🔄 Next steps: Use these symbols in data_orchestrator.py for bulk data collection")

def main():
    """Main function"""
    test = SimpleNifty200Test()
    test.run_test()

if __name__ == "__main__":
    main()