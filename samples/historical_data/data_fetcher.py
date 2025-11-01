"""
Data Fetcher module for PTIP
Handles fetching historical and real-time data from Fyers API
"""

import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys
from fyers_apiv3 import fyersModel

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class FyersDataFetcher:
    """Handles data fetching from Fyers API"""
    
    def __init__(self):
        """Initialize Fyers Data Fetcher"""
        self.client_id = config.FYERS_CLIENT_ID
        self.secret_key = config.FYERS_SECRET_KEY
        self.redirect_uri = config.FYERS_REDIRECT_URI
        self.access_token = None
        self.fyers = None
        
        print("✅ Fyers Data Fetcher initialized")
    
    def authenticate(self, access_token=None):
        """
        Authenticate with Fyers API
        
        Args:
            access_token (str): Pre-generated access token (optional)
            
        Note: For now, we'll use a simplified authentication.
        In production, you'll need to implement the full OAuth flow.
        """
        if access_token:
            self.access_token = access_token
        else:
            # For MVP, we'll generate access token manually
            # Full OAuth implementation will be added later
            print("\n" + "="*60)
            print("FYERS AUTHENTICATION REQUIRED")
            print("="*60)
            print("\nTo authenticate with Fyers API, you need to:")
            print("1. Go to: https://api-dashboard.fyers.in/")
            print("2. Generate an access token")
            print("3. Provide it when prompted")
            print("\nFor automated authentication, we'll implement OAuth flow later.")
            print("="*60 + "\n")
            
            # For now, return False to indicate manual token needed
            return False
        
        # Initialize Fyers model with access token
        try:
            self.fyers = fyersModel.FyersModel(
                client_id=self.client_id,
                token=self.access_token,
                log_path=""
            )
            print("✅ Fyers authentication successful!")
            return True
        except Exception as e:
            print(f"❌ Fyers authentication failed: {e}")
            return False
    
    def fetch_historical_data(self, symbol, from_date, to_date, resolution='5'):
        """
        Fetch historical data for a symbol
        
        Args:
            symbol (str): Stock symbol (e.g., 'NSE:RELIANCE-EQ')
            from_date (datetime): Start date
            to_date (datetime): End date
            resolution (str): Data resolution ('1', '5', '15', '60', 'D')
            
        Returns:
            pd.DataFrame: Historical OHLCV data
        """
        if not self.fyers:
            print("❌ Not authenticated. Please authenticate first.")
            return pd.DataFrame()
        
        try:
            # Convert dates to YYYY-MM-DD format (required by Fyers API)
            from_date_str = from_date.strftime("%Y-%m-%d")
            to_date_str = to_date.strftime("%Y-%m-%d")

            # Prepare data request
            data = {
                "symbol": symbol,
                "resolution": resolution,
                "date_format": "1",  # Returns Unix timestamp in response
                "range_from": from_date_str,
                "range_to": to_date_str,
                "cont_flag": "1"
            }
            
            # Fetch data
            print(f"📊 Fetching data for {symbol} from {from_date.date()} to {to_date.date()}...")
            response = self.fyers.history(data=data)
            
            # Check response
            if response['s'] == 'ok':
                # Convert to DataFrame
                df = pd.DataFrame(response['candles'])
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                
                # Convert timestamp to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                
                print(f"✅ Fetched {len(df)} records for {symbol}")
                return df
            else:
                print(f"❌ Error fetching data: {response.get('message', 'Unknown error')}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Exception while fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_multiple_stocks(self, symbols, from_date, to_date, resolution='5', delay=1):
        """
        Fetch historical data for multiple stocks
        
        Args:
            symbols (list): List of stock symbols
            from_date (datetime): Start date
            to_date (datetime): End date
            resolution (str): Data resolution
            delay (int): Delay between requests in seconds (to avoid rate limiting)
            
        Returns:
            dict: Dictionary with symbol as key and DataFrame as value
        """
        results = {}
        
        for i, symbol in enumerate(symbols):
            print(f"\n[{i+1}/{len(symbols)}] Processing {symbol}...")
            
            df = self.fetch_historical_data(symbol, from_date, to_date, resolution)
            
            if not df.empty:
                results[symbol] = df
            
            # Add delay to avoid rate limiting (except for last symbol)
            if i < len(symbols) - 1:
                print(f"⏳ Waiting {delay} second(s) before next request...")
                time.sleep(delay)
        
        print(f"\n✅ Completed fetching data for {len(results)}/{len(symbols)} symbols")
        return results
    
    def get_quote(self, symbols):
        """
        Get current quote for symbols (for future real-time implementation)
        
        Args:
            symbols (list): List of stock symbols
            
        Returns:
            dict: Quote data
        """
        if not self.fyers:
            print("❌ Not authenticated. Please authenticate first.")
            return {}
        
        try:
            data = {"symbols": ",".join(symbols)}
            response = self.fyers.quotes(data=data)
            
            if response['s'] == 'ok':
                return response['d']
            else:
                print(f"❌ Error fetching quotes: {response.get('message', 'Unknown error')}")
                return {}
                
        except Exception as e:
            print(f"❌ Exception while fetching quotes: {e}")
            return {}


# Test function
if __name__ == "__main__":
    print("Testing Fyers Data Fetcher module...")
    
    # Validate config first
    if not config.validate_config():
        print("\n❌ Please configure your .env file with Fyers credentials")
        exit(1)
    
    fetcher = FyersDataFetcher()
    
    # Note: Authentication requires manual token for now
    print("\n⚠️  Manual authentication required for testing")
    print("This will be automated in the next phase")
    
    print("\n✅ Data Fetcher module test completed!")

