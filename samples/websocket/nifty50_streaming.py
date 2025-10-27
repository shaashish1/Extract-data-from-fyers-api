#!/usr/bin/env python3
"""
🎯 Fyers WebSocket Live - Nifty50 Real-time Streaming
================================================

Advanced WebSocket streaming example for Nifty50 constituents with:
- Complete Nifty50 portfolio streaming
- Professional data persistence
- Rich analytics dashboard
- Performance monitoring

Author: Fyers WebSocket Live Project
Date: October 27, 2025
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import threading
import time

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from fyers_apiv3.FyersWebsocket import data_ws
from my_fyers_model import MyFyersModel
from data_storage import get_parquet_manager
from index_constituents import get_nifty50_symbols
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout

# Initialize Rich console
console = Console()

class Nifty50WebSocketStreamer:
    def __init__(self):
        """Initialize the Nifty50 streaming system."""
        self.parquet_manager = get_parquet_manager()
        self.fyers_model = None
        self.websocket = None
        self.is_running = False
        self.data_buffer = []
        self.latest_data = {}
        self.message_count = 0
        self.start_time = datetime.now()
        self.save_interval = 60  # Save every 60 seconds
        self.last_save = datetime.now()
        
    def setup_authentication(self):
        """Setup FYERS authentication using our MyFyersModel."""
        try:
            console.print("🔐 Initializing FYERS authentication...", style="blue")
            self.fyers_model = MyFyersModel()
            access_token = self.fyers_model.get_access_token()
            console.print("✅ Authentication successful!", style="green")
            return access_token
        except Exception as e:
            console.print(f"❌ Authentication failed: {str(e)}", style="red")
            return None
    
    def get_nifty50_streaming_symbols(self):
        """Get Nifty50 symbols in FYERS format for streaming."""
        try:
            symbols = get_nifty50_symbols()
            # Convert to FYERS format
            fyers_symbols = []
            for symbol in symbols:
                if not symbol.startswith('NSE:'):
                    fyers_symbol = f"NSE:{symbol}-EQ"
                else:
                    fyers_symbol = symbol
                fyers_symbols.append(fyers_symbol)
            
            # Add Nifty50 Index
            fyers_symbols.append("NSE:NIFTY50-INDEX")
            
            return fyers_symbols[:25]  # Limit to 25 symbols for demo
        except Exception as e:
            console.print(f"⚠️ Error getting symbols, using defaults: {str(e)}", style="yellow")
            return [
                'NSE:RELIANCE-EQ', 'NSE:TCS-EQ', 'NSE:HDFCBANK-EQ',
                'NSE:INFY-EQ', 'NSE:ICICIBANK-EQ', 'NSE:KOTAKBANK-EQ',
                'NSE:HINDUNILVR-EQ', 'NSE:LT-EQ', 'NSE:SBIN-EQ',
                'NSE:BHARTIARTL-EQ', 'NSE:NIFTY50-INDEX'
            ]
    
    def onmessage(self, message):
        """Enhanced callback function to handle incoming WebSocket messages."""
        try:
            self.message_count += 1
            
            # Process message
            if isinstance(message, dict) and 'symbol' in message:
                symbol = message.get('symbol', 'Unknown')
                
                # Create standardized record
                record = {
                    'timestamp': datetime.now(),
                    'symbol': symbol,
                    'ltp': message.get('ltp', 0),
                    'open': message.get('o', 0),
                    'high': message.get('h', 0),
                    'low': message.get('l', 0),
                    'close': message.get('c', 0),
                    'volume': message.get('vol', 0),
                    'change': message.get('ch', 0),
                    'change_percent': message.get('chp', 0),
                    'avg_price': message.get('ap', 0),
                    'lower_circuit': message.get('lc', 0),
                    'upper_circuit': message.get('uc', 0)
                }
                
                # Update latest data for display
                self.latest_data[symbol] = record
                
                # Add to buffer
                self.data_buffer.append(record)
                
                # Auto-save based on interval
                if datetime.now() - self.last_save > timedelta(seconds=self.save_interval):
                    self.save_buffered_data()
                    
        except Exception as e:
            console.print(f"⚠️ Error processing message: {str(e)}", style="yellow")
    
    def save_buffered_data(self):
        """Save buffered data to Parquet storage."""
        if not self.data_buffer:
            return
        
        try:
            # Create DataFrame from buffer
            df = pd.DataFrame(self.data_buffer)
            
            # Save to our enhanced storage system
            for symbol in df['symbol'].unique():
                symbol_data = df[df['symbol'] == symbol].copy()
                # Clean symbol name for filename
                clean_symbol = symbol.replace('NSE:', '').replace('-EQ', '').replace('-INDEX', '').lower()
                
                # Save with timestamp
                filename = f"nifty50_stream_{clean_symbol}_{datetime.now().strftime('%Y%m%d')}"
                self.parquet_manager.save_data(
                    symbol_data, 
                    symbol=clean_symbol, 
                    timeframe='realtime',
                    mode='append'
                )
            
            console.print(f"💾 Saved {len(self.data_buffer)} records to storage", style="green")
            
            # Clear buffer
            self.data_buffer.clear()
            self.last_save = datetime.now()
            
        except Exception as e:
            console.print(f"❌ Error saving data: {str(e)}", style="red")
    
    def onerror(self, message):
        """Callback function to handle WebSocket errors."""
        console.print(f"🚨 WebSocket Error: {message}", style="red")
    
    def onclose(self, message):
        """Callback function to handle WebSocket connection close events."""
        console.print(f"🔌 Connection closed: {message}", style="yellow")
        self.is_running = False
        
        # Save any remaining buffered data
        if self.data_buffer:
            self.save_buffered_data()
    
    def onopen(self):
        """Callback function to subscribe to Nifty50 symbols upon WebSocket connection."""
        try:
            console.print("🌐 WebSocket connection established!", style="green")
            
            # Get Nifty50 symbols
            symbols = self.get_nifty50_streaming_symbols()
            
            console.print(f"📡 Subscribing to {len(symbols)} Nifty50 symbols...", style="blue")
            
            # Subscribe to SymbolUpdate data type
            self.websocket.subscribe(symbols=symbols, data_type="SymbolUpdate")
            self.is_running = True
            
            console.print("✅ Subscription successful! Streaming live data...", style="green")
            
            # Keep the socket running
            self.websocket.keep_running()
            
        except Exception as e:
            console.print(f"❌ Subscription failed: {str(e)}", style="red")
    
    def create_market_overview_table(self):
        """Create a comprehensive market overview table."""
        table = Table(show_header=True, header_style="bold magenta", title="📈 Nifty50 Live Portfolio")
        table.add_column("Symbol", style="cyan", width=12)
        table.add_column("LTP", justify="right", style="white", width=10)
        table.add_column("Change", justify="right", width=10)
        table.add_column("Change%", justify="right", width=10)
        table.add_column("Volume", justify="right", style="blue", width=12)
        table.add_column("H/L", justify="center", style="yellow", width=15)
        
        # Sort by change percentage
        sorted_data = sorted(
            self.latest_data.items(),
            key=lambda x: x[1].get('change_percent', 0),
            reverse=True
        )
        
        for symbol, data in sorted_data[:15]:  # Top 15
            change = data.get('change', 0)
            change_pct = data.get('change_percent', 0)
            
            # Determine color based on change
            if change > 0:
                change_style = "green"
                change_symbol = "+"
            elif change < 0:
                change_style = "red"
                change_symbol = ""
            else:
                change_style = "white"
                change_symbol = ""
            
            clean_symbol = symbol.split(':')[-1].replace('-EQ', '').replace('-INDEX', '')
            
            table.add_row(
                clean_symbol,
                f"₹{data.get('ltp', 0):.2f}",
                f"{change_symbol}{change:.2f}",
                f"{change_symbol}{change_pct:.2f}%",
                f"{data.get('volume', 0):,}",
                f"{data.get('high', 0):.1f}/{data.get('low', 0):.1f}",
                style=change_style
            )
        
        return table
    
    def create_statistics_panel(self):
        """Create statistics panel."""
        runtime = datetime.now() - self.start_time
        rate = self.message_count / max(runtime.total_seconds(), 1)
        
        stats = Table(show_header=False, box=None)
        stats.add_column("Metric", style="cyan")
        stats.add_column("Value", style="white")
        
        stats.add_row("📊 Messages", f"{self.message_count:,}")
        stats.add_row("⏱️ Runtime", f"{str(runtime).split('.')[0]}")
        stats.add_row("⚡ Rate", f"{rate:.1f}/sec")
        stats.add_row("📈 Active Symbols", f"{len(self.latest_data)}")
        stats.add_row("💾 Buffer Size", f"{len(self.data_buffer)}")
        
        # Calculate portfolio stats if we have data
        if self.latest_data:
            gainers = sum(1 for data in self.latest_data.values() if data.get('change', 0) > 0)
            losers = sum(1 for data in self.latest_data.values() if data.get('change', 0) < 0)
            
            stats.add_row("📈 Gainers", f"{gainers}")
            stats.add_row("📉 Losers", f"{losers}")
        
        return Panel(stats, title="📊 Live Statistics", border_style="blue")
    
    def run_stream(self, duration_minutes=30):
        """Run the Nifty50 WebSocket stream for specified duration."""
        access_token = self.setup_authentication()
        if not access_token:
            return False
        
        try:
            console.print("\n🚀 Starting Nifty50 Real-time Streaming", style="bold green")
            console.print(f"⏱️ Stream Duration: {duration_minutes} minutes", style="blue")
            console.print(f"💾 Auto-save interval: {self.save_interval} seconds", style="blue")
            
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
            with Live(self.create_dashboard(), refresh_per_second=2, screen=True) as live:
                end_time = time.time() + (duration_minutes * 60)
                
                while time.time() < end_time and self.is_running:
                    live.update(self.create_dashboard())
                    time.sleep(0.5)
            
            # Final save
            if self.data_buffer:
                self.save_buffered_data()
            
            console.print(f"\n✅ Stream completed! Processed {self.message_count:,} messages", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Stream failed: {str(e)}", style="red")
            return False
        
        finally:
            if self.websocket:
                try:
                    self.websocket.close()
                except:
                    pass
    
    def create_dashboard(self):
        """Create the main dashboard layout."""
        layout = Layout()
        
        layout.split_row(
            Layout(self.create_statistics_panel(), name="stats", size=25),
            Layout(self.create_market_overview_table(), name="market")
        )
        
        return Panel(
            layout,
            title="🏦 Fyers WebSocket Live - Nifty50 Portfolio Streaming Dashboard",
            border_style="bright_blue"
        )

def main():
    """Main function to run the Nifty50 streaming test."""
    streamer = Nifty50WebSocketStreamer()
    
    console.print("""
    🏦 [bold blue]Fyers WebSocket Live - Nifty50 Portfolio Streaming[/bold blue]
    
    This advanced demo will:
    • Stream live data for Nifty50 constituents
    • Display real-time portfolio dashboard
    • Auto-save data to Parquet storage every minute
    • Show professional analytics and statistics
    
    """)
    
    try:
        # Ask for stream duration
        duration = console.input("⏱️ Enter stream duration in minutes (default 10): ").strip()
        duration = int(duration) if duration.isdigit() else 10
        
        # Run the stream
        success = streamer.run_stream(duration)
        
        if success:
            console.print("\n🎉 [bold green]Nifty50 streaming completed successfully![/bold green]")
            console.print("💾 [blue]Data saved to Parquet storage for analysis![/blue]")
        else:
            console.print("\n❌ [red]Streaming failed. Please check your credentials.[/red]")
            
    except KeyboardInterrupt:
        console.print("\n⏹️ Stream interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {str(e)}", style="red")

if __name__ == "__main__":
    main()