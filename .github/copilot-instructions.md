# Copilot Instructions for Fyers API Data Extraction Project

## Project Overview
Professional Indian stock market data extraction system using Fyers API v3, storing data in **Parquet files** for analytics. Supports historical data, real-time WebSocket streaming, market depth (Level 2), and dynamic symbol discovery.

## Core Architecture

### Central Service Components
- **`my_fyers_model.py`**: Main API wrapper with auto-authentication (`MyFyersModel` class)
- **`data_storage.py`**: Parquet data manager (`ParquetDataManager` - use `get_parquet_manager()`)
- **`symbol_discovery.py`**: Dynamic symbol discovery from Fyers API (replaces hardcoded lists)
- **`market_depth_storage.py`**: Level 2 market data (order book/DOM) management

### Data Flow Architecture
1. **Historical**: `stocks_data.py` → Fyers API → DataFrame → Parquet (`indices/`, `stocks/`, `options/`)
2. **Real-time**: `run_websocket.py` → WebSocket → buffer → batch-save to Parquet  
3. **Updates**: `update_tables.py` checks `get_last_timestamp()` → incremental fetch
4. **Market Depth**: `MarketDepthManager` → Level 2 data → separate Parquet storage

### Storage Organization
```python
data/parquet/
├── indices/         # nifty50_1D.parquet, niftybank_1m.parquet
├── stocks/          # tatapower_1D.parquet, reliance_1m.parquet
├── options/         # option chain data
├── market_depth/    # Level 2 order book data
├── market_updates/  # raw SymbolUpdate messages
├── fyers_symbols/   # Direct Fyers symbol cache (preferred)
└── nse_symbols/     # NSE symbol mappings (fallback)

# Standard usage pattern
from data_storage import get_parquet_manager
manager = get_parquet_manager()
df = manager.load_data('nifty50', '1D', start_date='2024-01-01')
manager.save_data(df, 'symbol', '1D', mode='append')

# Optimized symbol discovery
from fyers_direct_discovery import get_fyers_direct_discovery
fyers_direct = get_fyers_direct_discovery()
nifty50_symbols = fyers_direct.get_nifty50_constituents()  # No downloads needed
```

## Critical Configuration & Auth

### Authentication Flow (Manual Process)
1. **Setup**: Configure `auth/credentials.ini` with Fyers client_id, secret_key
2. **First Run**: Script generates auth URL → **manual browser auth** → paste auth code
3. **Token Storage**: `auth/access_token.txt` auto-created (expires periodically)
4. **Path Resolution**: Scripts use relative paths to find auth files from any working directory

### Symbol Management
- **Direct Fyers Discovery**: `fyers_direct_discovery.py` gets symbols directly from Fyers API (preferred)
- **NSE Data Integration**: `nse_data_fetcher.py` downloads live symbol lists from NSE APIs (fallback)
- **Unified Discovery**: `symbol_discovery.py` combines both approaches with smart fallbacks
- **Index Constituents**: Real-time Nifty50/100/200 from proven lists + Fyers validation
- **ETF & Derivatives**: Direct discovery via Fyers quotes and option chain APIs
- **Auto-cleanup**: Downloaded CSV/TXT files automatically deleted after processing

### Symbol Discovery Workflow (Optimized)
```python
# Method 1: Direct Fyers (Preferred - No downloads)
from fyers_direct_discovery import get_fyers_direct_discovery
fyers_direct = get_fyers_direct_discovery()
nifty50 = fyers_direct.get_nifty50_constituents()  # Uses proven lists
options = fyers_direct.discover_option_symbols('NSE:NIFTY50-INDEX')

# Method 2: Unified (Smart fallbacks)
from symbol_discovery import SymbolDiscovery
discovery = SymbolDiscovery()
nifty50 = discovery.get_nifty50_constituents()  # Tries Fyers → NSE → fallback

# Method 3: NSE Data (Legacy/validation)
from nse_data_fetcher import get_nse_fetcher
nse_fetcher = get_nse_fetcher()
nse_fetcher.fetch_all_nse_data(save_to_parquet=True)  # Auto-deletes CSVs
```

## Development Patterns

### Data Processing Standards
- **Timestamps**: Always epoch → UTC → `Asia/Kolkata` → remove timezone info before storage
- **Column Order**: Standardized `["timestamp", "open", "high", "low", "close", "volume"]`
- **File Naming**: `{symbol}_{timeframe}.parquet` (e.g., `nifty50_1D`, `reliance_5m`)
- **Auto-categorization**: Storage dir determined by symbol pattern (indices/stocks/options)

### WebSocket Real-time Patterns
```python
# Real-time data collection with buffer management
data_buffer = []  # Collect data in memory
buffer_size = 100  # Save every 100 points
save_interval = timedelta(minutes=5)  # Or every 5 minutes

# Threading pattern for non-blocking WebSocket
threading.Thread(target=websocket_runner, daemon=True).start()
```

