"""
Dynamic Symbol Discovery Module for Fyers API
Replaces hardcoded symbol lists with runtime discovery from Fyers API
Enhanced with NSE data integration for comprehensive symbol management
"""
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import requests
from my_fyers_model import MyFyersModel
from data_storage import get_parquet_manager


class SymbolDiscovery:
    """Dynamically discover and manage trading symbols from Fyers API and NSE data"""
    
    def __init__(self):
        self.fyers = MyFyersModel()
        self.manager = get_parquet_manager()
        self.symbols_dir = Path("data/parquet/symbols")
        self.symbols_dir.mkdir(parents=True, exist_ok=True)
        
        # Known index symbols for reference
        self.index_symbols = {
            'NIFTY50': 'NSE:NIFTY50-INDEX',
            'BANKNIFTY': 'NSE:NIFTYBANK-INDEX', 
            'FINNIFTY': 'NSE:FINNIFTY-INDEX',
            'INDIAVIX': 'NSE:INDIAVIX-INDEX',
            'SENSEX': 'NSE:SENSEX-INDEX'
        }
        
        # Initialize direct Fyers discovery (preferred method)
        self._fyers_direct = None
        # Initialize NSE data fetcher (fallback method) 
        self._nse_fetcher = None
    
    @property
    def fyers_direct(self):
        """Lazy load direct Fyers discovery"""
        if self._fyers_direct is None:
            from fyers_direct_discovery import get_fyers_direct_discovery
            self._fyers_direct = get_fyers_direct_discovery()
        return self._fyers_direct
    
    @property
    def nse_fetcher(self):
        """Lazy load NSE data fetcher to avoid circular imports"""
        if self._nse_fetcher is None:
            from nse_data_fetcher import get_nse_fetcher
            self._nse_fetcher = get_nse_fetcher()
        return self._nse_fetcher
    
    def get_nse_symbols_by_index(self, index_name: str) -> List[str]:
        """
        Get symbols from NSE data for specific index
        
        Args:
            index_name (str): Index name (nifty50, nifty100, nifty200, etc.)
            
        Returns:
            List[str]: List of Fyers format symbols
        """
        try:
            return self.nse_fetcher.get_fyers_symbols_by_category('indices', index_name)
        except Exception as e:
            print(f"❌ Failed to get NSE symbols for {index_name}: {e}")
            return self._get_fallback_symbols(index_name)
    
    def get_nse_etf_symbols(self, etf_type: str = None) -> List[str]:
        """
        Get ETF symbols from NSE data
        
        Args:
            etf_type (str): ETF type (nifty50_etf, gold_etf, all_etf) or None for all
            
        Returns:
            List[str]: List of Fyers format ETF symbols
        """
        try:
            return self.nse_fetcher.get_fyers_symbols_by_category('etfs', etf_type)
        except Exception as e:
            print(f"❌ Failed to get NSE ETF symbols: {e}")
            return []
    
    def get_nse_derivative_symbols(self) -> List[str]:
        """
        Get derivative underlying symbols from NSE data
        
        Returns:
            List[str]: List of Fyers format derivative symbols
        """
        try:
            return self.nse_fetcher.get_fyers_symbols_by_category('derivatives', 'stock_options')
        except Exception as e:
            print(f"❌ Failed to get NSE derivative symbols: {e}")
            return []
    
    def refresh_nse_data(self) -> bool:
        """
        Refresh NSE symbol data by fetching latest from APIs
        
        Returns:
            bool: Success status
        """
        try:
            print("🔄 Refreshing NSE symbol data...")
            all_data = self.nse_fetcher.fetch_all_nse_data(save_to_parquet=True)
            
            total_symbols = 0
            for category, endpoints in all_data.items():
                if category != 'fetch_timestamp':
                    total_symbols += sum(
                        len(data.get('symbols', data.get('etfs', data.get('derivatives', []))))
                        for data in endpoints.values()
                    )
            
            print(f"✅ Successfully refreshed {total_symbols} symbols from NSE")
            return True
            
        except Exception as e:
            print(f"❌ Failed to refresh NSE data: {e}")
            return False
    
    def _get_fallback_symbols(self, index_name: str) -> List[str]:
        """Fallback symbol lists if NSE data fetch fails"""
        fallback_symbols = {
            'nifty50': [
                'NSE:RELIANCE-EQ', 'NSE:TCS-EQ', 'NSE:HDFCBANK-EQ',
                'NSE:INFY-EQ', 'NSE:ICICIBANK-EQ', 'NSE:SBIN-EQ',
                'NSE:BHARTIARTL-EQ', 'NSE:ITC-EQ', 'NSE:KOTAKBANK-EQ',
                'NSE:LT-EQ', 'NSE:ASIANPAINT-EQ', 'NSE:MARUTI-EQ',
                'NSE:AXISBANK-EQ', 'NSE:HCLTECH-EQ', 'NSE:WIPRO-EQ',
                'NSE:NESTLEIND-EQ', 'NSE:ULTRACEMCO-EQ', 'NSE:BAJFINANCE-EQ',
                'NSE:ONGC-EQ', 'NSE:POWERGRID-EQ', 'NSE:NTPC-EQ',
                'NSE:TECHM-EQ', 'NSE:TATAMOTORS-EQ', 'NSE:HINDUNILVR-EQ',
                'NSE:SUNPHARMA-EQ', 'NSE:TITAN-EQ', 'NSE:DRREDDY-EQ',
                'NSE:BAJAJFINSV-EQ', 'NSE:COALINDIA-EQ', 'NSE:INDUSINDBK-EQ',
                'NSE:TATASTEEL-EQ', 'NSE:ADANIPORTS-EQ', 'NSE:JSWSTEEL-EQ',
                'NSE:HINDALCO-EQ', 'NSE:GRASIM-EQ', 'NSE:BRITANNIA-EQ',
                'NSE:CIPLA-EQ', 'NSE:DIVISLAB-EQ', 'NSE:BAJAJ-AUTO-EQ',
                'NSE:EICHERMOT-EQ', 'NSE:HEROMOTOCO-EQ', 'NSE:APOLLOHOSP-EQ',
                'NSE:BPCL-EQ', 'NSE:TATACONSUM-EQ', 'NSE:SBILIFE-EQ',
                'NSE:HDFCLIFE-EQ', 'NSE:LTIM-EQ', 'NSE:TATAPOWER-EQ'
            ],
            'banknifty': [
                'NSE:HDFCBANK-EQ', 'NSE:ICICIBANK-EQ', 'NSE:AXISBANK-EQ',
                'NSE:KOTAKBANK-EQ', 'NSE:SBIN-EQ', 'NSE:INDUSINDBK-EQ',
                'NSE:BANKBARODA-EQ', 'NSE:PNB-EQ', 'NSE:FEDERALBNK-EQ',
                'NSE:IDFCFIRSTB-EQ', 'NSE:BANDHANBNK-EQ', 'NSE:AUBANK-EQ'
            ]
        }
        return fallback_symbols.get(index_name, [])
    
    def get_nifty50_constituents(self) -> List[str]:
        """
        Get complete Nifty50 constituent symbols (50 stocks)
        Uses direct Fyers approach with fallback to NSE data
        """
        # Method 1: Direct Fyers discovery (preferred)
        try:
            fyers_symbols = self.fyers_direct.get_nifty50_constituents()
            if fyers_symbols and len(fyers_symbols) >= 40:  # Reasonable threshold
                print(f"✅ Using direct Fyers Nifty50: {len(fyers_symbols)} symbols")
                return fyers_symbols[:50]  # Ensure max 50
        except Exception as e:
            print(f"⚠️ Direct Fyers method failed: {e}")
        
        # Method 2: NSE data (fallback)
        try:
            nse_symbols = self.get_nse_symbols_by_index('nifty50')
            if nse_symbols and len(nse_symbols) >= 40:
                print(f"✅ Using NSE Nifty50: {len(nse_symbols)} symbols")
                return nse_symbols[:50]
        except Exception as e:
            print(f"⚠️ NSE data method failed: {e}")
        
        # Method 3: Hardcoded fallback (last resort)
        fallback_symbols = self._get_fallback_symbols('nifty50')
        print(f"✅ Using fallback Nifty50: {len(fallback_symbols)} symbols")
        return fallback_symbols
    
    def get_nifty100_constituents(self) -> List[str]:
        """
        Get Nifty100 constituent symbols (100 stocks)
        Uses direct Fyers approach with fallback
        """
        # Method 1: Direct Fyers discovery (preferred)
        try:
            fyers_symbols = self.fyers_direct.get_nifty100_constituents()
            if fyers_symbols and len(fyers_symbols) >= 80:
                print(f"✅ Using direct Fyers Nifty100: {len(fyers_symbols)} symbols")
                return fyers_symbols[:100]
        except Exception as e:
            print(f"⚠️ Direct Fyers method failed: {e}")
        
        # Method 2: NSE data (fallback)
        try:
            nse_symbols = self.get_nse_symbols_by_index('nifty100')
            if nse_symbols and len(nse_symbols) >= 80:
                print(f"✅ Using NSE Nifty100: {len(nse_symbols)} symbols")
                return nse_symbols[:100]
        except Exception as e:
            print(f"⚠️ NSE data method failed: {e}")
        
        # Method 3: Combine Nifty50 + additional stocks (fallback)
        nifty50 = self.get_nifty50_constituents()
        additional_50 = [
            'NSE:GODREJCP-EQ', 'NSE:MARICO-EQ', 'NSE:DABUR-EQ',
            'NSE:PIDILITIND-EQ', 'NSE:UBL-EQ', 'NSE:COLPAL-EQ',
            'NSE:TORNTPHARM-EQ', 'NSE:BIOCON-EQ', 'NSE:LUPIN-EQ',
            'NSE:ALKEM-EQ', 'NSE:AUBANK-EQ', 'NSE:BANDHANBNK-EQ',
            'NSE:FEDERALBNK-EQ', 'NSE:IDFCFIRSTB-EQ', 'NSE:PNB-EQ',
            'NSE:BANKBARODA-EQ', 'NSE:CANBK-EQ', 'NSE:IOC-EQ',
            'NSE:HINDPETRO-EQ', 'NSE:GAIL-EQ', 'NSE:SAIL-EQ',
            'NSE:VEDL-EQ', 'NSE:NATIONALUM-EQ', 'NSE:NMDC-EQ',
            'NSE:AMBUJACEM-EQ', 'NSE:ACC-EQ', 'NSE:SHREECEM-EQ',
            'NSE:RAMCOCEM-EQ', 'NSE:AUROPHARMA-EQ', 'NSE:CONCOR-EQ',
            'NSE:ESCORT-EQ', 'NSE:ASHOKLEY-EQ', 'NSE:TVSMOTOR-EQ',
            'NSE:MOTHERSON-EQ', 'NSE:BALKRISIND-EQ', 'NSE:MRF-EQ',
            'NSE:APOLLOTYRE-EQ', 'NSE:BERGEPAINT-EQ', 'NSE:INDIGO-EQ',
            'NSE:DLF-EQ', 'NSE:GODREJPROP-EQ', 'NSE:OBEROIRLTY-EQ',
            'NSE:MPHASIS-EQ', 'NSE:COFORGE-EQ', 'NSE:LTTS-EQ',
            'NSE:PERSISTENT-EQ', 'NSE:MINDTREE-EQ', 'NSE:OFSS-EQ',
            'NSE:L&TFH-EQ', 'NSE:CHOLAFIN-EQ'
        ]
        
        combined = (nifty50 + additional_50)[:100]
        print(f"✅ Using combined Nifty100: {len(combined)} symbols")
        return combined
    
    def get_nifty200_constituents(self) -> List[str]:
        """
        Get Nifty200 constituent symbols (200 stocks) 
        Uses direct Fyers approach with fallback
        """
        # Method 1: Direct Fyers discovery (preferred)
        try:
            fyers_symbols = self.fyers_direct.get_nifty200_constituents()
            if fyers_symbols and len(fyers_symbols) >= 150:
                print(f"✅ Using direct Fyers Nifty200: {len(fyers_symbols)} symbols")
                return fyers_symbols[:200]
        except Exception as e:
            print(f"⚠️ Direct Fyers method failed: {e}")
        
        # Method 2: NSE data (fallback)
        try:
            nse_symbols = self.get_nse_symbols_by_index('nifty200')
            if nse_symbols and len(nse_symbols) >= 150:
                print(f"✅ Using NSE Nifty200: {len(nse_symbols)} symbols")
                return nse_symbols[:200]
        except Exception as e:
            print(f"⚠️ NSE data method failed: {e}")
        
        # Method 3: Combine Nifty100 + additional stocks (fallback)
        nifty100 = self.get_nifty100_constituents()
        
        # Add 100 more liquid stocks to complete Nifty200
        additional_100_symbols = [
            'NSE:ZEEL-EQ', 'NSE:PVR-EQ', 'NSE:INOXLEISUR-EQ',
            'NSE:ADANIGREEN-EQ', 'NSE:ADANIPOWER-EQ', 'NSE:ADANITRANS-EQ',
            'NSE:JINDALSTEL-EQ', 'NSE:RPOWER-EQ', 'NSE:TORNTPOWER-EQ',
            'NSE:SIEMENS-EQ', 'NSE:ABB-EQ', 'NSE:BHEL-EQ',
            'NSE:CROMPTON-EQ', 'NSE:HAVELLS-EQ', 'NSE:VOLTAS-EQ',
            'NSE:BLUESTARCO-EQ', 'NSE:WHIRLPOOL-EQ', 'NSE:JKCEMENT-EQ',
            'NSE:INDIACEM-EQ', 'NSE:ORIENT-EQ', 'NSE:JKPAPER-EQ',
            'NSE:BALRAMCHIN-EQ', 'NSE:CHAMBLFERT-EQ', 'NSE:COROMANDEL-EQ',
            'NSE:GNFC-EQ', 'NSE:GSFC-EQ', 'NSE:NFL-EQ',
            'NSE:RCF-EQ', 'NSE:SRF-EQ', 'NSE:TATACHEMICALS-EQ',
            'NSE:AJANTA-EQ', 'NSE:APLAPOLLO-EQ', 'NSE:AAVAS-EQ',
            'NSE:ABCAPITAL-EQ', 'NSE:ABFRL-EQ', 'NSE:ADANIGAS-EQ',
            'NSE:AIAENG-EQ', 'NSE:AJANTPHARM-EQ', 'NSE:AKZOINDIA-EQ',
            'NSE:ALKYLAMINE-EQ', 'NSE:ALLCARGO-EQ', 'NSE:AMARAJABAT-EQ',
            'NSE:APLLTD-EQ', 'NSE:ARVINDFASN-EQ', 'NSE:ASAHIINDIA-EQ',
            'NSE:ASTRAL-EQ', 'NSE:ATUL-EQ', 'NSE:AVANTIFEED-EQ',
            'NSE:BAJAJCON-EQ', 'NSE:BAJAJHLDNG-EQ', 'NSE:BATAINDIA-EQ',
            'NSE:BEL-EQ', 'NSE:BEML-EQ', 'NSE:BHARATFORG-EQ',
            'NSE:BIRLACORPN-EQ', 'NSE:BLUEDART-EQ', 'NSE:BOSCHLTD-EQ',
            'NSE:BSOFT-EQ', 'NSE:CANFINHOME-EQ', 'NSE:CAPLIPOINT-EQ',
            'NSE:CARBORUNIV-EQ', 'NSE:CASTROLIND-EQ', 'NSE:CCL-EQ',
            'NSE:CERA-EQ', 'NSE:CHEMCON-EQ', 'NSE:CHEMPLASTS-EQ',
            'NSE:CHENNPETRO-EQ', 'NSE:CHOLAHLDNG-EQ', 'NSE:CUB-EQ',
            'NSE:CUMMINSIND-EQ', 'NSE:CYIENT-EQ', 'NSE:DBREALTY-EQ',
            'NSE:DEEPAKFERT-EQ', 'NSE:DEEPAKNTR-EQ', 'NSE:DHANUKA-EQ',
            'NSE:DIXON-EQ', 'NSE:DMART-EQ', 'NSE:EDELWEISS-EQ',
            'NSE:EMAMILTD-EQ', 'NSE:ENDURANCE-EQ', 'NSE:ENGINERSIN-EQ',
            'NSE:EQUITAS-EQ', 'NSE:ERIS-EQ', 'NSE:ESABINDIA-EQ',
            'NSE:EXIDEIND-EQ', 'NSE:FDC-EQ', 'NSE:FINEORG-EQ',
            'NSE:FINCABLES-EQ', 'NSE:FORCEMOT-EQ', 'NSE:FORTIS-EQ',
            'NSE:GESHIP-EQ', 'NSE:GILLETTE-EQ', 'NSE:GLAXO-EQ',
            'NSE:GLENMARK-EQ', 'NSE:GMRINFRA-EQ', 'NSE:GODFRYPHLP-EQ',
            'NSE:GRANULES-EQ', 'NSE:GRAPHITE-EQ', 'NSE:GREAVESCOT-EQ',
            'NSE:GRINDWELL-EQ', 'NSE:GTLINFRA-EQ', 'NSE:GUJALKALI-EQ',
            'NSE:GUJGASLTD-EQ', 'NSE:GULFOILLUB-EQ', 'NSE:HAL-EQ',
            'NSE:HAPPSTMNDS-EQ', 'NSE:HATSUN-EQ', 'NSE:HCLTECH-EQ',
            'NSE:HEIDELBERG-EQ', 'NSE:HEXAWARE-EQ', 'NSE:HFCL-EQ',
            'NSE:HIMATSEIDE-EQ', 'NSE:HINDZINC-EQ', 'NSE:HOMEFIRST-EQ',
            'NSE:HONAUT-EQ', 'NSE:HUDCO-EQ', 'NSE:IBREALEST-EQ',
            'NSE:ICICIPRULI-EQ', 'NSE:IDEA-EQ', 'NSE:IDFC-EQ',
            'NSE:IDFCFIRSTB-EQ', 'NSE:IEX-EQ', 'NSE:IFBIND-EQ'
        ]
        
        combined = (nifty100 + additional_100_symbols)[:200]
        print(f"✅ Using combined Nifty200: {len(combined)} symbols")
        return combined
    
    def get_banknifty_constituents(self) -> List[str]:
        """Get BankNifty constituent symbols using direct Fyers approach"""
        # Method 1: Direct Fyers discovery (preferred)
        try:
            fyers_symbols = self.fyers_direct.get_bank_nifty_constituents()
            if fyers_symbols:
                print(f"✅ Using direct Fyers BankNifty: {len(fyers_symbols)} symbols")
                return fyers_symbols
        except Exception as e:
            print(f"⚠️ Direct Fyers method failed: {e}")
        
        # Method 2: Fallback to hardcoded list
        bank_symbols = [
            'NSE:HDFCBANK-EQ', 'NSE:ICICIBANK-EQ', 'NSE:AXISBANK-EQ',
            'NSE:KOTAKBANK-EQ', 'NSE:SBIN-EQ', 'NSE:INDUSINDBK-EQ',
            'NSE:BANKBARODA-EQ', 'NSE:PNB-EQ', 'NSE:FEDERALBNK-EQ',
            'NSE:IDFCFIRSTB-EQ', 'NSE:BANDHANBNK-EQ', 'NSE:AUBANK-EQ'
        ]
        print(f"✅ Using fallback BankNifty: {len(bank_symbols)} symbols")
        return bank_symbols
    
    def get_etf_symbols(self, etf_type: str = None) -> List[str]:
        """
        Get ETF symbols using direct Fyers approach
        
        Args:
            etf_type (str): ETF type filter (optional)
            
        Returns:
            List[str]: ETF symbols
        """
        # Method 1: Direct Fyers discovery (preferred)
        try:
            fyers_etfs = self.fyers_direct.get_popular_etfs()
            if etf_type:
                fyers_etfs = [etf for etf in fyers_etfs if etf_type.upper() in etf.upper()]
            if fyers_etfs:
                print(f"✅ Using direct Fyers ETFs: {len(fyers_etfs)} symbols")
                return fyers_etfs
        except Exception as e:
            print(f"⚠️ Direct Fyers ETF method failed: {e}")
        
        # Method 2: NSE data (fallback)
        try:
            nse_etfs = self.get_nse_etf_symbols(etf_type)
            if nse_etfs:
                print(f"✅ Using NSE ETFs: {len(nse_etfs)} symbols")
                return nse_etfs
        except Exception as e:
            print(f"⚠️ NSE ETF method failed: {e}")
        
        # Method 3: Hardcoded fallback
        fallback_etfs = [
            'NSE:NIFTYBEES-ETF',
            'NSE:BANKBEES-ETF', 
            'NSE:GOLDBEES-ETF'
        ]
        print(f"✅ Using fallback ETFs: {len(fallback_etfs)} symbols")
        return fallback_etfs
    
    def get_option_symbols(self, underlying: str, strike_count: int = 10) -> List[str]:
        """
        Get option symbols using direct Fyers optionchain API
        
        Args:
            underlying (str): Underlying symbol
            strike_count (int): Number of strikes to fetch
            
        Returns:
            List[str]: Option symbols
        """
        try:
            return self.fyers_direct.discover_option_symbols(underlying, strike_count)
        except Exception as e:
            print(f"❌ Error getting option symbols for {underlying}: {e}")
            return []
    
    def get_banknifty_constituents(self) -> List[str]:
        """Get BankNifty constituent symbols"""
        try:
            # Bank Nifty major constituents
            bank_symbols = [
                'NSE:HDFCBANK-EQ', 'NSE:ICICIBANK-EQ', 'NSE:AXISBANK-EQ',
                'NSE:KOTAKBANK-EQ', 'NSE:SBIN-EQ', 'NSE:INDUSINDBK-EQ',
                'NSE:BANKBARODA-EQ', 'NSE:PNB-EQ', 'NSE:FEDERALBNK-EQ',
                'NSE:IDFCFIRSTB-EQ', 'NSE:BANDHANBNK-EQ', 'NSE:AUBANK-EQ'
            ]
            
            # Validate and return active symbols
            active_symbols = []
            for symbol in bank_symbols:
                if self._is_symbol_active(symbol):
                    active_symbols.append(symbol)
            
            return active_symbols
            
        except Exception as e:
            print(f"Error fetching BankNifty constituents: {e}")
            return [
                'NSE:HDFCBANK-EQ', 'NSE:ICICIBANK-EQ', 'NSE:AXISBANK-EQ',
                'NSE:KOTAKBANK-EQ', 'NSE:SBIN-EQ'
            ]
    
    def get_active_option_symbols(self, underlying: str) -> List[str]:
        """
        Get active option symbols for an underlying
        
        Args:
            underlying (str): Underlying symbol (e.g., 'NSE:NIFTY50-INDEX')
            
        Returns:
            List[str]: List of active option symbols
        """
        try:
            data = {
                'symbol': underlying,
                'strikecount': 20,
                'timestamp': ''
            }
            
            result = self.fyers.fyers_model.optionchain(data=data)
            
            if result.get('s') == 'ok' and 'data' in result:
                option_symbols = []
                
                # Extract option symbols from chain data
                if 'optionsChain' in result['data']:
                    for option_data in result['data']['optionsChain']:
                        if 'symbol' in option_data:
                            option_symbols.append(option_data['symbol'])
                
                return option_symbols[:50]  # Limit to 50 most active
                
        except Exception as e:
            print(f"Error fetching option symbols for {underlying}: {e}")
            return []
    
    def discover_all_symbols(self) -> Dict[str, List[str]]:
        """
        Discover all available symbols across different categories
        
        Returns:
            Dict[str, List[str]]: Dictionary with symbol categories
        """
        print("🔍 Discovering symbols across all categories...")
        
        symbols = {
            'indices': list(self.index_symbols.values()),
            'nifty50_stocks': self.get_nifty50_constituents(),
            'nifty100_stocks': self.get_nifty100_constituents(),
            'nifty200_stocks': self.get_nifty200_constituents(),
            'banknifty_stocks': self.get_banknifty_constituents(),
            'nifty50_options': self.get_active_option_symbols('NSE:NIFTY50-INDEX'),
            'banknifty_options': self.get_active_option_symbols('NSE:NIFTYBANK-INDEX')
        }
        
        # Add metadata
        total_symbols = sum(len(v) for v in symbols.values() if isinstance(v, list))
        symbols['metadata'] = {
            'last_updated': datetime.now().isoformat(),
            'total_symbols': total_symbols,
            'discovery_method': 'fyers_api_dynamic_enhanced',
            'categories': {
                'indices': len(symbols['indices']),
                'nifty50_stocks': len(symbols['nifty50_stocks']),
                'nifty100_stocks': len(symbols['nifty100_stocks']),
                'nifty200_stocks': len(symbols['nifty200_stocks']),
                'banknifty_stocks': len(symbols['banknifty_stocks']),
                'nifty50_options': len(symbols['nifty50_options']),
                'banknifty_options': len(symbols['banknifty_options'])
            }
        }
        
        print(f"📊 Discovery Summary:")
        for category, count in symbols['metadata']['categories'].items():
            print(f"  {category}: {count} symbols")
        
        return symbols
    
    def save_symbol_universe(self, symbols: Dict[str, List[str]]) -> None:
        """
        Save discovered symbols to Parquet file
        
        Args:
            symbols (Dict): Symbol universe dictionary
        """
        try:
            # Convert to DataFrame for easy storage
            symbol_records = []
            
            for category, symbol_list in symbols.items():
                if isinstance(symbol_list, list):
                    for symbol in symbol_list:
                        symbol_records.append({
                            'symbol': symbol,
                            'category': category,
                            'exchange': symbol.split(':')[0] if ':' in symbol else 'NSE',
                            'instrument': symbol.split(':')[1] if ':' in symbol else symbol,
                            'last_updated': datetime.now(),
                            'is_active': True
                        })
            
            df = pd.DataFrame(symbol_records)
            
            # Save to Parquet
            symbol_file = self.symbols_dir / "active_symbols.parquet"
            df.to_parquet(symbol_file, compression='snappy', index=False)
            
            # Also save metadata
            metadata_file = self.symbols_dir / "symbol_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(symbols.get('metadata', {}), f, indent=2)
            
            print(f"✅ Saved {len(symbol_records)} symbols to {symbol_file}")
            
        except Exception as e:
            print(f"❌ Error saving symbol universe: {e}")
    
    def load_symbol_universe(self) -> Optional[Dict[str, List[str]]]:
        """
        Load previously discovered symbols from Parquet file
        
        Returns:
            Optional[Dict]: Symbol universe or None if not found
        """
        try:
            symbol_file = self.symbols_dir / "active_symbols.parquet"
            
            if not symbol_file.exists():
                return None
            
            df = pd.read_parquet(symbol_file)
            
            # Convert back to dictionary format
            symbols = {}
            for category in df['category'].unique():
                category_symbols = df[df['category'] == category]['symbol'].tolist()
                symbols[category] = category_symbols
            
            # Check if data is fresh (less than 1 day old)
            latest_update = df['last_updated'].max()
            if datetime.now() - latest_update > timedelta(days=1):
                print("⚠️ Symbol data is more than 1 day old, consider refreshing")
            
            return symbols
            
        except Exception as e:
            print(f"❌ Error loading symbol universe: {e}")
            return None
    
    def refresh_symbol_universe(self, force_refresh: bool = False) -> Dict[str, List[str]]:
        """
        Refresh symbol universe (discover new symbols)
        
        Args:
            force_refresh (bool): Force refresh even if data is recent
            
        Returns:
            Dict[str, List[str]]: Updated symbol universe
        """
        # Try loading existing data first
        existing_symbols = self.load_symbol_universe()
        
        if existing_symbols and not force_refresh:
            print("✅ Using cached symbol data (use force_refresh=True to update)")
            return existing_symbols
        
        print("🔄 Discovering symbols from Fyers API...")
        
        # Discover new symbols
        symbols = self.discover_all_symbols()
        
        # Save for future use
        self.save_symbol_universe(symbols)
        
        return symbols
    
    def get_symbol_metadata(self, symbol: str) -> Optional[Dict]:
        """
        Get metadata for a specific symbol
        
        Args:
            symbol (str): Symbol to get metadata for
            
        Returns:
            Optional[Dict]: Symbol metadata or None
        """
        try:
            # Get basic quote to extract metadata
            quotes = self.fyers.get_quotes({'symbols': symbol})
            
            if quotes.get('s') == 'ok' and 'd' in quotes:
                quote_data = quotes['d'][0]['v']
                
                metadata = {
                    'symbol': symbol,
                    'last_price': quote_data.get('lp', 0),
                    'volume': quote_data.get('vol', 0),
                    'change_percent': quote_data.get('chp', 0),
                    'high': quote_data.get('h', 0),
                    'low': quote_data.get('l', 0),
                    'open': quote_data.get('o', 0),
                    'prev_close': quote_data.get('prev_close_price', 0),
                    'last_updated': datetime.now()
                }
                
                return metadata
                
        except Exception as e:
            print(f"Error getting metadata for {symbol}: {e}")
            return None
    
    def _is_symbol_active(self, symbol: str) -> bool:
        """
        Check if a symbol is actively trading (simplified for performance)
        
        Args:
            symbol (str): Symbol to check
            
        Returns:
            bool: True if symbol is active
        """
        try:
            # Quick validation - just check if quotes return successfully
            quotes = self.fyers.get_quotes({'symbols': symbol})
            return quotes.get('s') == 'ok' and 'd' in quotes and len(quotes['d']) > 0
        except:
            return False


def get_symbol_discovery() -> SymbolDiscovery:
    """Get Symbol Discovery instance (singleton pattern)"""
    return SymbolDiscovery()


if __name__ == "__main__":
    # Test symbol discovery
    discovery = SymbolDiscovery()
    
    print("🔍 Testing Symbol Discovery...")
    
    # Test Nifty50 constituents
    nifty_symbols = discovery.get_nifty50_constituents()
    print(f"📈 Found {len(nifty_symbols)} Nifty50 constituents")
    
    # Test BankNifty constituents  
    bank_symbols = discovery.get_banknifty_constituents()
    print(f"🏦 Found {len(bank_symbols)} BankNifty constituents")
    
    # Discover and save complete universe
    universe = discovery.refresh_symbol_universe()
    total_symbols = universe.get('metadata', {}).get('total_symbols', 0)
    print(f"🌌 Complete symbol universe: {total_symbols} symbols")
    
    # Test loading saved data
    loaded_universe = discovery.load_symbol_universe()
    if loaded_universe:
        print(f"💾 Loaded {len(loaded_universe)} symbol categories from cache")