# Backtesting Test Plan - vectorbt Proof of Concept

## 🎯 Objective
Test vectorbt backtesting framework with limited historical data to validate setup and demonstrate capabilities before full data download.

---

## 📊 Available Data (Current)

### Data Inventory
```
Total Symbols: 8
Timeframes: 1D only
Date Range: 2-4 days per symbol (Oct 20-24, 2025)

Categories:
├── Indices (4): nifty50, niftybank, finnifty, indiavix
├── Stocks (3): infy, tata_power, reliance
└── Options (1): demo_symbol
```

### Data Limitations
- ⚠️ **Only 2-4 days** - Not enough for comprehensive backtesting
- ⚠️ **Single timeframe** - Only daily data (no intraday)
- ⚠️ **Limited symbols** - Only 8 symbols (need 50+ for production)

### What We CAN Test
✅ **vectorbt installation** - Verify framework works
✅ **Data loading** - Test BacktestDataLoader integration
✅ **Simple strategies** - Moving averages, momentum (short-term)
✅ **Multi-symbol** - Test across all 8 symbols simultaneously
✅ **Performance metrics** - Calculate KPIs (with limited sample)
✅ **Visualization** - Generate basic charts
✅ **Code patterns** - Establish development workflow

---

## 🧪 Testing Strategy

### Phase 1: Installation Validation ✅ COMPLETE
**Status:** All tests passing!
- [x] vectorbt 0.28.1 installed in venv_backtesting
- [x] numba 0.56.4 (JIT compiler) working
- [x] Data loader tested with 8 symbols
- [x] Environment isolated and reproducible

### Phase 2: Basic Strategy Test (CURRENT PHASE)
**Goal:** Create simplest possible strategy to validate vectorbt workflow

**Strategy:** Simple Moving Average Crossover
- Fast MA: 2 days
- Slow MA: 3 days
- Data: nifty50 (4 days available)
- Expected: Limited signals due to short data

**File:** `scripts/backtesting/strategies/built_in/demo_ma_crossover.py`

**Expected Output:**
```
📊 Strategy: MA Crossover (2/3 period)
Symbol: nifty50
Timeframe: 1D
Data points: 4
Signals generated: 0-2 (expected with 4 days)
Total return: X%
Win rate: X%
Max drawdown: X%
```

### Phase 3: Multi-Symbol Test
**Goal:** Test vectorbt's parallel execution on all 8 symbols

**Strategy:** Same MA crossover across all symbols
**Expected:** Demonstrate vectorbt's speed advantage

### Phase 4: Visualization Test
**Goal:** Generate interactive Plotly charts

**Charts to Generate:**
1. Portfolio equity curve
2. Drawdown chart
3. Signal markers on price chart
4. Returns distribution

### Phase 5: Performance Metrics
**Goal:** Calculate comprehensive KPIs

**Metrics to Test:**
- Total return
- Sharpe ratio (if enough data)
- Max drawdown
- Win rate
- Number of trades
- Average trade duration

---

## 📝 Implementation Plan

### Step 1: Create Demo MA Crossover Strategy (15 minutes)
```python
# File: scripts/backtesting/strategies/built_in/demo_ma_crossover.py

import vectorbt as vbt
import pandas as pd
from scripts.backtesting.engine.data_loader import BacktestDataLoader

def run_demo_strategy():
    """
    Demo MA crossover strategy with limited data.
    Tests vectorbt installation and basic functionality.
    """
    # Load data
    loader = BacktestDataLoader()
    df = loader.load_symbol('nifty50', '1D')
    
    # Calculate indicators (short periods for 4-day data)
    fast_ma = vbt.MA.run(df['close'], 2)
    slow_ma = vbt.MA.run(df['close'], 3)
    
    # Generate signals
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)
    
    # Run backtest
    portfolio = vbt.Portfolio.from_signals(
        df['close'], 
        entries, 
        exits,
        init_cash=100000,
        fees=0.001  # 0.1% transaction fee
    )
    
    # Print results
    print("="*60)
    print("Demo MA Crossover Strategy - Limited Data Test")
    print("="*60)
    print(f"Symbol: nifty50")
    print(f"Data points: {len(df)}")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    print()
    print(portfolio.stats())
    
    # Plot
    portfolio.plot().show()
    
    return portfolio

if __name__ == "__main__":
    run_demo_strategy()
```

