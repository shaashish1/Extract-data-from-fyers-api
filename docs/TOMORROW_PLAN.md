# 📅 Tomorrow's Action Plan - October 29, 2025

**Goal:** Download complete historical data and identify best trading strategies  
**Status:** Ready to execute after API recovery (Midnight IST)  
**Estimated Time:** 6-8 hours total

---

## ⏰ Timeline & Milestones

### Phase 1: API Recovery & Validation (00:00 - 00:15 IST) - 15 minutes

#### Step 1.1: Verify API Access Restored (5 minutes)
```powershell
# Test API recovery
python -c "from scripts.auth.my_fyers_model import MyFyersModel; fyers = MyFyersModel(); print('✅ API ACTIVE' if fyers.fyers else '❌ STILL BLOCKED')"

# Check rate limiter reset
python -c "from scripts.core.rate_limit_manager import get_rate_limiter; limiter = get_rate_limiter(); limiter.print_statistics()"

# Expected output:
# Requests today: 0
# Violations today: 0/3
# Daily reset at: 2025-10-30 00:00:00 IST
```

#### Step 1.2: Test Rate-Limited APIs (10 minutes)
```powershell
# Test each API with rate limiter
python tests/test_rate_limit_recovery.py

# Expected: All 4 APIs working, 0 violations
```

---

### Phase 2: Historical Data Download (00:15 - 02:00 IST) - 90-105 minutes

#### Step 2.1: Download Index Data (5-10 minutes)
```powershell
# Create download script or use history_api.py
# Download these indices:
Indices to Download:
├── NSE:NIFTY50-INDEX (Nifty 50)
├── NSE:NIFTYBANK-INDEX (Bank Nifty)
├── NSE:FINNIFTY-INDEX (Fin Nifty)
└── NSE:INDIAVIX-INDEX (India VIX)

Configuration:
├── Start Date: 2020-01-01
├── End Date: 2025-10-28
├── Timeframes: 1D, 1h, 15m
└── Expected: 12 files (4 indices × 3 timeframes)
```

#### Step 2.2: Download Nifty 50 Stock Data (60-90 minutes)
```powershell
# Download all 50 Nifty50 stocks
# Rate limiter will auto-throttle to prevent blocks

Nifty 50 Stocks (50 symbols):
1. NSE:RELIANCE-EQ          18. NSE:SUNPHARMA-EQ        35. NSE:GRASIM-EQ
2. NSE:TCS-EQ               19. NSE:BAJAJ-AUTO-EQ       36. NSE:SHREECEM-EQ
3. NSE:HDFCBANK-EQ          20. NSE:BAJAJFINSV-EQ       37. NSE:ULTRACEMCO-EQ
4. NSE:INFY-EQ              21. NSE:BAJFINANCE-EQ       38. NSE:POWERGRID-EQ
5. NSE:ICICIBANK-EQ         22. NSE:HCLTECH-EQ          39. NSE:NTPC-EQ
6. NSE:HINDUNILVR-EQ        23. NSE:DRREDDY-EQ          40. NSE:ONGC-EQ
7. NSE:ITC-EQ               24. NSE:ASIANPAINT-EQ       41. NSE:JSWSTEEL-EQ
8. NSE:SBIN-EQ              25. NSE:KOTAKBANK-EQ        42. NSE:HINDALCO-EQ
9. NSE:BHARTIARTL-EQ        26. NSE:LT-EQ               43. NSE:ADANIENT-EQ
10. NSE:KOTAKBANK-EQ        27. NSE:AXISBANK-EQ         44. NSE:TATAMOTORS-EQ
11. NSE:LT-EQ               28. NSE:WIPRO-EQ            45. NSE:ADANIPORTS-EQ
12. NSE:AXISBANK-EQ         29. NSE:M&M-EQ              46. NSE:INDUSINDBK-EQ
13. NSE:WIPRO-EQ            30. NSE:TITAN-EQ            47. NSE:DIVISLAB-EQ
14. NSE:M&M-EQ              31. NSE:NESTLEIND-EQ        48. NSE:APOLLOHOSP-EQ
15. NSE:TITAN-EQ            32. NSE:TECHM-EQ            49. NSE:COALINDIA-EQ
16. NSE:MARUTI-EQ           33. NSE:BRITANNIA-EQ        50. NSE:CIPLA-EQ
17. NSE:TATASTEEL-EQ        34. NSE:EICHERMOT-EQ

Configuration:
├── Start Date: 2020-01-01 (5 years of data)
├── End Date: 2025-10-28
├── Timeframes: 1D, 1h, 15m
├── Expected Files: 150 files (50 stocks × 3 timeframes)
└── Estimated Time: 60-90 minutes (rate-limited)

Rate Limiter Protection:
├── Auto-throttles to 5 req/sec (safe limit)
├── Monitors violations (stops at 2/3)
├── Logs progress continuously
└── Saves incrementally (won't lose data if interrupted)
```

