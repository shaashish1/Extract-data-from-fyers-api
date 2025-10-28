"""
Test script to search for TMPV symbol using new JSON discovery
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.symbol_discovery.fyers_json_symbol_discovery import FyersJSONSymbolDiscovery

def main():
    print("="*80)
    print("Testing TMPV Symbol Search")
    print("="*80)
    
    discovery = FyersJSONSymbolDiscovery()
    
    # Test 1: Search for TMPV
    print("\n1. Searching for 'TMPV'...")
    results = discovery.search_symbol("TMPV", max_results=50)
    
    if results:
        print(f"\nFound {len(results)} matches:")
        print("-"*80)
        for i, symbol in enumerate(results, 1):
            print(f"{i}. {symbol.symbol_ticker}")
            print(f"   Name: {symbol.symbol_desc}")
            print(f"   Exchange: {symbol.exchange_name}")
            print(f"   ISIN: {symbol.isin}")
            print(f"   FyToken: {symbol.fytoken}")
            print()
    else:
        print("\nNo results found for 'TMPV'")
    
    # Test 2: Try exact ticker searches
    print("\n2. Testing exact ticker searches...")
    test_tickers = [
        "NSE:TMPV-EQ",
        "NSE:TMPV",
        "BSE:TMPV-EQ",
        "BSE:TMPV-A"
    ]
    
    for ticker in test_tickers:
        print(f"\nSearching for: {ticker}")
        symbol = discovery.get_symbol_by_ticker(ticker)
        if symbol:
            print(f"  ✓ Found: {symbol.symbol_desc}")
        else:
            print(f"  ✗ Not found")
    
    # Test 3: Get statistics
    print("\n3. Symbol Statistics:")
    print("-"*80)
    stats = discovery.get_statistics()
    for segment, count in sorted(stats.items()):
        if segment != 'TOTAL':
            print(f"{segment:15} : {count:>8,} symbols")
    print("-"*80)
    print(f"{'TOTAL':15} : {stats['TOTAL']:>8,} symbols")

if __name__ == "__main__":
    main()