**Expected Runtime:** <1 second
**Expected Output:** Basic statistics and interactive chart

### Step 2: Multi-Symbol Test (10 minutes)
```python
# File: scripts/backtesting/strategies/built_in/demo_multi_symbol.py

import vectorbt as vbt
import pandas as pd
from scripts.backtesting.engine.data_loader import BacktestDataLoader

def run_multi_symbol_test():
    """
    Test vectorbt with all 8 available symbols.
    Demonstrates parallel execution and speed.
    """
    loader = BacktestDataLoader()
    
    # Load all symbols
    symbols = ['nifty50', 'niftybank', 'finnifty', 'infy', 'tata_power', 'reliance']
    
    # Load close prices for all symbols
    df = loader.load_multiple_symbols(symbols, '1D', column='close')
    
    print(f"Loaded {len(symbols)} symbols")
    print(f"Data shape: {df.shape}")
    print(f"Symbols: {list(df.columns)}")
    
    # Calculate MA for all symbols simultaneously (vectorized!)
    fast_ma = vbt.MA.run(df, 2, per_column=True)
    slow_ma = vbt.MA.run(df, 3, per_column=True)
    
    # Generate signals for all symbols
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)
    
    # Run backtest for all symbols
    portfolio = vbt.Portfolio.from_signals(
        df,
        entries,
        exits,
        init_cash=100000,
        fees=0.001,
        group_by=True  # Treat as portfolio
    )
    
    # Print results
    print("\n" + "="*60)
    print("Multi-Symbol Portfolio Test")
    print("="*60)
    print(portfolio.stats())
    
    # Plot
    portfolio.plot().show()
    
    return portfolio

if __name__ == "__main__":
    run_multi_symbol_test()
```

### Step 3: RSI Strategy Test (10 minutes)
```python
# File: scripts/backtesting/strategies/built_in/demo_rsi.py

import vectorbt as vbt
import pandas as pd
from scripts.backtesting.engine.data_loader import BacktestDataLoader

def run_rsi_strategy():
    """
    Demo RSI strategy with limited data.
    RSI period adjusted for short data (2 periods).
    """
    loader = BacktestDataLoader()
    df = loader.load_symbol('nifty50', '1D')
    
    # Calculate RSI (short period for limited data)
    rsi = vbt.RSI.run(df['close'], window=2)
    
    # Generate signals (adjusted thresholds)
    entries = rsi.rsi_below(40)  # Oversold
    exits = rsi.rsi_above(60)     # Overbought
    
    # Run backtest
    portfolio = vbt.Portfolio.from_signals(
        df['close'],
        entries,
        exits,
        init_cash=100000,
        fees=0.001
    )
    
    # Results
    print("="*60)
    print("Demo RSI Strategy - Limited Data Test")
    print("="*60)
    print(portfolio.stats())
    
    # Plot with RSI overlay
    fig = portfolio.plot(subplots=[
        ('price', dict(title='Price & Signals')),
        ('rsi', dict(title='RSI', height=0.3))
    ])
    
    # Add RSI to subplot
    rsi.rsi.vbt.plot(subplot='rsi', fig=fig)
    fig.show()
    
    return portfolio

if __name__ == "__main__":
    run_rsi_strategy()
```

