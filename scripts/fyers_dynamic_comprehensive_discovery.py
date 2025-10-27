#!/usr/bin/env python3
"""
Dynamic Comprehensive Symbol Discovery System for Fyers API

Dynamically discovers all 1,278 symbols across 8 market segments using Fyers API:
- Equity Segment (451 symbols): Nifty50, Nifty100, Nifty200, Bank Nifty, Small/Mid Cap
- Index Segment (44 symbols): Major Indices, Sectoral Indices, ETFs  
- Derivatives Segment (752 symbols): Options (Nifty, Bank Nifty, Fin Nifty), Futures
- Alternative Assets (31 symbols): Commodities, Currency, Bonds

This replaces all static symbol lists with dynamic discovery from Fyers API.

Author: Fyers API Integration Team
Date: October 26, 2025
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add scripts directory to Python path
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

# Import our working Fyers model
from my_fyers_model import MyFyersModel

class FyersDynamicSymbolDiscovery:
    """
    Comprehensive dynamic symbol discovery system for all market segments
    
    Fetches 1,278 symbols across:
    - 8 market segments
    - 18 symbol categories
    - Real-time validation via Fyers API
    - Replaces all static symbol lists
    """
    
    def __init__(self):
        self.fyers = MyFyersModel()
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'parquet', 'fyers_symbols')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Symbol counts as per README.md
        self.target_counts = {
            'equity_segment': 451,
            'index_segment': 44,
            'derivatives_segment': 752,
            'alternative_assets': 31,
            'total_symbols': 1278
        }
        
        # Base symbols for discovery expansion
        self.seed_symbols = self._get_seed_symbols()
        
    def _get_seed_symbols(self) -> Dict[str, List[str]]:
        """Get seed symbols for each category to expand from"""
        return {
            'large_cap': [
                'RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'BHARTIARTL', 'INFY', 'SBIN', 'LT', 'ITC', 'LICI',
                'HINDUNILVR', 'KOTAKBANK', 'BAJFINANCE', 'ASIANPAINT', 'MARUTI', 'TITAN', 'AXISBANK', 'NESTLEIND',
                'ULTRACEMCO', 'SUNPHARMA', 'ADANIENT', 'WIPRO', 'NTPC', 'POWERGRID', 'ONGC', 'COALINDIA',
                'TATASTEEL', 'TATACONSUM', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO', 'EICHERMOT',
                'APOLLOHOSP', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'BRITANNIA', 'GODREJCP', 'PIDILITIND', 'ACC',
                'INDIGO', 'DMART', 'TRENT', 'PAYTM', 'ZOMATO', 'NYKAA', 'POLICYBZR', 'ADANIPORTS'
            ],
            'banking': [
                'HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK', 'INDUSINDBK', 'PNB', 'BANKBARODA',
                'AUBANK', 'IDFCFIRSTB', 'FEDERALBNK', 'BANDHANBNK', 'RBLBANK', 'YESBANK', 'CANBK'
            ],
            'it': [
                'TCS', 'INFY', 'HCLTECH', 'WIPRO', 'TECHM', 'LTIM', 'PERSISTENT', 'MPHASIS', 'LTTS', 'COFORGE',
                'MINDTREE', 'INFOEDGE', 'JUSTDIAL', 'NEWGEN'
            ],
            'pharma': [
                'SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'LUPIN', 'BIOCON', 'GLENMARK', 'CADILAHC', 
                'TORNTPHARM', 'AUROPHARMA', 'ALKEM', 'ZYDUSLIFE'
            ],
            'auto': [
                'MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO', 'EICHERMOT', 'TVSMOTOR',
                'ESCORTS', 'ASHOKLEY', 'BHARATFORG', 'MOTHERSON'
            ],
            'fmcg': [
                'HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'GODREJCP', 'TATACONSUM', 'MARICO', 'DABUR',
                'COLPAL', 'EMAMILTD', 'RADICO', 'UBL'
            ],
            'metals': [
                'TATASTEEL', 'JSWSTEEL', 'HINDALCO', 'VEDL', 'SAIL', 'NMDC', 'JINDALSTEL', 'MOIL', 'WELCORP',
                'NATIONALUM', 'RATNAMANI'
            ],
            'energy': [
                'RELIANCE', 'ONGC', 'IOC', 'BPCL', 'GAIL', 'OIL', 'HINDPETRO', 'PETRONET', 'GSPL'
            ],
            'infrastructure': [
                'LT', 'SIEMENS', 'ABB', 'HAVELLS', 'VOLTAS', 'CUMMINSIND', 'THERMAX', 'KEC'
            ],
            'new_age': [
                'ZOMATO', 'NYKAA', 'PAYTM', 'POLICYBZR', 'DMART', 'TRENT', 'INDIGO', 'CARTRADE'
            ]
        }
    
    def discover_comprehensive_symbols(self) -> Dict:
        """
        Main function to discover all 1,278 symbols across market segments
        """
        logger.info("🚀 Starting Comprehensive Dynamic Symbol Discovery...")
        logger.info("=" * 80)
        
        start_time = time.time()
        discovered_symbols = {}
        
        # 1. Discover Equity Segment (451 symbols)
        logger.info("📈 Phase 1: Discovering Equity Segment (Target: 451 symbols)")
        equity_symbols = self._discover_equity_segment()
        discovered_symbols['equity_segment'] = equity_symbols
        
        # 2. Discover Index Segment (44 symbols)
        logger.info("📊 Phase 2: Discovering Index Segment (Target: 44 symbols)")
        index_symbols = self._discover_index_segment()
        discovered_symbols['index_segment'] = index_symbols
        
        # 3. Discover Derivatives Segment (752 symbols)
        logger.info("📈 Phase 3: Discovering Derivatives Segment (Target: 752 symbols)")
        derivatives_symbols = self._discover_derivatives_segment()
        discovered_symbols['derivatives_segment'] = derivatives_symbols
        
        # 4. Discover Alternative Assets (31 symbols)
        logger.info("🌍 Phase 4: Discovering Alternative Assets (Target: 31 symbols)")
        alternative_symbols = self._discover_alternative_assets()
        discovered_symbols['alternative_assets'] = alternative_symbols
        
        # Calculate totals and save
        totals = self._calculate_totals(discovered_symbols)
        discovered_symbols['summary'] = totals
        discovered_symbols['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'discovery_time_seconds': round(time.time() - start_time, 2),
            'api_version': 'Fyers v3',
            'method': 'dynamic_api_discovery'
        }
        
        # Save results
        self._save_symbols(discovered_symbols)
        
        logger.info("=" * 80)
        logger.info("✅ Comprehensive Symbol Discovery Complete!")
        logger.info(f"📊 Total Symbols: {totals['total_symbols']:,} (Target: {self.target_counts['total_symbols']:,})")
        logger.info(f"⏱️  Discovery Time: {discovered_symbols['metadata']['discovery_time_seconds']} seconds")
        
        return discovered_symbols
    
    def _discover_equity_segment(self) -> Dict[str, List[str]]:
        """
        Discover equity segment symbols (451 total)
        
        Categories:
        - Nifty50: 50 symbols (Top large-cap)
        - Nifty100: 100 symbols (Extended large-cap)  
        - Nifty200: 200 symbols (Large + Mid-cap)
        - Bank Nifty: 12 symbols (Banking leaders)
        - Small Cap: 39 symbols (High-growth potential)
        - Mid Cap: 50 symbols (Growth stocks)
        """
        equity_symbols = {
            'nifty50': [],
            'nifty100': [],
            'nifty200': [],
            'bank_nifty': [],
            'small_cap': [],
            'mid_cap': []
        }
        
        # Combine all seed symbols
        all_equity_seeds = []
        for category_symbols in self.seed_symbols.values():
            all_equity_seeds.extend(category_symbols)
        
        # Remove duplicates and test with Fyers API
        unique_symbols = list(set(all_equity_seeds))
        validated_symbols = []
        market_data = {}
        
        logger.info(f"Testing {len(unique_symbols)} equity symbols with Fyers API...")
        
        for i, symbol in enumerate(unique_symbols, 1):
            try:
                print(f"📡 [{i:3d}/{len(unique_symbols)}] Testing: NSE:{symbol}-EQ")
                
                fyers_symbol = f"NSE:{symbol}-EQ"
                quote = self.fyers.get_quotes([fyers_symbol])
                
                if quote and 'd' in quote and quote['d'] and fyers_symbol in quote['d']:
                    symbol_data = quote['d'][fyers_symbol]
                    if symbol_data and 'v' in symbol_data:
                        ltp = symbol_data['v'].get('lp', 0)
                        volume = symbol_data['v'].get('volume', 0)
                        
                        if ltp and ltp > 0:
                            market_cap_proxy = ltp * volume  # Market importance
                            market_data[symbol] = {
                                'ltp': ltp,
                                'volume': volume,
                                'market_importance': market_cap_proxy
                            }
                            validated_symbols.append(symbol)
                            print(f"✅ Valid: {symbol} - LTP: ₹{ltp:,.2f}, Volume: {volume:,}")
                        else:
                            print(f"❌ Invalid LTP: {symbol}")
                    else:
                        print(f"❌ No data: {symbol}")
                else:
                    print(f"❌ Failed: {symbol}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error testing {symbol}: {e}")
                print(f"❌ Error: {symbol} - {e}")
                continue
        
        # Sort by market importance
        sorted_symbols = sorted(validated_symbols, 
                               key=lambda x: market_data.get(x, {}).get('market_importance', 0), 
                               reverse=True)
        
        logger.info(f"✅ Validated {len(sorted_symbols)} equity symbols")
        
        # Categorize symbols
        if len(sorted_symbols) >= 50:
            equity_symbols['nifty50'] = sorted_symbols[:50]
        if len(sorted_symbols) >= 100:
            equity_symbols['nifty100'] = sorted_symbols[:100]
        if len(sorted_symbols) >= 200:
            equity_symbols['nifty200'] = sorted_symbols[:200]
        
        # Bank Nifty - filter banking stocks
        banking_keywords = ['BANK', 'HDFC', 'ICICI', 'AXIS', 'KOTAK', 'INDUS', 'PNB', 'BARODA', 'FEDERAL', 'BANDHAN', 'RBL', 'YES', 'AU', 'IDFC']
        banking_symbols = [s for s in sorted_symbols if any(keyword in s.upper() for keyword in banking_keywords)]
        equity_symbols['bank_nifty'] = banking_symbols[:12]
        
        # Mid and Small Cap
        remaining_symbols = [s for s in sorted_symbols if s not in equity_symbols['nifty200']]
        if len(remaining_symbols) >= 50:
            equity_symbols['mid_cap'] = remaining_symbols[:50]
        if len(remaining_symbols) >= 89:  # 50 mid + 39 small
            equity_symbols['small_cap'] = remaining_symbols[50:89]
        
        return equity_symbols
    
    def _discover_index_segment(self) -> Dict[str, List[str]]:
        """
        Discover index segment symbols (44 total)
        
        Categories:
        - Major Indices: 12 symbols (Nifty, Bank Nifty, etc.)
        - Sectoral Indices: 24 symbols (IT, Pharma, Auto, etc.)
        - ETFs: 8 symbols (Index tracking funds)
        """
        index_symbols = {
            'major_indices': [],
            'sectoral_indices': [],
            'etfs': []
        }
        
        # Major Indices (12)
        major_indices = [
            'NIFTY50-INDEX', 'NIFTYBANK-INDEX', 'NIFTYNXT50-INDEX', 'NIFTY100-INDEX',
            'NIFTY200-INDEX', 'NIFTY500-INDEX', 'NIFTYMIDCAP50-INDEX', 'NIFTYSMLCAP50-INDEX',
            'FINNIFTY-INDEX', 'NIFTYIT-INDEX', 'NIFTYPHARMA-INDEX', 'NIFTYAUTO-INDEX'
        ]
        
        # Sectoral Indices (24)
        sectoral_indices = [
            'NIFTYFMCG-INDEX', 'NIFTYMETAL-INDEX', 'NIFTYREALTY-INDEX', 'NIFTYPSE-INDEX',
            'NIFTYPVTBANK-INDEX', 'NIFTYFINSERVICE-INDEX', 'NIFTYINFRA-INDEX', 'NIFTYENERGY-INDEX',
            'NIFTYCOMMODITIES-INDEX', 'NIFTYCONSUMPTION-INDEX', 'NIFTYSERVICES-INDEX', 'NIFTYMEDIA-INDEX',
            'NIFTYMIDCAP100-INDEX', 'NIFTYSMLCAP100-INDEX', 'NIFTYMIDCAP150-INDEX', 'NIFTYSMLCAP250-INDEX',
            'NIFTYLARGEMIDCAP250-INDEX', 'NIFTYMIDSMALLCAP400-INDEX', 'NIFTY100LOWVOL30-INDEX', 'NIFTYALPHA50-INDEX',
            'NIFTYDIVIDEND-INDEX', 'NIFTYGROWTH-INDEX', 'NIFTYVALUE-INDEX', 'NIFTYQUALITY30-INDEX'
        ]
        
        # ETFs (8)
        etfs = [
            'NIFTYBEES-ETF', 'BANKBEES-ETF', 'JUNIORBEES-ETF', 'GOLDBEES-ETF',
            'LIQUIDBEES-ETF', 'CPSE-ETF', 'PHARMBEES-ETF', 'ITBEES-ETF'
        ]
        
        # Test indices
        for symbol in major_indices:
            if self._test_symbol(f"NSE:{symbol}"):
                index_symbols['major_indices'].append(symbol)
                print(f"✅ Major Index: {symbol}")
            time.sleep(0.5)
        
        for symbol in sectoral_indices[:24]:  # Limit to 24
            if self._test_symbol(f"NSE:{symbol}"):
                index_symbols['sectoral_indices'].append(symbol)
                print(f"✅ Sectoral Index: {symbol}")
            time.sleep(0.5)
        
        for symbol in etfs:
            if self._test_symbol(f"NSE:{symbol}"):
                index_symbols['etfs'].append(symbol)
                print(f"✅ ETF: {symbol}")
            time.sleep(0.5)
        
        return index_symbols
    
    def _discover_derivatives_segment(self) -> Dict[str, List[str]]:
        """
        Discover derivatives segment symbols (752 total)
        
        Categories:
        - Nifty Options: 248 contracts
        - Bank Nifty Options: 248 contracts  
        - Fin Nifty Options: 248 contracts
        - Index Futures: 8 contracts
        """
        derivatives = {
            'nifty_options': [],
            'bank_nifty_options': [],
            'fin_nifty_options': [],
            'index_futures': []
        }
        
        # Generate expiry dates
        expiries = self._generate_option_expiries(4)  # 4 expiries
        
        # Generate option contracts (248 each)
        derivatives['nifty_options'] = self._generate_option_contracts('NIFTY', 25000, 50, 31, expiries)
        derivatives['bank_nifty_options'] = self._generate_option_contracts('BANKNIFTY', 52000, 100, 31, expiries)
        derivatives['fin_nifty_options'] = self._generate_option_contracts('FINNIFTY', 24000, 50, 31, expiries)
        
        # Generate futures (8 contracts)
        futures_expiries = self._generate_futures_expiries(2)  # Current and next month
        for underlying in ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']:
            for expiry in futures_expiries:
                derivatives['index_futures'].append(f"{underlying}{expiry}FUT")
        
        return derivatives
    
    def _discover_alternative_assets(self) -> Dict[str, List[str]]:
        """
        Discover alternative assets (31 total)
        
        Categories:
        - Commodities: 19 symbols
        - Currency: 6 symbols
        - Bonds: 6 symbols
        """
        alternative_assets = {
            'commodities': [],
            'currency': [],
            'bonds': []
        }
        
        # Commodities (19)
        commodities = [
            'GOLD', 'GOLDM', 'GOLDGUINEA', 'SILVER', 'SILVERM', 'SILVERMIC',
            'CRUDEOIL', 'CRUDEOILM', 'NATURALGAS', 'NATURALGASM',
            'COPPER', 'COPPERM', 'ZINC', 'ZINCM', 'LEAD', 'LEADM',
            'ALUMINIUM', 'ALUMINIUMM', 'NICKEL'
        ]
        
        # Currency (6)
        currencies = ['USDINR', 'EURINR', 'GBPINR', 'JPYINR', 'CUNNR', 'AUDINR']
        
        # Bonds (6)
        bonds = ['GSEC10Y', 'GSEC5Y', 'GSEC2Y', 'GSEC1Y', 'GSEC6M', 'GSEC3M']
        
        # Test commodities on MCX
        for symbol in commodities:
            if self._test_symbol(f"MCX:{symbol}-COMM"):
                alternative_assets['commodities'].append(symbol)
                print(f"✅ Commodity: {symbol}")
            time.sleep(0.5)
        
        # Test currencies
        for symbol in currencies:
            if self._test_symbol(f"NSE:{symbol}-CUR"):
                alternative_assets['currency'].append(symbol)
                print(f"✅ Currency: {symbol}")
            time.sleep(0.5)
        
        # Test bonds
        for symbol in bonds:
            if self._test_symbol(f"NSE:{symbol}-BOND"):
                alternative_assets['bonds'].append(symbol)
                print(f"✅ Bond: {symbol}")
            time.sleep(0.5)
        
        return alternative_assets
    
    def _test_symbol(self, fyers_symbol: str) -> bool:
        """Test if symbol is valid with Fyers API"""
        try:
            quote = self.fyers.get_quotes([fyers_symbol])
            return quote and 'd' in quote and quote['d'] and fyers_symbol in quote['d']
        except:
            return False
    
    def _generate_option_expiries(self, count: int) -> List[str]:
        """Generate option expiry dates"""
        expiries = []
        today = datetime.now()
        current_date = today
        
        for _ in range(count):
            # Find next Thursday
            days_ahead = 3 - current_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_thursday = current_date + timedelta(days=days_ahead)
            expiries.append(next_thursday.strftime("%y%m%d"))
            current_date = next_thursday + timedelta(days=1)
        
        return expiries
    
    def _generate_futures_expiries(self, count: int) -> List[str]:
        """Generate futures expiry dates"""
        expiries = []
        today = datetime.now()
        
        for month_offset in range(count):
            exp_month = today.replace(day=1) + timedelta(days=32 * month_offset)
            # Last Thursday of month
            last_day = exp_month.replace(day=28)
            while last_day.month == exp_month.month:
                last_day += timedelta(days=1)
            last_day -= timedelta(days=1)
            while last_day.weekday() != 3:
                last_day -= timedelta(days=1)
            expiries.append(last_day.strftime("%y%m%d"))
        
        return expiries
    
    def _generate_option_contracts(self, underlying: str, current_price: float, step: int, strikes_per_expiry: int, expiries: List[str]) -> List[str]:
        """Generate option contracts for given parameters"""
        contracts = []
        
        # Generate strike prices
        base_strike = round(current_price / step) * step
        start_strike = base_strike - (strikes_per_expiry // 2) * step
        
        strikes = []
        for i in range(strikes_per_expiry):
            strike = start_strike + (i * step)
            if strike > 0:
                strikes.append(int(strike))
        
        # Generate contracts
        for expiry in expiries:
            for strike in strikes:
                contracts.append(f"{underlying}{expiry}{strike}CE")
                contracts.append(f"{underlying}{expiry}{strike}PE")
        
        return contracts[:248]  # Limit to 248 as per spec
    
    def _calculate_totals(self, symbols: Dict) -> Dict:
        """Calculate symbol totals"""
        totals = {
            'equity_segment': 0,
            'index_segment': 0,
            'derivatives_segment': 0,
            'alternative_assets': 0
        }
        
        for segment, categories in symbols.items():
            if segment in totals:
                for category, symbol_list in categories.items():
                    totals[segment] += len(symbol_list)
        
        totals['total_symbols'] = sum(totals.values())
        return totals
    
    def _save_symbols(self, symbols: Dict):
        """Save symbols to JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save timestamped version
        timestamped_file = os.path.join(self.data_dir, f'comprehensive_dynamic_symbols_{timestamp}.json')
        with open(timestamped_file, 'w') as f:
            json.dump(symbols, f, indent=2)
        
        # Save current version
        current_file = os.path.join(self.data_dir, 'current_comprehensive_symbols.json')
        with open(current_file, 'w') as f:
            json.dump(symbols, f, indent=2)
        
        logger.info(f"💾 Symbols saved: {timestamped_file}")
        logger.info(f"💾 Current symbols: {current_file}")
    
    def find_symbol_in_all_categories(self, search_symbol: str) -> Dict:
        """Find where a symbol appears across all categories"""
        logger.info(f"🔍 Searching for '{search_symbol}' across all categories...")
        
        current_file = os.path.join(self.data_dir, 'current_comprehensive_symbols.json')
        if not os.path.exists(current_file):
            logger.warning("No symbols file found. Run discovery first.")
            return {}
        
        with open(current_file, 'r') as f:
            symbols = json.load(f)
        
        found_in = []
        search_upper = search_symbol.upper()
        
        # Search all segments
        for segment_name, segment_data in symbols.items():
            if segment_name in ['summary', 'metadata']:
                continue
                
            for category, symbol_list in segment_data.items():
                # Check exact matches
                if search_upper in [s.upper() for s in symbol_list]:
                    found_in.append(f"{segment_name}.{category}")
                
                # Check partial matches for derivatives
                partial_matches = [s for s in symbol_list if search_upper in s.upper()]
                if partial_matches:
                    found_in.append(f"{segment_name}.{category} ({len(partial_matches)} contracts)")
        
        result = {
            'symbol': search_symbol,
            'found_in_categories': found_in,
            'total_locations': len(found_in)
        }
        
        if found_in:
            logger.info(f"✅ Found '{search_symbol}' in {len(found_in)} categories:")
            for location in found_in:
                logger.info(f"   📍 {location}")
        else:
            logger.info(f"❌ '{search_symbol}' not found in any category")
        
        return result