#### Step 2.3: Verify Downloaded Data (10 minutes)
```powershell
# Check data completeness
python -c "from scripts.backtesting.engine.data_loader import BacktestDataLoader; loader = BacktestDataLoader(); summary = loader.get_available_data_summary(); print(f'Total symbols: {len(summary[\"symbols\"])}\nTotal files: {summary[\"total_files\"]}\nTimeframes: {summary[\"timeframes\"]}')"

# Expected output:
# Total symbols: 54 (50 stocks + 4 indices)
# Total files: ~162 (54 symbols × 3 timeframes)
# Timeframes: ['1D', '1h', '15m']

# Verify data quality
python scripts/backtesting/engine/data_loader.py

# Check for gaps or missing data
# Review logs for any download errors
```

---

### Phase 3: Strategy Implementation (02:00 - 06:00 IST) - 4 hours

#### Step 3.1: Implement MA Crossover Strategy (30 minutes)
```python
# File: scripts/backtesting/strategies/built_in/ma_crossover.py

"""
Moving Average Crossover Strategy

Tests multiple MA period combinations:
- Fast/Slow: (20,50), (50,200), (10,30)
- Signals: Buy when fast MA crosses above slow MA, Sell when crosses below
- Initial capital: ₹100,000
- Fees: 0.1% per trade
"""

import vectorbt as vbt
import pandas as pd
from scripts.backtesting.engine.data_loader import BacktestDataLoader

class MACrossoverStrategy:
    def __init__(self):
        self.loader = BacktestDataLoader()
        self.results = {}
    
    def run(self, symbol='nifty50', timeframe='1D', fast_period=20, slow_period=50):
        # Load data
        df = self.loader.load_symbol(symbol, timeframe)
        
        # Calculate MAs
        fast_ma = vbt.MA.run(df['close'], fast_period)
        slow_ma = vbt.MA.run(df['close'], slow_period)
        
        # Generate signals
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)
        
        # Backtest
        portfolio = vbt.Portfolio.from_signals(
            df['close'], entries, exits,
            init_cash=100000,
            fees=0.001,
            freq='1D'
        )
        
        return portfolio
    
    def optimize(self, symbol='nifty50', timeframe='1D'):
        """Test multiple MA period combinations"""
        df = self.loader.load_symbol(symbol, timeframe)
        
        # Parameter grid
        fast_periods = [10, 20, 50]
        slow_periods = [30, 50, 100, 200]
        
        # Run grid search
        fast_ma = vbt.MA.run(df['close'], fast_periods, per_column=False)
        slow_ma = vbt.MA.run(df['close'], slow_periods, per_column=False)
        
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)
        
        portfolio = vbt.Portfolio.from_signals(
            df['close'], entries, exits,
            init_cash=100000,
            fees=0.001
        )
        
        # Find best parameters
        best_params = portfolio.sharpe_ratio().idxmax()
        
        return portfolio, best_params

if __name__ == "__main__":
    strategy = MACrossoverStrategy()
    
    # Test on Nifty50
    pf = strategy.run('nifty50', '1D', 20, 50)
    print(pf.stats())
    
    # Optimize parameters
    pf_opt, best = strategy.optimize('nifty50', '1D')
    print(f"Best parameters: {best}")
```

