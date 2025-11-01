"""
Test Bollinger Bands Strategy on Sample Stock
==============================================

Tests the Bollinger Bands strategy implementation and displays results.
"""

import sys
import pandas as pd
from pathlib import Path

# Add scripts to path
sys.path.append(str(Path(__file__).parent / 'scripts' / 'backtesting' / 'strategies' / 'built_in'))

from bollinger_bands import BollingerBandsStrategy


def main():
    print("=" * 80)
    print("Bollinger Bands Strategy Test")
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
    print("Creating Bollinger Bands Strategy")
    print("=" * 80)
    
    strategy = BollingerBandsStrategy(
        period=20,
        std_dev=2.0,
        touch_threshold=0.001
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
    
    # Show current bands
    df_signals = results['signals_df']
    last_row = df_signals.iloc[-1]
    
    print(f"\n📊 Current Bollinger Bands:")
    print(f"  Upper Band: ₹{last_row['bb_upper']:.2f}")
    print(f"  Middle Band: ₹{last_row['bb_middle']:.2f}")
    print(f"  Lower Band: ₹{last_row['bb_lower']:.2f}")
    print(f"  Current Price: ₹{last_row['close']:.2f}")
    print(f"  Bandwidth: {last_row['bb_bandwidth']:.2%}")
    print(f"  %B Position: {last_row['bb_percent']:.1%}")
    
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
    
    # Strategy comparison summary
    print("\n" + "=" * 80)
    print("Strategy Comparison (RELIANCE)")
    print("=" * 80)
    
    print("\n📊 Three Strategies Tested:")
    print(f"  1. MA Crossover:        30.42% return, 0.36 Sharpe, 36.8% win rate")
    print(f"  2. RSI Mean Reversion:   6.97% return, 0.16 Sharpe, 61.1% win rate")
    print(f"  3. Bollinger Bands:     {perf['total_return']*100:.2f}% return, {perf['sharpe_ratio']:.2f} Sharpe, {perf['win_rate']*100:.1f}% win rate")


if __name__ == "__main__":
    main()
