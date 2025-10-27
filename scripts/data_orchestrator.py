"""
Enhanced Data Orchestrator - Comprehensive Market Data Collection
Coordinates data collection across all data types with dynamic symbol discovery
"""
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional
import concurrent.futures
from pathlib import Path

from my_fyers_model import MyFyersModel
from data_storage import get_parquet_manager
from symbol_discovery import get_symbol_discovery
from market_depth_storage import get_market_depth_manager
from constants import time_zone


class DataOrchestrator:
    """Orchestrates comprehensive data collection across all Fyers data types"""
    
    def __init__(self):
        self.fyers = MyFyersModel()
        self.parquet_manager = get_parquet_manager()
        self.symbol_discovery = get_symbol_discovery()
        self.depth_manager = get_market_depth_manager()
        
        # Collection settings
        self.max_workers = 5  # Parallel processing limit
        self.api_delay = 0.5  # Delay between API calls (seconds)
        
    def discover_and_update_symbols(self, force_refresh: bool = False) -> Dict[str, List[str]]:
        """
        Discover all available symbols and update symbol universe
        
        Args:
            force_refresh (bool): Force refresh symbol discovery
            
        Returns:
            Dict[str, List[str]]: Complete symbol universe
        """
        print("🔍 Discovering symbol universe...")
        
        # Get fresh symbol universe
        symbol_universe = self.symbol_discovery.refresh_symbol_universe(force_refresh)
        
        # Print summary
        total_symbols = 0
        for category, symbols in symbol_universe.items():
            if isinstance(symbols, list):
                total_symbols += len(symbols)
                print(f"  📊 {category}: {len(symbols)} symbols")
        
        print(f"✅ Total symbols discovered: {total_symbols}")
        return symbol_universe
    
    def collect_ohlcv_data(self, symbols: List[str], timeframe: str = '1D', 
                          days_back: int = 30) -> Dict[str, bool]:
        """
        Collect OHLCV data for multiple symbols
        
        Args:
            symbols (List[str]): List of symbols to collect
            timeframe (str): Data timeframe (1m, 5m, 1D, etc.)
            days_back (int): Number of days of historical data
            
        Returns:
            Dict[str, bool]: Success status for each symbol
        """
        print(f"📈 Collecting OHLCV data for {len(symbols)} symbols ({timeframe})")
        
        results = {}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        for i, symbol in enumerate(symbols):
            try:
                print(f"  📊 [{i+1}/{len(symbols)}] Processing {symbol}")
                
                # Check if we already have recent data
                symbol_clean = symbol.replace('NSE:', '').replace('-EQ', '').replace('-INDEX', '').lower()
                existing_data = self.parquet_manager.load_data(symbol_clean, timeframe)
                
                if existing_data is not None and len(existing_data) > 0:
                    last_date = existing_data['timestamp'].max()
                    if (datetime.now() - last_date).days < 2:
                        print(f"    ✅ Recent data exists, skipping")
                        results[symbol] = True
                        continue
                
                # Fetch historical data
                data_request = {
                    'symbol': symbol,
                    'resolution': timeframe,
                    'date_format': '1',
                    'range_from': start_date.strftime('%Y-%m-%d'),
                    'range_to': end_date.strftime('%Y-%m-%d'),
                    'cont_flag': '1'
                }
                
                response = self.fyers.get_history(data_request)
                
                if response.get('s') == 'ok' and 'candles' in response:
                    # Convert to DataFrame
                    candles = response['candles']
                    if candles:
                        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                        
                        # Save to Parquet
                        success = self.parquet_manager.save_data(df, symbol_clean, timeframe, mode='append')
                        results[symbol] = success
                        
                        if success:
                            print(f"    ✅ Saved {len(df)} records")
                        else:
                            print(f"    ❌ Failed to save data")
                    else:
                        print(f"    ⚠️ No candle data received")
                        results[symbol] = False
                else:
                    print(f"    ❌ API error: {response.get('message', 'Unknown error')}")
                    results[symbol] = False
                
                # Rate limiting
                time.sleep(self.api_delay)
                
            except Exception as e:
                print(f"    ❌ Error processing {symbol}: {e}")
                results[symbol] = False
        
        success_count = sum(1 for success in results.values() if success)
        print(f"✅ OHLCV collection complete: {success_count}/{len(symbols)} successful")
        
        return results
    
    def collect_market_depth_data(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Collect market depth data for multiple symbols
        
        Args:
            symbols (List[str]): List of symbols to collect depth data for
            
        Returns:
            Dict[str, bool]: Success status for each symbol
        """
        print(f"📊 Collecting market depth for {len(symbols)} symbols")
        
        results = {}
        
        for i, symbol in enumerate(symbols):
            try:
                print(f"  🔍 [{i+1}/{len(symbols)}] Processing depth for {symbol}")
                
                success = self.depth_manager.collect_and_save_depth(symbol)
                results[symbol] = success
                
                if success:
                    print(f"    ✅ Depth data collected")
                else:
                    print(f"    ❌ Failed to collect depth data")
                
                # Rate limiting
                time.sleep(self.api_delay)
                
            except Exception as e:
                print(f"    ❌ Error collecting depth for {symbol}: {e}")
                results[symbol] = False
        
        success_count = sum(1 for success in results.values() if success)
        print(f"✅ Depth collection complete: {success_count}/{len(symbols)} successful")
        
        return results
    
    def collect_option_chain_data(self, underlying_symbols: List[str]) -> Dict[str, bool]:
        """
        Collect option chain data for underlying symbols
        
        Args:
            underlying_symbols (List[str]): List of underlying symbols
            
        Returns:
            Dict[str, bool]: Success status for each underlying
        """
        print(f"⚡ Collecting option chains for {len(underlying_symbols)} underlyings")
        
        results = {}
        
        for i, symbol in enumerate(underlying_symbols):
            try:
                print(f"  📋 [{i+1}/{len(underlying_symbols)}] Processing options for {symbol}")
                
                # Get option chain
                data = {
                    'symbol': symbol,
                    'strikecount': 20,
                    'timestamp': ''
                }
                
                response = self.fyers.fyers_model.optionchain(data=data)
                
                if response.get('s') == 'ok' and 'data' in response:
                    # Save option chain data (simplified for now)
                    chain_data = response['data']
                    
                    # Create option chain summary
                    summary = {
                        'timestamp': datetime.now(),
                        'underlying': symbol,
                        'total_call_oi': chain_data.get('callOi', {}),
                        'total_put_oi': chain_data.get('putOi', {}),
                        'available_expiries': chain_data.get('expiryData', []),
                        'vix_data': chain_data.get('indiavixData', {})
                    }
                    
                    # Save to JSON file for now (can be enhanced to Parquet later)
                    option_dir = Path("data/parquet/options")
                    option_dir.mkdir(parents=True, exist_ok=True)
                    
                    symbol_clean = symbol.replace(':', '_').replace('-', '_')
                    file_path = option_dir / f"{symbol_clean}_chain_{datetime.now().strftime('%Y%m%d')}.json"
                    
                    import json
                    with open(file_path, 'w') as f:
                        json.dump(summary, f, indent=2, default=str)
                    
                    results[symbol] = True
                    print(f"    ✅ Option chain saved")
                else:
                    print(f"    ❌ Failed to get option chain")
                    results[symbol] = False
                
                # Rate limiting
                time.sleep(self.api_delay)
                
            except Exception as e:
                print(f"    ❌ Error processing options for {symbol}: {e}")
                results[symbol] = False
        
        success_count = sum(1 for success in results.values() if success)
        print(f"✅ Option chain collection complete: {success_count}/{len(underlying_symbols)} successful")
        
        return results
    
    def run_comprehensive_collection(self, timeframes: List[str] = ['1D'], 
                                   include_depth: bool = True,
                                   include_options: bool = True) -> Dict[str, Dict]:
        """
        Run comprehensive data collection across all data types
        
        Args:
            timeframes (List[str]): List of timeframes to collect
            include_depth (bool): Whether to collect market depth data
            include_options (bool): Whether to collect option chain data
            
        Returns:
            Dict[str, Dict]: Comprehensive collection results
        """
        print("🚀 Starting comprehensive data collection...")
        start_time = datetime.now()
        
        # Step 1: Discover symbols
        symbol_universe = self.discover_and_update_symbols()
        
        results = {
            'symbols_discovered': symbol_universe,
            'ohlcv_results': {},
            'depth_results': {},
            'options_results': {}
        }
        
        # Step 2: Collect OHLCV data for all timeframes
        all_symbols = []
        for category, symbols in symbol_universe.items():
            if isinstance(symbols, list):
                all_symbols.extend(symbols)
        
        for timeframe in timeframes:
            print(f"\n📈 Collecting OHLCV data for timeframe: {timeframe}")
            ohlcv_results = self.collect_ohlcv_data(all_symbols, timeframe)
            results['ohlcv_results'][timeframe] = ohlcv_results
        
        # Step 3: Collect market depth data (for active stocks and indices)
        if include_depth:
            print(f"\n📊 Collecting market depth data...")
            
            # Focus on liquid symbols for depth data
            depth_symbols = []
            if 'indices' in symbol_universe:
                depth_symbols.extend(symbol_universe['indices'])
            if 'nifty50_stocks' in symbol_universe:
                depth_symbols.extend(symbol_universe['nifty50_stocks'][:10])  # Top 10 for now
            
            depth_results = self.collect_market_depth_data(depth_symbols)
            results['depth_results'] = depth_results
        
        # Step 4: Collect option chain data
        if include_options:
            print(f"\n⚡ Collecting option chain data...")
            
            # Get option data for major indices
            option_underlyings = ['NSE:NIFTY50-INDEX', 'NSE:NIFTYBANK-INDEX', 'NSE:FINNIFTY-INDEX']
            options_results = self.collect_option_chain_data(option_underlyings)
            results['options_results'] = options_results
        
        # Summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n🎉 Comprehensive collection complete!")
        print(f"⏱️  Duration: {duration}")
        print(f"📊 Total symbols processed: {len(all_symbols)}")
        
        # Save collection summary
        summary = {
            'collection_time': start_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'symbols_count': len(all_symbols),
            'timeframes_collected': timeframes,
            'included_depth': include_depth,
            'included_options': include_options,
            'results_summary': {
                'ohlcv_success_rate': {},
                'depth_success_rate': 0,
                'options_success_rate': 0
            }
        }
        
        # Calculate success rates
        for timeframe, tf_results in results['ohlcv_results'].items():
            success_rate = sum(1 for success in tf_results.values() if success) / len(tf_results) if tf_results else 0
            summary['results_summary']['ohlcv_success_rate'][timeframe] = success_rate
        
        if results['depth_results']:
            depth_success_rate = sum(1 for success in results['depth_results'].values() if success) / len(results['depth_results'])
            summary['results_summary']['depth_success_rate'] = depth_success_rate
        
        if results['options_results']:
            options_success_rate = sum(1 for success in results['options_results'].values() if success) / len(results['options_results'])
            summary['results_summary']['options_success_rate'] = options_success_rate
        
        # Save summary
        summary_dir = Path("data/parquet/collection_logs")
        summary_dir.mkdir(parents=True, exist_ok=True)
        
        summary_file = summary_dir / f"collection_summary_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"📝 Collection summary saved to: {summary_file}")
        
        return results
    
    def run_daily_update(self) -> Dict[str, Dict]:
        """
        Run daily data update routine
        Focuses on updating recent data efficiently
        
        Returns:
            Dict[str, Dict]: Update results
        """
        print("🌅 Running daily data update...")
        
        # Use cached symbols to avoid re-discovery
        symbol_universe = self.symbol_discovery.load_symbol_universe()
        
        if not symbol_universe:
            print("⚠️ No cached symbols found, running full discovery...")
            symbol_universe = self.discover_and_update_symbols()
        
        # Quick update for essential data
        results = self.run_comprehensive_collection(
            timeframes=['1D'],  # Daily data only
            include_depth=True,  # Current depth snapshots
            include_options=False  # Skip options for daily updates
        )
        
        return results
    
    def get_collection_status(self) -> Dict[str, any]:
        """
        Get status of all data collections
        
        Returns:
            Dict[str, any]: Collection status summary
        """
        status = {
            'ohlcv_data': self.parquet_manager.list_available_data(),
            'depth_data': self.depth_manager.list_available_depth_data(),
            'symbol_universe': self.symbol_discovery.load_symbol_universe(),
            'last_updated': datetime.now().isoformat()
        }
        
        return status


def get_data_orchestrator() -> DataOrchestrator:
    """Get Data Orchestrator instance"""
    return DataOrchestrator()


if __name__ == "__main__":
    # Test comprehensive data collection
    orchestrator = DataOrchestrator()
    
    print("🎯 Testing Enhanced Data Orchestrator...")
    
    # Test symbol discovery
    print("\n🔍 Testing symbol discovery...")
    symbols = orchestrator.discover_and_update_symbols()
    
    # Test daily update (quick test)
    print("\n🌅 Testing daily update...")
    results = orchestrator.run_daily_update()
    
    # Show status
    print("\n📊 Collection Status:")
    status = orchestrator.get_collection_status()
    for category, data in status.items():
        if isinstance(data, dict) and 'metadata' not in category:
            total_files = sum(len(files) for files in data.values()) if data else 0
            print(f"  {category}: {total_files} files")
        elif isinstance(data, dict) and 'metadata' in category:
            print(f"  {category}: {data.get('total_symbols', 0)} symbols")
    
    print("\n✅ Orchestrator test complete!")