#!/usr/bin/env python3
"""
Market Depth Display for Nifty 50 Stocks
=========================================

This script fetches and displays market depth (Level 2) data for all Nifty 50 stocks,
showing the complete order book with bid/ask levels, volumes, and order counts.

Features:
- Real-time market depth for all 50 Nifty stocks
- Complete order book (5 levels each side)
- Current quotes (OHLC, LTP, volume)
- Bid-ask spread analysis
- Order flow statistics
- Beautiful formatted display

Author: Fyers API Integration Team
Date: October 26, 2025
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import time
import json
from typing import Dict, List, Optional, Tuple

# Add scripts directory to Python path for imports
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.append(str(script_dir))

from my_fyers_model import MyFyersModel
from symbol_discovery import SymbolDiscovery


class MarketDepthAnalyzer:
    """
    Comprehensive market depth analyzer for Nifty 50 stocks
    """
    
    def __init__(self):
        """Initialize the market depth analyzer"""
        self.fyers_model = MyFyersModel()
        self.symbol_discovery = SymbolDiscovery()
        self.nifty50_symbols = []
        self.market_data = {}
        self.start_time = datetime.now()
        
        print("🔍 NIFTY 50 MARKET DEPTH ANALYZER")
        print("=" * 80)
        print(f"📅 Session: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def load_nifty50_symbols(self):
        """Load Nifty 50 symbol list"""
        try:
            print("📊 Loading Nifty 50 symbols...")
            self.nifty50_symbols = self.symbol_discovery.get_nifty50_constituents()
            print(f"✅ Loaded {len(self.nifty50_symbols)} Nifty 50 symbols")
            return True
        except Exception as e:
            print(f"❌ Error loading symbols: {e}")
            return False
    
    def get_market_depth(self, symbol: str) -> Optional[Dict]:
        """
        Get market depth data for a single symbol
        
        Args:
            symbol: Symbol in Fyers format (e.g., 'NSE:RELIANCE-EQ')
            
        Returns:
            Market depth data or None if error
        """
        try:
            data = {
                "symbol": symbol,
                "ohlcv_flag": "1"
            }
            
            response = self.fyers_model.fyers_model.depth(data=data)
            
            if response and response.get('s') == 'ok':
                return response.get('d', {}).get(symbol, {})
            else:
                print(f"⚠️  Error for {symbol}: {response.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Exception for {symbol}: {e}")
            return None
    
    def format_price(self, price: float) -> str:
        """Format price with proper decimal places"""
        return f"₹{price:.2f}"
    
    def format_volume(self, volume: int) -> str:
        """Format volume with commas"""
        if volume >= 10000000:  # 1 crore
            return f"{volume/10000000:.1f}Cr"
        elif volume >= 100000:  # 1 lakh
            return f"{volume/100000:.1f}L"
        else:
            return f"{volume:,}"
    
    def format_percentage(self, value: float) -> str:
        """Format percentage with color coding"""
        if value > 0:
            return f"📈 +{value:.2f}%"
        elif value < 0:
            return f"📉 {value:.2f}%"
        else:
            return f"➡️  {value:.2f}%"
    
    def calculate_spread(self, bids: List, asks: List) -> Tuple[float, float]:
        """Calculate bid-ask spread"""
        if not bids or not asks:
            return 0.0, 0.0
        
        best_bid = bids[0]['price']
        best_ask = asks[0]['price']
        spread = best_ask - best_bid
        spread_percent = (spread / best_ask) * 100 if best_ask > 0 else 0
        
        return spread, spread_percent
    
    def display_market_depth(self, symbol: str, data: Dict):
        """Display market depth for a single symbol"""
        try:
            symbol_name = symbol.replace('NSE:', '').replace('-EQ', '')
            
            print(f"\n🏢 {symbol_name} ({symbol})")
            print("-" * 75)
            
            # Current quote information
            ltp = data.get('ltp', 0)
            change = data.get('ch', 0)
            change_percent = data.get('chp', 0)
            volume = data.get('v', 0)
            open_price = data.get('o', 0)
            high_price = data.get('h', 0)
            low_price = data.get('l', 0)
            atp = data.get('atp', 0)
            
            print(f"💰 LTP: {self.format_price(ltp)} | "
                  f"Change: {self.format_percentage(change_percent)} "
                  f"({self.format_price(change)})")
            print(f"📊 OHLC: {self.format_price(open_price)} | "
                  f"{self.format_price(high_price)} | "
                  f"{self.format_price(low_price)} | "
                  f"{self.format_price(ltp)}")
            print(f"📈 Volume: {self.format_volume(volume)} | "
                  f"ATP: {self.format_price(atp)}")
            
            # Market depth data
            bids = data.get('bids', [])
            asks = data.get('ask', [])
            total_buy_qty = data.get('totalbuyqty', 0)
            total_sell_qty = data.get('totalsellqty', 0)
            
            spread, spread_percent = self.calculate_spread(bids, asks)
            
            print(f"\n📋 Market Depth (Spread: {self.format_price(spread)} "
                  f"/ {spread_percent:.3f}%)")
            print(f"{'BID SIDE':<35} | {'ASK SIDE'}")
            print(f"{'Price':<12} {'Volume':<12} {'Orders':<8} | "
                  f"{'Price':<12} {'Volume':<12} {'Orders'}")
            print("-" * 75)
            
            # Display 5 levels of market depth
            max_levels = max(len(bids), len(asks), 5)
            
            for i in range(max_levels):
                # Bid side
                if i < len(bids):
                    bid = bids[i]
                    bid_str = (f"{self.format_price(bid['price']):<12} "
                             f"{self.format_volume(bid['volume']):<12} "
                             f"{bid['ord']:<8}")
                else:
                    bid_str = f"{'---':<12} {'---':<12} {'---':<8}"
                
                # Ask side
                if i < len(asks):
                    ask = asks[i]
                    ask_str = (f"{self.format_price(ask['price']):<12} "
                             f"{self.format_volume(ask['volume']):<12} "
                             f"{ask['ord']}")
                else:
                    ask_str = f"{'---':<12} {'---':<12} {'---'}"
                
                print(f"{bid_str} | {ask_str}")
            
            print("-" * 75)
            print(f"📊 Total Buy Qty: {self.format_volume(total_buy_qty)} | "
                  f"Total Sell Qty: {self.format_volume(total_sell_qty)}")
            
            # Order flow analysis
            buy_sell_ratio = total_buy_qty / total_sell_qty if total_sell_qty > 0 else 0
            if buy_sell_ratio > 1.1:
                flow_indicator = "🟢 Bullish Flow"
            elif buy_sell_ratio < 0.9:
                flow_indicator = "🔴 Bearish Flow"
            else:
                flow_indicator = "🟡 Neutral Flow"
            
            print(f"🔄 Order Flow: {flow_indicator} (Ratio: {buy_sell_ratio:.2f})")
            
        except Exception as e:
            print(f"❌ Error displaying data for {symbol}: {e}")
    
    def get_all_market_depth(self):
        """Get market depth for all Nifty 50 symbols"""
        print(f"\n🚀 Fetching market depth for {len(self.nifty50_symbols)} symbols...")
        print("⏱️  This may take a few minutes due to API rate limits...")
        
        successful = 0
        failed = 0
        
        for i, symbol in enumerate(self.nifty50_symbols, 1):
            try:
                print(f"\n📡 [{i:2d}/{len(self.nifty50_symbols)}] Fetching: {symbol}")
                
                depth_data = self.get_market_depth(symbol)
                
                if depth_data:
                    self.market_data[symbol] = depth_data
                    self.display_market_depth(symbol, depth_data)
                    successful += 1
                else:
                    print(f"❌ Failed to get data for {symbol}")
                    failed += 1
                
                # Rate limiting - respect API limits
                if i < len(self.nifty50_symbols):
                    time.sleep(1)  # 1 second delay between calls
                    
            except KeyboardInterrupt:
                print(f"\n🛑 Interrupted by user at symbol {i}")
                break
            except Exception as e:
                print(f"❌ Error processing {symbol}: {e}")
                failed += 1
        
        return successful, failed
    
    def display_summary(self, successful: int, failed: int):
        """Display session summary"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("📊 MARKET DEPTH ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"⏱️  Session Duration: {duration.total_seconds():.1f} seconds")
        print(f"✅ Successful: {successful} symbols")
        print(f"❌ Failed: {failed} symbols")
        print(f"📊 Total Symbols: {len(self.nifty50_symbols)}")
        print(f"📈 Success Rate: {(successful/len(self.nifty50_symbols)*100):.1f}%")
        
        if self.market_data:
            print(f"\n🎯 Top Performers by Volume:")
            # Sort by volume and show top 5
            sorted_symbols = sorted(
                self.market_data.items(),
                key=lambda x: x[1].get('v', 0),
                reverse=True
            )[:5]
            
            for symbol, data in sorted_symbols:
                symbol_name = symbol.replace('NSE:', '').replace('-EQ', '')
                volume = data.get('v', 0)
                ltp = data.get('ltp', 0)
                change_percent = data.get('chp', 0)
                print(f"  📈 {symbol_name:<15} Volume: {self.format_volume(volume):<10} "
                      f"LTP: {self.format_price(ltp):<10} "
                      f"Change: {self.format_percentage(change_percent)}")
        
        print("\n🔄 Data can be refreshed by running this script again")
        print("💡 Consider scheduling this for regular market monitoring")
        print("=" * 80)
    
    def save_market_data(self):
        """Save market data to JSON file for analysis"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nifty50_market_depth_{timestamp}.json"
            filepath = Path("data/market_depth") / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            save_data = {
                "timestamp": self.start_time.isoformat(),
                "total_symbols": len(self.nifty50_symbols),
                "successful_symbols": len(self.market_data),
                "market_data": self.market_data
            }
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"💾 Market data saved to: {filepath}")
            
        except Exception as e:
            print(f"⚠️  Could not save market data: {e}")
    
    def run_analysis(self):
        """Run the complete market depth analysis"""
        try:
            # Load symbols
            if not self.load_nifty50_symbols():
                return False
            
            # Get market depth for all symbols
            successful, failed = self.get_all_market_depth()
            
            # Display summary
            self.display_summary(successful, failed)
            
            # Save data
            if self.market_data:
                self.save_market_data()
            
            return True
            
        except Exception as e:
            print(f"❌ Critical error in analysis: {e}")
            return False


def main():
    """Main execution function"""
    print("🚀 NIFTY 50 MARKET DEPTH ANALYZER")
    print("=" * 80)
    print("📊 This script fetches real-time market depth for all Nifty 50 stocks")
    print("⏱️  Estimated time: 1-2 minutes (due to API rate limits)")
    print("🔄 Press Ctrl+C to interrupt if needed")
    print("=" * 80)
    
    analyzer = MarketDepthAnalyzer()
    
    try:
        success = analyzer.run_analysis()
        
        if success:
            print("\n✅ Analysis completed successfully!")
        else:
            print("\n❌ Analysis completed with errors")
            
    except KeyboardInterrupt:
        print("\n🛑 Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")


if __name__ == "__main__":
    main()