#### Step 3.2: Implement RSI Mean Reversion (30 minutes)
```python
# File: scripts/backtesting/strategies/built_in/rsi_mean_reversion.py

"""
RSI Mean Reversion Strategy

Configuration:
- RSI Period: 14 (standard)
- Oversold: RSI < 30 (buy signal)
- Overbought: RSI > 70 (sell signal)
- Alternative levels: 20/80, 25/75 for testing
"""

import vectorbt as vbt
from scripts.backtesting.engine.data_loader import BacktestDataLoader

class RSIMeanReversionStrategy:
    def __init__(self):
        self.loader = BacktestDataLoader()
    
    def run(self, symbol='nifty50', timeframe='1D', 
            rsi_period=14, oversold=30, overbought=70):
        df = self.loader.load_symbol(symbol, timeframe)
        
        # Calculate RSI
        rsi = vbt.RSI.run(df['close'], window=rsi_period)
        
        # Generate signals
        entries = rsi.rsi_below(oversold)
        exits = rsi.rsi_above(overbought)
        
        # Backtest
        portfolio = vbt.Portfolio.from_signals(
            df['close'], entries, exits,
            init_cash=100000,
            fees=0.001,
            freq='1D'
        )
        
        return portfolio
    
    def optimize(self, symbol='nifty50', timeframe='1D'):
        """Test multiple RSI threshold combinations"""
        df = self.loader.load_symbol(symbol, timeframe)
        
        # Test different threshold combinations
        oversold_levels = [20, 25, 30]
        overbought_levels = [70, 75, 80]
        
        results = []
        for oversold in oversold_levels:
            for overbought in overbought_levels:
                pf = self.run(symbol, timeframe, 14, oversold, overbought)
                results.append({
                    'oversold': oversold,
                    'overbought': overbought,
                    'sharpe': pf.sharpe_ratio(),
                    'return': pf.total_return(),
                    'trades': pf.trades.count()
                })
        
        return pd.DataFrame(results).sort_values('sharpe', ascending=False)
```

#### Step 3.3: Implement Bollinger Bands Breakout (30 minutes)
```python
# File: scripts/backtesting/strategies/built_in/bollinger_breakout.py

"""
Bollinger Bands Breakout Strategy

Configuration:
- Period: 20 (standard)
- Standard Deviations: 2 (can test 1.5, 2.5)
- Buy: Price crosses above upper band
- Sell: Price crosses below lower band
"""

import vectorbt as vbt
from scripts.backtesting.engine.data_loader import BacktestDataLoader

class BollingerBreakoutStrategy:
    def __init__(self):
        self.loader = BacktestDataLoader()
    
    def run(self, symbol='nifty50', timeframe='1D', 
            bb_period=20, bb_std=2):
        df = self.loader.load_symbol(symbol, timeframe)
        
        # Calculate Bollinger Bands
        bb = vbt.BBANDS.run(df['close'], window=bb_period, alpha=bb_std)
        
        # Generate signals (breakout strategy)
        entries = df['close'] > bb.upper  # Price breaks above upper band
        exits = df['close'] < bb.lower    # Price breaks below lower band
        
        # Backtest
        portfolio = vbt.Portfolio.from_signals(
            df['close'], entries, exits,
            init_cash=100000,
            fees=0.001,
            freq='1D'
        )
        
        return portfolio
```

