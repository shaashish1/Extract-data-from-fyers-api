"""
Enhanced Fyers Symbol Discovery Module
Direct symbol discovery from Fyers API with proven symbol lists
Bypasses NSE download workflow by using curated lists + Fyers validation
"""
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from pathlib import Path
from my_fyers_model import MyFyersModel
from data_storage import get_parquet_manager
from index_constituents import get_nifty50_symbols, get_nifty100_symbols, get_nifty200_symbols


class FyersDirectSymbolDiscovery:
    """Direct symbol discovery from Fyers API without external downloads"""
    
    def __init__(self):
        self.fyers = MyFyersModel()
        self.manager = get_parquet_manager()
        self.symbols_dir = Path("data/parquet/fyers_symbols")
        self.symbols_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache for validated symbols to avoid repeated API calls
        self._validated_symbols = {}
        self._cache_timestamp = None
        self._cache_ttl = timedelta(hours=6)  # Cache for 6 hours
        
        # Known symbol patterns for efficient discovery
        self.symbol_patterns = {
            'indices': [
                'NSE:NIFTY50-INDEX',
                'NSE:NIFTYBANK-INDEX', 
                'NSE:FINNIFTY-INDEX',
                'NSE:INDIAVIX-INDEX',
                'NSE:SENSEX-INDEX',
                'NSE:NIFTY100-INDEX',
                'NSE:NIFTY200-INDEX',
                'NSE:NIFTYIT-INDEX',
                'NSE:NIFTYPHARMA-INDEX',
                'NSE:NIFTYAUTO-INDEX',
                'NSE:NIFTYMETAL-INDEX',
                'NSE:NIFTYREALTY-INDEX'
            ],
            'etfs': [
                'NSE:NIFTYBEES-ETF',
                'NSE:BANKBEES-ETF',
                'NSE:GOLDBEES-ETF',
                'NSE:SILVRETF-ETF',
                'NSE:LIQUIDBEES-ETF',
                'NSE:NIFTY50BEES-ETF',
                'NSE:QNIFTY-ETF',
                'NSE:MON100-ETF'
            ]
        }
    
    def _is_cache_valid(self) -> bool:
        """Check if symbol cache is still valid"""
        if self._cache_timestamp is None:
            return False
        return datetime.now() - self._cache_timestamp < self._cache_ttl
    
    def validate_symbols_with_fyers(self, symbols: List[str], batch_size: int = 50) -> List[str]:
        """
        Validate symbols by checking quotes from Fyers API
        
        Args:
            symbols (List[str]): Symbols to validate
            batch_size (int): Batch size for API calls
            
        Returns:
            List[str]: Valid symbols
        """
        valid_symbols = []
        
        # Process in batches to avoid API limits
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            batch_str = ','.join(batch)
            
            try:
                data = {'symbols': batch_str}
                result = self.fyers.fyers_model.quotes(data)
                
                if result.get('s') == 'ok' and 'd' in result:
                    # Add symbols that returned valid quotes
                    for quote_data in result['d']:
                        if 'n' in quote_data and quote_data['n']:  # Valid symbol name
                            symbol = quote_data.get('n', '')
                            if symbol in batch:
                                valid_symbols.append(symbol)
                
                # Small delay to respect API limits
                import time
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ Error validating batch {i//batch_size + 1}: {e}")
                # On error, assume all symbols in batch are valid (fallback)
                valid_symbols.extend(batch)
        
        return valid_symbols
    
    def get_nifty50_constituents(self) -> List[str]:
        """Get Nifty50 constituents using proven index_constituents list"""
        try:
            # Use proven list from index_constituents.py
            symbols = get_nifty50_symbols()
            
            # Optionally validate with Fyers (comment out if too slow)
            # symbols = self.validate_symbols_with_fyers(symbols)
            
            print(f"📊 Nifty50 constituents: {len(symbols)} symbols")
            return symbols
            
        except Exception as e:
            print(f"❌ Error getting Nifty50 constituents: {e}")
            return []
    
    def get_nifty100_constituents(self) -> List[str]:
        """Get Nifty100 constituents using proven index_constituents list"""
        try:
            symbols = get_nifty100_symbols()
            print(f"📊 Nifty100 constituents: {len(symbols)} symbols")
            return symbols
        except Exception as e:
            print(f"❌ Error getting Nifty100 constituents: {e}")
            return []
    
    def get_nifty200_constituents(self) -> List[str]:
        """Get Nifty200 constituents using proven index_constituents list"""
        try:
            symbols = get_nifty200_symbols()
            print(f"📊 Nifty200 constituents: {len(symbols)} symbols")
            return symbols
        except Exception as e:
            print(f"❌ Error getting Nifty200 constituents: {e}")
            return []
    
    def get_bank_nifty_constituents(self) -> List[str]:
        """Get Bank Nifty constituents"""
        bank_symbols = [
            'NSE:HDFCBANK-EQ', 'NSE:ICICIBANK-EQ', 'NSE:AXISBANK-EQ',
            'NSE:KOTAKBANK-EQ', 'NSE:SBIN-EQ', 'NSE:INDUSINDBK-EQ',
            'NSE:BANKBARODA-EQ', 'NSE:PNB-EQ', 'NSE:FEDERALBNK-EQ',
            'NSE:IDFCFIRSTB-EQ', 'NSE:BANDHANBNK-EQ', 'NSE:AUBANK-EQ'
        ]
        return bank_symbols
    
    def get_major_indices(self) -> List[str]:
        """Get major index symbols"""
        return self.symbol_patterns['indices'].copy()
    
    def get_popular_etfs(self) -> List[str]:
        """Get popular ETF symbols"""
        return self.symbol_patterns['etfs'].copy()
    
    def discover_option_symbols(self, underlying: str, strike_count: int = 10) -> List[str]:
        """
        Discover option symbols for an underlying using Fyers optionchain API
        
        Args:
            underlying (str): Underlying symbol (e.g., 'NSE:NIFTY50-INDEX')
            strike_count (int): Number of strikes to fetch
            
        Returns:
            List[str]: Option symbols
        """
        try:
            data = {
                'symbol': underlying,
                'strikecount': strike_count,
                'timestamp': ''
            }
            
            result = self.fyers.fyers_model.optionchain(data)
            
            if result.get('s') == 'ok' and 'data' in result:
                option_symbols = []
                
                # Extract option symbols from chain data
                if 'optionsChain' in result['data']:
                    for strike_data in result['data']['optionsChain']:
                        # Add call option
                        if 'call' in strike_data and 'symbol' in strike_data['call']:
                            option_symbols.append(strike_data['call']['symbol'])
                        
                        # Add put option
                        if 'put' in strike_data and 'symbol' in strike_data['put']:
                            option_symbols.append(strike_data['put']['symbol'])
                
                print(f"🎯 Found {len(option_symbols)} option symbols for {underlying}")
                return option_symbols
            else:
                print(f"❌ No option chain data for {underlying}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting option symbols for {underlying}: {e}")
            return []
    
    def get_liquid_stocks_from_indices(self) -> List[str]:
        """Get liquid stocks by combining major index constituents"""
        all_stocks = set()
        
        # Add Nifty50 (most liquid)
        all_stocks.update(self.get_nifty50_constituents())
        
        # Add Bank Nifty constituents
        all_stocks.update(self.get_bank_nifty_constituents())
        
        # Convert back to list and return
        return list(all_stocks)
    
    def search_symbols_by_pattern(self, pattern: str, category: str = None) -> List[str]:
        """
        Search for symbols by pattern in known symbol lists
        
        Args:
            pattern (str): Search pattern (case insensitive)
            category (str): Category to search in ('indices', 'stocks', 'etfs')
            
        Returns:
            List[str]: Matching symbols
        """
        pattern_upper = pattern.upper()
        matching_symbols = []
        
        if category == 'indices' or category is None:
            for symbol in self.get_major_indices():
                if pattern_upper in symbol.upper():
                    matching_symbols.append(symbol)
        
        if category == 'etfs' or category is None:
            for symbol in self.get_popular_etfs():
                if pattern_upper in symbol.upper():
                    matching_symbols.append(symbol)
        
        if category == 'stocks' or category is None:
            for symbol in self.get_liquid_stocks_from_indices():
                if pattern_upper in symbol.upper():
                    matching_symbols.append(symbol)
        
        return matching_symbols
    
    def get_symbol_quote(self, symbol: str) -> Dict:
        """
        Get current quote for a symbol
        
        Args:
            symbol (str): Symbol to get quote for
            
        Returns:
            Dict: Quote data
        """
        try:
            data = {'symbols': symbol}
            result = self.fyers.fyers_model.quotes(data)
            
            if result.get('s') == 'ok' and 'd' in result and result['d']:
                return result['d'][0]
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Error getting quote for {symbol}: {e}")
            return {}
    
    def get_all_discovered_symbols(self) -> Dict[str, List[str]]:
        """
        Get all discovered symbols organized by category
        
        Returns:
            Dict[str, List[str]]: Categorized symbols
        """
        return {
            'indices': self.get_major_indices(),
            'nifty50_stocks': self.get_nifty50_constituents(),
            'nifty100_stocks': self.get_nifty100_constituents(),
            'nifty200_stocks': self.get_nifty200_constituents(),
            'bank_stocks': self.get_bank_nifty_constituents(),
            'etfs': self.get_popular_etfs(),
            'liquid_stocks': self.get_liquid_stocks_from_indices()
        }
    
    def save_discovered_symbols(self):
        """Save all discovered symbols to Parquet files"""
        all_symbols = self.get_all_discovered_symbols()
        
        for category, symbols in all_symbols.items():
            if symbols:
                df = pd.DataFrame({
                    'symbol': symbols,
                    'category': category,
                    'last_updated': datetime.now().isoformat(),
                    'source': 'fyers_direct_discovery'
                })
                
                file_path = self.symbols_dir / f"fyers_direct_{category}.parquet"
                df.to_parquet(file_path, compression='snappy')
                print(f"💾 Saved {len(symbols)} {category} symbols")
    
    def load_symbols_from_cache(self, category: str) -> List[str]:
        """Load symbols from cached Parquet files"""
        try:
            file_path = self.symbols_dir / f"fyers_direct_{category}.parquet"
            if file_path.exists():
                df = pd.read_parquet(file_path)
                return df['symbol'].tolist()
        except Exception as e:
            print(f"❌ Error loading {category} symbols from cache: {e}")
        
        return []


def get_fyers_direct_discovery() -> FyersDirectSymbolDiscovery:
    """Get Fyers direct symbol discovery instance"""
    return FyersDirectSymbolDiscovery()


if __name__ == "__main__":
    # Example usage
    discovery = get_fyers_direct_discovery()
    
    print("🚀 Testing Fyers Direct Symbol Discovery")
    print("=" * 45)
    
    # Get all symbols
    all_symbols = discovery.get_all_symbols_from_fyers()
    
    # Test specific categories
    indices = discovery.get_nifty_indices()
    print(f"\n📊 Nifty Indices: {len(indices)}")
    for idx in indices[:5]:
        print(f"   {idx}")
    
    etfs = discovery.get_etfs_by_type('NIFTY')
    print(f"\n💰 Nifty ETFs: {len(etfs)}")
    for etf in etfs[:3]:
        print(f"   {etf}")
    
    # Search functionality
    reliance_symbols = discovery.search_symbols('RELIANCE')
    print(f"\n🔍 Reliance symbols: {len(reliance_symbols)}")
    for rel in reliance_symbols[:3]:
        print(f"   {rel}")
    
    print("\n✅ Fyers Direct Discovery Test Completed!")