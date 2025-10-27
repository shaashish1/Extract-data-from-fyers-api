#!/usr/bin/env python3
"""
🚀 Fyers WebSocket Live - Basic WebSocket Streaming Test
=====================================

Enhanced FYERS WebSocket streaming example adapted for our comprehensive system.
Features:
- Auto-authentication with MyFyersModel
- Symbol discovery integration
- Professional data storage with Parquet
- Rich progress monitoring

Author: Fyers WebSocket Live Project
Date: October 27, 2025
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from fyers_apiv3.FyersWebsocket import data_ws
from my_fyers_model import MyFyersModel
from data_storage import get_parquet_manager
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
import time

# Initialize Rich console
console = Console()

# Global variables for monitoring
message_count = 0
start_time = datetime.now()
latest_data = {}

class EnhancedWebSocketTest:
    def __init__(self):
        """Initialize the enhanced WebSocket test system."""
        self.parquet_manager = get_parquet_manager()
        self.fyers_model = None
        self.websocket = None
        self.is_running = False
        
    def setup_authentication(self):
        """Setup FYERS authentication using our MyFyersModel."""
        try:
            console.print("🔐 Initializing FYERS authentication...", style="blue")
            self.fyers_model = MyFyersModel()
            
            # Get access token in the correct format
            access_token = self.fyers_model.get_access_token()
            console.print(f"✅ Authentication successful!", style="green")
            return access_token
            
        except Exception as e:
            console.print(f"❌ Authentication failed: {str(e)}", style="red")
            return None
    
    def onmessage(self, message):
        """Enhanced callback function to handle incoming WebSocket messages."""
        global message_count, latest_data
        
        try:
            message_count += 1
            
            # Store latest data for display
            if isinstance(message, dict) and 'symbol' in message:
                symbol = message.get('symbol', 'Unknown')
                latest_data[symbol] = {
                    'ltp': message.get('ltp', 0),
                    'change': message.get('ch', 0),
                    'volume': message.get('vol', 0),
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                }
            
            # Optional: Save to Parquet (uncomment for data persistence)
            # self.save_to_storage(message)
            
        except Exception as e:
            console.print(f"⚠️ Error processing message: {str(e)}", style="yellow")
    
    def onerror(self, message):
        """Callback function to handle WebSocket errors."""
        console.print(f"🚨 WebSocket Error: {message}", style="red")
    
    def onclose(self, message):
        """Callback function to handle WebSocket connection close events."""
        console.print(f"🔌 Connection closed: {message}", style="yellow")
        self.is_running = False
    
    def onopen(self):
        """Callback function to subscribe to symbols upon WebSocket connection."""
        try:
            console.print("🌐 WebSocket connection established!", style="green")
            
            # Specify the data type and symbols you want to subscribe to
            data_type = "SymbolUpdate"
            
            # Use popular symbols for testing
            symbols = [
                'NSE:RELIANCE-EQ',     # Reliance Industries
                'NSE:TCS-EQ',          # Tata Consultancy Services
                'NSE:HDFCBANK-EQ',     # HDFC Bank
                'NSE:INFY-EQ',         # Infosys
                'NSE:NIFTY50-INDEX'    # Nifty 50 Index
            ]
            
            console.print(f"📡 Subscribing to {len(symbols)} symbols...", style="blue")
            for symbol in symbols:
                console.print(f"  • {symbol}", style="dim blue")
            
            # Subscribe to the specified symbols and data type
            self.websocket.subscribe(symbols=symbols, data_type=data_type)
            self.is_running = True
            
            # Keep the socket running to receive real-time data
            self.websocket.keep_running()
            
        except Exception as e:
            console.print(f"❌ Subscription failed: {str(e)}", style="red")
    
    def save_to_storage(self, message):
        """Save WebSocket data to our Parquet storage system."""
        try:
            if isinstance(message, dict) and 'symbol' in message:
                # Create a standardized record for storage
                record = {
                    'timestamp': datetime.now(),
                    'symbol': message.get('symbol'),
                    'ltp': message.get('ltp', 0),
                    'open': message.get('o', 0),
                    'high': message.get('h', 0),
                    'low': message.get('l', 0),
                    'close': message.get('c', 0),
                    'volume': message.get('vol', 0),
                    'change': message.get('ch', 0),
                    'change_percent': message.get('chp', 0)
                }
                
                # Save using our enhanced storage system
                self.parquet_manager.save_market_update(record)
                
        except Exception as e:
            console.print(f"⚠️ Storage error: {str(e)}", style="yellow")
    
    def create_monitoring_table(self):
        """Create a Rich table for real-time monitoring."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Symbol", style="cyan", no_wrap=True)
        table.add_column("LTP", justify="right", style="green")
        table.add_column("Change", justify="right")
        table.add_column("Volume", justify="right", style="blue")
        table.add_column("Time", style="dim")
        
        for symbol, data in latest_data.items():
            change_style = "red" if data['change'] < 0 else "green"
            table.add_row(
                symbol.split(':')[-1].replace('-EQ', ''),  # Clean symbol name
                f"₹{data['ltp']:.2f}",
                f"{data['change']:+.2f}",
                f"{data['volume']:,}",
                data['timestamp'],
                style=change_style if data['change'] != 0 else "white"
            )
        
        return table
    
    def run_test(self, duration_minutes=5):
        """Run the WebSocket test for specified duration."""
        access_token = self.setup_authentication()
        if not access_token:
            return False
        
        try:
            console.print("\n🚀 Starting Enhanced WebSocket Test", style="bold green")
            console.print(f"⏱️ Test Duration: {duration_minutes} minutes", style="blue")
            
            # Create FyersDataSocket instance
            self.websocket = data_ws.FyersDataSocket(
                access_token=access_token,
                log_path="",
                litemode=False,
                write_to_file=False,
                reconnect=True,
                on_connect=self.onopen,
                on_close=self.onclose,
                on_error=self.onerror,
                on_message=self.onmessage
            )
            
            # Start connection
            self.websocket.connect()
            
            # Live monitoring with Rich
            with Live(self.create_status_panel(), refresh_per_second=2, screen=True) as live:
                end_time = time.time() + (duration_minutes * 60)
                
                while time.time() < end_time and self.is_running:
                    live.update(self.create_status_panel())
                    time.sleep(0.5)
            
            console.print(f"\n✅ Test completed! Processed {message_count} messages", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Test failed: {str(e)}", style="red")
            return False
        
        finally:
            if self.websocket:
                try:
                    self.websocket.close()
                except:
                    pass
    
    def create_status_panel(self):
        """Create a comprehensive status panel."""
        # Statistics
        runtime = datetime.now() - start_time
        rate = message_count / max(runtime.total_seconds(), 1)
        
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Messages Received", f"{message_count:,}")
        stats_table.add_row("Runtime", f"{runtime}")
        stats_table.add_row("Messages/Second", f"{rate:.1f}")
        stats_table.add_row("Active Symbols", f"{len(latest_data)}")
        
        # Market data table
        market_table = self.create_monitoring_table()
        
        # Create main panel
        status_content = Table(show_header=False, box=None, padding=0)
        status_content.add_column(justify="left")
        status_content.add_column(justify="left")
        
        status_content.add_row(
            Panel(stats_table, title="📊 Statistics", border_style="blue"),
            Panel(market_table, title="📈 Live Market Data", border_style="green")
        )
        
        return Panel(
            status_content,
            title="🚀 Fyers WebSocket Live - Real-time Monitoring",
            border_style="bright_blue"
        )

def main():
    """Main function to run the WebSocket test."""
    test = EnhancedWebSocketTest()
    
    console.print("""
    🚀 [bold blue]Fyers WebSocket Live - Enhanced Testing System[/bold blue]
    
    This test will:
    • Connect to FYERS WebSocket using your credentials
    • Subscribe to popular stocks and indices
    • Display real-time market data
    • Demonstrate our enhanced architecture
    
    """)
    
    try:
        # Ask for test duration
        duration = console.input("⏱️ Enter test duration in minutes (default 2): ").strip()
        duration = int(duration) if duration.isdigit() else 2
        
        # Run the test
        success = test.run_test(duration)
        
        if success:
            console.print("\n🎉 [bold green]WebSocket test completed successfully![/bold green]")
            console.print("💡 [yellow]Ready for live trading and data collection![/yellow]")
        else:
            console.print("\n❌ [red]WebSocket test failed. Please check your credentials.[/red]")
            
    except KeyboardInterrupt:
        console.print("\n⏹️ Test interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {str(e)}", style="red")

if __name__ == "__main__":
    main()