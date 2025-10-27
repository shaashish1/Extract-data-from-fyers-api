"""
Market Depth (Order Book/DOM) Data Storage Module
Handles Level 2 market data from Fyers API
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from my_fyers_model import MyFyersModel
from data_storage import get_parquet_manager
from constants import time_zone


class MarketDepthManager:
    """Manages market depth (Level 2) data storage and analysis"""
    
    def __init__(self, base_data_dir="data/parquet"):
        self.fyers = MyFyersModel()
        self.base_data_dir = Path(base_data_dir)
        
        # Create market depth directories
        self.depth_dir = self.base_data_dir / "market_depth"
        self.depth_dir.mkdir(parents=True, exist_ok=True)
        
        self.indices_depth = self.depth_dir / "indices"
        self.stocks_depth = self.depth_dir / "stocks"
        self.options_depth = self.depth_dir / "options"
        
        for dir_path in [self.indices_depth, self.stocks_depth, self.options_depth]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_market_depth(self, symbol: str) -> Optional[Dict]:
        """
        Fetch current market depth for a symbol
        
        Args:
            symbol (str): Trading symbol (e.g., 'NSE:HDFCBANK-EQ')
            
        Returns:
            Optional[Dict]: Market depth data or None
        """
        try:
            data = {
                'symbol': symbol,
                'ohlcv_flag': '1'
            }
            
            result = self.fyers.get_market_depth(data)
            
            if result.get('s') == 'ok' and 'd' in result:
                depth_data = result['d'].get(symbol, {})
                
                if depth_data:
                    # Add timestamp
                    depth_data['timestamp'] = datetime.now()
                    depth_data['symbol'] = symbol
                    
                    return depth_data
            
            return None
            
        except Exception as e:
            print(f"Error fetching market depth for {symbol}: {e}")
            return None
    
    def parse_depth_data(self, raw_depth: Dict) -> Dict:
        """
        Parse raw depth data into structured format
        
        Args:
            raw_depth (Dict): Raw market depth data from Fyers
            
        Returns:
            Dict: Parsed and structured depth data
        """
        try:
            parsed = {
                'timestamp': raw_depth.get('timestamp'),
                'symbol': raw_depth.get('symbol'),
                
                # OHLCV Data
                'open': raw_depth.get('o', 0),
                'high': raw_depth.get('h', 0),
                'low': raw_depth.get('l', 0),
                'close': raw_depth.get('c', 0),
                'ltp': raw_depth.get('ltp', 0),
                'volume': raw_depth.get('v', 0),
                'atp': raw_depth.get('atp', 0),  # Average traded price
                
                # Price Changes
                'change': raw_depth.get('ch', 0),
                'change_percent': raw_depth.get('chp', 0),
                
                # Circuit Limits
                'upper_circuit': raw_depth.get('upper_ckt', 0),
                'lower_circuit': raw_depth.get('lower_ckt', 0),
                
                # Order Book Totals
                'total_buy_qty': raw_depth.get('totalbuyqty', 0),
                'total_sell_qty': raw_depth.get('totalsellqty', 0),
                
                # Last Trade Info
                'last_traded_qty': raw_depth.get('ltq', 0),
                'last_traded_time': raw_depth.get('ltt', 0),
                
                # Options specific (if available)
                'open_interest': raw_depth.get('oi', 0),
                'prev_day_oi': raw_depth.get('pdoi', 0),
                'oi_percent_change': raw_depth.get('oipercent', 0),
                
                # Tick size
                'tick_size': raw_depth.get('tick_Size', 0),
            }
            
            # Parse bid levels (up to 5 levels)
            bid_data = raw_depth.get('bids', [])
            for i in range(5):
                if i < len(bid_data):
                    bid = bid_data[i]
                    parsed[f'bid_price_{i+1}'] = bid.get('price', 0)
                    parsed[f'bid_volume_{i+1}'] = bid.get('volume', 0)
                    parsed[f'bid_orders_{i+1}'] = bid.get('ord', 0)
                else:
                    parsed[f'bid_price_{i+1}'] = 0
                    parsed[f'bid_volume_{i+1}'] = 0
                    parsed[f'bid_orders_{i+1}'] = 0
            
            # Parse ask levels (up to 5 levels)
            ask_data = raw_depth.get('ask', [])
            for i in range(5):
                if i < len(ask_data):
                    ask = ask_data[i]
                    parsed[f'ask_price_{i+1}'] = ask.get('price', 0)
                    parsed[f'ask_volume_{i+1}'] = ask.get('volume', 0)
                    parsed[f'ask_orders_{i+1}'] = ask.get('ord', 0)
                else:
                    parsed[f'ask_price_{i+1}'] = 0
                    parsed[f'ask_volume_{i+1}'] = 0
                    parsed[f'ask_orders_{i+1}'] = 0
            
            # Calculate derived metrics
            best_bid = parsed['bid_price_1']
            best_ask = parsed['ask_price_1']
            
            if best_bid > 0 and best_ask > 0:
                parsed['spread'] = best_ask - best_bid
                parsed['spread_percent'] = (parsed['spread'] / best_ask) * 100
                parsed['mid_price'] = (best_bid + best_ask) / 2
            else:
                parsed['spread'] = 0
                parsed['spread_percent'] = 0
                parsed['mid_price'] = parsed['ltp']
            
            # Order imbalance
            total_bid_vol = sum(parsed[f'bid_volume_{i+1}'] for i in range(5))
            total_ask_vol = sum(parsed[f'ask_volume_{i+1}'] for i in range(5))
            
            if total_bid_vol + total_ask_vol > 0:
                parsed['order_imbalance'] = (total_bid_vol - total_ask_vol) / (total_bid_vol + total_ask_vol)
            else:
                parsed['order_imbalance'] = 0
            
            return parsed
            
        except Exception as e:
            print(f"Error parsing depth data: {e}")
            return {}
    
    def save_depth_snapshot(self, symbol: str, depth_data: Dict) -> bool:
        """
        Save a single market depth snapshot
        
        Args:
            symbol (str): Trading symbol
            depth_data (Dict): Parsed depth data
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Determine file path based on symbol type
            symbol_clean = symbol.replace(':', '_').replace('-', '_')
            
            if any(idx in symbol.lower() for idx in ['nifty', 'bank', 'finnifty', 'indiavix']):
                file_path = self.indices_depth / f"{symbol_clean}_depth.parquet"
            elif symbol.lower().endswith('_option') or 'ce' in symbol.lower() or 'pe' in symbol.lower():
                file_path = self.options_depth / f"{symbol_clean}_depth.parquet"
            else:
                file_path = self.stocks_depth / f"{symbol_clean}_depth.parquet"
            
            # Convert to DataFrame
            df_new = pd.DataFrame([depth_data])
            
            # Append to existing file or create new
            if file_path.exists():
                # Read existing data
                df_existing = pd.read_parquet(file_path)
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                
                # Remove duplicates based on timestamp (keep latest)
                df_combined = df_combined.drop_duplicates(subset=['timestamp'], keep='last')
                
                # Keep only last 10,000 records for storage efficiency
                if len(df_combined) > 10000:
                    df_combined = df_combined.tail(10000)
                
                df_combined.to_parquet(file_path, compression='snappy', index=False)
            else:
                df_new.to_parquet(file_path, compression='snappy', index=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving depth snapshot for {symbol}: {e}")
            return False
    
    def collect_and_save_depth(self, symbol: str) -> bool:
        """
        Collect current market depth and save it
        
        Args:
            symbol (str): Trading symbol
            
        Returns:
            bool: True if successful
        """
        try:
            # Get raw depth data
            raw_depth = self.get_market_depth(symbol)
            
            if raw_depth:
                # Parse the data
                parsed_depth = self.parse_depth_data(raw_depth)
                
                if parsed_depth:
                    # Save to Parquet
                    return self.save_depth_snapshot(symbol, parsed_depth)
            
            return False
            
        except Exception as e:
            print(f"Error collecting depth for {symbol}: {e}")
            return False
    
    def get_depth_history(self, symbol: str, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Get historical market depth data for a symbol
        
        Args:
            symbol (str): Trading symbol
            start_date (Optional[str]): Start date (YYYY-MM-DD)
            end_date (Optional[str]): End date (YYYY-MM-DD)
            
        Returns:
            Optional[pd.DataFrame]: Historical depth data or None
        """
        try:
            symbol_clean = symbol.replace(':', '_').replace('-', '_')
            
            # Determine file path
            if any(idx in symbol.lower() for idx in ['nifty', 'bank', 'finnifty', 'indiavix']):
                file_path = self.indices_depth / f"{symbol_clean}_depth.parquet"
            elif symbol.lower().endswith('_option') or 'ce' in symbol.lower() or 'pe' in symbol.lower():
                file_path = self.options_depth / f"{symbol_clean}_depth.parquet"
            else:
                file_path = self.stocks_depth / f"{symbol_clean}_depth.parquet"
            
            if not file_path.exists():
                return None
            
            # Read data
            df = pd.read_parquet(file_path)
            
            # Convert timestamp to datetime if needed
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
            
            # Filter by date range if provided
            if start_date:
                start_dt = pd.to_datetime(start_date)
                df = df[df['timestamp'] >= start_dt]
            
            if end_date:
                end_dt = pd.to_datetime(end_date)
                df = df[df['timestamp'] <= end_dt]
            
            return df
            
        except Exception as e:
            print(f"Error reading depth history for {symbol}: {e}")
            return None
    
    def analyze_order_flow(self, symbol: str, timeframe: str = '1min') -> Optional[pd.DataFrame]:
        """
        Analyze order flow patterns from depth data
        
        Args:
            symbol (str): Trading symbol
            timeframe (str): Analysis timeframe
            
        Returns:
            Optional[pd.DataFrame]: Order flow analysis
        """
        try:
            # Get recent depth data
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            df = self.get_depth_history(symbol, start_date, end_date)
            
            if df is None or len(df) == 0:
                return None
            
            # Resample to specified timeframe
            df.set_index('timestamp', inplace=True)
            
            # Calculate order flow metrics
            resampled = df.resample(timeframe).agg({
                'ltp': 'last',
                'volume': 'last',
                'spread': 'mean',
                'spread_percent': 'mean',
                'order_imbalance': 'mean',
                'total_buy_qty': 'mean',
                'total_sell_qty': 'mean',
                'bid_price_1': 'last',
                'ask_price_1': 'last',
                'bid_volume_1': 'mean',
                'ask_volume_1': 'mean'
            })
            
            # Calculate additional metrics
            resampled['price_change'] = resampled['ltp'].pct_change()
            resampled['volume_change'] = resampled['volume'].diff()
            resampled['liquidity_score'] = resampled['bid_volume_1'] + resampled['ask_volume_1']
            
            # Classify order flow
            conditions = [
                (resampled['order_imbalance'] > 0.1),
                (resampled['order_imbalance'] < -0.1),
            ]
            choices = ['buy_pressure', 'sell_pressure']
            resampled['flow_direction'] = np.select(conditions, choices, default='balanced')
            
            return resampled.reset_index()
            
        except Exception as e:
            print(f"Error analyzing order flow for {symbol}: {e}")
            return None
    
    def get_current_spread_analysis(self, symbols: List[str]) -> pd.DataFrame:
        """
        Get current spread analysis for multiple symbols
        
        Args:
            symbols (List[str]): List of symbols to analyze
            
        Returns:
            pd.DataFrame: Spread analysis results
        """
        results = []
        
        for symbol in symbols:
            try:
                depth = self.get_market_depth(symbol)
                if depth:
                    parsed = self.parse_depth_data(depth)
                    
                    results.append({
                        'symbol': symbol,
                        'timestamp': parsed['timestamp'],
                        'ltp': parsed['ltp'],
                        'spread': parsed['spread'],
                        'spread_percent': parsed['spread_percent'],
                        'order_imbalance': parsed['order_imbalance'],
                        'total_buy_qty': parsed['total_buy_qty'],
                        'total_sell_qty': parsed['total_sell_qty'],
                        'best_bid': parsed['bid_price_1'],
                        'best_ask': parsed['ask_price_1']
                    })
                    
            except Exception as e:
                print(f"Error analyzing spread for {symbol}: {e}")
        
        return pd.DataFrame(results)
    
    def list_available_depth_data(self) -> Dict[str, List[str]]:
        """
        List all available market depth data files
        
        Returns:
            Dict[str, List[str]]: Available data by category
        """
        available = {
            'indices': [],
            'stocks': [],
            'options': []
        }
        
        # Check each directory
        for category, directory in [
            ('indices', self.indices_depth),
            ('stocks', self.stocks_depth),
            ('options', self.options_depth)
        ]:
            if directory.exists():
                for file_path in directory.glob("*_depth.parquet"):
                    symbol = file_path.stem.replace('_depth', '').replace('_', ':')
                    available[category].append(symbol)
        
        return available


def get_market_depth_manager() -> MarketDepthManager:
    """Get Market Depth Manager instance"""
    return MarketDepthManager()


if __name__ == "__main__":
    # Test market depth functionality
    depth_manager = MarketDepthManager()
    
    print("📊 Testing Market Depth Manager...")
    
    # Test symbols
    test_symbols = ['NSE:HDFCBANK-EQ', 'NSE:RELIANCE-EQ', 'NSE:NIFTY50-INDEX']
    
    for symbol in test_symbols:
        print(f"\n🔍 Testing {symbol}:")
        
        # Collect current depth
        success = depth_manager.collect_and_save_depth(symbol)
        if success:
            print(f"  ✅ Depth data collected and saved")
            
            # Get history
            history = depth_manager.get_depth_history(symbol)
            if history is not None:
                print(f"  📈 History: {len(history)} records")
        else:
            print(f"  ❌ Failed to collect depth data")
    
    # Test spread analysis
    print(f"\n📊 Current Spread Analysis:")
    spread_analysis = depth_manager.get_current_spread_analysis(test_symbols)
    if not spread_analysis.empty:
        print(spread_analysis[['symbol', 'ltp', 'spread', 'spread_percent']].to_string(index=False))
    
    # List available data
    available = depth_manager.list_available_depth_data()
    total_files = sum(len(files) for files in available.values())
    print(f"\n💾 Available depth data files: {total_files}")
    for category, files in available.items():
        if files:
            print(f"  {category}: {len(files)} files")