#### Step 3.4: Implement MACD Strategy (30 minutes)
```python
# File: scripts/backtesting/strategies/built_in/macd_strategy.py

"""
MACD (Moving Average Convergence Divergence) Strategy

Configuration:
- Fast EMA: 12
- Slow EMA: 26
- Signal Line: 9
- Buy: MACD crosses above signal line
- Sell: MACD crosses below signal line
"""

import vectorbt as vbt
from scripts.backtesting.engine.data_loader import BacktestDataLoader

class MACDStrategy:
    def __init__(self):
        self.loader = BacktestDataLoader()
    
    def run(self, symbol='nifty50', timeframe='1D',
            fast=12, slow=26, signal=9):
        df = self.loader.load_symbol(symbol, timeframe)
        
        # Calculate MACD
        macd = vbt.MACD.run(df['close'], 
                            fast_window=fast,
                            slow_window=slow,
                            signal_window=signal)
        
        # Generate signals
        entries = macd.macd_crossed_above(macd.signal)
        exits = macd.macd_crossed_below(macd.signal)
        
        # Backtest
        portfolio = vbt.Portfolio.from_signals(
            df['close'], entries, exits,
            init_cash=100000,
            fees=0.001,
            freq='1D'
        )
        
        return portfolio
```

#### Step 3.5: Implement Momentum Strategy (30 minutes)
```python
# File: scripts/backtesting/strategies/built_in/momentum_strategy.py

"""
Momentum Strategy

Configuration:
- Lookback periods: 5, 10, 20 days
- Buy: Current price > price N days ago (positive momentum)
- Sell: Current price < price N days ago (negative momentum)
"""

import vectorbt as vbt
from scripts.backtesting.engine.data_loader import BacktestDataLoader

class MomentumStrategy:
    def __init__(self):
        self.loader = BacktestDataLoader()
    
    def run(self, symbol='nifty50', timeframe='1D', lookback=10):
        df = self.loader.load_symbol(symbol, timeframe)
        
        # Calculate momentum (price change over lookback period)
        momentum = df['close'].pct_change(lookback)
        
        # Generate signals
        entries = momentum > 0  # Positive momentum
        exits = momentum < 0    # Negative momentum
        
        # Backtest
        portfolio = vbt.Portfolio.from_signals(
            df['close'], entries, exits,
            init_cash=100000,
            fees=0.001,
            freq='1D'
        )
        
        return portfolio
```

