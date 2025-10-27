"""
Enhanced Symbol Discovery Module
Fixed to provide complete symbol lists and better error handling
"""
import pandas as pd
import requests
import json
import time
from typing import List, Dict, Optional
from pathlib import Path
from index_constituents import (
    get_nifty50_symbols, get_nifty100_symbols, get_nifty200_symbols,
    NIFTY50_SYMBOLS, NIFTY100_SYMBOLS, NIFTY200_SYMBOLS,
    BANK_NIFTY_SYMBOLS, POPULAR_ETFS, MAJOR_INDICES
)

class EnhancedSymbolDiscovery:
    """Enhanced symbol discovery with complete symbol lists and fallbacks"""
    
    def __init__(self):
        self.base_dir = Path("data/parquet/symbols")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhanced symbol categories with actual counts
        self.symbol_categories = {
            'nifty50': {
                'symbols': NIFTY50_SYMBOLS,
                'count': 50,
                'description': 'Top 50 large-cap stocks by market capitalization'
            },
            'nifty100': {
                'symbols': NIFTY100_SYMBOLS,
                'count': 100, 
                'description': 'Top 100 large-cap stocks by market capitalization'
            },
            'nifty200': {
                'symbols': NIFTY200_SYMBOLS,
                'count': 200,
                'description': 'Top 200 stocks covering large and mid-cap'
            },
            'bank_nifty': {
                'symbols': BANK_NIFTY_SYMBOLS,
                'count': len(BANK_NIFTY_SYMBOLS),
                'description': 'Banking sector stocks in Bank Nifty index'
            },
            'etfs': {
                'symbols': POPULAR_ETFS,
                'count': len(POPULAR_ETFS),
                'description': 'Popular Exchange Traded Funds'
            },
            'indices': {
                'symbols': MAJOR_INDICES,
                'count': len(MAJOR_INDICES),
                'description': 'Major market indices'
            }
        }
        
        # Additional symbol lists for comprehensive coverage
        self.additional_stocks = self._get_additional_popular_stocks()
        
    def _get_additional_popular_stocks(self) -> List[str]:
        """Get additional popular stocks not in Nifty200"""
        additional = [
            # Popular mid-cap stocks
            "NSE:DIXON-EQ", "NSE:JUBLFOOD-EQ", "NSE:BALKRISIND-EQ", "NSE:MPHASIS-EQ",
            "NSE:MINDTREE-EQ", "NSE:PERSISTENT-EQ", "NSE:ASHOKLEY-EQ", "NSE:FEDERALBNK-EQ",
            "NSE:INDUSTOWER-EQ", "NSE:LICHSGFIN-EQ", "NSE:OBEROIRLTY-EQ", "NSE:GODREJPROP-EQ",
            "NSE:COFORGE-EQ", "NSE:LALPATHLAB-EQ", "NSE:NAVINFLUOR-EQ", "NSE:PIIND-EQ",
            
            # Popular small-cap stocks  
            "NSE:RELAXO-EQ", "NSE:VGUARD-EQ", "NSE:CRISIL-EQ", "NSE:SYMPHONY-EQ",
            "NSE:CREDITACC-EQ", "NSE:THYROCARE-EQ", "NSE:REDINGTON-EQ", "NSE:TEAMLEASE-EQ",
            "NSE:FINEORG-EQ", "NSE:KNRCON-EQ", "NSE:RAJESHEXPO-EQ", "NSE:CENTURYTEX-EQ",
            
            # Technology stocks
            "NSE:RATEGAIN-EQ", "NSE:ROUTE-EQ", "NSE:HAPPSTMNDS-EQ", "NSE:TATAELXSI-EQ",
            "NSE:SONACOMS-EQ", "NSE:KPITTECH-EQ", "NSE:CYIENT-EQ", "NSE:INTELLECT-EQ",
            
            # Pharma and Healthcare
            "NSE:LAURUSLABS-EQ", "NSE:SUNPHARMA-EQ", "NSE:ALKEM-EQ", "NSE:METROPOLIS-EQ",
            "NSE:DIVISLABS-EQ", "NSE:GLENMARK-EQ", "NSE:CADILAHC-EQ", "NSE:IPCALAB-EQ"
        ]
        return additional
        
    def get_all_symbols_by_category(self) -> Dict[str, List[str]]:
        """Get all symbols organized by category with actual counts"""
        all_symbols = {}
        
        for category, info in self.symbol_categories.items():
            symbols = info['symbols'].copy()  # Create a copy to avoid mutation
            all_symbols[category] = symbols
            print(f"📊 {category.title()}: {len(symbols)} symbols ({info['description']})")
        
        # Add additional popular stocks
        all_symbols['additional_popular'] = self.additional_stocks
        print(f"📊 Additional Popular: {len(self.additional_stocks)} symbols")
        
        return all_symbols
    
    def get_complete_symbol_universe(self) -> List[str]:
        """Get complete symbol universe with no duplicates"""
        all_symbols_dict = self.get_all_symbols_by_category()
        
        # Combine all symbols and remove duplicates while preserving order
        complete_universe = []
        seen = set()
        
        for category, symbols in all_symbols_dict.items():
            for symbol in symbols:
                if symbol not in seen:
                    complete_universe.append(symbol)
                    seen.add(symbol)
        
        print(f"🎯 Complete Symbol Universe: {len(complete_universe)} unique symbols")
        return complete_universe
    
    def get_symbols_for_category(self, category: str) -> List[str]:
        """Get symbols for a specific category"""
        if category not in self.symbol_categories:
            print(f"❌ Unknown category: {category}")
            print(f"📋 Available categories: {list(self.symbol_categories.keys())}")
            return []
        
        symbols = self.symbol_categories[category]['symbols']
        count = len(symbols)
        expected = self.symbol_categories[category]['count']
        
        print(f"📊 {category.title()}: {count} symbols (expected: {expected})")
        
        if count != expected and category in ['nifty50', 'nifty100', 'nifty200']:
            print(f"⚠️  Warning: Expected {expected} symbols but got {count}")
        
        return symbols.copy()
    
    def get_websocket_symbols(self, max_symbols: int = 200) -> List[str]:
        """Get optimized symbol list for WebSocket streaming"""
        # Priority order for WebSocket
        priority_symbols = []
        
        # 1. Nifty50 (highest priority)
        priority_symbols.extend(self.get_symbols_for_category('nifty50'))
        
        # 2. Bank Nifty constituents
        bank_nifty = self.get_symbols_for_category('bank_nifty')
        for symbol in bank_nifty:
            if symbol not in priority_symbols:
                priority_symbols.append(symbol)
        
        # 3. Major indices
        indices = self.get_symbols_for_category('indices')
        for symbol in indices:
            if symbol not in priority_symbols:
                priority_symbols.append(symbol)
        
        # 4. Popular ETFs
        etfs = self.get_symbols_for_category('etfs')
        for symbol in etfs:
            if symbol not in priority_symbols:
                priority_symbols.append(symbol)
        
        # 5. Additional popular stocks if space allows
        if len(priority_symbols) < max_symbols:
            remaining_slots = max_symbols - len(priority_symbols)
            for symbol in self.additional_stocks[:remaining_slots]:
                if symbol not in priority_symbols:
                    priority_symbols.append(symbol)
        
        final_list = priority_symbols[:max_symbols]
        print(f"🌐 WebSocket Symbol List: {len(final_list)} symbols (max: {max_symbols})")
        
        return final_list
    
    def save_symbol_lists(self) -> None:
        """Save all symbol lists to JSON files for caching"""
        all_symbols = self.get_all_symbols_by_category()
        
        # Save individual category files
        for category, symbols in all_symbols.items():
            file_path = self.base_dir / f"{category}_symbols.json"
            with open(file_path, 'w') as f:
                json.dump({
                    'category': category,
                    'count': len(symbols),
                    'last_updated': pd.Timestamp.now().isoformat(),
                    'symbols': symbols
                }, f, indent=2)
            print(f"💾 Saved {category}: {len(symbols)} symbols to {file_path}")
        
        # Save complete universe
        complete_universe = self.get_complete_symbol_universe()
        universe_path = self.base_dir / "complete_universe.json"
        with open(universe_path, 'w') as f:
            json.dump({
                'total_symbols': len(complete_universe),
                'last_updated': pd.Timestamp.now().isoformat(),
                'categories': {cat: len(syms) for cat, syms in all_symbols.items()},
                'symbols': complete_universe
            }, f, indent=2)
        print(f"💾 Saved complete universe: {len(complete_universe)} symbols to {universe_path}")
        
        # Save WebSocket optimized list
        websocket_symbols = self.get_websocket_symbols()
        websocket_path = self.base_dir / "websocket_symbols.json"
        with open(websocket_path, 'w') as f:
            json.dump({
                'count': len(websocket_symbols),
                'last_updated': pd.Timestamp.now().isoformat(),
                'description': 'Optimized symbol list for WebSocket streaming',
                'symbols': websocket_symbols
            }, f, indent=2)
        print(f"💾 Saved WebSocket list: {len(websocket_symbols)} symbols to {websocket_path}")
    
    def load_cached_symbols(self, category: str) -> Optional[List[str]]:
        """Load symbols from cache if available"""
        file_path = self.base_dir / f"{category}_symbols.json"
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"📦 Loaded cached {category}: {data['count']} symbols")
                return data['symbols']
            except Exception as e:
                print(f"❌ Failed to load cached {category}: {e}")
        
        return None
    
    def get_symbol_statistics(self) -> Dict:
        """Get comprehensive statistics about symbol coverage"""
        all_symbols = self.get_all_symbols_by_category()
        
        stats = {
            'total_categories': len(all_symbols),
            'category_breakdown': {},
            'symbol_overlap': {},
            'coverage_summary': {}
        }
        
        # Category breakdown
        for category, symbols in all_symbols.items():
            stats['category_breakdown'][category] = len(symbols)
        
        # Calculate overlaps
        nifty50_set = set(all_symbols.get('nifty50', []))
        nifty100_set = set(all_symbols.get('nifty100', []))
        nifty200_set = set(all_symbols.get('nifty200', []))
        
        stats['symbol_overlap'] = {
            'nifty50_in_nifty100': len(nifty50_set & nifty100_set),
            'nifty100_in_nifty200': len(nifty100_set & nifty200_set),
            'unique_symbols': len(set().union(*all_symbols.values()))
        }
        
        # Coverage summary
        stats['coverage_summary'] = {
            'large_cap': len(all_symbols.get('nifty50', [])),
            'large_mid_cap': len(all_symbols.get('nifty100', [])),
            'broad_market': len(all_symbols.get('nifty200', [])),
            'banking': len(all_symbols.get('bank_nifty', [])),
            'etfs': len(all_symbols.get('etfs', [])),
            'indices': len(all_symbols.get('indices', [])),
            'additional': len(all_symbols.get('additional_popular', []))
        }
        
        return stats


