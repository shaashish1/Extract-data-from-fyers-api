"""
Fyers Quotes API Integration
=============================

Get real-time market quotes for up to 50 symbols at once.

Features:
- Real-time LTP, bid/ask, OHLC, volume
- Batch processing (max 50 symbols per request)
- Auto-retry with rate limiting
- Data storage in Parquet format

API Endpoint: https://api-t1.fyers.in/data/quotes
Max Symbols: 50 per request

Author: Fyers Trading Platform
Created: October 28, 2025
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import time
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.auth.my_fyers_model import MyFyersModel
from scripts.data.data_storage import get_parquet_manager
from scripts.core.rate_limit_manager import get_rate_limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FyersQuotesAPI:
    """
    Fyers Quotes API Wrapper
    
    Get real-time market quotes for multiple symbols (max 50 per request).
    """
    
    MAX_SYMBOLS_PER_REQUEST = 50
    
    def __init__(self):
        """Initialize the Quotes API."""
        self.fyers = MyFyersModel()
        self.parquet_manager = get_parquet_manager()
        logger.info("Fyers Quotes API initialized")
    
    def get_quotes(self, symbols: List[str]) -> Optional[Dict]:
        """
        Get quotes for multiple symbols.
        
        Args:
            symbols: List of symbol tickers (max 50)
        
        Returns:
            Dictionary with quote data or None on error
        """
        if not symbols:
            logger.warning("No symbols provided")
            return None
        
        if len(symbols) > self.MAX_SYMBOLS_PER_REQUEST:
            logger.warning(f"Too many symbols ({len(symbols)}). Max is {self.MAX_SYMBOLS_PER_REQUEST}")
            symbols = symbols[:self.MAX_SYMBOLS_PER_REQUEST]
        
        # Format symbols for API (comma-separated)
        symbols_str = ",".join(symbols)
        
        try:
            logger.info(f"Fetching quotes for {len(symbols)} symbols...")
            
            # CRITICAL: Use global rate limiter to prevent API blocks
            limiter = get_rate_limiter()
            limiter.wait_if_needed()  # Auto-throttle based on current rates
            
            data = {"symbols": symbols_str}
            response = self.fyers.get_fyre_model().quotes(data=data)
            
            # Record request (success or failure)
            success = response and response.get('s') == 'ok'
            limiter.record_request(success=success)
            
            if response and response.get('s') == 'ok':
                logger.info(f"Successfully fetched quotes for {len(symbols)} symbols")
                return response
            elif response and response.get('code') == 429:
                logger.error("⛔ RATE LIMIT EXCEEDED (429)!")
                logger.error("Fyers API limits: 10/sec, 200/min, 100k/day")
                logger.error("⚠️ WARNING: 3 violations/day = BLOCKED UNTIL MIDNIGHT")
                logger.error("Rate limiter will enforce cooldown...")
                return None
            else:
                logger.error(f"Quotes API error: {response}")
                return None
                
        except RuntimeError as e:
            # Rate limiter stopped execution to prevent block
            logger.error(f"⛔ Rate limiter prevented execution: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch quotes: {e}")
            return None
    
    def get_quotes_batch(self, symbols: List[str]) -> List[Dict]:
        """
        Get quotes for large number of symbols (auto-batching).
        
        Args:
            symbols: List of symbol tickers (any length)
        
        Returns:
            List of quote responses
        """
        results = []
        
        # Split into batches of 50
        for i in range(0, len(symbols), self.MAX_SYMBOLS_PER_REQUEST):
            batch = symbols[i:i + self.MAX_SYMBOLS_PER_REQUEST]
            logger.info(f"Processing batch {i//self.MAX_SYMBOLS_PER_REQUEST + 1} ({len(batch)} symbols)")
            
            response = self.get_quotes(batch)  # Rate limiter handles delays automatically
            if response:
                results.append(response)
        
        return results
    
    def parse_quote_response(self, response: Dict) -> pd.DataFrame:
        """
        Parse quote response into DataFrame.
        
        Args:
            response: Raw API response
        
        Returns:
            DataFrame with quote data
        """
        if not response or response.get('s') != 'ok':
            return pd.DataFrame()
        
        quotes_data = response.get('d', [])
        
        rows = []
        for quote in quotes_data:
            if quote.get('s') != 'ok':
                continue
            
            v = quote.get('v', {})
            rows.append({
                'timestamp': datetime.now(),
                'symbol': quote.get('n', ''),
                'ltp': v.get('lp', 0.0),  # Last traded price
                'open': v.get('open_price', 0.0),
                'high': v.get('high_price', 0.0),
                'low': v.get('low_price', 0.0),
                'prev_close': v.get('prev_close_price', 0.0),
                'change': v.get('ch', 0.0),
                'change_pct': v.get('chp', 0.0),
                'volume': v.get('volume', 0),
                'bid': v.get('bid', 0.0),
                'ask': v.get('ask', 0.0),
                'spread': v.get('spread', 0.0),
                'avg_price': v.get('atp', 0.0),
                'fytoken': v.get('fyToken', ''),
                'exchange': v.get('exchange', ''),
                'description': v.get('description', ''),
                'short_name': v.get('short_name', '')
            })
        
        return pd.DataFrame(rows)
    
    def save_quotes(self, df: pd.DataFrame, filename: str = "quotes") -> bool:
        """
        Save quotes to Parquet file.
        
        Args:
            df: DataFrame with quote data
            filename: Base filename (without extension)
        
        Returns:
            True if saved successfully
        """
        if df.empty:
            logger.warning("No data to save")
            return False
        
        try:
            # Save to data/quotes/ directory
            output_dir = project_root / "data" / "quotes"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = output_dir / f"{filename}_{timestamp}.parquet"
            
            df.to_parquet(filepath, index=False)
            logger.info(f"Saved {len(df)} quotes to {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save quotes: {e}")
            return False
    
    def get_and_save_quotes(self, symbols: List[str], save: bool = True) -> pd.DataFrame:
        """
        Get quotes and optionally save to file.
        
        Args:
            symbols: List of symbol tickers
            save: Whether to save to Parquet file
        
        Returns:
            DataFrame with quote data
        """
        # Get quotes (with auto-batching)
        responses = self.get_quotes_batch(symbols)
        
        # Parse all responses
        dfs = []
        for response in responses:
            df = self.parse_quote_response(response)
            if not df.empty:
                dfs.append(df)
        
        # Combine all dataframes
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Total quotes retrieved: {len(combined_df)}")
            
            if save:
                self.save_quotes(combined_df)
            
            return combined_df
        else:
            logger.warning("No quotes data retrieved")
            return pd.DataFrame()


def demo_quotes_api():
    """Demo: Fetch quotes for Nifty 50 stocks."""
    print("="*80)
    print("Fyers Quotes API Demo")
    print("="*80)
    
    # Sample Nifty 50 symbols
    symbols = [
        "NSE:RELIANCE-EQ",
        "NSE:TCS-EQ",
        "NSE:HDFCBANK-EQ",
        "NSE:INFY-EQ",
        "NSE:ICICIBANK-EQ",
        "NSE:HINDUNILVR-EQ",
        "NSE:SBIN-EQ",
        "NSE:BHARTIARTL-EQ",
        "NSE:ITC-EQ",
        "NSE:KOTAKBANK-EQ"
    ]
    
    quotes_api = FyersQuotesAPI()
    
    # Get quotes
    df = quotes_api.get_and_save_quotes(symbols, save=True)
    
    if not df.empty:
        print("\nQuotes Retrieved:")
        print("-"*80)
        print(df[['symbol', 'ltp', 'change_pct', 'volume', 'bid', 'ask']].to_string(index=False))
        print()
        print(f"Total symbols: {len(df)}")
        print(f"Data saved to: data/quotes/")
    
    # Print rate limiter statistics
    print("\n")
    limiter = get_rate_limiter()
    limiter.print_statistics()


if __name__ == "__main__":
    demo_quotes_api()
