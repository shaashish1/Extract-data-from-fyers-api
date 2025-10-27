"""
📊 QUICK TIMEFRAME DATA ANALYSIS
===============================
Get key timeframe data availability for README documentation
"""

from my_fyers_model import MyFyersModel
from fyers_retry_handler import EnhancedFyersAPI
from datetime import datetime, timedelta
import time

def quick_timeframe_analysis():
    """Quick analysis of key timeframes"""
    
    print("📊 QUICK TIMEFRAME ANALYSIS FOR README")
    print("=" * 50)
    
    try:
        fyers = MyFyersModel()
        enhanced_api = EnhancedFyersAPI(fyers)
        
        # Test one reliable symbol
        test_symbol = 'NSE:RELIANCE-EQ'
        
        timeframes = {
            '1 Minute': '1',
            '5 Minutes': '5', 
            '15 Minutes': '15',
            '1 Hour': '60',
            '1 Day': '1D'
        }
        
        date_ranges = [
            ('7 Days', 7),
            ('30 Days', 30),
            ('1 Year', 365)
        ]
        
        results = {}
        
        for tf_name, tf_code in timeframes.items():
            print(f"\n⏱️  Testing {tf_name} ({tf_code}):")
            results[tf_name] = {}
            
            for range_name, days in date_ranges:
                try:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days)
                    
                    data = enhanced_api.get_historical_data(
                        symbol=test_symbol,
                        timeframe=tf_code,
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d')
                    )
                    
                    if data and 'candles' in data and data['candles']:
                        bar_count = len(data['candles'])
                        results[tf_name][range_name] = bar_count
                        print(f"   📊 {range_name}: {bar_count} bars")
                    else:
                        results[tf_name][range_name] = 0
                        print(f"   ❌ {range_name}: No data")
                        
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    results[tf_name][range_name] = f"Error"
                    print(f"   💥 {range_name}: Error - {str(e)[:30]}...")
        
        return results
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

def display_theoretical_data():
    """Display theoretical data expectations"""
    
    print("\n📋 THEORETICAL DATA AVAILABILITY")
    print("=" * 50)
    
    theoretical_data = {
        '1 Minute': {
            'bars_per_day': 375,  # 6.25 hours * 60 minutes
            'typical_30_days': '~11,250 bars',
            'typical_1_year': '~99,000 bars',
            'best_for': 'Scalping, HFT strategies'
        },
        '5 Minutes': {
            'bars_per_day': 75,   # 375 / 5
            'typical_30_days': '~2,250 bars', 
            'typical_1_year': '~19,800 bars',
            'best_for': 'Day trading, intraday'
        },
        '15 Minutes': {
            'bars_per_day': 25,   # 375 / 15
            'typical_30_days': '~750 bars',
            'typical_1_year': '~6,600 bars', 
            'best_for': 'Swing trading'
        },
        '1 Hour': {
            'bars_per_day': 6,    # 6.25 hours
            'typical_30_days': '~180 bars',
            'typical_1_year': '~1,650 bars',
            'best_for': 'Position trading'
        },
        '1 Day': {
            'bars_per_day': 1,    
            'typical_30_days': '~22 bars',
            'typical_1_year': '~264 bars',
            'best_for': 'Long-term analysis'
        }
    }
    
    for timeframe, info in theoretical_data.items():
        print(f"\n🎯 {timeframe}:")
        print(f"   📊 Bars per Day: {info['bars_per_day']}")
        print(f"   📅 30 Days: {info['typical_30_days']}")
        print(f"   📈 1 Year: {info['typical_1_year']}")
        print(f"   💡 Best For: {info['best_for']}")
    
    return theoretical_data

if __name__ == "__main__":
    print("🔍 QUICK TIMEFRAME ANALYSIS")
    print("Testing RELIANCE stock for timeframe data availability")
    
    # Get actual data
    actual_results = quick_timeframe_analysis()
    
    # Display theoretical expectations
    theoretical_data = display_theoretical_data()
    
    print(f"\n✅ Analysis complete - Data ready for README update")