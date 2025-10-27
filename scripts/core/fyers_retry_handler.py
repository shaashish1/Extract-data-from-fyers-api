#!/usr/bin/env python3
"""
ENHANCED RETRY LOGIC MODULE
Implements OpenAI's suggested retry with exponential backoff
Enhances my_fyers_model.py with robust error handling
"""

import time
import functools
import logging
from typing import Any, Callable, List, Optional, Type
from requests.exceptions import ConnectionError, Timeout, HTTPError
from fyers_config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RetryError(Exception):
    """Custom exception for retry failures"""
    pass

class FyersRetryHandler:
    """Enhanced retry handler with exponential backoff"""
    
    def __init__(self, 
                 max_retries: int = None,
                 backoff_factor: float = None,
                 max_backoff: int = None,
                 retry_on_status: List[int] = None,
                 retry_on_exceptions: List[str] = None):
        
        # Use config defaults if not provided
        retry_config = config.RETRY_CONFIG
        self.max_retries = max_retries or retry_config["max_retries"]
        self.backoff_factor = backoff_factor or retry_config["backoff_factor"]
        self.max_backoff = max_backoff or retry_config["max_backoff"]
        self.retry_on_status = retry_on_status or retry_config["retry_on_status"]
        self.retry_on_exceptions = retry_on_exceptions or retry_config["retry_on_exceptions"]
        
        # Map exception names to classes
        self.exception_classes = {
            "ConnectionError": ConnectionError,
            "Timeout": Timeout,
            "HTTPError": HTTPError,
        }
    
    def should_retry(self, exception: Exception, response=None) -> bool:
        """Determine if the operation should be retried"""
        
        # Check HTTP status codes
        if response and hasattr(response, 'status_code'):
            if response.status_code in self.retry_on_status:
                logger.warning(f"Retrying due to HTTP status {response.status_code}")
                return True
        
        # Check exception types
        exception_name = type(exception).__name__
        if exception_name in self.retry_on_exceptions:
            logger.warning(f"Retrying due to exception: {exception_name}")
            return True
        
        # Fyers-specific error patterns
        error_msg = str(exception).lower()
        fyers_retry_patterns = [
            "rate limit",
            "server error", 
            "timeout",
            "connection",
            "temporary",
            "unavailable"
        ]
        
        for pattern in fyers_retry_patterns:
            if pattern in error_msg:
                logger.warning(f"Retrying due to Fyers error pattern: {pattern}")
                return True
        
        return False
    
    def calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff time with exponential increase"""
        backoff = min(
            self.backoff_factor ** attempt,
            self.max_backoff
        )
        
        # Add small random jitter to prevent thundering herd
        import random
        jitter = random.uniform(0.1, 0.3)
        return backoff + jitter
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to add retry logic to functions"""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    # Add rate limiting delay
                    if attempt > 0:
                        rate_delay = config.RATE_LIMITS["delay_between_calls"]
                        time.sleep(rate_delay)
                    
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    # Log successful retry
                    if attempt > 0:
                        logger.info(f"✅ Function {func.__name__} succeeded on attempt {attempt + 1}")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry
                    if attempt < self.max_retries and self.should_retry(e):
                        backoff_time = self.calculate_backoff(attempt)
                        logger.warning(
                            f"🔄 Attempt {attempt + 1}/{self.max_retries + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {backoff_time:.2f} seconds..."
                        )
                        time.sleep(backoff_time)
                        continue
                    else:
                        # Final attempt failed or non-retryable error
                        logger.error(f"❌ Function {func.__name__} failed after {attempt + 1} attempts: {e}")
                        break
            
            # All retries exhausted
            raise RetryError(f"Function {func.__name__} failed after {self.max_retries + 1} attempts. Last error: {last_exception}")
        
        return wrapper

# === Convenience Decorators ===

def retry_api_call(max_retries: int = None, backoff_factor: float = None):
    """Decorator for standard API calls with retry logic"""
    return FyersRetryHandler(
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        retry_on_status=[429, 500, 502, 503, 504],
        retry_on_exceptions=["ConnectionError", "Timeout", "HTTPError"]
    )

def retry_websocket_connection(max_retries: int = 5, backoff_factor: float = 2.0):
    """Decorator specifically for WebSocket connections"""
    return FyersRetryHandler(
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        max_backoff=30,
        retry_on_exceptions=["ConnectionError", "Timeout"]
    )

def retry_data_operation(max_retries: int = 2, backoff_factor: float = 1.0):
    """Decorator for data operations (less aggressive retries)"""
    return FyersRetryHandler(
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        max_backoff=10,
        retry_on_status=[500, 502, 503, 504],
        retry_on_exceptions=["ConnectionError"]
    )

