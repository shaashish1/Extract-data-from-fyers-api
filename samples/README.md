# 🚀 Fyers WebSocket Live - Sample Code & Testing Suite

**Professional testing and sample code for FYERS API integration with our enhanced system**

## 📂 Directory Structure

```
samples/
├── websocket/              # WebSocket streaming examples
│   ├── basic_streaming_test.py    # Basic WebSocket test
│   └── nifty50_streaming.py       # Nifty50 portfolio streaming
├── market_data/            # Market data API testing
│   └── api_testing_suite.py       # Comprehensive API tests
├── run_tests.py           # Master test runner
└── README.md              # This file
```

## 🎯 Quick Start Guide

### 1. Prerequisites

Ensure you have completed the basic setup:
- ✅ FYERS API credentials configured in `auth/credentials.ini`
- ✅ Access token generated and saved
- ✅ Required dependencies installed (`pip install -r requirements.txt`)
- ✅ MyFyersModel authentication system working

### 2. Master Test Runner (RECOMMENDED)

**Run all tests in sequence with professional reporting:**

```bash
python samples/run_tests.py
```

**Features:**
- 🔐 Authentication verification using MyFyersModel
- � Market data API testing
- 🔍 Symbol discovery validation
- ⚡ WebSocket streaming test
- � Comprehensive test report

### 3. Market Data API Testing

**Test all FYERS API endpoints:**

```bash
python samples/market_data/api_testing_suite.py
```

**Features:**
- 📊 Market status checking
- 💰 Real-time quotes testing
- 📈 Market depth analysis
- 📉 Historical data retrieval
- 🔍 Symbol discovery integration

### 4. Basic WebSocket Streaming

**Simple WebSocket streaming test:**

```bash
python samples/websocket/basic_streaming_test.py
```

**Features:**
- ⚡ Real-time data streaming
- 📱 Rich monitoring dashboard
- 💾 Optional data persistence
- 🎯 Popular stock symbols
- 📊 Live statistics

### 5. Advanced Nifty50 Streaming

**Professional portfolio streaming:**

```bash
python samples/websocket/nifty50_streaming.py
```

**Features:**
- 🏦 Complete Nifty50 portfolio
- 📈 Real-time analytics dashboard
- 💾 Auto-save to Parquet storage
- 📊 Portfolio performance metrics
- 🔄 Professional error handling

## 🧪 Testing Workflow

### Recommended Testing Sequence:

1. **🧪 Master Test Runner**
   ```bash
   python samples/run_tests.py
   ```
   - Complete system verification
   - Authentication via MyFyersModel
   - All components validation

2. **📊 API Functionality**
   ```bash
   python samples/market_data/api_testing_suite.py
   ```
   - Test all API endpoints
   - Verify data access
   - Check market status

3. **⚡ Basic WebSocket**
   ```bash
   python samples/websocket/basic_streaming_test.py
   ```
   - Test real-time streaming
   - Verify data reception
   - Check performance

4. **🏦 Advanced Streaming**
   ```bash
   python samples/websocket/nifty50_streaming.py
   ```
   - Full portfolio streaming
   - Data persistence testing
   - Analytics verification

## 🔧 Sample Code Features

### Master Test Runner (`run_tests.py`)

**Comprehensive test suite runner with professional reporting**

```python
# Key Features:
🧪 Sequential test execution
🔐 Authentication verification via MyFyersModel
📊 API endpoint testing
🔍 Symbol discovery validation
⚡ WebSocket streaming test
📋 Professional test reporting
```

**Usage Scenarios:**
- Complete system verification
- Production readiness check
- Troubleshooting guidance
- Performance validation

### WebSocket Streaming (`basic_streaming_test.py`)

**Real-time market data streaming with professional monitoring**

```python
# Key Features:
⚡ Real-time WebSocket streaming
📱 Rich monitoring dashboard  
📊 Live market data display
💾 Optional Parquet storage
🎯 Popular symbol tracking
```

**Configuration Options:**
```python
# Customize symbols
symbols = [
    'NSE:RELIANCE-EQ',
    'NSE:TCS-EQ', 
    'NSE:HDFCBANK-EQ'
]

# Set duration
duration_minutes = 5

# Enable data persistence
save_to_storage = True
```

### Nifty50 Portfolio Streaming (`nifty50_streaming.py`)

**Advanced portfolio streaming with analytics**

```python
# Key Features:
🏦 Complete Nifty50 portfolio
📈 Real-time portfolio dashboard
💾 Auto-save every 60 seconds
📊 Performance analytics
🔄 Auto-reconnection
```

**Advanced Configuration:**
```python
# Portfolio settings
save_interval = 60  # Auto-save interval
buffer_size = 100   # Data buffer size
lite_mode = False   # Full data mode

# Analytics options
show_gainers_losers = True
display_volume = True
track_circuit_limits = True
```

### Market Data API Testing (`api_testing_suite.py`)

**Comprehensive API endpoint testing**

```python
# Test Coverage:
📅 Market status API
💰 Real-time quotes
📊 Market depth (Level 2)
📈 Historical data
🔍 Symbol search integration
```

**Test Results:**
- ✅ Pass/Fail status for each API
- 📊 Response data samples
- ⚡ Performance metrics
- 💾 Sample data storage

## 📊 Sample Output Examples

