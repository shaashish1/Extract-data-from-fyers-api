# 📊 Enhanced Fyers Data Extraction System - Implementation Plan

## 🎯 Objectives

1. **Dynamic Symbol Discovery**: Replace hardcoded symbols with runtime fetching from Fyers API
2. **Market Depth Data**: Implement Order Book/DOM data extraction and storage
3. **Comprehensive Data Coverage**: Extract all available data types from Fyers API
4. **Scalable Architecture**: Design for easy addition of new data types and symbols

## 📈 Current Data Sources Analysis

### ✅ **Currently Available Data**
1. **OHLCV Historical Data** (`get_history`)
   - Indices: Nifty50, BankNifty, FinNifty, IndiaVIX
   - Stocks: 12 hardcoded symbols (TATAPOWER, RELIANCE, etc.)
   - Timeframes: 1m, 5m, 15m, 1D

2. **Real-time Quotes** (`get_quotes`)
   - Live price updates
   - Basic market data

### 🚀 **New Data Sources to Implement**

#### 1. **Market Depth/Order Book Data** (`get_market_depth`)
```python
# Available fields from market depth:
{
    'totalbuyqty': 12345,      # Total buy quantity
    'totalsellqty': 9876,      # Total sell quantity
    'ask': [                   # Ask orders (5 levels)
        {'price': 1500.50, 'volume': 100, 'ord': 5},
        {'price': 1500.75, 'volume': 200, 'ord': 3},
        # ... up to 5 levels
    ],
    'bids': [                  # Bid orders (5 levels)
        {'price': 1500.25, 'volume': 150, 'ord': 4},
        {'price': 1500.00, 'volume': 300, 'ord': 7},
        # ... up to 5 levels
    ],
    'o': 1499.00,             # Open
    'h': 1505.00,             # High
    'l': 1495.00,             # Low
    'c': 1500.30,             # Close/LTP
    'v': 2500000,             # Volume
    'ltp': 1500.30,           # Last traded price
    'ltq': 25,                # Last traded quantity
    'ltt': timestamp,         # Last traded time
    'atp': 1500.15,           # Average traded price
    'chp': 0.25,              # Change percentage
    'ch': 1.30,               # Change value
    'upper_ckt': 1650.00,     # Upper circuit limit
    'lower_ckt': 1350.00,     # Lower circuit limit
    'oi': 15000,              # Open interest (for F&O)
    'tick_Size': 0.05         # Minimum price movement
}
```

#### 2. **Option Chain Data** (`optionchain`)
```python
# Available from option chain:
{
    'callOi': {...},          # Call options open interest
    'putOi': {...},           # Put options open interest
    'expiryData': [...],      # Available expiry dates
    'indiavixData': {...},    # VIX data
    'optionsChain': [...]     # Complete option chain
}
```

#### 3. **Symbol Discovery** (Dynamic fetching)
- Use option chain to discover available strikes and expiries
- Extract symbols from market data responses
- Build symbol universe dynamically

## 🏗️ Architecture Design

### 📁 **Enhanced Directory Structure**
```
data/parquet/
├── indices/
│   ├── ohlcv/              # Traditional OHLCV data
│   │   ├── nifty50_1D.parquet
│   │   └── niftybank_1m.parquet
│   ├── market_depth/       # Order book data
│   │   ├── nifty50_depth_realtime.parquet
│   │   └── niftybank_depth_realtime.parquet
│   └── option_chains/      # Option chain snapshots
│       ├── nifty50_chain_daily.parquet
│       └── banknifty_chain_daily.parquet
├── stocks/
│   ├── ohlcv/              # Traditional OHLCV data
│   ├── market_depth/       # Order book data
│   └── fundamentals/       # Future: Company fundamentals
├── options/
│   ├── ohlcv/              # Option price data
│   ├── market_depth/       # Option order book
│   └── greeks/             # Future: Option Greeks
└── symbols/
    ├── active_symbols.parquet      # Dynamic symbol list
    ├── symbol_metadata.parquet     # Symbol details
    └── index_constituents.parquet  # Index composition
```

### 🔧 **New Module Structure**

#### 1. **Symbol Discovery Module** (`symbol_discovery.py`)
```python
class SymbolDiscovery:
    def get_active_indices(self) -> List[str]
    def get_active_stocks(self, index: str = None) -> List[str]
    def get_option_symbols(self, underlying: str) -> List[str]
    def get_futures_symbols(self, underlying: str) -> List[str]
    def refresh_symbol_universe(self) -> Dict
    def save_symbol_metadata(self, symbols: Dict) -> None
```

#### 2. **Market Depth Module** (`market_depth_storage.py`)
```python
class MarketDepthManager:
    def save_depth_data(self, symbol: str, depth_data: Dict) -> None
    def get_depth_history(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame
    def get_level2_snapshots(self, symbol: str, timestamp: str) -> Dict
    def analyze_order_flow(self, symbol: str, timeframe: str) -> pd.DataFrame
```

#### 3. **Enhanced Data Orchestrator** (`data_orchestrator.py`)
```python
class DataOrchestrator:
    def discover_and_update_symbols(self) -> None
    def collect_all_data_types(self, symbols: List[str]) -> None
    def schedule_data_collection(self) -> None
    def run_comprehensive_update(self) -> None
```

## 🚀 Implementation Phases

### **Phase 1: Symbol Discovery System** (Week 1)

