# 🚀 Quick Reference Guide - Backtesting System

**Last Updated:** October 28, 2025, 22:30 IST  
**Status:** ✅ Production Ready (Awaiting Full Data)

---

## 🎯 Quick Commands

### Activate Backtesting Environment
```powershell
# ALWAYS activate this before running backtesting code
.\venv_backtesting\Scripts\Activate.ps1

# Verify activation (should show Python 3.9.13)
python --version
```

### Check System Status
```powershell
# Check rate limiter statistics
python -c "from scripts.core.rate_limit_manager import get_rate_limiter; get_rate_limiter().print_statistics()"

# Check available data
python -c "from scripts.backtesting.engine.data_loader import BacktestDataLoader; print(BacktestDataLoader().get_available_data_summary())"

# Test API access (check if block cleared)
python -c "from scripts.auth.my_fyers_model import MyFyersModel; fyers = MyFyersModel(); print('✅ API Active' if fyers.fyers else '❌ Still Blocked')"
```

### Run Demos
```powershell
# Activate environment first
.\venv_backtesting\Scripts\Activate.ps1

# Run comprehensive demo (7 tests)
python scripts\backtesting\demo_vectorbt_capabilities.py

# Expected output: All demos pass ✅
```

---

## 📊 System Architecture

### Two Python Environments

#### System Python (3.14.0)
```
Location: C:\Python314\
Purpose: Fyers API operations
Use for: 
  - Data downloads (history_api.py)
  - Real-time WebSocket (run_websocket.py)
  - Market data (quotes_api.py, market_depth_api.py)
  - Option chain (option_chain_api.py)
```

#### Backtesting Python (3.9.13 in venv)
```
Location: venv_backtesting\
Purpose: vectorbt backtesting
Use for:
  - Backtesting (demo_vectorbt_capabilities.py)
  - Strategy development
  - Performance analysis
  - Optimization
```

---

## 🗂️ Key File Locations

### Core Infrastructure
```
scripts/core/rate_limit_manager.py       # Rate limiter (prevents API blocks)
scripts/auth/my_fyers_model.py           # Authentication wrapper
scripts/data/data_storage.py             # Parquet data manager
```

### Market Data APIs (Rate-Limited)
```
scripts/market_data/history_api.py       # Historical OHLCV data
scripts/market_data/quotes_api.py        # Real-time quotes
scripts/market_data/market_depth_api.py  # Level 2 order book
scripts/market_data/option_chain_api.py  # Option chain data
```

### Backtesting
```
scripts/backtesting/engine/data_loader.py              # Data loading
scripts/backtesting/demo_vectorbt_capabilities.py      # Comprehensive demo
scripts/backtesting/strategies/built_in/               # Built-in strategies (pending)
scripts/backtesting/strategies/custom/                 # Custom strategies
```

### Data Storage
```
data/parquet/
├── indices/        # Index data (NIFTY50, BANKNIFTY, etc.)
├── stocks/         # Stock data (RELIANCE, TCS, etc.)
└── options/        # Option data
```

### Documentation
```
docs/PROGRESS_TRACKER.md                  # Master progress tracker
docs/BACKTESTING_TEST_PLAN.md            # Testing strategy
docs/SESSION_SUMMARY_EVENING.md          # Today's summary
docs/VENV_SETUP_COMPLETE.md              # Environment setup guide
docs/BACKTESTING_FRAMEWORK_SELECTION.md  # Framework analysis
docs/FYERS_RATE_LIMITS.md                # Rate limit reference
```

---

## 🔄 Common Workflows

### Workflow 1: Download Historical Data (After API Recovery)
```powershell
# 1. Verify API access restored
python -c "from scripts.auth.my_fyers_model import MyFyersModel; fyers = MyFyersModel(); print('✅' if fyers.fyers else '❌')"

# 2. Download indices (fast)
python scripts\market_data\history_api.py
# Edit script to download: NIFTY50, BANKNIFTY, FINNIFTY, INDIAVIX
# Date range: 2020-01-01 to 2025-10-28
# Timeframes: 1D, 1h, 15m

# 3. Download Nifty50 stocks (rate-limited, ~60-90 minutes)
# Edit history_api.py with Nifty50 symbol list
# Run same command, rate limiter auto-throttles

# 4. Verify download
python -c "from scripts.backtesting.engine.data_loader import BacktestDataLoader; print(BacktestDataLoader().get_available_data_summary())"
```

