#!/usr/bin/env python3
"""
FYERS CONFIGURATION MODULE
Centralized configuration inspired by OpenAI guide
Enhanced version of their config.py approach
"""

import os
from typing import Dict, Any
from datetime import timedelta

class FyersConfig:
    """Centralized configuration for Fyers API system"""
    
    # === API Configuration ===
    FYERS_API_BASE = os.getenv("FYERS_API_BASE", "https://api.fyers.in")
    
    # API Endpoints (Fyers API v3)
    ENDPOINTS = {
        "token": "/api/v3/token",
        "profile": "/api/v3/profile", 
        "funds": "/api/v3/funds",
        "history": "/api/v3/history",
        "quotes": "/api/v3/quotes",
        "market_depth": "/api/v3/depth",
        "option_chain": "/api/v3/optionchain",
        "symbols": "/api/v3/symbols",
        "instruments": "/api/v3/instruments",  # if available
        "websocket": "wss://api.fyers.in/socket/v3/dataSock",
        "order_socket": "wss://api.fyers.in/socket/v3/orderSock"
    }
    
    # === Cache TTL Configuration (in seconds) ===
    CACHE_TTLS = {
        # Static symbol lists (refresh daily)
        "indices": 24 * 3600,          # 24 hours
        "etfs": 24 * 3600,             # 24 hours  
        "large_cap": 24 * 3600,        # 24 hours
        "mid_cap": 24 * 3600,          # 24 hours
        "small_cap": 24 * 3600,        # 24 hours
        "sectoral_indices": 24 * 3600, # 24 hours
        "commodities": 24 * 3600,      # 24 hours
        "currency": 24 * 3600,         # 24 hours
        "bonds": 24 * 3600,            # 24 hours
        
        # Dynamic instruments (shorter TTL)
        "futures": 3600,               # 1 hour
        "options": 10 * 60,            # 10 minutes
        "option_chains": 5 * 60,       # 5 minutes
        
        # Market data (very short TTL)
        "quotes": 30,                  # 30 seconds
        "market_depth": 10,            # 10 seconds
        "real_time_data": 1,           # 1 second
        
        # Full instrument list (daily refresh)
        "instruments_full": 24 * 3600, # 24 hours
    }
    
    # === Retry Configuration ===
    RETRY_CONFIG = {
        "max_retries": 3,
        "backoff_factor": 1.5,
        "retry_on_status": [429, 500, 502, 503, 504],  # HTTP status codes to retry
        "retry_on_exceptions": ["ConnectionError", "Timeout", "HTTPError"],
        "max_backoff": 60,  # Maximum backoff time in seconds
    }
    
    # === Rate Limiting ===
    RATE_LIMITS = {
        "api_calls_per_second": 10,
        "api_calls_per_minute": 600,
        "websocket_subscriptions": 1000,
        "concurrent_requests": 5,
        "delay_between_calls": 0.1,  # 100ms delay between API calls
    }
    
    # === WebSocket Configuration ===
    WEBSOCKET_CONFIG = {
        "heartbeat_interval": 30,
        "reconnect_attempts": 5,
        "reconnect_delay": 5,
        "buffer_size": 100,
        "batch_save_interval": 300,  # 5 minutes
        "max_queue_size": 10000,
    }
    
    # === Data Storage Configuration ===
    STORAGE_CONFIG = {
        "data_directory": "data/parquet",
        "backup_directory": "data/backup", 
        "log_directory": "logs",
        "temp_directory": "temp",
        "compression": "snappy",
        "max_file_size_mb": 100,
        "partition_by": "date",
        "file_format": "parquet",
    }
    
    # === Symbol Categories Configuration ===
    SYMBOL_CATEGORIES = {
        "equity": {
            "nifty50": {"priority": 1, "refresh_interval": "daily"},
            "nifty100": {"priority": 2, "refresh_interval": "daily"},
            "nifty200": {"priority": 3, "refresh_interval": "daily"},
            "bank_nifty": {"priority": 1, "refresh_interval": "daily"},
            "small_cap": {"priority": 4, "refresh_interval": "daily"},
            "mid_cap": {"priority": 4, "refresh_interval": "daily"},
        },
        "indices": {
            "major_indices": {"priority": 1, "refresh_interval": "daily"},
            "sectoral_indices": {"priority": 2, "refresh_interval": "daily"},
        },
        "derivatives": {
            "nifty_options": {"priority": 1, "refresh_interval": "hourly"},
            "banknifty_options": {"priority": 1, "refresh_interval": "hourly"},
            "finnifty_options": {"priority": 2, "refresh_interval": "hourly"},
            "stock_options": {"priority": 3, "refresh_interval": "hourly"},
            "index_futures": {"priority": 2, "refresh_interval": "hourly"},
            "stock_futures": {"priority": 3, "refresh_interval": "hourly"},
        },
        "alternatives": {
            "etfs": {"priority": 2, "refresh_interval": "daily"},
            "commodities": {"priority": 3, "refresh_interval": "daily"},
            "currency": {"priority": 3, "refresh_interval": "daily"},
            "bonds": {"priority": 4, "refresh_interval": "daily"},
        }
    }
    
    # === Option Chain Configuration ===
    OPTION_CONFIG = {
        "strike_range": 20,            # Number of strikes above/below current price
        "expiry_count": 4,             # Number of expiry dates to include
        "min_open_interest": 0,        # Minimum OI filter
        "include_weekly": True,
        "include_monthly": True,
    }
    
    # === Timeframe Configuration ===
    TIMEFRAMES = {
        "1m": {"seconds": 60, "api_code": "1"},
        "5m": {"seconds": 300, "api_code": "5"},
        "15m": {"seconds": 900, "api_code": "15"},
        "30m": {"seconds": 1800, "api_code": "30"},
        "1H": {"seconds": 3600, "api_code": "60"},
        "1D": {"seconds": 86400, "api_code": "D"},
        "1W": {"seconds": 604800, "api_code": "W"},
        "1M": {"seconds": 2592000, "api_code": "M"},
    }
    
    # === Scheduled Tasks Configuration ===
    SCHEDULE_CONFIG = {
        "symbol_refresh": {
            "time": "08:00",           # 8 AM daily refresh
            "timezone": "Asia/Kolkata",
            "enabled": True,
        },
        "data_cleanup": {
            "time": "02:00",           # 2 AM daily cleanup
            "timezone": "Asia/Kolkata", 
            "enabled": True,
        },
        "backup": {
            "time": "23:00",           # 11 PM daily backup
            "timezone": "Asia/Kolkata",
            "enabled": False,          # Disabled by default
        }
    }
    
    # === Logging Configuration ===
    LOGGING_CONFIG = {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_rotation": "daily",
        "max_file_size_mb": 10,
        "backup_count": 7,
        "log_to_console": True,
        "log_to_file": True,
    }
    
    # === Environment-specific Overrides ===
    @classmethod
    def get_env_config(cls) -> Dict[str, Any]:
        """Get environment-specific configuration overrides"""
        env = os.getenv("FYERS_ENV", "production").lower()
        
        if env == "development":
            return {
                "RATE_LIMITS": {**cls.RATE_LIMITS, "delay_between_calls": 0.5},
                "LOGGING_CONFIG": {**cls.LOGGING_CONFIG, "level": "DEBUG"},
                "CACHE_TTLS": {**cls.CACHE_TTLS, "options": 60},  # Longer TTL for dev
            }
        elif env == "testing":
            return {
                "RATE_LIMITS": {**cls.RATE_LIMITS, "delay_between_calls": 0},
                "CACHE_TTLS": {k: 10 for k in cls.CACHE_TTLS},  # Short TTL for testing
                "RETRY_CONFIG": {**cls.RETRY_CONFIG, "max_retries": 1},
            }
        else:  # production
            return {}
    
    # === Validation Methods ===
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        try:
            # Check required environment variables
            required_env_vars = ["FYERS_CLIENT_ID", "FYERS_SECRET_KEY"]
            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            
            if missing_vars:
                print(f"❌ Missing environment variables: {missing_vars}")
                return False
            
            # Validate directories exist or can be created
            directories = [
                cls.STORAGE_CONFIG["data_directory"],
                cls.STORAGE_CONFIG["log_directory"],
                cls.STORAGE_CONFIG["temp_directory"]
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            print("✅ Configuration validation passed")
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False
    
    # === Utility Methods ===
    @classmethod
    def get_cache_ttl(cls, category: str) -> int:
        """Get cache TTL for a specific category"""
        return cls.CACHE_TTLS.get(category, 3600)  # Default 1 hour
    
    @classmethod
    def get_endpoint_url(cls, endpoint: str) -> str:
        """Get full URL for an API endpoint"""
        endpoint_path = cls.ENDPOINTS.get(endpoint, "")
        return f"{cls.FYERS_API_BASE}{endpoint_path}"
    
    @classmethod
    def get_symbol_priority(cls, category: str, subcategory: str) -> int:
        """Get priority for symbol category"""
        try:
            return cls.SYMBOL_CATEGORIES[category][subcategory]["priority"]
        except KeyError:
            return 5  # Default low priority

# === Global Configuration Instance ===
config = FyersConfig()

# === Configuration Display Function ===
def display_config():
    """Display current configuration summary"""
    print("🔧 FYERS SYSTEM CONFIGURATION")
    print("=" * 50)
    print(f"📡 API Base: {config.FYERS_API_BASE}")
    print(f"🗂️  Data Directory: {config.STORAGE_CONFIG['data_directory']}")
    print(f"📊 Symbol Categories: {len(config.SYMBOL_CATEGORIES)}")
    print(f"⏱️  Cache TTL Types: {len(config.CACHE_TTLS)}")
    print(f"🔄 Max Retries: {config.RETRY_CONFIG['max_retries']}")
    print(f"📈 Rate Limit: {config.RATE_LIMITS['api_calls_per_second']} calls/sec")
    print(f"🔗 WebSocket Buffer: {config.WEBSOCKET_CONFIG['buffer_size']}")
    print(f"📅 Auto Refresh: {config.SCHEDULE_CONFIG['symbol_refresh']['time']}")
    
    # Validate configuration
    is_valid = config.validate_config()
    status = "✅ VALID" if is_valid else "❌ INVALID"
    print(f"\n🎯 Configuration Status: {status}")

if __name__ == "__main__":
    display_config()