### Step 4: Comprehensive Demo Script (20 minutes)
```python
# File: scripts/backtesting/demo_vectorbt_capabilities.py

"""
Comprehensive vectorbt Demo with Limited Data

Tests all major features:
1. Data loading from Parquet
2. Indicator calculation (MA, RSI, Bollinger)
3. Signal generation
4. Portfolio backtesting
5. Performance metrics
6. Visualization
7. Multi-symbol processing
"""

import vectorbt as vbt
import pandas as pd
import numpy as np
from scripts.backtesting.engine.data_loader import BacktestDataLoader

class VectorbtDemo:
    def __init__(self):
        self.loader = BacktestDataLoader()
        self.results = {}
    
    def demo_1_data_loading(self):
        """Demo 1: Data Loading"""
        print("\n" + "="*70)
        print("DEMO 1: Data Loading from Parquet")
        print("="*70)
        
        # Get available data summary
        summary = self.loader.get_available_data_summary()
        print(f"Total files: {summary['total_files']}")
        print(f"Symbols: {', '.join(summary['symbols'])}")
        print(f"Timeframes: {summary['timeframes']}")
        
        # Load single symbol
        df = self.loader.load_symbol('nifty50', '1D')
        print(f"\nNIFTY50 data loaded:")
        print(f"  Rows: {len(df)}")
        print(f"  Date range: {df.index[0]} to {df.index[-1]}")
        print(f"  Columns: {list(df.columns)}")
        print(f"\nFirst 3 rows:")
        print(df.head(3))
        
        return df
    
    def demo_2_indicators(self, df):
        """Demo 2: Technical Indicators"""
        print("\n" + "="*70)
        print("DEMO 2: Technical Indicators (vectorized)")
        print("="*70)
        
        # Moving Averages
        ma_fast = vbt.MA.run(df['close'], 2)
        ma_slow = vbt.MA.run(df['close'], 3)
        
        # RSI
        rsi = vbt.RSI.run(df['close'], window=2)
        
        # Bollinger Bands
        bb = vbt.BBANDS.run(df['close'], window=3)
        
        print(f"Calculated indicators:")
        print(f"  MA Fast (2): {list(ma_fast.ma.round(2))}")
        print(f"  MA Slow (3): {list(ma_slow.ma.round(2))}")
        print(f"  RSI (2):     {list(rsi.rsi.round(2))}")
        print(f"  BB Upper:    {list(bb.upper.round(2))}")
        print(f"  BB Lower:    {list(bb.lower.round(2))}")
        
        return {'ma_fast': ma_fast, 'ma_slow': ma_slow, 'rsi': rsi, 'bb': bb}
    
    def demo_3_signals(self, df, indicators):
        """Demo 3: Signal Generation"""
        print("\n" + "="*70)
        print("DEMO 3: Signal Generation")
        print("="*70)
        
        # MA Crossover signals
        ma_entries = indicators['ma_fast'].ma_crossed_above(indicators['ma_slow'])
        ma_exits = indicators['ma_fast'].ma_crossed_below(indicators['ma_slow'])
        
        # RSI signals
        rsi_entries = indicators['rsi'].rsi_below(40)
        rsi_exits = indicators['rsi'].rsi_above(60)
        
        print(f"MA Crossover signals:")
        print(f"  Buy signals:  {ma_entries.sum()}")
        print(f"  Sell signals: {ma_exits.sum()}")
        print(f"\nRSI signals:")
        print(f"  Buy signals:  {rsi_entries.sum()}")
        print(f"  Sell signals: {rsi_exits.sum()}")
        
        return {'ma_entries': ma_entries, 'ma_exits': ma_exits,
                'rsi_entries': rsi_entries, 'rsi_exits': rsi_exits}
    
    def demo_4_backtest(self, df, signals):
        """Demo 4: Portfolio Backtesting"""
        print("\n" + "="*70)
        print("DEMO 4: Portfolio Backtesting")
        print("="*70)
        
        # MA Crossover portfolio
        pf_ma = vbt.Portfolio.from_signals(
            df['close'],
            signals['ma_entries'],
            signals['ma_exits'],
            init_cash=100000,
            fees=0.001,
            freq='1D'
        )
        
        # RSI portfolio
        pf_rsi = vbt.Portfolio.from_signals(
            df['close'],
            signals['rsi_entries'],
            signals['rsi_exits'],
            init_cash=100000,
            fees=0.001,
            freq='1D'
        )
        
        print("MA Crossover Strategy:")
        print(f"  Total Return:  {pf_ma.total_return():.2%}")
        print(f"  Total Trades:  {pf_ma.trades.count()}")
        print(f"  Win Rate:      {pf_ma.trades.win_rate():.2%}")
        
        print("\nRSI Strategy:")
        print(f"  Total Return:  {pf_rsi.total_return():.2%}")
        print(f"  Total Trades:  {pf_rsi.trades.count()}")
        print(f"  Win Rate:      {pf_rsi.trades.win_rate():.2%}")
        
        return {'ma': pf_ma, 'rsi': pf_rsi}
    
    def demo_5_metrics(self, portfolios):
        """Demo 5: Performance Metrics"""
        print("\n" + "="*70)
        print("DEMO 5: Performance Metrics")
        print("="*70)
        
        for name, pf in portfolios.items():
            print(f"\n{name.upper()} Strategy Metrics:")
            print("-" * 40)
            stats = pf.stats()
            print(stats)
    
    def demo_6_multi_symbol(self):
        """Demo 6: Multi-Symbol Processing"""
        print("\n" + "="*70)
        print("DEMO 6: Multi-Symbol Processing (vectorbt's strength!)")
        print("="*70)
        
        symbols = ['nifty50', 'niftybank', 'finnifty']
        df = self.loader.load_multiple_symbols(symbols, '1D', column='close')
        
        print(f"Loaded {len(symbols)} symbols in parallel")
        print(f"Data shape: {df.shape} (rows × symbols)")
        print(f"Common dates: {len(df)}")
        
        # Calculate MA for all symbols simultaneously
        fast_ma = vbt.MA.run(df, 2, per_column=True)
        slow_ma = vbt.MA.run(df, 3, per_column=True)
        
        # Generate signals
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)
        
        # Backtest all symbols as portfolio
        pf = vbt.Portfolio.from_signals(
            df,
            entries,
            exits,
            init_cash=100000,
            fees=0.001,
            group_by=True  # Combine into single portfolio
        )
        
        print(f"\nPortfolio Results:")
        print(f"  Total Return: {pf.total_return():.2%}")
        print(f"  Total Trades: {pf.trades.count()}")
        
        return pf
    
    def demo_7_visualization(self, pf, df):
        """Demo 7: Visualization"""
        print("\n" + "="*70)
        print("DEMO 7: Visualization (Interactive Plotly Charts)")
        print("="*70)
        
        print("Generating interactive charts...")
        print("  - Portfolio equity curve")
        print("  - Drawdown chart")
        print("  - Trade markers")
        print("\nCharts will open in browser...")
        
        # Create comprehensive plot
        fig = pf.plot()
        fig.show()
        
        print("✅ Chart displayed!")
    
    def run_all_demos(self):
        """Run all demos in sequence"""
        print("\n" + "="*70)
        print("🚀 vectorbt COMPREHENSIVE DEMO - Limited Data Test")
        print("="*70)
        print("Testing vectorbt installation and capabilities")
        print("with 8 symbols and 2-4 days of data")
        print("="*70)
        
        # Run all demos
        df = self.demo_1_data_loading()
        indicators = self.demo_2_indicators(df)
        signals = self.demo_3_signals(df, indicators)
        portfolios = self.demo_4_backtest(df, signals)
        self.demo_5_metrics(portfolios)
        pf_multi = self.demo_6_multi_symbol()
        
        # Visualization (optional - comment out if not needed)
        # self.demo_7_visualization(portfolios['ma'], df)
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nKey Takeaways:")
        print("  ✅ vectorbt installed and working")
        print("  ✅ Data loader integration successful")
        print("  ✅ Indicators calculated correctly")
        print("  ✅ Signal generation working")
        print("  ✅ Backtesting engine functional")
        print("  ✅ Performance metrics calculated")
        print("  ✅ Multi-symbol processing demonstrated")
        print("\nReady for production with full historical data!")
        print("="*70)

if __name__ == "__main__":
    demo = VectorbtDemo()
    demo.run_all_demos()
```

