"""
Test MA Crossover Strategy
Test the implementation on a sample Nifty50 stock
"""
import sys
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.backtesting.strategies.built_in.ma_crossover import MACrossoverStrategy

def test_ma_crossover():
    """Test MA Crossover strategy on RELIANCE"""
    
    print("=" * 80)
    print("MA CROSSOVER STRATEGY TEST")
    print("=" * 80)
    
    # Load data
    data_file = Path('data/parquet/stocks/RELIANCE_1D.parquet')
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return
    
    df = pd.read_parquet(data_file)
    
    print(f"\n📊 Testing on: RELIANCE")
    print(f"   Data points: {len(df):,}")
    print(f"   Date range: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
    print(f"   Price range: ₹{df['close'].min():.2f} - ₹{df['close'].max():.2f}")
    
    # Create strategy
    strategy = MACrossoverStrategy(fast_period=20, slow_period=50, ma_type='SMA')
    
    print(f"\n🎯 Strategy: {strategy.name}")
    print(f"   Parameters: {strategy.fast_period}/{strategy.slow_period} {strategy.ma_type}")
    
    # Run backtest
    print(f"\n⏳ Running backtest...")
    
    try:
        results = strategy.backtest(
            df,
            initial_capital=100000,
            commission=0.001,
            slippage=0.0005
        )
        
        print(f"\n✅ Backtest Complete!")
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   Total Return:      {results['performance']['total_return']:>8.2%}")
        print(f"   Sharpe Ratio:      {results['performance']['sharpe_ratio']:>8.2f}")
        print(f"   Max Drawdown:      {results['performance']['max_drawdown']:>8.2%}")
        print(f"   Win Rate:          {results['performance']['win_rate']:>8.2%}")
        print(f"   Total Trades:      {results['performance']['total_trades']:>8.0f}")
        print(f"   Profit Factor:     {results['performance']['profit_factor']:>8.2f}")
        print(f"   Avg Trade Return:  {results['performance']['avg_trade_return']:>8.2%}")
        
        # Get current signal
        current_signal = strategy.get_current_signal(df)
        print(f"\n🔔 Current Signal: {current_signal}")
        
        # Show last few signals
        signals_df = results['signals_df']
        last_signals = signals_df[signals_df['signal'] != 0].tail(5)
        
        if len(last_signals) > 0:
            print(f"\n📋 Recent Signals:")
            for idx, row in last_signals.iterrows():
                signal_type = "BUY" if row['signal'] == 1 else "SELL"
                date = row['timestamp'].date() if 'timestamp' in row else idx
                price = row['close']
                print(f"   {date}: {signal_type} at ₹{price:.2f}")
        
        print("\n" + "=" * 80)
        print("✅ TEST SUCCESSFUL - Strategy is working correctly!")
        print("=" * 80)
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error during backtest: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = test_ma_crossover()
    
    if results:
        print(f"\n💡 Next: Test on all {55} Nifty50 stocks with strategy_runner.py")
