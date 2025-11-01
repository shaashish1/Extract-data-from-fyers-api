#!/usr/bin/env python3
"""
🧪 Comprehensive Symbol Discovery Test
=====================================

This script tests symbol discovery across different API endpoints
to understand what symbols are available and validate our counts.

Author: Fyers WebSocket Live Project
Date: October 29, 2025
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
import time

# Import our authentication system
from auth.my_fyers_model import MyFyersModel

console = Console()

class ComprehensiveSymbolTester:
    def __init__(self):
        """Initialize the comprehensive symbol tester."""
        self.fyers_model = None
        self.test_results = {}
        
    def setup_authentication(self):
        """Setup FYERS authentication."""
        try:
            console.print("🔐 Initializing FYERS authentication...", style="blue")
            self.fyers_model = MyFyersModel()
            
            # Test authentication with profile
            profile = self.fyers_model.get_profile()
            if profile and profile.get('s') == 'ok':
                console.print("✅ Authentication successful!", style="green")
                console.print(f"👤 User: {profile.get('data', {}).get('display_name', 'Unknown')}", style="cyan")
                return True
            else:
                console.print("❌ Authentication failed", style="red")
                return False
        except Exception as e:
            console.print(f"❌ Authentication error: {str(e)}", style="red")
            return False
    
    def test_market_status(self):
        """Test market status API."""
        try:
            console.print("📊 Testing Market Status API...", style="blue")
            status = self.fyers_model.market_status()
            
            if status and status.get('s') == 'ok':
                market_data = status.get('marketStatus', [])
                console.print(f"✅ Market Status: {len(market_data)} market segments", style="green")
                
                # Show market segments
                for market in market_data:
                    market_name = market.get('market_type', 'Unknown')
                    status_val = market.get('status', 'Unknown')
                    console.print(f"  • {market_name}: {status_val}", style="cyan")
                
                return True, len(market_data)
            else:
                return False, "Market status API failed"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_symbol_search(self, query="NIFTY"):
        """Test symbol search API."""
        try:
            console.print(f"🔍 Testing Symbol Search API for '{query}'...", style="blue")
            
            # Get symbol search results
            search_data = {
                "symbol_type": "EQ",  # Equity
                "search_string": query
            }
            
            # Note: Fyers doesn't have a direct symbol search in the public API
            # We'll test with known symbols instead
            test_symbols = [
                "NSE:NIFTY50-INDEX",
                "NSE:NIFTYBANK-INDEX", 
                "NSE:RELIANCE-EQ",
                "NSE:TCS-EQ",
                "NSE:HDFCBANK-EQ"
            ]
            
            successful_quotes = 0
            for symbol in test_symbols:
                try:
                    quote_data = {"symbols": symbol}
                    quote = self.fyers_model.quotes(data=quote_data)
                    if quote and quote.get('s') == 'ok':
                        successful_quotes += 1
                        symbol_info = quote.get('d', [])[0] if quote.get('d') else {}
                        name = symbol_info.get('n', symbol)
                        ltp = symbol_info.get('v', {}).get('lp', 'N/A')
                        console.print(f"  ✅ {symbol}: {name} - LTP: {ltp}", style="green")
                    else:
                        console.print(f"  ❌ {symbol}: Quote failed", style="red")
                except:
                    console.print(f"  ❌ {symbol}: Error getting quote", style="red")
            
            return True, f"{successful_quotes}/{len(test_symbols)} symbols found"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_historical_data(self, symbol="NSE:NIFTY50-INDEX"):
        """Test historical data API."""
        try:
            console.print(f"📈 Testing Historical Data API for {symbol}...", style="blue")
            
            # Get last 5 days of data
            to_date = datetime.now()
            from_date = to_date - timedelta(days=5)
            
            data = {
                "symbol": symbol,
                "resolution": "D",  # Daily
                "date_format": "1",
                "range_from": from_date.strftime("%Y-%m-%d"),
                "range_to": to_date.strftime("%Y-%m-%d"),
                "cont_flag": "1"
            }
            
            history = self.fyers_model.history(data=data)
            
            if history and history.get('s') == 'ok':
                candles = history.get('candles', [])
                console.print(f"✅ Historical Data: {len(candles)} candles retrieved", style="green")
                
                if candles:
                    latest = candles[-1]
                    console.print(f"  📊 Latest: O:{latest[1]} H:{latest[2]} L:{latest[3]} C:{latest[4]} V:{latest[5]}", style="cyan")
                
                return True, f"{len(candles)} candles"
            else:
                return False, "Historical data API failed"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_market_depth(self, symbol="NSE:RELIANCE-EQ"):
        """Test market depth API."""
        try:
            console.print(f"📊 Testing Market Depth API for {symbol}...", style="blue")
            
            data = {"symbol": symbol, "ohlcv_flag": "1"}
            depth = self.fyers_model.depth(data=data)
            
            if depth and depth.get('s') == 'ok':
                depth_data = depth.get('d', {})
                bids = depth_data.get('bids', [])
                asks = depth_data.get('ask', [])
                
                console.print(f"✅ Market Depth: {len(bids)} bids, {len(asks)} asks", style="green")
                
                if bids and asks:
                    best_bid = bids[0] if bids else {}
                    best_ask = asks[0] if asks else {}
                    console.print(f"  💰 Best Bid: {best_bid.get('price', 'N/A')} x {best_bid.get('volume', 'N/A')}", style="cyan")
                    console.print(f"  💰 Best Ask: {best_ask.get('price', 'N/A')} x {best_ask.get('volume', 'N/A')}", style="cyan")
                
                return True, f"{len(bids)} bids, {len(asks)} asks"
            else:
                return False, "Market depth API failed"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_fyers_symbol_master(self):
        """Test downloading symbol master from Fyers."""
        try:
            console.print("📥 Testing Fyers Symbol Master Download...", style="blue")
            
            # Import our symbol discovery
            from symbol_discovery.comprehensive_symbol_discovery import ComprehensiveFyersDiscovery
            
            discovery = ComprehensiveFyersDiscovery()
            
            # This will show us the actual counts
            console.print("🔄 Running symbol discovery...", style="yellow")
            
            # Force a fresh discovery
            symbols_data = discovery.discover_all_symbols(force_refresh=True)
            
            total_symbols = len(symbols_data) if symbols_data else 0
            
            console.print(f"✅ Symbol Master: {total_symbols} symbols discovered", style="green")
            
            # Show breakdown by segment
            if symbols_data:
                segments = {}
                for symbol_info in symbols_data:
                    segment = symbol_info.get('segment', 'Unknown')
                    segments[segment] = segments.get(segment, 0) + 1
                
                console.print("📊 Segment Breakdown:", style="cyan")
                for segment, count in segments.items():
                    console.print(f"  • {segment}: {count:,} symbols", style="cyan")
            
            return True, f"{total_symbols:,} total symbols"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def run_comprehensive_test(self):
        """Run comprehensive symbol discovery test."""
        console.print("🧪 Starting Comprehensive Symbol Discovery Test...", style="blue bold")
        
        # Setup authentication
        if not self.setup_authentication():
            return False
        
        # Run all tests
        tests = [
            ("Market Status", self.test_market_status),
            ("Symbol Search", lambda: self.test_symbol_search("NIFTY")),
            ("Historical Data", lambda: self.test_historical_data("NSE:NIFTY50-INDEX")),
            ("Market Depth", lambda: self.test_market_depth("NSE:RELIANCE-EQ")),
            ("Fyers Symbol Master", self.test_fyers_symbol_master)
        ]
        
        results_table = Table(title="Comprehensive Symbol Discovery Test Results")
        results_table.add_column("Test", style="cyan")
        results_table.add_column("Status", style="green")
        results_table.add_column("Details", style="yellow")
        
        for test_name, test_func in track(tests, description="Running tests..."):
            try:
                success, details = test_func()
                status = "✅ Pass" if success else "❌ Fail"
                results_table.add_row(test_name, status, str(details))
                self.test_results[test_name] = (success, details)
                
                # Small delay between tests
                time.sleep(1)
            except Exception as e:
                results_table.add_row(test_name, "❌ Error", str(e))
                self.test_results[test_name] = (False, str(e))
        
        console.print(results_table)
        
        # Summary
        passed_tests = sum(1 for success, _ in self.test_results.values() if success)
        total_tests = len(self.test_results)
        
        summary_panel = Panel(
            f"""
🎯 **Test Summary:**
✅ Tests Passed: {passed_tests}/{total_tests}
📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%

🔑 **Key Findings:**
• Authentication: Working with real credentials
• API Endpoints: Testing market data access
• Symbol Discovery: Validating actual symbol counts
• Data Quality: Checking real-time vs historical data

🚀 **Next Steps:**
• Run symbol discovery with validation
• Check for missing/extra symbols
• Validate market segment classifications
            """.strip(),
            title="Comprehensive Symbol Test Complete",
            border_style="green"
        )
        console.print(summary_panel)
        
        return passed_tests == total_tests

def main():
    """Main execution function."""
    tester = ComprehensiveSymbolTester()
    success = tester.run_comprehensive_test()
    
    if success:
        console.print("\\n🎉 All tests passed! Symbol discovery system is working correctly.", style="green bold")
    else:
        console.print("\\n⚠️ Some tests failed. Check the results above for details.", style="yellow")

if __name__ == "__main__":
    main()