# === Enhanced Function Wrappers ===

class EnhancedFyersAPI:
    """Enhanced wrapper for Fyers API calls with retry logic"""
    
    def __init__(self, fyers_model):
        self.fyers_model = fyers_model
        self.retry_handler = FyersRetryHandler()
    
    @retry_api_call()
    def get_quotes(self, symbols: List[str]) -> dict:
        """Get quotes with retry logic"""
        logger.info(f"📊 Fetching quotes for {len(symbols)} symbols")
        return self.fyers_model.get_quotes({"symbols": ",".join(symbols)})
    
    @retry_api_call()
    def get_historical_data(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> dict:
        """Get historical data with retry logic"""
        logger.info(f"📈 Fetching historical data for {symbol} ({timeframe})")
        return self.fyers_model.get_history({
            "symbol": symbol,
            "resolution": timeframe,
            "date_format": "1",
            "range_from": start_date,
            "range_to": end_date,
            "cont_flag": "1"
        })
    
    @retry_api_call()
    def get_market_depth(self, symbol: str) -> dict:
        """Get market depth with retry logic"""
        logger.info(f"📊 Fetching market depth for {symbol}")
        return self.fyers_model.depth({"symbol": symbol, "ohlcv_flag": "1"})
    
    @retry_api_call()
    def get_profile(self) -> dict:
        """Get profile with retry logic"""
        logger.info("👤 Fetching profile information")
        return self.fyers_model.get_profile()
    
    @retry_websocket_connection()
    def connect_websocket(self, websocket_instance, symbols: List[str]) -> bool:
        """Connect WebSocket with retry logic"""
        logger.info(f"🔗 Connecting WebSocket for {len(symbols)} symbols")
        try:
            websocket_instance.websocket_data = symbols
            websocket_instance.connect()
            return True
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            raise

# === Utility Functions ===

def test_retry_logic():
    """Test the retry logic implementation"""
    print("🧪 TESTING RETRY LOGIC")
    print("=" * 50)
    
    @retry_api_call(max_retries=2, backoff_factor=1.0)
    def mock_api_call(fail_times: int = 0):
        """Mock API call that fails specified number of times"""
        if not hasattr(mock_api_call, 'call_count'):
            mock_api_call.call_count = 0
        
        mock_api_call.call_count += 1
        
        if mock_api_call.call_count <= fail_times:
            raise ConnectionError(f"Mock failure {mock_api_call.call_count}")
        
        return {"status": "success", "attempt": mock_api_call.call_count}
    
    # Test 1: Success on first try
    try:
        result = mock_api_call(fail_times=0)
        print(f"✅ Test 1 (Immediate Success): {result}")
    except Exception as e:
        print(f"❌ Test 1 Failed: {e}")
    
    # Reset counter
    mock_api_call.call_count = 0
    
    # Test 2: Success after 1 retry
    try:
        result = mock_api_call(fail_times=1)
        print(f"✅ Test 2 (Success after 1 retry): {result}")
    except Exception as e:
        print(f"❌ Test 2 Failed: {e}")
    
    # Reset counter
    mock_api_call.call_count = 0
    
    # Test 3: Failure after all retries
    try:
        result = mock_api_call(fail_times=5)
        print(f"❌ Test 3 Should Have Failed: {result}")
    except RetryError as e:
        print(f"✅ Test 3 (Expected Failure): {e}")
    
    print("\n🎯 Retry logic testing complete!")

def demonstrate_enhanced_api():
    """Demonstrate enhanced API usage"""
    print("\n💡 ENHANCED API USAGE EXAMPLE")
    print("=" * 50)
    
    print("""
📝 CODE EXAMPLE:

from fyers_retry_handler import EnhancedFyersAPI, retry_api_call
from my_fyers_model import MyFyersModel

# Initialize enhanced API
fy_model = MyFyersModel()
enhanced_api = EnhancedFyersAPI(fy_model)

# Get quotes with automatic retry
quotes = enhanced_api.get_quotes(['NSE:NIFTY50-INDEX', 'NSE:RELIANCE-EQ'])

# Get historical data with retry
data = enhanced_api.get_historical_data('NSE:NIFTY50-INDEX', '1D', '2024-01-01', '2024-12-31')

# Custom function with retry
@retry_api_call(max_retries=3, backoff_factor=2.0)
def custom_api_function():
    # Your API code here
    pass
""")

if __name__ == "__main__":
    test_retry_logic()
    demonstrate_enhanced_api()