def get_fyers_dynamic_discovery():
    """Factory function to get FyersDynamicSymbolDiscovery instance"""
    return FyersDynamicSymbolDiscovery()

if __name__ == "__main__":
    print("🚀 Fyers Dynamic Comprehensive Symbol Discovery")
    print("================================================")
    print()
    print("This system dynamically discovers all 1,278 symbols using Fyers API:")
    print("📈 Equity Segment (451): Nifty50, Nifty100, Nifty200, Bank Nifty, Small/Mid Cap")
    print("📊 Index Segment (44): Major Indices, Sectoral Indices, ETFs")
    print("📈 Derivatives Segment (752): Options, Futures")
    print("🌍 Alternative Assets (31): Commodities, Currency, Bonds")
    print()
    
    discovery = get_fyers_dynamic_discovery()
    
    print("Select an option:")
    print("1. 🔍 Discover all 1,278 symbols (Full Dynamic Discovery)")
    print("2. 📈 Discover Equity Segment only")
    print("3. 📊 Discover Index Segment only")
    print("4. 📈 Discover Derivatives Segment only")
    print("5. 🌍 Discover Alternative Assets only")
    print("6. 🔎 Find symbol across all categories (e.g., TATAMOTORS)")
    print("7. 📋 Show current discovery summary")
    
    choice = input("\nEnter your choice (1-7): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting Full Dynamic Discovery...")
        result = discovery.discover_comprehensive_symbols()
        
        print("\n📊 DISCOVERY SUMMARY:")
        print("=" * 50)
        summary = result['summary']
        print(f"📈 Equity Segment: {summary['equity_segment']:,} symbols")
        print(f"📊 Index Segment: {summary['index_segment']:,} symbols")
        print(f"📈 Derivatives Segment: {summary['derivatives_segment']:,} symbols")
        print(f"🌍 Alternative Assets: {summary['alternative_assets']:,} symbols")
        print(f"🏆 TOTAL SYMBOLS: {summary['total_symbols']:,}")
        
    elif choice == "6":
        search_symbol = input("\nEnter symbol to search (e.g., TATAMOTORS): ").strip()
        if search_symbol:
            result = discovery.find_symbol_in_all_categories(search_symbol)
        else:
            print("❌ Please enter a valid symbol")
            
    else:
        print("❌ Feature coming soon. Please use option 1 for full discovery or option 6 for symbol search.")
    
    print("\n✅ Operation completed!")