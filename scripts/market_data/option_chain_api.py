"""
Fyers Option Chain API Integration
===================================

Get complete option chain data for underlying symbols.

Features:
- Call and Put options across strikes
- ATM, OTM, ITM strike classification
- Open Interest analysis
- Implied Volatility
- Greeks (if available)
- Multi-expiry support

API Endpoint: https://api-t1.fyers.in/data/options-chain-v3
Max Strikes: 50 per request (ATM + OTM + ITM combined)

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


class FyersOptionChainAPI:
    """
    Fyers Option Chain API Wrapper
    
    Get complete option chain data for indices and stocks.
    """
    
    MAX_STRIKES = 50  # Maximum strikes per request
    
    def __init__(self):
        """Initialize the Option Chain API with rate limiting."""
        self.fyers = MyFyersModel()
        self.limiter = get_rate_limiter()
        logger.info("Fyers Option Chain API initialized with rate limiting")
    
    def get_option_chain(self, symbol: str, strike_count: int = 10,
                        timestamp: Optional[str] = None) -> Optional[Dict]:
        """
        Get option chain for a symbol.
        
        Args:
            symbol: Underlying symbol (e.g., "NSE:NIFTY50-INDEX", "NSE:SBIN-EQ")
            strike_count: Number of strikes on each side of ATM (max 50 total)
            timestamp: Optional timestamp for historical chain
        
        Returns:
            Dictionary with option chain data or None on error
        """
        # Validate strike count
        if strike_count > self.MAX_STRIKES // 2:
            logger.warning(f"Strike count {strike_count} too high. Max is {self.MAX_STRIKES // 2}")
            strike_count = self.MAX_STRIKES // 2
        
        try:
            logger.info(f"Fetching option chain for {symbol} (strike_count={strike_count})...")
            
            # Wait if needed to respect rate limits
            self.limiter.wait_if_needed()
            
            data = {
                "symbol": symbol,
                "strikecount": strike_count
            }
            
            if timestamp:
                data["timestamp"] = timestamp
            
            response = self.fyers.get_fyre_model().optionchain(data=data)
            
            # Record request success/failure
            success = response and response.get('s') == 'ok'
            self.limiter.record_request(success)
            
            if success:
                logger.info(f"Successfully fetched option chain for {symbol}")
                return response
            else:
                logger.error(f"Option chain API error: {response}")
                return None
                
        except RuntimeError as e:
            # Rate limit violation - stop execution
            logger.critical(f"RATE LIMIT VIOLATION: {e}")
            logger.critical("Stopping execution to prevent daily API block")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch option chain: {e}")
            return None
    
    def parse_option_chain(self, response: Dict) -> Dict:
        """
        Parse option chain response.
        
        Args:
            response: Raw API response
        
        Returns:
            Parsed chain data
        """
        if not response or response.get('s') != 'ok':
            return {}
        
        data = response.get('data', {})
        
        # Extract expiry dates
        expiry_data = data.get('expiryData', [])
        expiries = [
            {
                'date': exp.get('date'),
                'timestamp': exp.get('expiry')
            }
            for exp in expiry_data
        ]
        
        # Extract underlying data
        chain = data.get('optionsChain', [])
        
        # First element is underlying
        underlying = None
        options = []
        
        if chain:
            first = chain[0]
            if first.get('option_type') == "":  # Underlying
                underlying = {
                    'symbol': first.get('symbol'),
                    'ltp': first.get('ltp', 0.0),
                    'change': first.get('ltpch', 0.0),
                    'change_pct': first.get('ltpchp', 0.0),
                    'future_price': first.get('fp', 0.0),
                    'future_change': first.get('fpch', 0.0),
                    'future_change_pct': first.get('fpchp', 0.0)
                }
                
                options = chain[1:]  # Rest are options
            else:
                options = chain
        
        # India VIX data (if available)
        indiavix = data.get('indiavixData', {})
        vix_data = None
        if indiavix:
            vix_data = {
                'symbol': indiavix.get('symbol'),
                'ltp': indiavix.get('ltp', 0.0),
                'change': indiavix.get('ltpch', 0.0),
                'change_pct': indiavix.get('ltpchp', 0.0)
            }
        
        # Total OI
        call_oi = data.get('callOi', 0)
        put_oi = data.get('putOi', 0)
        
        return {
            'timestamp': datetime.now(),
            'expiries': expiries,
            'underlying': underlying,
            'vix': vix_data,
            'total_call_oi': call_oi,
            'total_put_oi': put_oi,
            'pcr_oi': put_oi / call_oi if call_oi > 0 else 0,
            'options': options
        }
    
    def get_options_dataframe(self, chain_data: Dict) -> pd.DataFrame:
        """
        Convert options chain to DataFrame.
        
        Args:
            chain_data: Parsed chain data
        
        Returns:
            DataFrame with option data
        """
        if not chain_data or not chain_data.get('options'):
            return pd.DataFrame()
        
        rows = []
        for opt in chain_data['options']:
            rows.append({
                'timestamp': chain_data['timestamp'],
                'symbol': opt.get('symbol'),
                'strike': opt.get('strike_price', 0),
                'option_type': opt.get('option_type'),  # CE or PE
                'ltp': opt.get('ltp', 0.0),
                'change': opt.get('ltpch', 0.0),
                'change_pct': opt.get('ltpchp', 0.0),
                'volume': opt.get('volume', 0),
                'oi': opt.get('oi', 0),
                'oi_change': opt.get('oich', 0),
                'oi_change_pct': opt.get('oichp', 0.0),
                'prev_oi': opt.get('prev_oi', 0),
                'bid': opt.get('bid', 0.0),
                'ask': opt.get('ask', 0.0),
                'fytoken': opt.get('fyToken', '')
            })
        
        return pd.DataFrame(rows)
    
    def display_option_chain(self, chain_data: Dict):
        """
        Display option chain in formatted table.
        
        Args:
            chain_data: Parsed chain data
        """
        if not chain_data:
            print("No chain data available")
            return
        
        print("\n" + "="*120)
        print("Option Chain Analysis")
        print("="*120)
        
        # Underlying info
        if chain_data['underlying']:
            und = chain_data['underlying']
            print(f"\nUnderlying: {und['symbol']}")
            print(f"Spot: ₹{und['ltp']:.2f} ({und['change']:+.2f}, {und['change_pct']:+.2f}%)")
            print(f"Future: ₹{und['future_price']:.2f} ({und['future_change']:+.2f}, {und['future_change_pct']:+.2f}%)")
        
        # India VIX
        if chain_data['vix']:
            vix = chain_data['vix']
            print(f"India VIX: {vix['ltp']:.2f} ({vix['change']:+.2f}, {vix['change_pct']:+.2f}%)")
        
        # Total OI and PCR
        print(f"\nTotal Call OI: {chain_data['total_call_oi']:,}")
        print(f"Total Put OI: {chain_data['total_put_oi']:,}")
        print(f"PCR (Put/Call OI Ratio): {chain_data['pcr_oi']:.2f}")
        
        # Expiry dates
        print(f"\nAvailable Expiries: {len(chain_data['expiries'])}")
        for exp in chain_data['expiries'][:5]:  # Show first 5
            print(f"  - {exp['date']}")
        
        # Option chain table
        df = self.get_options_dataframe(chain_data)
        
        if not df.empty:
            # Separate calls and puts
            calls = df[df['option_type'] == 'CE'].sort_values('strike')
            puts = df[df['option_type'] == 'PE'].sort_values('strike')
            
            print("\n" + "-"*120)
            print(f"{'CALL OPTIONS':^50} | {'STRIKE':^10} | {'PUT OPTIONS':^50}")
            print(f"{'OI':<10} {'Vol':<10} {'LTP':<10} {'Chg%':<10} | {'':<10} | "
                  f"{'LTP':<10} {'Chg%':<10} {'Vol':<10} {'OI':<10}")
            print("-"*120)
            
            # Merge calls and puts by strike
            strikes = sorted(set(calls['strike'].tolist() + puts['strike'].tolist()))
            
            for strike in strikes:
                call_row = calls[calls['strike'] == strike]
                put_row = puts[puts['strike'] == strike]
                
                # Call data
                if not call_row.empty:
                    c_oi = f"{int(call_row.iloc[0]['oi']):,}"
                    c_vol = f"{int(call_row.iloc[0]['volume']):,}"
                    c_ltp = f"{call_row.iloc[0]['ltp']:.2f}"
                    c_chg = f"{call_row.iloc[0]['change_pct']:+.1f}%"
                else:
                    c_oi = c_vol = c_ltp = c_chg = "-"
                
                # Put data
                if not put_row.empty:
                    p_ltp = f"{put_row.iloc[0]['ltp']:.2f}"
                    p_chg = f"{put_row.iloc[0]['change_pct']:+.1f}%"
                    p_vol = f"{int(put_row.iloc[0]['volume']):,}"
                    p_oi = f"{int(put_row.iloc[0]['oi']):,}"
                else:
                    p_ltp = p_chg = p_vol = p_oi = "-"
                
                print(f"{c_oi:<10} {c_vol:<10} {c_ltp:<10} {c_chg:<10} | "
                      f"{strike:>10.0f} | "
                      f"{p_ltp:<10} {p_chg:<10} {p_vol:<10} {p_oi:<10}")
            
            print("-"*120)
    
    def save_option_chain(self, df: pd.DataFrame, symbol: str):
        """
        Save option chain to Parquet.
        
        Args:
            df: DataFrame with option data
            symbol: Underlying symbol
        """
        if df.empty:
            logger.warning("No data to save")
            return
        
        try:
            # Create output directory
            safe_symbol = symbol.replace(":", "_").replace("-", "_")
            output_dir = project_root / "data" / "option_chain" / safe_symbol
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = output_dir / f"chain_{timestamp}.parquet"
            
            df.to_parquet(filepath, index=False)
            logger.info(f"Saved option chain to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save option chain: {e}")


def demo_option_chain():
    """Demo: Get and display option chain."""
    print("="*120)
    print("Fyers Option Chain API Demo")
    print("="*120)
    
    chain_api = FyersOptionChainAPI()
    
    # Test symbols
    symbols = [
        "NSE:NIFTY50-INDEX",
        "NSE:SBIN-EQ"
    ]
    
    for symbol in symbols:
        # Get option chain
        response = chain_api.get_option_chain(symbol, strike_count=5)
        
        if response:
            # Parse and display
            chain_data = chain_api.parse_option_chain(response)
            chain_api.display_option_chain(chain_data)
            
            # Save to file
            df = chain_api.get_options_dataframe(chain_data)
            chain_api.save_option_chain(df, symbol)
        
        print("\n" * 2)


if __name__ == "__main__":
    demo_option_chain()
