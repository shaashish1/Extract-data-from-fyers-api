"""
Test script to display Nifty 50 stocks and related data
"""
import sys
import os
from pathlib import Path
from datetime import datetime

class SimpleNifty50Test:
    def __init__(self):
        """Initialize with Nifty 50 symbols (exactly 50)"""
        # Nifty 50 symbols (top 50 large-cap stocks)
        self.nifty50_symbols = [
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
            'NSE:SBILIFE-EQ', 'NSE:PIDILITIND-EQ'
        ]
    
    def display_nifty50_symbols(self):
        """Display all Nifty 50 symbols in organized format"""
        print("📋 NIFTY 50 SYMBOLS LIST")
        print("=" * 80)
        print(f"📊 Total Symbols: {len(self.nifty50_symbols)}")
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
            'Infrastructure': [],
            'Chemicals': [],
            'Telecom': [],
            'Others': []
        }
        
        # Categorize symbols
        for symbol in self.nifty50_symbols:
            symbol_name = symbol.replace('NSE:', '').replace('-EQ', '').upper()
            
            # Banking & Finance
            if any(keyword in symbol_name for keyword in ['BANK', 'HDFC', 'ICICI', 'AXIS', 'KOTAK', 'BAJFINANCE', 'SBIN', 'INDUSIND', 'FINANCE', 'SBILIFE']):
                sectors['Banking & Finance'].append(symbol)
            # IT & Technology  
            elif any(keyword in symbol_name for keyword in ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTIM']):
                sectors['IT & Technology'].append(symbol)
            # Pharmaceuticals
            elif any(keyword in symbol_name for keyword in ['PHARMA', 'CIPLA', 'DRREDDY', 'SUNPHARMA', 'DIVISLAB']):
                sectors['Pharmaceuticals'].append(symbol)
            # Automobiles
            elif any(keyword in symbol_name for keyword in ['MARUTI', 'TATAMOTORS', 'M&M', 'HERO', 'BAJAJ', 'EICHER']):
                sectors['Automobiles'].append(symbol)
            # Energy & Power
            elif any(keyword in symbol_name for keyword in ['POWER', 'COAL', 'OIL', 'GAS', 'ENERGY', 'RELIANCE', 'ONGC', 'IOC', 'BPCL', 'NTPC', 'POWERGRID']):
                sectors['Energy & Power'].append(symbol)
            # Metals & Mining
            elif any(keyword in symbol_name for keyword in ['STEEL', 'METAL', 'HINDALCO', 'TATA', 'JSW', 'JINDAL', 'COALINDIA']):
                sectors['Metals & Mining'].append(symbol)
            # FMCG
            elif any(keyword in symbol_name for keyword in ['UNILEVER', 'ITC', 'NEST', 'BRITANNIA', 'TITAN', 'PIDILITE']):
                sectors['FMCG & Consumer'].append(symbol)
            # Infrastructure
            elif any(keyword in symbol_name for keyword in ['INFRA', 'CONSTRUCTION', 'CEMENT', 'L&T', 'UBL', 'ULTRA', 'ADANIPORTS']):
                sectors['Infrastructure'].append(symbol)
            # Chemicals
            elif any(keyword in symbol_name for keyword in ['CHEM', 'ASIAN', 'PAINT']):
                sectors['Chemicals'].append(symbol)
            # Telecom
            elif any(keyword in symbol_name for keyword in ['BHARTI', 'TELECOM']):
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
        total_symbols = len(self.nifty50_symbols)
        for sector, symbols in sectors.items():
            if symbols:
                percentage = (len(symbols) / total_symbols) * 100
                print(f"  {sector:<25}: {len(symbols):2d} stocks ({percentage:5.1f}%)")
        
        print(f"\n✅ Total: {total_symbols} stocks (100% coverage)")
    
    def save_symbols_to_file(self):
        """Save all symbols to a text file"""
        try:
            # Create output directory if it doesn't exist
            test_dir = Path(__file__).parent / "output"
            test_dir.mkdir(exist_ok=True)
            results_file = test_dir / f"nifty50_symbols_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(results_file, 'w') as f:
                f.write(f"NIFTY 50 SYMBOLS LIST\n")
                f.write(f"====================\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Symbols: {len(self.nifty50_symbols)}\n\n")
                
                f.write("ALL SYMBOLS:\n")
                f.write("============\n")
                for i, symbol in enumerate(self.nifty50_symbols, 1):
                    clean_name = symbol.replace('NSE:', '').replace('-EQ', '')
                    f.write(f"{i:2d}. {clean_name:<20} {symbol}\n")
            
            print(f"\n💾 Symbols saved to: {results_file}")
            return results_file
            
        except Exception as e:
            print(f"⚠️  Could not save symbols: {e}")
            return None
    
    def run_test(self):
        """Run the complete Nifty 50 display test"""
        print("🚀 NIFTY 50 SYMBOL DISCOVERY TEST")
        print("=" * 80)
        
        # Display all symbols
        self.display_nifty50_symbols()
        
        # Save to file
        self.save_symbols_to_file()
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"📊 Displayed {len(self.nifty50_symbols)} Nifty 50 symbols")
        print("💡 These symbols can be used with Fyers API for data collection")
        print("🔄 Next steps: Use these symbols for historical or real-time data extraction")

def main():
    """Main function"""
    test = SimpleNifty50Test()
    test.run_test()

if __name__ == "__main__":
    main()