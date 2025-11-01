"""
Test RSI Mean Reversion Strategy on Sample Stock
=================================================

Tests the RSI strategy implementation and displays results.
"""

import sys
import pandas as pd
from pathlib import Path

# Add scripts to path
sys.path.append(str(Path(__file__).parent / 'scripts' / 'backtesting' / 'strategies' / 'built_in'))

from rsi_mean_reversion import RSIMeanReversionStrategy


def main():
    print("=" * 80)
    print("RSI Mean Reversion Strategy Test")
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
    print("Creating RSI Mean Reversion Strategy")
    print("=" * 80)
    
    strategy = RSIMeanReversionStrategy(
        rsi_period=14,
        oversold_threshold=30,
        overbought_threshold=70
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


if __name__ == "__main__":
    main()
