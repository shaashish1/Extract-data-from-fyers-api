"""
Fyers Market Depth API Integration
===================================

Get complete market depth (Level 2 data) for symbols.

Features:
- Full order book with 5 bid/ask levels
- Total buy/sell quantities
- OHLCV data
- Circuit limits
- Open interest (for derivatives)
- Real-time depth updates

API Endpoint: https://api-t1.fyers.in/data/depth
Levels: 5 bid/ask levels (standard market depth)

Author: Fyers Trading Platform
Created: October 28, 2025
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import pandas as pd
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.auth.my_fyers_model import MyFyersModel
from scripts.core.rate_limit_manager import get_rate_limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FyersMarketDepthAPI:
    """
    Fyers Market Depth API Wrapper
    
    Get complete Level 2 market depth data including:
    - 5 levels of bid/ask
    - Total buy/sell quantities
    - OHLCV data
    - Circuit limits
    - Open Interest
    """
    
    def __init__(self):
        """Initialize the Market Depth API."""
        self.fyers = MyFyersModel()
        logger.info("Fyers Market Depth API initialized")
    
    def get_market_depth(self, symbol: str, include_ohlcv: bool = True) -> Optional[Dict]:
        """
        Get market depth for a symbol.
        
        Args:
            symbol: Symbol ticker (e.g., "NSE:SBIN-EQ")
            include_ohlcv: Include OHLCV data
        
        Returns:
            Dictionary with depth data or None on error
        """
        try:
            logger.info(f"Fetching market depth for {symbol}...")
            
            # CRITICAL: Use rate limiter to prevent API blocks
            limiter = get_rate_limiter()
            limiter.wait_if_needed()
            
            data = {
                "symbol": symbol,
                "ohlcv_flag": 1 if include_ohlcv else 0
            }
            
            response = self.fyers.get_fyre_model().depth(data=data)
            
            # Record request (success or failure)
            success = response and response.get('s') == 'ok'
            limiter.record_request(success=success)
            
            if response and response.get('s') == 'ok':
                logger.info(f"Successfully fetched market depth for {symbol}")
                return response
            else:
                logger.error(f"Market depth API error: {response}")
                return None
                
        except RuntimeError as e:
            logger.error(f"⛔ Rate limiter prevented execution: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch market depth: {e}")
            return None
    
    def parse_depth_response(self, symbol: str, response: Dict) -> Dict:
        """
        Parse market depth response into structured format.
        
        Args:
            symbol: Symbol ticker
            response: Raw API response
        
        Returns:
            Parsed depth data dictionary
        """
        if not response or response.get('s') != 'ok':
            return {}
        
        depth_data = response.get('d', {}).get(symbol, {})
        
        # Parse bid/ask levels
        bids = []
        asks = []
        
        for i in range(1, 6):  # 5 levels
            bids.append({
                'level': i,
                'price': depth_data.get(f'bid_price{i}', 0.0),
                'size': depth_data.get(f'bid_size{i}', 0),
                'orders': depth_data.get(f'bid_order{i}', 0)
            })
            asks.append({
                'level': i,
                'price': depth_data.get(f'ask_price{i}', 0.0),
                'size': depth_data.get(f'ask_size{i}', 0),
                'orders': depth_data.get(f'ask_order{i}', 0)
            })
        
        parsed = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            
            # Summary
            'total_buy_qty': depth_data.get('totalbuyqty', 0),
            'total_sell_qty': depth_data.get('totalsellqty', 0),
            
            # Current prices
            'ltp': depth_data.get('ltp', 0.0),
            'ltq': depth_data.get('ltq', 0),  # Last traded quantity
            'ltt': depth_data.get('ltt', 0),  # Last traded time
            
            # OHLCV
            'open': depth_data.get('o', 0.0),
            'high': depth_data.get('h', 0.0),
            'low': depth_data.get('l', 0.0),
            'close': depth_data.get('c', 0.0),
            'volume': depth_data.get('v', 0),
            'avg_price': depth_data.get('atp', 0.0),
            
            # Change
            'change': depth_data.get('ch', 0.0),
            'change_pct': depth_data.get('chp', 0.0),
            
            # Circuit limits
            'lower_circuit': depth_data.get('lower_ckt', 0.0),
            'upper_circuit': depth_data.get('upper_ckt', 0.0),
            
            # Open Interest (for derivatives)
            'oi': depth_data.get('oi', 0),
            'prev_oi': depth_data.get('pdoi', 0),
            'oi_change_pct': depth_data.get('oipercent', 0.0),
            
            # Tick size
            'tick_size': depth_data.get('tick_Size', 0.05),
            
            # Order book
            'bids': bids,
            'asks': asks
        }
        
        return parsed
    
    def display_depth(self, depth_data: Dict):
        """
        Display market depth in a formatted table.
        
        Args:
            depth_data: Parsed depth data
        """
        if not depth_data:
            print("No depth data available")
            return
        
        print("\n" + "="*100)
        print(f"Market Depth: {depth_data['symbol']}")
        print("="*100)
        
        # Summary
        print(f"\nLast Traded Price: ₹{depth_data['ltp']:.2f}")
        print(f"Change: ₹{depth_data['change']:.2f} ({depth_data['change_pct']:.2f}%)")
        print(f"Volume: {depth_data['volume']:,}")
        print(f"Total Buy Qty: {depth_data['total_buy_qty']:,} | Total Sell Qty: {depth_data['total_sell_qty']:,}")
        
        # OHLCV
        print(f"\nOHLC: Open={depth_data['open']:.2f} | High={depth_data['high']:.2f} | "
              f"Low={depth_data['low']:.2f} | Close={depth_data['close']:.2f}")
        
        # Circuit limits
        print(f"Circuits: Lower={depth_data['lower_circuit']:.2f} | Upper={depth_data['upper_circuit']:.2f}")
        
        # Open Interest (if available)
        if depth_data['oi'] > 0:
            print(f"\nOpen Interest: {depth_data['oi']:,} (Prev: {depth_data['prev_oi']:,}, "
                  f"Change: {depth_data['oi_change_pct']:.2f}%)")
        
        # Order Book
        print("\n" + "-"*100)
        print(f"{'BID':^45} | {'ASK':^45}")
        print(f"{'Orders':<8} {'Qty':<10} {'Price':<12} | {'Price':<12} {'Qty':<10} {'Orders':<8}")
        print("-"*100)
        
        for i in range(5):
            bid = depth_data['bids'][i]
            ask = depth_data['asks'][i]
            
            print(f"{bid['orders']:<8} {bid['size']:<10,} ₹{bid['price']:<11.2f} | "
                  f"₹{ask['price']:<11.2f} {ask['size']:<10,} {ask['orders']:<8}")
        
        print("-"*100)
    
    def get_depth_dataframe(self, depth_data: Dict) -> pd.DataFrame:
        """
        Convert depth data to DataFrame.
        
        Args:
            depth_data: Parsed depth data
        
        Returns:
            DataFrame with depth snapshot
        """
        if not depth_data:
            return pd.DataFrame()
        
        # Create a single row with all data
        row = {
            'timestamp': depth_data['timestamp'],
            'symbol': depth_data['symbol'],
            'ltp': depth_data['ltp'],
            'volume': depth_data['volume'],
            'total_buy_qty': depth_data['total_buy_qty'],
            'total_sell_qty': depth_data['total_sell_qty'],
            'open': depth_data['open'],
            'high': depth_data['high'],
            'low': depth_data['low'],
            'close': depth_data['close'],
            'change': depth_data['change'],
            'change_pct': depth_data['change_pct']
        }
        
        # Add bid levels
        for i, bid in enumerate(depth_data['bids'], 1):
            row[f'bid_price_{i}'] = bid['price']
            row[f'bid_size_{i}'] = bid['size']
            row[f'bid_orders_{i}'] = bid['orders']
        
        # Add ask levels
        for i, ask in enumerate(depth_data['asks'], 1):
            row[f'ask_price_{i}'] = ask['price']
            row[f'ask_size_{i}'] = ask['size']
            row[f'ask_orders_{i}'] = ask['orders']
        
        return pd.DataFrame([row])
    
    def save_depth(self, df: pd.DataFrame, symbol: str):
        """
        Save depth data to Parquet file.
        
        Args:
            df: DataFrame with depth data
            symbol: Symbol ticker
        """
        if df.empty:
            logger.warning("No data to save")
            return
        
        try:
            # Create output directory
            output_dir = project_root / "data" / "market_depth"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Clean symbol name for filename
            safe_symbol = symbol.replace(":", "_").replace("-", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = output_dir / f"{safe_symbol}_{timestamp}.parquet"
            
            df.to_parquet(filepath, index=False)
            logger.info(f"Saved market depth to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save depth data: {e}")


def demo_market_depth():
    """Demo: Get and display market depth."""
    print("="*100)
    print("Fyers Market Depth API Demo")
    print("="*100)
    
    depth_api = FyersMarketDepthAPI()
    
    # Test symbols
    symbols = [
        "NSE:SBIN-EQ",
        "NSE:NIFTY50-INDEX"
    ]
    
    for symbol in symbols:
        # Get market depth
        response = depth_api.get_market_depth(symbol)
        
        if response:
            # Parse and display
            depth_data = depth_api.parse_depth_response(symbol, response)
            depth_api.display_depth(depth_data)
            
            # Save to file
            df = depth_api.get_depth_dataframe(depth_data)
            depth_api.save_depth(df, symbol)
        
        print()


if __name__ == "__main__":
    demo_market_depth()
