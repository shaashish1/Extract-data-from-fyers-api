"""
Test Fyers API Rate Limit Recovery
===================================
Test quotes API with minimal request to check if rate limit has cleared.

Created: October 28, 2025
"""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.market_data.quotes_api import FyersQuotesAPI

def test_single_symbol():
    """Test with just ONE symbol to avoid rate limits."""
    print("="*80)
    print("Fyers API Rate Limit Recovery Test")
    print("="*80)
    print("\n📋 Fyers API Rate Limits:")
    print("   - Per Second: 10 requests")
    print("   - Per Minute: 200 requests")
    print("   - Per Day: 100,000 requests")
    print("   ⚠️  WARNING: 3 violations/day = BLOCKED UNTIL MIDNIGHT")
    print("\n⏰ Waiting 60 seconds for rate limit cooldown...")
    
    for i in range(60, 0, -10):
        print(f"   {i} seconds remaining...")
        time.sleep(10)
    
    print("\n📊 Testing with single symbol: NSE:SBIN-EQ")
    
    quotes_api = FyersQuotesAPI()
    
    # Test with just ONE symbol
    symbols = ["NSE:SBIN-EQ"]
    
    response = quotes_api.get_quotes(symbols)
    
    if response:
        print("\n✅ SUCCESS! Rate limit cleared.")
        print(f"\nResponse: {response}")
        
        # Parse and display
        parsed = quotes_api.parse_quote_response(response)
        if not parsed.empty:
            print("\n📈 Quote Data:")
            print(parsed.to_string())
    else:
        print("\n❌ FAILED! Still rate limited or blocked.")
        print("\n💡 Possible reasons:")
        print("   1. You may be BLOCKED for the entire day (until midnight)")
        print("   2. Exceeded per-minute limit 3+ times today")
        print("   3. Token expired (check auth/access_token.txt timestamp)")
        print("\n💡 Solutions:")
        print("   1. Wait until midnight (IST) for block to clear")
        print("   2. Generate new token: cd auth && python generate_token.py")
        print("   3. Check token age: should be < 24 hours old")

if __name__ == "__main__":
    test_single_symbol()