### Workflow 2: Run Backtesting Demo
```powershell
# 1. Activate backtesting environment
.\venv_backtesting\Scripts\Activate.ps1

# 2. Run comprehensive demo
python scripts\backtesting\demo_vectorbt_capabilities.py

# 3. Review output (7 demos):
#    - Data loading
#    - Indicators (MA, RSI, Bollinger)
#    - Signal generation
#    - Portfolio backtesting
#    - Performance metrics
#    - Multi-symbol processing
#    - Visualization

# 4. Check for errors
# All demos should pass ✅
```

### Workflow 3: Develop New Strategy
```powershell
# 1. Activate environment
.\venv_backtesting\Scripts\Activate.ps1

# 2. Create strategy file
# Location: scripts/backtesting/strategies/built_in/your_strategy.py

# 3. Template:
"""
import vectorbt as vbt
from scripts.backtesting.engine.data_loader import BacktestDataLoader

def run_strategy(symbol='nifty50', timeframe='1D'):
    # Load data
    loader = BacktestDataLoader()
    df = loader.load_symbol(symbol, timeframe)
    
    # Calculate indicators
    fast_ma = vbt.MA.run(df['close'], 50)
    slow_ma = vbt.MA.run(df['close'], 200)
    
    # Generate signals
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)
    
    # Backtest
    pf = vbt.Portfolio.from_signals(
        df['close'], entries, exits,
        init_cash=100000, fees=0.001
    )
    
    # Results
    print(pf.stats())
    pf.plot().show()
    
    return pf

if __name__ == "__main__":
    run_strategy()
"""

# 4. Run strategy
python scripts\backtesting\strategies\built_in\your_strategy.py

# 5. Analyze results
```

### Workflow 4: Check Rate Limiter Status
```powershell
# Quick status check
python -c "from scripts.core.rate_limit_manager import get_rate_limiter; get_rate_limiter().print_statistics()"

# Expected output:
# ==================== RATE LIMITER STATISTICS ====================
# Per-second rate limit:   5 requests/sec
# Per-minute rate limit:   150 requests/min
# Per-day rate limit:      90000 requests/day
# 
# Current Status:
#   Requests (last second):  0
#   Requests (last minute):  0
#   Requests today:          0
#   Violations today:        0/3
#   Daily reset at:          2025-10-29 00:00:00 IST
# 
# Protection Status:        ✅ ACTIVE
```

---

## ⚡ Critical Notes

### ⚠️ API Rate Limits
```
Fyers API Limits:
├── Per-second:  10 requests/sec  (We use 5 - 50% margin)
├── Per-minute:  200 requests/min (We use 150 - 25% margin)
├── Per-day:     100,000 requests (We use 90,000 - 10% margin)
└── Violations:  3 violations = 24-hour block

Current Status:
├── Blocked until: Midnight IST (00:00 UTC+5:30)
├── Time remaining: ~1.5 hours
└── Rate limiter: ✅ Active and ready to prevent future blocks
```

### ⚠️ Data Limitations (Current)
```
Current Data:
├── Symbols: 8 (very limited)
├── Timeframes: 1D only
├── Date range: Oct 20-24, 2025 (2-4 days)
└── Status: Insufficient for production backtesting

Target Data (After Download):
├── Symbols: 50+ Nifty50 stocks + 4 indices
├── Timeframes: 1D, 1h, 15m
├── Date range: Jan 1, 2020 - Oct 28, 2025 (5 years)
└── Files: ~162 Parquet files (~500 MB - 2 GB)
```

### ⚠️ Virtual Environment
```
ALWAYS activate before backtesting:
.\venv_backtesting\Scripts\Activate.ps1

Why? 
├── System Python 3.14: Fyers API works, vectorbt FAILS
├── venv Python 3.9: Both Fyers API and vectorbt work
└── Result: Use venv for backtesting, system for data download
```

---

## 🧪 Testing Checklist

### Before Running Backtests
- [ ] Virtual environment activated (`.\venv_backtesting\Scripts\Activate.ps1`)
- [ ] Python version is 3.9.13 (`python --version`)
- [ ] vectorbt imports successfully (`python -c "import vectorbt as vbt; print(vbt.__version__)"`)
- [ ] Data files exist (`BacktestDataLoader().get_available_data_summary()`)

