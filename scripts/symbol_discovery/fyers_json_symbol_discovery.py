"""
Fyers JSON-based Symbol Discovery
==================================

Direct integration with Fyers official JSON symbol master endpoints.
No local storage required - fetches real-time symbol data on demand.

Official Fyers JSON Endpoints:
- NSE Capital Market: https://public.fyers.in/sym_details/NSE_CM_sym_master.json
- NSE Futures & Options: https://public.fyers.in/sym_details/NSE_FO_sym_master.json
- NSE Currency Derivatives: https://public.fyers.in/sym_details/NSE_CD_sym_master.json
- NSE Commodity: https://public.fyers.in/sym_details/NSE_COM_sym_master.json
- BSE Capital Market: https://public.fyers.in/sym_details/BSE_CM_sym_master.json
- BSE Futures & Options: https://public.fyers.in/sym_details/BSE_FO_sym_master.json
- MCX Commodity: https://public.fyers.in/sym_details/MCX_COM_sym_master.json

Author: Fyers Trading Platform
Created: October 28, 2025
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.auth.my_fyers_model import MyFyersModel


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SymbolInfo:
    """Comprehensive symbol information from Fyers JSON master."""
    fytoken: str
    symbol_ticker: str
    exchange_name: str
    symbol_desc: str
    exchange: int
    segment: int
    ex_symbol: str
    ex_token: int
    isin: str = ""
    ex_series: str = ""
    opt_type: str = "XX"
    underlying_symbol: str = ""
    underlying_fytoken: str = ""
    strike_price: float = 0.0
    expiry_date: str = ""
    min_lot_size: int = 1
    tick_size: float = 0.05
    trading_session: str = ""
    last_update: str = ""
    is_tradeable: bool = True
    is_mtf_tradable: int = 0
    mtf_margin: float = 0.0
    instrument_type: int = 0
    currency_code: str = "INR"
    upper_circuit: float = 0.0
    lower_circuit: float = 0.0
    previous_close: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.symbol_ticker} - {self.symbol_desc} ({self.exchange_name})"


class FyersJSONSymbolDiscovery:
    """
    Fyers JSON-based Symbol Discovery System
    
    Features:
    - Direct JSON API integration (no local storage)
    - Real-time symbol data from Fyers
    - Fast search across all segments
    - Category-wise symbol organization
    - 156K+ symbols support
    """
    
    # Official Fyers JSON endpoints
    JSON_ENDPOINTS = {
        "NSE_CM": "https://public.fyers.in/sym_details/NSE_CM_sym_master.json",
        "NSE_FO": "https://public.fyers.in/sym_details/NSE_FO_sym_master.json",
        "NSE_CD": "https://public.fyers.in/sym_details/NSE_CD_sym_master.json",
        "NSE_COM": "https://public.fyers.in/sym_details/NSE_COM_sym_master.json",
        "BSE_CM": "https://public.fyers.in/sym_details/BSE_CM_sym_master.json",
        "BSE_FO": "https://public.fyers.in/sym_details/BSE_FO_sym_master.json",
        "MCX_COM": "https://public.fyers.in/sym_details/MCX_COM_sym_master.json"
    }
    
    # Exchange and segment mappings
    EXCHANGE_NAMES = {10: "NSE", 11: "MCX", 12: "BSE"}
    SEGMENT_NAMES = {10: "Capital Market", 11: "F&O", 12: "Currency", 20: "Commodity"}
    
    def __init__(self):
        """Initialize the discovery system."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Cache for downloaded data (valid for current session only)
        self._cache: Dict[str, Dict] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        
        logger.info("Fyers JSON Symbol Discovery initialized")
    
    def fetch_symbols(self, segment: str, use_cache: bool = True) -> Dict[str, Dict]:
        """
        Fetch symbols from Fyers JSON endpoint.
        
        Args:
            segment: Segment key (NSE_CM, NSE_FO, etc.)
            use_cache: Use cached data if available
        
        Returns:
            Dictionary with symbol_ticker as key and symbol data as value
        """
        if segment not in self.JSON_ENDPOINTS:
            raise ValueError(f"Invalid segment: {segment}. Valid: {list(self.JSON_ENDPOINTS.keys())}")
        
        # Check cache
        if use_cache and segment in self._cache:
            logger.info(f"Using cached data for {segment}")
            return self._cache[segment]
        
        url = self.JSON_ENDPOINTS[segment]
        logger.info(f"Fetching symbols from {segment}: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched {len(data)} symbols from {segment}")
            
            # Cache the data
            self._cache[segment] = data
            self._cache_timestamp[segment] = datetime.now()
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {segment}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON for {segment}: {e}")
            raise
    
    def fetch_all_symbols(self, use_cache: bool = True) -> Dict[str, Dict[str, Dict]]:
        """
        Fetch symbols from all segments.
        
        Args:
            use_cache: Use cached data if available
        
        Returns:
            Dictionary with segment as key and symbols dict as value
        """
        all_symbols = {}
        
        for segment in self.JSON_ENDPOINTS.keys():
            try:
                symbols = self.fetch_symbols(segment, use_cache)
                all_symbols[segment] = symbols
            except Exception as e:
                logger.error(f"Failed to fetch {segment}: {e}")
                all_symbols[segment] = {}
        
        total = sum(len(symbols) for symbols in all_symbols.values())
        logger.info(f"Total symbols fetched: {total:,}")
        
        return all_symbols
    
    def parse_symbol_info(self, symbol_ticker: str, symbol_data: Dict) -> SymbolInfo:
        """
        Parse symbol data into SymbolInfo object.
        
        Args:
            symbol_ticker: Symbol ticker (e.g., "NSE:SBIN-EQ")
            symbol_data: Raw symbol data from JSON
        
        Returns:
            SymbolInfo object
        """
        return SymbolInfo(
            fytoken=symbol_data.get('fyToken', ''),
            symbol_ticker=symbol_ticker,
            exchange_name=symbol_data.get('exchangeName', ''),
            symbol_desc=symbol_data.get('symbolDesc', ''),
            exchange=symbol_data.get('exchange', 0),
            segment=symbol_data.get('segment', 0),
            ex_symbol=symbol_data.get('exSymbol', ''),
            ex_token=symbol_data.get('exToken', 0),
            isin=symbol_data.get('isin', ''),
            ex_series=symbol_data.get('exSeries', ''),
            opt_type=symbol_data.get('optType', 'XX'),
            underlying_symbol=symbol_data.get('underSym', ''),
            underlying_fytoken=symbol_data.get('underFyTok', ''),
            strike_price=symbol_data.get('strikePrice', 0.0),
            expiry_date=symbol_data.get('expiryDate', ''),
            min_lot_size=symbol_data.get('minLotSize', 1),
            tick_size=symbol_data.get('tickSize', 0.05),
            trading_session=symbol_data.get('tradingSession', ''),
            last_update=symbol_data.get('lastUpdate', ''),
            is_tradeable=symbol_data.get('tradeStatus', 1) == 1,
            is_mtf_tradable=symbol_data.get('is_mtf_tradable', 0),
            mtf_margin=symbol_data.get('mtf_margin', 0.0),
            instrument_type=symbol_data.get('exInstType', 0),
            currency_code=symbol_data.get('currencyCode', 'INR'),
            upper_circuit=symbol_data.get('upperPrice', 0.0),
            lower_circuit=symbol_data.get('lowerPrice', 0.0),
            previous_close=symbol_data.get('previousClose', 0.0)
        )
    
    def search_symbol(self, query: str, segment: Optional[str] = None, 
                     max_results: int = 50) -> List[SymbolInfo]:
        """
        Search for symbols matching the query.
        
        Args:
            query: Search query (symbol ticker, name, ISIN, etc.)
            segment: Optional segment filter (NSE_CM, NSE_FO, etc.)
            max_results: Maximum results to return
        
        Returns:
            List of matching SymbolInfo objects
        """
        query = query.upper().strip()
        results = []
        
        # Determine which segments to search
        segments_to_search = [segment] if segment else list(self.JSON_ENDPOINTS.keys())
        
        for seg in segments_to_search:
            try:
                symbols = self.fetch_symbols(seg)
                
                for ticker, data in symbols.items():
                    # Search in multiple fields
                    ticker_upper = ticker.upper()
                    desc_upper = data.get('symbolDesc', '').upper()
                    ex_symbol_upper = data.get('exSymbol', '').upper()
                    isin_upper = data.get('isin', '').upper()
                    
                    if (query in ticker_upper or 
                        query in desc_upper or 
                        query in ex_symbol_upper or
                        query in isin_upper):
                        
                        symbol_info = self.parse_symbol_info(ticker, data)
                        results.append(symbol_info)
                        
                        if len(results) >= max_results:
                            break
                
                if len(results) >= max_results:
                    break
                    
            except Exception as e:
                logger.error(f"Error searching {seg}: {e}")
                continue
        
        logger.info(f"Found {len(results)} results for query: {query}")
        return results
    
    def get_symbol_by_ticker(self, ticker: str) -> Optional[SymbolInfo]:
        """
        Get symbol information by exact ticker match.
        
        Args:
            ticker: Exact symbol ticker (e.g., "NSE:SBIN-EQ")
        
        Returns:
            SymbolInfo object or None
        """
        ticker = ticker.upper().strip()
        
        # Try to determine segment from ticker
        if ticker.startswith("NSE:"):
            if "-EQ" in ticker or "-BE" in ticker:
                segments = ["NSE_CM"]
            elif "FUT" in ticker or "CE" in ticker or "PE" in ticker:
                segments = ["NSE_FO"]
            elif "INR" in ticker:
                segments = ["NSE_CD"]
            else:
                segments = ["NSE_CM", "NSE_FO", "NSE_CD"]
        elif ticker.startswith("BSE:"):
            segments = ["BSE_CM", "BSE_FO"]
        elif ticker.startswith("MCX:"):
            segments = ["MCX_COM"]
        else:
            segments = list(self.JSON_ENDPOINTS.keys())
        
        for segment in segments:
            try:
                symbols = self.fetch_symbols(segment)
                
                if ticker in symbols:
                    return self.parse_symbol_info(ticker, symbols[ticker])
                    
            except Exception as e:
                logger.error(f"Error getting symbol from {segment}: {e}")
                continue
        
        logger.warning(f"Symbol not found: {ticker}")
        return None
    
    def get_symbols_by_exchange(self, exchange: str) -> List[SymbolInfo]:
        """
        Get all symbols from a specific exchange.
        
        Args:
            exchange: Exchange name (NSE, BSE, MCX)
        
        Returns:
            List of SymbolInfo objects
        """
        exchange = exchange.upper()
        segment_map = {
            "NSE": ["NSE_CM", "NSE_FO", "NSE_CD", "NSE_COM"],
            "BSE": ["BSE_CM", "BSE_FO"],
            "MCX": ["MCX_COM"]
        }
        
        if exchange not in segment_map:
            raise ValueError(f"Invalid exchange: {exchange}. Valid: NSE, BSE, MCX")
        
        results = []
        for segment in segment_map[exchange]:
            try:
                symbols = self.fetch_symbols(segment)
                for ticker, data in symbols.items():
                    symbol_info = self.parse_symbol_info(ticker, data)
                    results.append(symbol_info)
            except Exception as e:
                logger.error(f"Error fetching {segment}: {e}")
        
        logger.info(f"Found {len(results)} symbols for {exchange}")
        return results
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get symbol count statistics.
        
        Returns:
            Dictionary with segment-wise counts
        """
        stats = {}
        all_symbols = self.fetch_all_symbols()
        
        for segment, symbols in all_symbols.items():
            stats[segment] = len(symbols)
        
        stats['TOTAL'] = sum(stats.values())
        
        return stats
    
    def clear_cache(self):
        """Clear the symbol cache."""
        self._cache.clear()
        self._cache_timestamp.clear()
        logger.info("Cache cleared")


def interactive_search():
    """Interactive search interface."""
    print("\n" + "="*80)
    print("Fyers JSON Symbol Discovery - Interactive Search")
    print("="*80)
    
    discovery = FyersJSONSymbolDiscovery()
    
    while True:
        print("\n" + "-"*80)
        print("Options:")
        print("1. Search for symbol")
        print("2. Get symbol by exact ticker")
        print("3. View statistics")
        print("4. Get symbols by exchange")
        print("5. Clear cache and refresh data")
        print("0. Exit")
        print("-"*80)
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            query = input("Enter search query (symbol, name, ISIN): ").strip()
            if query:
                results = discovery.search_symbol(query, max_results=20)
                
                if results:
                    print(f"\nFound {len(results)} results:")
                    print("-"*80)
                    for i, symbol in enumerate(results, 1):
                        print(f"{i}. {symbol.symbol_ticker}")
                        print(f"   Name: {symbol.symbol_desc}")
                        print(f"   Exchange: {symbol.exchange_name} | Segment: {discovery.SEGMENT_NAMES.get(symbol.segment, 'Unknown')}")
                        print(f"   ISIN: {symbol.isin} | Lot Size: {symbol.min_lot_size} | Tick: {symbol.tick_size}")
                        print()
                else:
                    print("\nNo symbols found matching your query.")
        
        elif choice == "2":
            ticker = input("Enter exact symbol ticker (e.g., NSE:SBIN-EQ): ").strip()
            if ticker:
                symbol = discovery.get_symbol_by_ticker(ticker)
                
                if symbol:
                    print("\nSymbol Details:")
                    print("-"*80)
                    print(f"Ticker: {symbol.symbol_ticker}")
                    print(f"Name: {symbol.symbol_desc}")
                    print(f"FyToken: {symbol.fytoken}")
                    print(f"Exchange: {symbol.exchange_name} ({symbol.exchange})")
                    print(f"Segment: {discovery.SEGMENT_NAMES.get(symbol.segment, 'Unknown')} ({symbol.segment})")
                    print(f"ISIN: {symbol.isin}")
                    print(f"Instrument Type: {symbol.instrument_type}")
                    print(f"Lot Size: {symbol.min_lot_size}")
                    print(f"Tick Size: {symbol.tick_size}")
                    print(f"Trading Session: {symbol.trading_session}")
                    print(f"Previous Close: {symbol.previous_close}")
                    print(f"Circuit Limits: {symbol.lower_circuit} - {symbol.upper_circuit}")
                    print(f"Is Tradeable: {symbol.is_tradeable}")
                    print(f"MTF Available: {symbol.is_mtf_tradable == 1}")
                    if symbol.is_mtf_tradable:
                        print(f"MTF Margin: {symbol.mtf_margin}x")
                    print()
                else:
                    print("\nSymbol not found.")
        
        elif choice == "3":
            print("\nFetching statistics...")
            stats = discovery.get_statistics()
            
            print("\nSymbol Count by Segment:")
            print("-"*80)
            for segment, count in sorted(stats.items()):
                if segment != 'TOTAL':
                    print(f"{segment:15} : {count:>8,} symbols")
            print("-"*80)
            print(f"{'TOTAL':15} : {stats['TOTAL']:>8,} symbols")
            print()
        
        elif choice == "4":
            exchange = input("Enter exchange (NSE/BSE/MCX): ").strip().upper()
            if exchange in ["NSE", "BSE", "MCX"]:
                print(f"\nFetching all {exchange} symbols...")
                symbols = discovery.get_symbols_by_exchange(exchange)
                print(f"Found {len(symbols):,} symbols")
                
                # Show first 10
                print("\nFirst 10 symbols:")
                print("-"*80)
                for symbol in symbols[:10]:
                    print(f"{symbol.symbol_ticker:30} - {symbol.symbol_desc}")
            else:
                print("Invalid exchange. Use NSE, BSE, or MCX.")
        
        elif choice == "5":
            discovery.clear_cache()
            print("\nCache cleared. Next operation will fetch fresh data.")
        
        elif choice == "0":
            print("\nExiting...")
            break
        
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    interactive_search()
