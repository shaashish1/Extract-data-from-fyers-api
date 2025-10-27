#!/usr/bin/env python3
"""
Dynamic Nifty 50 Market Depth Analyzer
=======================================

Uses dynamic symbol discovery to always get current Nifty 50 constituents
and provide real-time market depth analysis.

Features:
- Dynamic symbol discovery from Fyers API
- Auto-refresh of symbol list
- Full order book analysis
- Real-time market data
- Future-proof against index changes

Author: Fyers API Integration Team
Date: October 26, 2025
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Optional, Tuple

# Add scripts directory to Python path for imports
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.append(str(script_dir))

from my_fyers_model import MyFyersModel
from fyers_symbol_discovery import FyersSymbolDiscovery


class DynamicMarketDepthAnalyzer:
    """
    Dynamic market depth analyzer that automatically discovers current Nifty 50 constituents
    """
    
    def __init__(self, auto_refresh_symbols=True):
        """Initialize the dynamic market depth analyzer"""
        self.fyers_model = MyFyersModel()
        self.symbol_discovery = FyersSymbolDiscovery()
        self.nifty50_symbols = []
        self.market_data = {}
        self.start_time = datetime.now()
        self.auto_refresh = auto_refresh_symbols
        
    def get_current_nifty50_symbols(self) -> List[str]:
        """Get current Nifty 50 symbols with smart caching and refresh logic"""
        print("🔍 Getting current Nifty 50 symbols...")
        
        # Check if we have recent symbols saved
        symbols_file = Path("data/symbols/current_nifty50_fyers.json")
        
        should_refresh = True
        if symbols_file.exists() and not self.auto_refresh:
            try:
                with open(symbols_file, 'r') as f:
                    data = json.load(f)
                
                # Check if symbols are recent (less than 7 days old)
                timestamp_str = data.get('timestamp', '')
                if timestamp_str:
                    saved_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    age_days = (datetime.now() - saved_time.replace(tzinfo=None)).days
                    
                    if age_days < 7 and len(data.get('symbols', [])) == 50:
                        print(f"📂 Using saved symbols (age: {age_days} days)")
                        should_refresh = False
                        return data['symbols']
                    else:
                        print(f"⚠️  Saved symbols are {age_days} days old, refreshing...")
                        
            except Exception as e:
                print(f"⚠️  Error reading saved symbols: {e}")
        
        if should_refresh or self.auto_refresh:
            print("🔄 Discovering current Nifty 50 constituents...")
            symbols = self.symbol_discovery.get_current_nifty50_dynamic()
            
            if symbols and len(symbols) >= 45:  # Accept if we have at least 45 symbols
                self.symbol_discovery.save_discovered_nifty50(symbols)
                return symbols
            else:
                print("⚠️  Dynamic discovery failed, using fallback symbols")
                return self._get_fallback_symbols()
        
        return self._get_fallback_symbols()
    
    def _get_fallback_symbols(self) -> List[str]:
        """Fallback symbols if dynamic discovery fails"""
        return [
            'NSE:RELIANCE-EQ', 'NSE:TCS-EQ', 'NSE:HDFCBANK-EQ',
            'NSE:INFY-EQ', 'NSE:ICICIBANK-EQ', 'NSE:SBIN-EQ',
            'NSE:BHARTIARTL-EQ', 'NSE:ITC-EQ', 'NSE:KOTAKBANK-EQ',
            'NSE:LT-EQ', 'NSE:ASIANPAINT-EQ', 'NSE:MARUTI-EQ',
            'NSE:AXISBANK-EQ', 'NSE:HCLTECH-EQ', 'NSE:WIPRO-EQ',
            'NSE:NESTLEIND-EQ', 'NSE:ULTRACEMCO-EQ', 'NSE:BAJFINANCE-EQ',
            'NSE:ONGC-EQ', 'NSE:POWERGRID-EQ', 'NSE:NTPC-EQ',
            'NSE:TECHM-EQ', 'NSE:HINDUNILVR-EQ', 'NSE:SUNPHARMA-EQ', 
            'NSE:TITAN-EQ', 'NSE:DRREDDY-EQ', 'NSE:BAJAJFINSV-EQ', 
            'NSE:COALINDIA-EQ', 'NSE:INDUSINDBK-EQ', 'NSE:TATASTEEL-EQ', 
            'NSE:ADANIPORTS-EQ', 'NSE:JSWSTEEL-EQ', 'NSE:HINDALCO-EQ', 
            'NSE:GRASIM-EQ', 'NSE:BRITANNIA-EQ', 'NSE:CIPLA-EQ', 
            'NSE:DIVISLAB-EQ', 'NSE:BAJAJ-AUTO-EQ', 'NSE:EICHERMOT-EQ', 
            'NSE:HEROMOTOCO-EQ', 'NSE:APOLLOHOSP-EQ', 'NSE:BPCL-EQ', 
            'NSE:ADANIENT-EQ', 'NSE:SBILIFE-EQ', 'NSE:LTIM-EQ',
            'NSE:SHRIRAMFIN-EQ', 'NSE:M&M-EQ', 'NSE:PIDILITIND-EQ',
            'NSE:IOC-EQ', 'NSE:HDFCLIFE-EQ', 'NSE:TATACONSUM-EQ'
        ]
    
    def load_nifty50_symbols(self):
        """Load current Nifty 50 symbols"""
        try:
            self.nifty50_symbols = self.get_current_nifty50_symbols()
            
            if self.nifty50_symbols:
                print(f"✅ Loaded {len(self.nifty50_symbols)} Nifty 50 symbols")
                
                # Show first few symbols
                print("📋 Sample symbols:")
                for i, symbol in enumerate(self.nifty50_symbols[:5]):
                    stock_name = symbol.replace('NSE:', '').replace('-EQ', '')
                    print(f"  {i+1}. {stock_name}")
                print(f"  ... and {len(self.nifty50_symbols) - 5} more")
                
                return True
            else:
                print("❌ Failed to load symbols")
                return False
                
        except Exception as e:
            print(f"❌ Error loading symbols: {e}")
            return False
        
    def get_market_depth(self, symbol: str) -> Optional[Dict]:
        """
        Get market depth data for a symbol
        """
        try:
            data = {
                "symbol": symbol,
                "ohlcv_flag": "1"
            }
            
            response = self.fyers_model.fyers_model.depth(data=data)
            
            if response and response.get('s') == 'ok':
                symbol_data = response.get('d', {}).get(symbol, {})
                if symbol_data:
                    return symbol_data
                else:
                    print(f"⚠️  No data returned for {symbol}")
                    return None
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
        
        # Find first non-zero bid and ask
        best_bid = 0
        best_ask = 0
        
        for bid in bids:
            if bid.get('price', 0) > 0:
                best_bid = bid['price']
                break
                
        for ask in asks:
            if ask.get('price', 0) > 0:
                best_ask = ask['price']
                break
        
        if best_bid > 0 and best_ask > 0:
            spread = best_ask - best_bid
            spread_percent = (spread / best_ask) * 100
            return spread, spread_percent
        
        return 0.0, 0.0
    
    def display_market_depth(self, symbol: str, data: Dict):
        """Display market depth for a single symbol"""
        try:
            symbol_name = symbol.replace('NSE:', '').replace('-EQ', '')
            
            print(f"\n🏢 {symbol_name} ({symbol})")
            print("-" * 85)
            
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
            
            # Filter out zero-price levels
            active_bids = [bid for bid in bids if bid.get('price', 0) > 0]
            active_asks = [ask for ask in asks if ask.get('price', 0) > 0]
            
            spread, spread_percent = self.calculate_spread(bids, asks)
            
            print(f"\n📋 Market Depth - Full Order Book")
            print(f"   Bid Levels: {len(active_bids)} | Ask Levels: {len(active_asks)} | "
                  f"Spread: {self.format_price(spread)} ({spread_percent:.3f}%)")
            print(f"{'BID SIDE':<40} | {'ASK SIDE'}")
            print(f"{'Price':<12} {'Volume':<12} {'Orders':<8} {'%':<6} | "
                  f"{'Price':<12} {'Volume':<12} {'Orders':<8} {'%'}")
            print("-" * 85)
            
            # Display all available levels
            max_levels = max(len(bids), len(asks))
            
            for i in range(max_levels):
                # Bid side
                if i < len(bids) and bids[i].get('price', 0) > 0:
                    bid = bids[i]
                    bid_vol_pct = (bid['volume'] / total_buy_qty * 100) if total_buy_qty > 0 else 0
                    bid_str = (f"{self.format_price(bid['price']):<12} "
                             f"{self.format_volume(bid['volume']):<12} "
                             f"{bid['ord']:<8} "
                             f"{bid_vol_pct:.1f}%")
                    bid_str = f"{bid_str:<40}"
                else:
                    bid_str = f"{'---':<12} {'---':<12} {'---':<8} {'---':<6}"
                    bid_str = f"{bid_str:<40}"
                
                # Ask side
                if i < len(asks) and asks[i].get('price', 0) > 0:
                    ask = asks[i]
                    ask_vol_pct = (ask['volume'] / total_sell_qty * 100) if total_sell_qty > 0 else 0
                    ask_str = (f"{self.format_price(ask['price']):<12} "
                             f"{self.format_volume(ask['volume']):<12} "
                             f"{ask['ord']:<8} "
                             f"{ask_vol_pct:.1f}%")
                else:
                    ask_str = f"{'---':<12} {'---':<12} {'---':<8} {'---'}"
                
                print(f"{bid_str} | {ask_str}")
            
            print("-" * 85)
            print(f"📊 Total Buy Qty: {self.format_volume(total_buy_qty)} | "
                  f"Total Sell Qty: {self.format_volume(total_sell_qty)}")
            
            # Enhanced order flow analysis
            buy_sell_ratio = total_buy_qty / total_sell_qty if total_sell_qty > 0 else float('inf')
            
            if total_buy_qty == 0 and total_sell_qty == 0:
                flow_indicator = "⚪ No Orders"
            elif buy_sell_ratio == float('inf'):
                flow_indicator = "🟢 Only Buyers"
            elif buy_sell_ratio == 0:
                flow_indicator = "🔴 Only Sellers"
            elif buy_sell_ratio > 2.0:
                flow_indicator = "🟢🟢 Strong Buy"
            elif buy_sell_ratio > 1.5:
                flow_indicator = "🟢 Bullish Flow"
            elif buy_sell_ratio < 0.5:
                flow_indicator = "🔴 Bearish Flow"
            elif buy_sell_ratio < 0.3:
                flow_indicator = "🔴🔴 Strong Sell"
            else:
                flow_indicator = "🟡 Balanced Flow"
            
            ratio_display = f"{buy_sell_ratio:.2f}" if buy_sell_ratio != float('inf') else "∞"
            print(f"🔄 Order Flow: {flow_indicator} (B/S Ratio: {ratio_display})")
            
        except Exception as e:
            print(f"❌ Error displaying depth for {symbol}: {e}")
    
    def analyze_all_stocks(self):
        """Analyze market depth for all current Nifty 50 stocks"""
        print(f"\n🚀 Dynamic Nifty 50 Market Depth Analysis")
        print(f"📅 Using symbols discovered: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Total symbols: {len(self.nifty50_symbols)}")
        print(f"⏰ Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        successful = 0
        failed = 0
        invalid_symbols = []
        
        for i, symbol in enumerate(self.nifty50_symbols, 1):
            try:
                print(f"\n📡 [{i:2d}/{len(self.nifty50_symbols)}] Fetching: {symbol}")
                
                depth_data = self.get_market_depth(symbol)
                
                if depth_data:
                    self.display_market_depth(symbol, depth_data)
                    self.market_data[symbol] = depth_data
                    successful += 1
                else:
                    print(f"❌ Failed to get data for {symbol}")
                    invalid_symbols.append(symbol)
                    failed += 1
                
                # Rate limiting
                if i < len(self.nifty50_symbols):
                    time.sleep(0.5)
                    
            except Exception as e:
                print(f"❌ Error processing {symbol}: {e}")
                invalid_symbols.append(symbol)
                failed += 1
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n" + "=" * 85)
        print(f"📊 DYNAMIC NIFTY 50 MARKET DEPTH ANALYSIS SUMMARY")
        print(f"=" * 85)
        print(f"⏱️  Session Duration: {duration:.1f} seconds")
        print(f"✅ Successful: {successful} symbols")
        print(f"❌ Failed: {failed} symbols")
        print(f"📊 Total Symbols: {len(self.nifty50_symbols)}")
        print(f"📈 Success Rate: {(successful/len(self.nifty50_symbols)*100):.1f}%")
        
        # Show invalid symbols for future symbol list updates
        if invalid_symbols:
            print(f"\n⚠️  Invalid symbols found (may need symbol list update):")
            for symbol in invalid_symbols:
                print(f"  • {symbol}")
            print(f"💡 Consider running symbol refresh to update the list")
        
        # Top performers by volume
        if self.market_data:
            print(f"\n🎯 Top Performers by Volume:")
            sorted_by_volume = sorted(
                self.market_data.items(),
                key=lambda x: x[1].get('v', 0),
                reverse=True
            )[:5]
            
            for symbol, data in sorted_by_volume:
                volume = data.get('v', 0)
                ltp = data.get('ltp', 0)
                change_pct = data.get('chp', 0)
                symbol_name = symbol.replace('NSE:', '').replace('-EQ', '')
                print(f"  📈 {symbol_name:<12} Volume: {self.format_volume(volume):<12} "
                      f"LTP: {self.format_price(ltp):<12} Change: {self.format_percentage(change_pct)}")
        
        # Save data
        self.save_market_data()
        
        print(f"\n🔄 Symbol list auto-refreshes to stay current with Nifty 50 changes")
        print(f"💡 Analysis uses dynamically discovered symbols - always up to date!")
        print(f"=" * 85)
        print(f"✅ Dynamic analysis completed successfully!")
    
    def save_market_data(self):
        """Save market data to JSON file"""
        try:
            data_dir = Path("data/market_depth")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dynamic_nifty50_depth_{timestamp}.json"
            filepath = data_dir / filename
            
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "session_duration": (datetime.now() - self.start_time).total_seconds(),
                "total_symbols": len(self.nifty50_symbols),
                "successful_symbols": len(self.market_data),
                "symbol_source": "dynamic_fyers_discovery",
                "symbols_used": self.nifty50_symbols,
                "market_data": self.market_data
            }
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
            
            print(f"💾 Dynamic market data saved to: {filepath}")
            
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def run_analysis(self):
        """Main method to run the dynamic analysis"""
        try:
            print("🚀 DYNAMIC NIFTY 50 MARKET DEPTH ANALYZER")
            print("=" * 85)
            print("🎯 Features: Dynamic symbol discovery, auto-refresh, future-proof")
            print("🔄 Symbols are automatically updated to reflect current Nifty 50 constituents")
            
            if not self.load_nifty50_symbols():
                print("❌ Failed to load symbols")
                return False
            
            self.analyze_all_stocks()
            return True
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return False


def main():
    """Main function"""
    print("Choose analysis mode:")
    print("1. Auto-refresh symbols (recommended - always current)")
    print("2. Use cached symbols (faster, but may be outdated)")
    
    try:
        choice = input("\nEnter choice (1-2, default=1): ").strip() or "1"
        
        auto_refresh = choice == "1"
        
        analyzer = DynamicMarketDepthAnalyzer(auto_refresh_symbols=auto_refresh)
        analyzer.run_analysis()
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()