### After Downloading Historical Data
- [ ] Total symbols: 54+ (50 stocks + 4 indices)
- [ ] Total files: ~162 (54 symbols × 3 timeframes)
- [ ] Timeframes: 1D, 1h, 15m
- [ ] Date range: 2020-01-01 to 2025-10-28 (5 years)
- [ ] No errors in download logs

### Before Production Deployment
- [ ] Rate limiter tested (0 violations)
- [ ] All demos passing (7/7)
- [ ] At least 3 strategies implemented
- [ ] Strategy ranking system working
- [ ] Performance reports generated
- [ ] Documentation up-to-date

---

## 🆘 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'vectorbt'"
**Solution:**
```powershell
# 1. Activate virtual environment
.\venv_backtesting\Scripts\Activate.ps1

# 2. Verify activation
python --version  # Should show 3.9.13

# 3. Reinstall if needed
pip install vectorbt
```

### Problem: "API still blocked after midnight"
**Solution:**
```powershell
# 1. Check current IST time
python -c "from datetime import datetime; import pytz; print(datetime.now(pytz.timezone('Asia/Kolkata')))"

# 2. Wait until exactly 00:00 IST
# 3. Test API
python -c "from scripts.auth.my_fyers_model import MyFyersModel; fyers = MyFyersModel(); print('✅' if fyers.fyers else '❌')"

# 4. Check rate limiter reset
python -c "from scripts.core.rate_limit_manager import get_rate_limiter; get_rate_limiter().print_statistics()"
```

### Problem: "Insufficient data for backtest"
**Solution:**
```powershell
# 1. Check available data
python -c "from scripts.backtesting.engine.data_loader import BacktestDataLoader; print(BacktestDataLoader().get_available_data_summary())"

# 2. If limited, download more:
#    - Run history_api.py after API recovery
#    - Configure symbols and date range
#    - Wait for rate-limited download

# 3. Verify download
python -c "from scripts.backtesting.engine.data_loader import BacktestDataLoader; print(BacktestDataLoader().get_available_data_summary())"
```

### Problem: "Demo fails with errors"
**Solution:**
```powershell
# 1. Check Python version
python --version  # Should be 3.9.13 in venv

# 2. Check dependencies
pip list | grep vectorbt  # Should show 0.28.1
pip list | grep numba     # Should show 0.56.4

# 3. Reinstall if needed
pip install --force-reinstall vectorbt

# 4. Re-run demo
python scripts\backtesting\demo_vectorbt_capabilities.py
```

---

## 📚 Documentation Index

### Core Documentation
- **PROGRESS_TRACKER.md** - Master progress tracker (2,000+ lines)
- **SESSION_SUMMARY_EVENING.md** - Today's comprehensive summary (2,000+ lines)
- **BACKTESTING_TEST_PLAN.md** - Testing strategy (1,000+ lines)

### Setup Guides
- **VENV_SETUP_COMPLETE.md** - Virtual environment setup (5,500+ lines)
- **VIRTUAL_ENV_SETUP.md** - Environment reference
- **BACKTESTING_FRAMEWORK_SELECTION.md** - Framework analysis

### Technical References
- **FYERS_RATE_LIMITS.md** - Rate limit complete reference
- **RATE_LIMITER_INTEGRATION.md** - Integration guide
- **RATE_LIMIT_IMPLEMENTATION_COMPLETE.md** - System overview

### Quick References
- **QUICK_REFERENCE.md** - This file
- **README.md** - Project overview (in root directory)
- **.github/copilot-instructions.md** - Development guidelines

---

## 🎯 Next Steps Timeline

### Tonight (After Midnight IST) - 2-3 hours
1. ✅ Verify API recovery
2. ✅ Download 5 years of historical data (50 stocks + 4 indices)
3. ✅ Validate downloaded data
4. ✅ Re-run demos with full data

### Tomorrow - 6-8 hours
1. ✅ Implement 5 production strategies
2. ✅ Build strategy ranking system
3. ✅ Generate performance reports
4. ✅ Validate results

### This Week - 10-15 hours
1. ✅ Strategy optimization
2. ✅ Risk management
3. ✅ Performance dashboard
4. ✅ Automation setup

---

**Created:** October 28, 2025, 22:35 IST  
**Status:** ✅ All systems ready for production data  
**Next Milestone:** API recovery at midnight IST