#### Step 3.6: Create Strategy Runner (1 hour)
```python
# File: scripts/backtesting/strategies/strategy_runner.py

"""
Strategy Runner - Run all strategies on all symbols

This script:
1. Loads all available symbols
2. Runs all strategies on each symbol
3. Collects performance metrics
4. Saves results to CSV/Parquet
"""

import pandas as pd
from pathlib import Path
from scripts.backtesting.engine.data_loader import BacktestDataLoader
from scripts.backtesting.strategies.built_in.ma_crossover import MACrossoverStrategy
from scripts.backtesting.strategies.built_in.rsi_mean_reversion import RSIMeanReversionStrategy
from scripts.backtesting.strategies.built_in.bollinger_breakout import BollingerBreakoutStrategy
from scripts.backtesting.strategies.built_in.macd_strategy import MACDStrategy
from scripts.backtesting.strategies.built_in.momentum_strategy import MomentumStrategy

class StrategyRunner:
    def __init__(self):
        self.loader = BacktestDataLoader()
        self.strategies = {
            'MA_Crossover': MACrossoverStrategy(),
            'RSI_MeanReversion': RSIMeanReversionStrategy(),
            'Bollinger_Breakout': BollingerBreakoutStrategy(),
            'MACD': MACDStrategy(),
            'Momentum': MomentumStrategy()
        }
        self.results = []
    
    def run_all_strategies(self, symbols=None, timeframe='1D'):
        """Run all strategies on all symbols"""
        
        if symbols is None:
            # Get all available symbols
            summary = self.loader.get_available_data_summary()
            symbols = summary['symbols']
        
        print(f"Running {len(self.strategies)} strategies on {len(symbols)} symbols...")
        
        for symbol in symbols:
            print(f"\nProcessing {symbol}...")
            
            for strategy_name, strategy in self.strategies.items():
                try:
                    # Run strategy
                    pf = strategy.run(symbol, timeframe)
                    
                    # Collect metrics
                    self.results.append({
                        'symbol': symbol,
                        'strategy': strategy_name,
                        'timeframe': timeframe,
                        'total_return': pf.total_return(),
                        'sharpe_ratio': pf.sharpe_ratio(),
                        'max_drawdown': pf.max_drawdown(),
                        'win_rate': pf.trades.win_rate() if pf.trades.count() > 0 else 0,
                        'total_trades': pf.trades.count(),
                        'avg_trade_duration': pf.trades.duration.mean() if pf.trades.count() > 0 else 0,
                        'final_value': pf.final_value()
                    })
                    
                    print(f"  ✅ {strategy_name}: {pf.total_return():.2%} return")
                    
                except Exception as e:
                    print(f"  ❌ {strategy_name}: {e}")
        
        return pd.DataFrame(self.results)
    
    def save_results(self, output_path='scripts/backtesting/results/strategy_results.csv'):
        """Save results to CSV"""
        df = pd.DataFrame(self.results)
        df.to_csv(output_path, index=False)
        print(f"\n✅ Results saved to {output_path}")
        return df

if __name__ == "__main__":
    runner = StrategyRunner()
    
    # Run all strategies
    results_df = runner.run_all_strategies(timeframe='1D')
    
    # Save results
    runner.save_results()
    
    # Print summary
    print("\n" + "="*80)
    print("STRATEGY PERFORMANCE SUMMARY")
    print("="*80)
    print(results_df.groupby('strategy').agg({
        'total_return': 'mean',
        'sharpe_ratio': 'mean',
        'win_rate': 'mean',
        'total_trades': 'sum'
    }).round(4))
```

---

### Phase 4: Strategy Ranking System (06:00 - 08:00 IST) - 2 hours