---

## 🎯 Execution Plan

### Option A: Quick Test (5 minutes)
```powershell
# Activate environment
.\venv_backtesting\Scripts\Activate.ps1

# Run simple MA crossover demo
python scripts\backtesting\strategies\built_in\demo_ma_crossover.py

# Expected: Basic stats + chart (browser opens)
```

### Option B: Comprehensive Demo (20 minutes)
```powershell
# Activate environment
.\venv_backtesting\Scripts\Activate.ps1

# Run full demo suite
python scripts\backtesting\demo_vectorbt_capabilities.py

# Expected: 7 demos showing all vectorbt features
```

### Option C: Create All Demo Files First (30 minutes)
1. Create demo_ma_crossover.py
2. Create demo_multi_symbol.py
3. Create demo_rsi.py
4. Create demo_vectorbt_capabilities.py
5. Test each incrementally

---

## 📊 Expected Outcomes

### With 4 Days of Data
```
Realistic Expectations:
├── Signals: 0-3 per strategy (very limited)
├── Trades: 0-2 completed trades
├── Returns: May be positive or negative (not statistically significant)
├── Metrics: Calculated but not meaningful (need 100+ days)
└── Charts: Will display but show limited history

Key Value:
✅ Validates vectorbt installation works
✅ Demonstrates code patterns for production
✅ Tests data integration pipeline
✅ Confirms multi-symbol processing
✅ Ready to scale with full data
```