def get_enhanced_symbol_discovery() -> EnhancedSymbolDiscovery:
    """Factory function to get enhanced symbol discovery instance"""
    return EnhancedSymbolDiscovery()


# Convenience functions for backward compatibility
def get_all_symbols() -> List[str]:
    """Get all symbols in the enhanced discovery system"""
    discovery = get_enhanced_symbol_discovery()
    return discovery.get_complete_symbol_universe()


def get_category_symbols(category: str) -> List[str]:
    """Get symbols for a specific category"""
    discovery = get_enhanced_symbol_discovery()
    return discovery.get_symbols_for_category(category)


def get_websocket_ready_symbols(max_count: int = 200) -> List[str]:
    """Get WebSocket-ready symbol list"""
    discovery = get_enhanced_symbol_discovery()
    return discovery.get_websocket_symbols(max_count)


if __name__ == "__main__":
    print("🚀 Enhanced Symbol Discovery System")
    print("=" * 50)
    
    discovery = get_enhanced_symbol_discovery()
    
    # Show all categories
    all_symbols = discovery.get_all_symbols_by_category()
    
    # Show statistics
    stats = discovery.get_symbol_statistics()
    print(f"\n📊 Symbol Statistics:")
    print(f"   Total Categories: {stats['total_categories']}")
    print(f"   Unique Symbols: {stats['symbol_overlap']['unique_symbols']}")
    
    # Show category breakdown
    print(f"\n📋 Category Breakdown:")
    for category, count in stats['category_breakdown'].items():
        print(f"   {category.title()}: {count} symbols")
    
    # Save all lists
    print(f"\n💾 Saving symbol lists...")
    discovery.save_symbol_lists()
    
    print(f"\n✅ Enhanced Symbol Discovery Complete!")