1. **Create Symbol Discovery Module**
   ```python
   # symbol_discovery.py
   def get_nifty50_constituents():
       """Dynamically fetch Nifty50 constituent symbols"""
       
   def get_banknifty_constituents():
       """Dynamically fetch BankNifty constituent symbols"""
       
   def discover_active_options(underlying):
       """Get all active option contracts for underlying"""
   ```

2. **Implement Symbol Caching**
   - Store discovered symbols in `symbols/active_symbols.parquet`
   - Daily refresh mechanism
   - Symbol metadata (sector, market cap, etc.)

3. **Update Constants Module**
   ```python
   # constants.py - Remove hardcoded symbols
   class SymbolUniverse:
       def __init__(self):
           self.load_from_cache()
       
       def refresh_symbols(self):
           # Dynamic loading from Fyers API
   ```

### **Phase 2: Market Depth Implementation** (Week 2)

1. **Create Market Depth Storage**
   ```python
   # market_depth_storage.py
   def save_depth_snapshot(symbol, depth_data):
       """Save order book snapshot to Parquet"""
       
   def get_bid_ask_spread_history(symbol, timeframe):
       """Analyze spread patterns"""
   ```

2. **Enhance Parquet Storage**
   - New schema for market depth data
   - Efficient storage of bid/ask levels
   - Time-series indexing for fast queries

3. **Real-time Depth Collection**
   ```python
   # Enhanced WebSocket for depth data
   def on_depth_update(symbol, depth_data):
       """Handle real-time depth updates"""
   ```

### **Phase 3: Option Chain Integration** (Week 3)

1. **Option Chain Storage**
   ```python
   # option_chain_storage.py
   def save_option_chain_snapshot(underlying, chain_data):
       """Store complete option chain"""
       
   def get_option_activity(underlying, expiry):
       """Analyze option trading activity"""
   ```

2. **Options Analytics**
   - OI analysis
   - PCR calculations
   - Strike-wise data

### **Phase 4: Data Orchestration** (Week 4)

1. **Unified Data Collection**
   ```python
   # data_orchestrator.py
   def run_comprehensive_collection():
       symbols = discover_all_symbols()
       for symbol in symbols:
           collect_ohlcv_data(symbol)
           collect_depth_data(symbol)
           if is_option_underlying(symbol):
               collect_option_chain(symbol)
   ```

2. **Scheduling & Automation**
   - Market hours detection
   - Intelligent scheduling based on market state
   - Error handling and recovery

## 📊 Data Schema Definitions

### **Market Depth Schema**
```python
depth_schema = {
    'timestamp': 'datetime64[ns]',
    'symbol': 'string',
    'bid_price_1': 'float64', 'bid_volume_1': 'int64', 'bid_orders_1': 'int64',
    'bid_price_2': 'float64', 'bid_volume_2': 'int64', 'bid_orders_2': 'int64',
    # ... up to 5 levels
    'ask_price_1': 'float64', 'ask_volume_1': 'int64', 'ask_orders_1': 'int64',
    'ask_price_2': 'float64', 'ask_volume_2': 'int64', 'ask_orders_2': 'int64',
    # ... up to 5 levels
    'total_bid_qty': 'int64',
    'total_ask_qty': 'int64',
    'spread': 'float64',
    'mid_price': 'float64'
}
```

### **Symbol Metadata Schema**
```python
symbol_metadata_schema = {
    'symbol': 'string',
    'company_name': 'string',
    'sector': 'string',
    'market_cap': 'float64',
    'tick_size': 'float64',
    'lot_size': 'int64',
    'circuit_limits': 'float64',
    'last_updated': 'datetime64[ns]',
    'is_active': 'bool',
    'data_types_available': 'string'  # JSON list of available data types
}
```

## ⚡ Performance Optimizations

1. **Batch Processing**: Collect multiple symbols in single API calls
2. **Compression**: Use Snappy compression for all Parquet files
3. **Partitioning**: Partition by date for faster queries
4. **Indexing**: Create efficient indexes for time-based queries
5. **Caching**: Cache frequently accessed symbol lists

## 🔍 Monitoring & Analytics

1. **Data Quality Metrics**
   - Missing data detection
   - Latency monitoring
   - Error rate tracking

2. **Market Analysis Features**
   - Order flow analysis
   - Liquidity metrics
   - Market microstructure insights

## 🎯 Success Metrics

1. **Symbol Coverage**: 100% dynamic discovery (no hardcoded symbols)
2. **Data Completeness**: All available Fyers data types collected
3. **Performance**: <1 second response time for data queries
4. **Storage Efficiency**: 50%+ reduction in storage size vs raw data
5. **Reliability**: 99.9% uptime for data collection

## 🚀 Quick Start Implementation

### **Priority 1: Symbol Discovery** (Immediate)
1. Create `symbol_discovery.py`
2. Implement Nifty50 constituent fetching
3. Replace hardcoded symbols in existing scripts

### **Priority 2: Market Depth** (This Week)
1. Extend `data_storage.py` for depth data
2. Create depth collection script
3. Test with 2-3 active stocks

### **Priority 3: Integration** (Next Week)
1. Update all existing scripts to use dynamic symbols
2. Implement unified data collection
3. Add comprehensive monitoring

This plan transforms the system from a static, limited data collector to a comprehensive, dynamic market data platform that can scale to handle thousands of symbols and multiple data types efficiently.