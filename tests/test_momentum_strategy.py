"""
Test Momentum Strategy on Sample Stock
=======================================

Tests the Momentum strategy implementation and displays results.
Final strategy test - completes Phase 1!
"""

import sys
import pandas as pd
from pathlib import Path

# Add scripts to path
sys.path.append(str(Path(__file__).parent / 'scripts' / 'backtesting' / 'strategies' / 'built_in'))

from momentum_strategy import MomentumStrategy


def main():
    print("=" * 80)
    print("Momentum Strategy Test - FINAL STRATEGY!")
    print("=" * 80)
    
    # Load RELIANCE data
    data_path = Path('data/parquet/stocks/RELIANCE_1D.parquet')
    
    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        print("Please run download_yahoo_history.py first")
        return
    
    print(f"\n📊 Loading data from: {data_path}")
    df = pd.read_parquet(data_path)
    
    print(f"✅ Loaded {len(df)} bars")
    print(f"📅 Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"💰 Price range: ₹{df['close'].min():.2f} - ₹{df['close'].max():.2f}")
    
    # Create strategy
    print("\n" + "=" * 80)
    print("Creating Momentum Strategy")
    print("=" * 80)
    
    strategy = MomentumStrategy(
        lookback_period=10,
        roc_threshold=0.0
    )
    
    info = strategy.get_strategy_info()
    print(f"\n📈 Strategy: {info['name']}")
    print(f"📝 Description: {info['description']}")
    print(f"🎯 Type: {info['characteristics']['type']}")
    print(f"✨ Best for: {info['characteristics']['best_for']}")
    
    # Run backtest
    print("\n" + "=" * 80)
    print("Running Backtest")
    print("=" * 80)
    
    results = strategy.backtest(
        df,
        initial_capital=100000,
        commission=0.001,
        slippage=0.0005
    )
    
    # Display results
    perf = results['performance']
    
    print("\n📊 Performance Metrics:")
    print(f"  💵 Total Return: {perf['total_return']*100:.2f}%")
    print(f"  📈 Sharpe Ratio: {perf['sharpe_ratio']:.2f}")
    print(f"  📉 Max Drawdown: {perf['max_drawdown']*100:.2f}%")
    print(f"  🎯 Win Rate: {perf['win_rate']*100:.1f}%")
    print(f"  🔄 Total Trades: {perf['total_trades']}")
    print(f"  💰 Profit Factor: {perf['profit_factor']:.2f}")
    print(f"  📊 Avg Trade Return: {perf['avg_trade_return']*100:.2f}%")
    print(f"  💵 Final Value: ₹{perf['final_value']:,.2f}")
    
    # Current signal
    print("\n" + "=" * 80)
    print("Current Signal")
    print("=" * 80)
    
    signal = strategy.get_current_signal(df)
    print(f"\n🎯 Signal: {signal}")
    
    # Show current momentum values
    df_signals = results['signals_df']
    last_row = df_signals.iloc[-1]
    
    print(f"\n📊 Current Momentum Values:")
    print(f"  ROC (10-day): {last_row['roc']:.2%}")
    print(f"  Current Price: ₹{last_row['close']:.2f}")
    print(f"  Price 10 days ago: ₹{df_signals.iloc[-11]['close']:.2f}")
    
    # Recent signals
    print("\n" + "=" * 80)
    print("Recent Signals (Last 5 trades)")
    print("=" * 80)
    
    recent_trades = results['trades'][-5:] if len(results['trades']) > 5 else results['trades']
    
    for i, trade in enumerate(recent_trades, 1):
        print(f"\nTrade {i}:")
        print(f"  Entry: ₹{trade['entry_price']:.2f}")
        print(f"  Exit: ₹{trade['exit_price']:.2f}")
        print(f"  Return: {trade['return']*100:.2f}%")
        print(f"  P&L: ₹{trade['profit']:,.2f}")
    
    print("\n" + "=" * 80)
    print("✅ Test Complete!")
    print("=" * 80)
    
    # FINAL STRATEGY COMPARISON
    print("\n" + "=" * 80)
    print("🏆 PHASE 1 COMPLETE - ALL 5 STRATEGIES TESTED!")
    print("=" * 80)
    
    print("\n📊 Complete Strategy Rankings (RELIANCE):")
    
    strategies = [
        ("Bollinger Bands", 40.30, 0.40, 73.3, 2.83),
        ("MACD", 35.35, 0.38, 33.9, 1.30),
        ("MA Crossover", 30.42, 0.36, 36.8, 1.55),
        ("Momentum", perf['total_return']*100, perf['sharpe_ratio'], perf['win_rate']*100, perf['profit_factor']),
        ("RSI", 6.97, 0.16, 61.1, 1.28)
    ]
    
    # Sort by return
    strategies.sort(key=lambda x: x[1], reverse=True)
    
    print("\n🥇 By Total Return:")
    for rank, (name, ret, sharpe, win, pf) in enumerate(strategies, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"  {medal} #{rank}. {name:20s} {ret:6.2f}% | Sharpe: {sharpe:.2f} | Win: {win:4.1f}% | PF: {pf:.2f}")
    
    # Sort by Sharpe
    strategies.sort(key=lambda x: x[2], reverse=True)
    
    print("\n📈 By Sharpe Ratio (Risk-Adjusted):")
    for rank, (name, ret, sharpe, win, pf) in enumerate(strategies, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"  {medal} #{rank}. {name:20s} Sharpe: {sharpe:.2f} | Return: {ret:6.2f}%")
    
    # Sort by Win Rate
    strategies.sort(key=lambda x: x[3], reverse=True)
    
    print("\n🎯 By Win Rate (Consistency):")
    for rank, (name, ret, sharpe, win, pf) in enumerate(strategies, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"  {medal} #{rank}. {name:20s} Win: {win:4.1f}% | Return: {ret:6.2f}%")
    
    print("\n" + "=" * 80)
    print("🎉 PHASE 1 COMPLETE! All 5 Classic Strategies Implemented & Tested!")
    print("=" * 80)
    
    print("\n✅ Next Steps:")
    print("  1. Build strategy_runner.py (test all 5 on 55 stocks)")
    print("  2. Build strategy_ranker.py (find best strategy per stock)")
    print("  3. Generate analysis report (comprehensive results)")
    print("  4. Move to Phase 2 (Quantitative Alphas)")


if __name__ == "__main__":
    main()