### Master Test Runner Results
```
🧪 Fyers WebSocket Live - Test Report
┌─────────────────────┬────────┬──────────┬──────────────────────┐
│ Test Component      │ Status │ Result   │ Details              │
├─────────────────────┼────────┼──────────┼──────────────────────┤
│ Authentication      │ ✅ PASS │ Success  │ MyFyersModel working │
│ Market Data APIs    │ ✅ PASS │ Success  │ All endpoints OK     │
│ Symbol Discovery    │ ✅ PASS │ Success  │ 50 symbols found     │
│ WebSocket Streaming │ ✅ PASS │ Success  │ 1 minute streaming   │
└─────────────────────┴────────┴──────────┴──────────────────────┘

🎉 ALL TESTS PASSED
✅ Your FYERS WebSocket Live system is ready for production!
```

### WebSocket Streaming Dashboard
```
📈 Nifty50 Live Portfolio
┌───────────┬──────────┬─────────┬─────────┬────────────┬──────────────┐
│ Symbol    │ LTP      │ Change  │ Change% │ Volume     │ H/L          │
├───────────┼──────────┼─────────┼─────────┼────────────┼──────────────┤
│ RELIANCE  │ ₹2,456.75│ +12.50  │ +0.51%  │ 1,234,567  │ 2,467/2,445  │
│ TCS       │ ₹3,890.20│ +8.75   │ +0.23%  │ 987,654    │ 3,895/3,882  │
└───────────┴──────────┴─────────┴─────────┴────────────┴──────────────┘
```

### API Test Summary
```
🧪 Test Results
┌─────────────────┬────────┬─────────┐
│ Test            │ Status │ Result  │
├─────────────────┼────────┼─────────┤
│ Market Status   │ ✅ PASS │ Success │
│ Quotes API      │ ✅ PASS │ Success │
│ Market Depth    │ ✅ PASS │ Success │
│ Historical Data │ ✅ PASS │ Success │
│ Symbol Discovery│ ✅ PASS │ Success │
└─────────────────┴────────┴─────────┘
```

## 🛠️ Customization Guide

### Adding New Symbols

**For WebSocket streaming:**
```python
# Edit symbols list in any WebSocket sample
symbols = [
    'NSE:YOUR_SYMBOL-EQ',
    'BSE:YOUR_SYMBOL-EQ',
    'MCX:YOUR_COMMODITY'
]
```

### Modifying Data Storage

**Enable/disable data persistence:**
```python
# In WebSocket samples
save_to_storage = True  # Enable Parquet storage
save_interval = 60      # Save every 60 seconds
buffer_size = 100       # Buffer 100 records
```

### Customizing Display

**Modify Rich tables and displays:**
```python
# Add new columns to market data tables
table.add_column("New Metric", style="cyan")

# Change refresh rates
with Live(dashboard, refresh_per_second=1):  # 1 Hz refresh
```

## 🔍 Troubleshooting

### Common Issues & Solutions

#### 1. Authentication Failures
```bash
# Run complete system test
python samples/run_tests.py

# Manual auth verification
python -c "from my_fyers_model import MyFyersModel; fyers = MyFyersModel(); print(fyers.get_profile())"

# Common fixes:
✅ Check credentials.ini format
✅ Generate new access token
✅ Verify client_id format
✅ Ensure access_token.txt exists
```

#### 2. WebSocket Connection Issues
```bash
# Check market hours
python samples/market_data/api_testing_suite.py

# Common fixes:
✅ Verify market is open
✅ Check symbol formats
✅ Test with basic symbols first
```

#### 3. Data Storage Problems
```bash
# Verify storage system
python scripts/data_storage.py

# Common fixes:
✅ Check write permissions
✅ Verify Parquet dependencies
✅ Test with small datasets
```

### Debug Mode

**Enable detailed logging in any sample:**
```python
# Add at the top of any sample file
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use Rich debugging
from rich.traceback import install
install(show_locals=True)
```

## 📈 Performance Tips

### Optimization Guidelines

1. **Symbol Limits**
   - Start with ≤10 symbols for testing
   - Gradually increase based on performance
   - Monitor memory usage with large symbol lists

2. **Data Buffer Management**
   ```python
   # Optimize buffer sizes
   buffer_size = 50    # Smaller for testing
   save_interval = 30  # More frequent saves
   ```

3. **Display Refresh Rates**
   ```python
   # Reduce refresh for better performance
   refresh_per_second = 1  # 1 Hz instead of 2 Hz
   ```

## 🎯 Next Steps

After completing all sample tests:

1. **✅ Verify All Tests Pass**
   - Authentication working
   - API endpoints accessible
   - WebSocket streaming functional

2. **🚀 Move to Production Scripts**
   - Use `scripts/run_websocket.py` for live streaming
   - Run `scripts/comprehensive_symbol_discovery.py` for full symbol universe
   - Implement `scripts/data_analysis.py` for analytics

3. **📊 Build Custom Applications**
   - Adapt sample code for specific needs
   - Integrate with trading algorithms
   - Create custom analytics dashboards

## 💡 Tips for Success

- **Start Small**: Begin with basic_streaming_test.py
- **Test Incrementally**: Add features one at a time  
- **Monitor Performance**: Watch memory and CPU usage
- **Use Market Hours**: Test during active trading sessions
- **Check Logs**: Review output for any warnings
- **Backup Data**: Save important streaming data

---

## 🎉 Ready to Go Live?

Once all samples pass successfully, your FYERS WebSocket Live system is ready for production use with the complete 156K+ symbol universe!

**Next**: Explore the main `scripts/` directory for production-ready tools and the comprehensive symbol discovery system.