#### Step 4.1: Build Ranking Engine (1 hour)
```python
# File: scripts/backtesting/strategies/strategy_ranker.py

"""
Strategy Ranking System

Ranks strategies based on multiple metrics:
- Sharpe Ratio (primary)
- Total Return
- Max Drawdown
- Win Rate
- Risk-adjusted returns
"""

import pandas as pd
import numpy as np
from pathlib import Path

class StrategyRanker:
    def __init__(self, results_path='scripts/backtesting/results/strategy_results.csv'):
        self.results = pd.read_csv(results_path)
        self.rankings = {}
    
    def calculate_composite_score(self):
        """Calculate composite score from multiple metrics"""
        
        # Normalize metrics (0-100 scale)
        df = self.results.copy()
        
        # Higher is better
        df['return_score'] = self._normalize(df['total_return'])
        df['sharpe_score'] = self._normalize(df['sharpe_ratio'])
        df['win_rate_score'] = self._normalize(df['win_rate'])
        
        # Lower is better (invert)
        df['drawdown_score'] = 100 - self._normalize(df['max_drawdown'].abs())
        
        # Composite score (weighted average)
        df['composite_score'] = (
            df['sharpe_score'] * 0.35 +      # 35% weight on Sharpe
            df['return_score'] * 0.30 +      # 30% weight on returns
            df['drawdown_score'] * 0.20 +    # 20% weight on drawdown
            df['win_rate_score'] * 0.15      # 15% weight on win rate
        )
        
        return df.sort_values('composite_score', ascending=False)
    
    def _normalize(self, series):
        """Normalize to 0-100 scale"""
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series))
        return ((series - min_val) / (max_val - min_val)) * 100
    
    def get_best_strategy_per_symbol(self):
        """Get best strategy for each symbol"""
        ranked = self.calculate_composite_score()
        
        best_per_symbol = ranked.groupby('symbol').apply(
            lambda x: x.nlargest(1, 'composite_score')
        ).reset_index(drop=True)
        
        return best_per_symbol[['symbol', 'strategy', 'composite_score', 
                                'total_return', 'sharpe_ratio', 'max_drawdown']]
    
    def generate_report(self):
        """Generate comprehensive ranking report"""
        ranked = self.calculate_composite_score()
        
        report = []
        report.append("="*80)
        report.append("STRATEGY RANKING REPORT")
        report.append("="*80)
        report.append(f"\nTotal Strategies Tested: {len(ranked)}")
        report.append(f"Symbols Analyzed: {ranked['symbol'].nunique()}")
        report.append(f"Timeframe: {ranked['timeframe'].iloc[0]}")
        
        report.append("\n" + "="*80)
        report.append("TOP 10 STRATEGY-SYMBOL COMBINATIONS")
        report.append("="*80)
        
        top10 = ranked.head(10)
        for idx, row in top10.iterrows():
            report.append(f"\n#{idx+1}. {row['strategy']} on {row['symbol']}")
            report.append(f"   Composite Score: {row['composite_score']:.2f}/100")
            report.append(f"   Return: {row['total_return']:.2%}")
            report.append(f"   Sharpe: {row['sharpe_ratio']:.2f}")
            report.append(f"   Max DD: {row['max_drawdown']:.2%}")
            report.append(f"   Win Rate: {row['win_rate']:.2%}")
        
        report.append("\n" + "="*80)
        report.append("STRATEGY PERFORMANCE AVERAGES")
        report.append("="*80)
        
        strategy_avg = ranked.groupby('strategy').agg({
            'total_return': 'mean',
            'sharpe_ratio': 'mean',
            'max_drawdown': 'mean',
            'win_rate': 'mean',
            'composite_score': 'mean'
        }).sort_values('composite_score', ascending=False)
        
        report.append(strategy_avg.to_string())
        
        return '\n'.join(report)
    
    def save_report(self, output_path='scripts/backtesting/results/ranking_report.txt'):
        """Save ranking report to file"""
        report = self.generate_report()
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"✅ Report saved to {output_path}")
        return report

if __name__ == "__main__":
    ranker = StrategyRanker()
    
    # Generate and print report
    report = ranker.generate_report()
    print(report)
    
    # Save report
    ranker.save_report()
    
    # Get best strategy per symbol
    best = ranker.get_best_strategy_per_symbol()
    best.to_csv('scripts/backtesting/results/best_strategy_per_symbol.csv', index=False)
    print("\n✅ Best strategies saved to best_strategy_per_symbol.csv")
```