### Timeframe Conversion
- **Use**: `timeframe_converter.py` functions for OHLCV resampling
- **Pattern**: 1m data → resample to 5m, 15m, hourly, daily using pandas `resample()`
- **Index**: Set timestamp as index before resampling operations

### Market Depth (Level 2)
```python
from market_depth_storage import MarketDepthManager
depth_mgr = MarketDepthManager()
depth_data = depth_mgr.get_market_depth('NSE:HDFCBANK-EQ')
# Returns bid/ask levels, spreads, order flow analysis
```

## Common Operations

### Running Core Components
```bash
# Historical data extraction (modify SYMBOL/dates in script)
python scripts/stocks_data.py

# Update all existing data files incrementally  
python scripts/update_tables.py

# Real-time data collection (optimized with direct Fyers discovery)
python scripts/run_websocket.py

# Data analysis and exports
python scripts/data_analysis.py

# Direct Fyers symbol discovery demo (PREFERRED)
python scripts/optimization_demo.py

# NSE symbol management demo (legacy)
python scripts/nse_symbol_demo.py

# Quick symbol refresh (no downloads needed with direct Fyers)
python -c "from fyers_direct_discovery import get_fyers_direct_discovery; fyers_direct = get_fyers_direct_discovery(); fyers_direct.save_discovered_symbols()"
```

### Data Operations
```python
# Check data coverage
manager.list_available_data()
info = manager.get_data_info('symbol', 'timeframe')

# Load with filtering
df = manager.load_data('nifty50', '1D', 
                       start_date='2024-01-01', 
                       end_date='2024-12-31')

# Export compatibility
from data_analysis import export_to_csv
export_to_csv('symbol', 'timeframe', output_dir='exports/')
```

### Adding New Symbols
1. **Direct Fyers**: Use `fyers_direct.get_*_constituents()` methods (preferred)
2. **Auto-discovery**: Use `discovery.get_nifty50_constituents()` with smart fallbacks
3. **NSE Refresh**: Run `nse_fetcher.fetch_all_nse_data()` for validation/backup
4. **Manual**: Add to `index_constituents.py` for proven lists
5. **Files**: Auto-created on first data save
6. **Updates**: `update_tables.py` automatically includes new data files

### Optimized Symbol Operations
```python
# Direct Fyers approach (PREFERRED - No downloads)
from fyers_direct_discovery import get_fyers_direct_discovery
fyers_direct = get_fyers_direct_discovery()

# 1. Get symbols directly from Fyers
nifty50 = fyers_direct.get_nifty50_constituents()
bank_nifty = fyers_direct.get_bank_nifty_constituents()
etfs = fyers_direct.get_popular_etfs()

# 2. Option chain discovery
options = fyers_direct.discover_option_symbols('NSE:NIFTY50-INDEX', strike_count=10)

# 3. Quote validation
quote = fyers_direct.get_symbol_quote('NSE:RELIANCE-EQ')

# 4. Save to cache for persistence
fyers_direct.save_discovered_symbols()

# Unified approach with fallbacks
from symbol_discovery import SymbolDiscovery
discovery = SymbolDiscovery()
nifty50 = discovery.get_nifty50_constituents()  # Tries Fyers → NSE → fallback
```

## Architecture Decisions

### Fyers-Only Data Strategy
- **No Fallbacks**: Removed Yahoo Finance/other sources for data accuracy
- **Real-time Focus**: Fyers API provides true real-time data vs delayed alternatives
- **API Limits**: Built-in `time.sleep(1)` in historical loops to respect rate limits

### Parquet Migration Benefits
- **Performance**: 10x faster than MySQL for analytics workloads
- **Deployment**: No database setup - files are portable
- **Compression**: Automatic Snappy compression reduces storage
- **Schema**: Auto-managed columnar storage with type preservation

## Debugging & Troubleshooting

### Authentication Issues
- Verify `auth/credentials.ini` has correct Fyers API credentials
- Check `auth/access_token.txt` exists and isn't expired
- Re-run auth flow when token expires (manual browser step required)

### Data Issues  
- Use `manager.list_available_data()` to see available files
- Check `get_last_timestamp()` for incremental update status
- Run `data_analysis.py` for coverage analysis and gap detection
- Inspect `logs/` directory for Fyers API error messages

### WebSocket Issues
- WebSocket requires active market hours for live data
- Check symbol format: must be Fyers format (`NSE:SYMBOL-EQ`)
- Buffer size and save intervals configurable in `run_websocket.py`

## Dependencies & Requirements
- **Core**: `fyers-apiv3`, `pandas`, `pyarrow` (for Parquet), `numpy`
- **Optional**: `matplotlib`, `seaborn` for analysis/visualization  
- **Auth**: `configparser` for credentials management
- **Real-time**: Fyers API subscription required for live data access