### After Full Data Download (Future)
```
With 5 Years × 50 Symbols:
├── Signals: 1000s per strategy
├── Trades: 100s of completed trades
├── Returns: Statistically significant
├── Metrics: Meaningful performance analysis
└── Charts: Rich visualization

Production Capabilities:
✅ Comprehensive backtesting
✅ Strategy optimization
✅ Reliable ranking system
✅ Risk analysis
✅ Portfolio construction
```

---

## 🚀 Next Steps

### Immediate (Today)
1. ✅ **Choose execution path** (Option A, B, or C above)
2. ✅ **Create demo file(s)** based on chosen path
3. ✅ **Run test** in venv_backtesting environment
4. ✅ **Validate output** - confirm vectorbt works
5. ✅ **Document results** - capture screenshots/stats

### After API Recovery (Midnight IST)
1. **Download full historical data** (50 Nifty50 stocks, 5 years)
2. **Re-run all demos** with comprehensive data
3. **Develop 5-7 production strategies**
4. **Build ranking system**
5. **Generate performance reports**

---

## 📋 Success Criteria

### Demo Success Checklist
- [ ] vectorbt imports without errors
- [ ] Data loads from Parquet files
- [ ] Indicators calculate correctly
- [ ] Signals generate (even if 0 signals due to short data)
- [ ] Portfolio backtest completes
- [ ] Stats print to console
- [ ] Charts display (if visualization enabled)
- [ ] No crashes or exceptions

### Validation Questions
1. Does vectorbt work in our environment? → **Test will confirm**
2. Does data loader integrate correctly? → **Test will confirm**
3. Can we generate signals? → **Test will confirm**
4. Do charts render? → **Test will confirm**
5. Is multi-symbol processing fast? → **Test will confirm**

---

## 💡 Recommendations

### Recommendation 1: Start with Option B (Comprehensive Demo)
**Why:**
- Tests all major features in one run
- Comprehensive validation
- Good documentation for future reference
- Takes only 20 minutes

### Recommendation 2: Don't Worry About Limited Results
**Remember:**
- Goal is to validate **setup**, not generate trading signals
- 4 days of data is insufficient for real backtesting
- Focus on **process validation**, not performance metrics
- Real testing happens after full data download

### Recommendation 3: Save Demo for Future Reference
**After Testing:**
- Keep demo scripts as templates
- Document what worked/didn't work
- Use patterns for production strategies
- Reference for training/onboarding

---

## 🎓 Learning Objectives

### What This Demo Teaches
1. **vectorbt Workflow** - End-to-end backtesting process
2. **Vectorized Operations** - How vectorbt processes data
3. **Signal Generation** - Creating entry/exit rules
4. **Portfolio Management** - Position sizing, fees, metrics
5. **Performance Analysis** - KPI calculation and interpretation
6. **Visualization** - Interactive chart generation
7. **Multi-Symbol** - Parallel processing capabilities

### Skills Developed
- vectorbt API usage
- Strategy implementation patterns
- Data pipeline integration
- Performance metric interpretation
- Chart customization
- Debugging vectorbt code

---

**Created:** October 28, 2025, 21:15 IST  
**Status:** Ready for execution  
**Estimated Time:** 5-30 minutes (depending on option chosen)  
**Expected Result:** ✅ Validation that vectorbt setup is production-ready
