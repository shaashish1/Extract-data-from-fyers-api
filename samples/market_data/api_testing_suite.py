#!/usr/bin/env python3
"""
📊 Fyers WebSocket Live - Market Data API Testing
============================================

Comprehensive market data API testing with:
- Real-time quotes and market depth
- Historical data retrieval
- Market status and broker info
- Enhanced error handling

Author: Fyers WebSocket Live Project
Date: October 27, 2025
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from my_fyers_model import MyFyersModel
from data_storage import get_parquet_manager
from index_constituents import get_nifty50_symbols
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
import time

# Initialize Rich console
console = Console()

class MarketDataTester:
    def __init__(self):
        """Initialize the market data tester."""
        self.fyers_model = None
        self.parquet_manager = get_parquet_manager()
        
    def setup_authentication(self):
        """Setup FYERS authentication."""
        try:
            console.print("🔐 Initializing FYERS authentication...", style="blue")
            self.fyers_model = MyFyersModel()
            console.print("✅ Authentication successful!", style="green")
            return True
        except Exception as e:
            console.print(f"❌ Authentication failed: {str(e)}", style="red")
            return False
    
    def test_market_status(self):
        """Test market status API."""
        console.print("\n📅 Testing Market Status API...", style="blue")
        
        try:
            response = self.fyers_model.market_status()
            
            if response and 'data' in response:
                table = Table(title="🏪 Market Status")
                table.add_column("Exchange", style="cyan")
                table.add_column("Market", style="blue")
                table.add_column("Status", style="green")
                table.add_column("Start Time", style="yellow")
                table.add_column("End Time", style="yellow")
                
                for market in response['data']:
                    status_style = "green" if market.get('marketStatus') == 'OPEN' else "red"
                    table.add_row(
                        market.get('exchange', 'N/A'),
                        market.get('market_type', 'N/A'),
                        market.get('marketStatus', 'N/A'),
                        market.get('start_time', 'N/A'),
                        market.get('end_time', 'N/A'),
                        style=status_style
                    )
                
                console.print(table)
                return True
            else:
                console.print("⚠️ No market status data received", style="yellow")
                return False
                
        except Exception as e:
            console.print(f"❌ Market status test failed: {str(e)}", style="red")
            return False
    
    def test_quotes_api(self):
        """Test quotes API for multiple symbols."""
        console.print("\n💰 Testing Quotes API...", style="blue")
        
        try:
            # Test symbols
            test_symbols = [
                "NSE:RELIANCE-EQ",
                "NSE:TCS-EQ", 
                "NSE:HDFCBANK-EQ",
                "NSE:NIFTY50-INDEX"
            ]
            
            symbols_str = ",".join(test_symbols)
            
            data = {"symbols": symbols_str}
            response = self.fyers_model.quotes(data=data)
            
            if response and 'd' in response:
                table = Table(title="💹 Live Quotes")
                table.add_column("Symbol", style="cyan")
                table.add_column("LTP", justify="right", style="green")
                table.add_column("Change", justify="right")
                table.add_column("Change %", justify="right")
                table.add_column("Volume", justify="right", style="blue")
                table.add_column("Market Cap", justify="right", style="yellow")
                
                for symbol_data in response['d']:
                    if symbol_data and 'v' in symbol_data:
                        v = symbol_data['v']
                        change = v.get('ch', 0)
                        change_style = "green" if change > 0 else "red" if change < 0 else "white"
                        
                        table.add_row(
                            symbol_data.get('n', 'Unknown'),
                            f"₹{v.get('lp', 0):.2f}",
                            f"{change:+.2f}",
                            f"{v.get('chp', 0):+.2f}%",
                            f"{v.get('vol', 0):,}",
                            f"₹{v.get('mc', 0):,.0f}L",
                            style=change_style
                        )
                
                console.print(table)
                return True
            else:
                console.print("⚠️ No quotes data received", style="yellow")
                return False
                
        except Exception as e:
            console.print(f"❌ Quotes test failed: {str(e)}", style="red")
            return False
    
    def test_market_depth(self):
        """Test market depth API."""
        console.print("\n📊 Testing Market Depth API...", style="blue")
        
        try:
            # Test with popular stock
            data = {
                "symbol": "NSE:RELIANCE-EQ",
                "ohlcv_flag": "1"
            }
            
            response = self.fyers_model.depth(data=data)
            
            if response and 'd' in response:
                depth_data = response['d']
                
                # Create depth table
                table = Table(title="📈 Market Depth - RELIANCE")
                table.add_column("Type", style="cyan")
                table.add_column("Price", justify="right", style="white")
                table.add_column("Quantity", justify="right", style="blue")
                table.add_column("Orders", justify="right", style="yellow")
                
                # Add bid data
                if 'bids' in depth_data:
                    for i, bid in enumerate(depth_data['bids'][:5]):
                        table.add_row(
                            f"BID {i+1}",
                            f"₹{bid.get('price', 0):.2f}",
                            f"{bid.get('quantity', 0):,}",
                            f"{bid.get('ord', 0)}",
                            style="green"
                        )
                
                # Add ask data
                if 'ask' in depth_data:
                    for i, ask in enumerate(depth_data['ask'][:5]):
                        table.add_row(
                            f"ASK {i+1}",
                            f"₹{ask.get('price', 0):.2f}",
                            f"{ask.get('quantity', 0):,}",
                            f"{ask.get('ord', 0)}",
                            style="red"
                        )
                
                console.print(table)
                
                # Show OHLCV data if available
                if 'ohlcv' in depth_data:
                    ohlcv = depth_data['ohlcv']
                    ohlcv_table = Table(title="OHLCV Data")
                    ohlcv_table.add_column("Metric", style="cyan")
                    ohlcv_table.add_column("Value", style="white")
                    
                    ohlcv_table.add_row("Open", f"₹{ohlcv.get('open', 0):.2f}")
                    ohlcv_table.add_row("High", f"₹{ohlcv.get('high', 0):.2f}")
                    ohlcv_table.add_row("Low", f"₹{ohlcv.get('low', 0):.2f}")
                    ohlcv_table.add_row("Close", f"₹{ohlcv.get('close', 0):.2f}")
                    ohlcv_table.add_row("Volume", f"{ohlcv.get('volume', 0):,}")
                    
                    console.print(ohlcv_table)
                
                return True
            else:
                console.print("⚠️ No market depth data received", style="yellow")
                return False
                
        except Exception as e:
            console.print(f"❌ Market depth test failed: {str(e)}", style="red")
            return False
    
    def test_historical_data(self):
        """Test historical data API."""
        console.print("\n📈 Testing Historical Data API...", style="blue")
        
        try:
            # Calculate date range (last 30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            data = {
                "symbol": "NSE:NIFTY50-INDEX",
                "resolution": "D",  # Daily
                "date_format": "1",  # Unix timestamp
                "range_from": start_date.strftime("%Y-%m-%d"),
                "range_to": end_date.strftime("%Y-%m-%d"),
                "cont_flag": "1"
            }
            
            response = self.fyers_model.history(data=data)
            
            if response and 'candles' in response:
                candles = response['candles']
                
                console.print(f"📊 Retrieved {len(candles)} historical candles", style="green")
                
                # Show sample data
                table = Table(title="📈 Historical Data (Last 10 Days)")
                table.add_column("Date", style="cyan")
                table.add_column("Open", justify="right", style="blue")
                table.add_column("High", justify="right", style="green")
                table.add_column("Low", justify="right", style="red")
                table.add_column("Close", justify="right", style="white")
                table.add_column("Volume", justify="right", style="yellow")
                
                for candle in candles[-10:]:  # Last 10 days
                    date = datetime.fromtimestamp(candle[0])
                    table.add_row(
                        date.strftime("%Y-%m-%d"),
                        f"{candle[1]:.2f}",
                        f"{candle[2]:.2f}",
                        f"{candle[3]:.2f}",
                        f"{candle[4]:.2f}",
                        f"{candle[5]:,.0f}"
                    )
                
                console.print(table)
                
                # Save sample to storage
                if len(candles) > 0:
                    self.save_sample_data(candles, "nifty50_historical")
                
                return True
            else:
                console.print("⚠️ No historical data received", style="yellow")
                return False
                
        except Exception as e:
            console.print(f"❌ Historical data test failed: {str(e)}", style="red")
            return False
    
    def save_sample_data(self, candles, symbol_name):
        """Save sample historical data to Parquet."""
        try:
            import pandas as pd
            
            # Convert candles to DataFrame
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            
            # Save using our storage system
            self.parquet_manager.save_data(df, symbol_name, "1D", mode="replace")
            console.print(f"💾 Saved sample data to Parquet: {symbol_name}_1D.parquet", style="green")
            
        except Exception as e:
            console.print(f"⚠️ Could not save sample data: {str(e)}", style="yellow")
    
    def test_symbol_search(self):
        """Test symbol search functionality."""
        console.print("\n🔍 Testing Symbol Discovery Integration...", style="blue")
        
        try:
            # Test our symbol discovery system
            symbols = get_nifty50_symbols()
            
            console.print(f"📋 Found {len(symbols)} Nifty50 symbols from our discovery system", style="green")
            
            # Show sample symbols
            table = Table(title="🏢 Sample Nifty50 Symbols")
            table.add_column("Index", style="cyan")
            table.add_column("Symbol", style="blue")
            table.add_column("FYERS Format", style="green")
            
            for i, symbol in enumerate(symbols[:10], 1):
                fyers_format = f"NSE:{symbol}-EQ" if not symbol.startswith('NSE:') else symbol
                table.add_row(str(i), symbol, fyers_format)
            
            console.print(table)
            return True
            
        except Exception as e:
            console.print(f"❌ Symbol discovery test failed: {str(e)}", style="red")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive market data API tests."""
        if not self.setup_authentication():
            return False
        
        console.print("\n🧪 [bold blue]Running Comprehensive Market Data Tests[/bold blue]")
        
        tests = [
            ("Market Status", self.test_market_status),
            ("Quotes API", self.test_quotes_api), 
            ("Market Depth", self.test_market_depth),
            ("Historical Data", self.test_historical_data),
            ("Symbol Discovery", self.test_symbol_search)
        ]
        
        results = {}
        
        for test_name, test_func in track(tests, description="Running tests..."):
            try:
                result = test_func()
                results[test_name] = result
                time.sleep(1)  # Rate limiting
            except Exception as e:
                console.print(f"❌ {test_name} failed: {str(e)}", style="red")
                results[test_name] = False
        
        # Summary
        console.print("\n📋 [bold blue]Test Results Summary[/bold blue]")
        
        summary_table = Table(title="🧪 Test Results")
        summary_table.add_column("Test", style="cyan")
        summary_table.add_column("Status", style="white")
        summary_table.add_column("Result", style="white")
        
        passed = 0
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            status_style = "green" if result else "red"
            summary_table.add_row(
                test_name,
                status,
                "Success" if result else "Failed",
                style=status_style
            )
            if result:
                passed += 1
        
        console.print(summary_table)
        
        # Overall result
        total_tests = len(tests)
        console.print(f"\n🎯 Overall Result: {passed}/{total_tests} tests passed", 
                     style="green" if passed == total_tests else "yellow")
        
        if passed == total_tests:
            console.print("🎉 All tests passed! Your FYERS integration is working perfectly!", style="bold green")
        elif passed > total_tests // 2:
            console.print("⚠️ Most tests passed. Check failed tests for issues.", style="yellow")
        else:
            console.print("❌ Multiple tests failed. Check your credentials and connection.", style="red")
        
        return passed == total_tests

def main():
    """Main function to run market data tests."""
    tester = MarketDataTester()
    
    console.print("""
    📊 [bold blue]Fyers WebSocket Live - Market Data API Testing Suite[/bold blue]
    
    This comprehensive test suite will verify:
    • FYERS API authentication and connectivity
    • Market status and broker information
    • Real-time quotes and market depth
    • Historical data retrieval
    • Symbol discovery integration
    
    """)
    
    try:
        # Run comprehensive test
        success = tester.run_comprehensive_test()
        
        if success:
            console.print("\n🎉 [bold green]All API tests completed successfully![/bold green]")
            console.print("✅ [blue]Your FYERS integration is ready for production use![/blue]")
        else:
            console.print("\n⚠️ [yellow]Some tests failed. Please review the results above.[/yellow]")
            
    except KeyboardInterrupt:
        console.print("\n⏹️ Tests interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {str(e)}", style="red")

if __name__ == "__main__":
    main()