#### Step 4.2: Create HTML Report Generator (1 hour)
```python
# File: scripts/backtesting/strategies/html_report_generator.py

"""
HTML Report Generator

Creates interactive HTML report with:
- Strategy rankings table (sortable)
- Performance charts
- Best strategy per symbol
- Summary statistics
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class HTMLReportGenerator:
    def __init__(self, results_path='scripts/backtesting/results/strategy_results.csv'):
        self.results = pd.read_csv(results_path)
    
    def generate_html_report(self, output_path='scripts/backtesting/results/strategy_report.html'):
        """Generate complete HTML report"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Strategy Performance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #3498db; color: white; cursor: pointer; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .positive {{ color: green; }}
                .negative {{ color: red; }}
            </style>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <h1>📊 Strategy Performance Report</h1>
            <p>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h2>Summary Statistics</h2>
            {self._generate_summary_table()}
            
            <h2>Strategy Rankings (All Combinations)</h2>
            {self._generate_rankings_table()}
            
            <h2>Performance Visualizations</h2>
            {self._generate_charts()}
            
            <h2>Best Strategy Per Symbol</h2>
            {self._generate_best_strategy_table()}
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        print(f"✅ HTML report saved to {output_path}")
        return html
    
    def _generate_summary_table(self):
        """Generate summary statistics table"""
        summary = self.results.groupby('strategy').agg({
            'total_return': ['mean', 'std'],
            'sharpe_ratio': 'mean',
            'win_rate': 'mean',
            'total_trades': 'sum'
        }).round(4)
        
        return summary.to_html()
    
    def _generate_rankings_table(self):
        """Generate sortable rankings table"""
        return self.results.to_html(index=False, classes='sortable')
    
    def _generate_charts(self):
        """Generate performance charts"""
        # Strategy comparison chart
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Average Return by Strategy', 
                          'Average Sharpe by Strategy',
                          'Win Rate by Strategy',
                          'Total Trades by Strategy')
        )
        
        strategy_avg = self.results.groupby('strategy').agg({
            'total_return': 'mean',
            'sharpe_ratio': 'mean',
            'win_rate': 'mean',
            'total_trades': 'sum'
        })
        
        # Add traces
        fig.add_trace(
            go.Bar(x=strategy_avg.index, y=strategy_avg['total_return']),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=strategy_avg.index, y=strategy_avg['sharpe_ratio']),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=strategy_avg.index, y=strategy_avg['win_rate']),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=strategy_avg.index, y=strategy_avg['total_trades']),
            row=2, col=2
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def _generate_best_strategy_table(self):
        """Generate best strategy per symbol table"""
        best = self.results.loc[self.results.groupby('symbol')['sharpe_ratio'].idxmax()]
        return best[['symbol', 'strategy', 'total_return', 'sharpe_ratio']].to_html(index=False)
```

---

### Phase 5: Analysis & Reporting (08:00 - 09:00 IST) - 1 hour

#### Step 5.1: Run Complete Analysis
```powershell
# Activate backtesting environment
.\venv_backtesting\Scripts\Activate.ps1

# Run all strategies on all symbols
python scripts/backtesting/strategies/strategy_runner.py

# Generate rankings
python scripts/backtesting/strategies/strategy_ranker.py

# Generate HTML report
python scripts/backtesting/strategies/html_report_generator.py

# Open report in browser
start scripts/backtesting/results/strategy_report.html
```

#### Step 5.2: Review and Document Results
- Review top 10 strategy-symbol combinations
- Identify best overall strategy
- Document findings in README or new doc
- Plan next steps for optimization

---

## 📋 Complete Execution Checklist

### Before Starting (Preparation)
- [ ] Virtual environment ready (`venv_backtesting`)
- [ ] All dependencies installed (vectorbt, numba, etc.)
- [ ] Rate limiter tested and working
- [ ] Enough disk space (~2-5 GB for data)

### Phase 1: API Recovery ✓
- [ ] API access verified (midnight IST)
- [ ] Rate limiter reset confirmed
- [ ] Test APIs working with 0 violations

### Phase 2: Data Download ✓
- [ ] 4 indices downloaded (3 timeframes each = 12 files)
- [ ] 50 Nifty50 stocks downloaded (3 timeframes each = 150 files)
- [ ] Total: 162 files (~500 MB - 2 GB)
- [ ] Data quality verified (no gaps, correct date ranges)
- [ ] No API violations occurred during download

### Phase 3: Strategy Implementation ✓
- [ ] MA Crossover strategy created and tested
- [ ] RSI Mean Reversion strategy created and tested
- [ ] Bollinger Bands strategy created and tested
- [ ] MACD strategy created and tested
- [ ] Momentum strategy created and tested
- [ ] Strategy runner script created
- [ ] All strategies run on all symbols

### Phase 4: Ranking System ✓
- [ ] Ranking engine implemented
- [ ] Composite scoring calculated
- [ ] Best strategy per symbol identified
- [ ] HTML report generated
- [ ] Reports saved to results/

### Phase 5: Analysis Complete ✓
- [ ] Results reviewed and validated
- [ ] Best strategies identified
- [ ] Findings documented
- [ ] Next steps planned

---

## 🎯 Expected Outcomes

### Data Download Results
```
Total Symbols: 54 (50 stocks + 4 indices)
Total Files: ~162 Parquet files
Total Size: 500 MB - 2 GB (compressed)
Date Range: 2020-01-01 to 2025-10-28 (5 years)
Timeframes: 1D, 1h, 15m
```

### Strategy Testing Results
```
Total Strategy-Symbol Combinations: 270
├── 5 strategies × 54 symbols = 270 backtests
├── Timeframe: 1D (can extend to 1h, 15m later)
└── Metrics per backtest: 8-10 KPIs

Expected Top Performers:
├── Best Return Strategy: TBD (likely MA Crossover or Momentum)
├── Best Sharpe Strategy: TBD (likely RSI or MACD)
├── Most Consistent: TBD (based on win rate and drawdown)
└── Best All-Around: TBD (composite score)
```

### Deliverables
1. ✅ Complete historical dataset (162 files)
2. ✅ 5 production-ready strategies
3. ✅ Strategy runner framework
4. ✅ Ranking system with composite scoring
5. ✅ HTML report with interactive visualizations
6. ✅ Best strategy recommendations per symbol
7. ✅ CSV exports for further analysis

---

## ⚠️ Risk Mitigation

### API Rate Limits
**Risk:** Exceed limits during data download  
**Mitigation:** Rate limiter auto-throttles to 5 req/sec (50% safety margin)  
**Monitoring:** Check violations count stays 0/3

### Data Quality
**Risk:** Missing data or gaps in historical data  
**Mitigation:** Verify each download, check for gaps, re-download if needed  
**Validation:** Run data_loader summary after download

### Strategy Failures
**Risk:** Strategy fails on certain symbols (insufficient data, errors)  
**Mitigation:** Try-except blocks in runner, log errors, continue processing  
**Handling:** Review error logs, exclude problematic symbols if needed

### Time Overruns
**Risk:** Download or testing takes longer than expected  
**Mitigation:** Incremental saving, can pause and resume  
**Plan B:** Focus on 1D timeframe first, add 1h/15m later

---

## 🚀 Quick Start Commands

### Tomorrow Morning (After Midnight IST)
```powershell
# 1. Verify API recovered
python -c "from scripts.auth.my_fyers_model import MyFyersModel; print('✅' if MyFyersModel().fyers else '❌')"

# 2. Check rate limiter
python -c "from scripts.core.rate_limit_manager import get_rate_limiter; get_rate_limiter().print_statistics()"

# 3. Start data download (create this script based on history_api.py)
python scripts/download_complete_dataset.py

# 4. Activate backtesting environment
.\venv_backtesting\Scripts\Activate.ps1

# 5. Run all strategies
python scripts/backtesting/strategies/strategy_runner.py

# 6. Generate rankings
python scripts/backtesting/strategies/strategy_ranker.py

# 7. View HTML report
start scripts/backtesting/results/strategy_report.html
```

---

## 📚 Additional Resources

### Documentation References
- `docs/QUICK_REFERENCE.md` - Quick command reference
- `docs/BACKTESTING_TEST_PLAN.md` - Testing strategy
- `docs/PROGRESS_TRACKER.md` - Overall progress
- `docs/RATE_LIMITER_INTEGRATION.md` - Rate limiter guide

### Code References
- `scripts/backtesting/engine/data_loader.py` - Data loading
- `scripts/market_data/history_api.py` - Historical data download
- `scripts/core/rate_limit_manager.py` - Rate limiting

---

**Created:** October 28, 2025, 23:00 IST  
**Status:** Ready for execution  
**Next Update:** After data download complete  

Good luck tomorrow! 🚀
