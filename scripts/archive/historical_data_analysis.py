"""
📊 HISTORICAL DATA AVAILABILITY ANALYSIS
=======================================
Comprehensive analysis of historical data bars available for different timeframes
Critical information for backtesting module development
"""

import pandas as pd
from datetime import datetime, timedelta
from my_fyers_model import MyFyersModel
from comprehensive_symbol_discovery import ComprehensiveSymbolDiscovery
from fyers_retry_handler import EnhancedFyersAPI
import time

class HistoricalDataAnalyzer:
    """Analyze historical data availability across timeframes"""
    
    def __init__(self):
        """Initialize analyzer with Fyers API"""
        try:
            self.fyers = MyFyersModel()
            self.enhanced_api = EnhancedFyersAPI(self.fyers)
            self.symbol_discovery = ComprehensiveSymbolDiscovery()
            print("✅ Historical Data Analyzer initialized")
        except Exception as e:
            print(f"❌ Failed to initialize analyzer: {e}")
            self.fyers = None
            self.enhanced_api = None
    
    def analyze_timeframe_data_availability(self):
        """Analyze historical data availability for different timeframes"""
        
        print("\n📊 HISTORICAL DATA AVAILABILITY ANALYSIS")
        print("=" * 70)
        print("🎯 Analyzing data bars available for different timeframes")
        print("🔍 Testing representative symbols from each market segment")
        print("=" * 70)
        
        # Timeframes to test (Fyers API format)
        timeframes = {
            '1m': '1',      # 1 minute
            '5m': '5',      # 5 minutes  
            '15m': '15',    # 15 minutes
            '30m': '30',    # 30 minutes
            '1H': '60',     # 1 hour
            '1D': '1D',     # 1 day
            '1W': '1W',     # 1 week
            '1M': '1M'      # 1 month
        }
        
        # Test symbols from different segments
        test_symbols = {
            'Large Cap Stock': 'NSE:RELIANCE-EQ',
            'Bank Stock': 'NSE:HDFCBANK-EQ',
            'Index': 'NSE:NIFTY50-INDEX',
            'ETF': 'NSE:NIFTYBEES-ETF',
            'Option': 'NSE:NIFTY25OCT18750CE',
            'Future': 'NSE:NIFTY25OCTFUT',
            'Commodity': 'MCX:GOLD-COMMODITY'
        }
        
        # Date ranges to test
        date_ranges = {
            '7 Days': 7,
            '30 Days': 30,
            '90 Days': 90,
            '1 Year': 365,
            '2 Years': 730,
            '5 Years': 1825
        }
        
        results = {}
        
        for symbol_type, symbol in test_symbols.items():
            print(f"\n📈 Analyzing {symbol_type}: {symbol}")
            results[symbol_type] = {}
            
            for timeframe_name, timeframe_code in timeframes.items():
                print(f"   ⏱️  Testing {timeframe_name} timeframe...")
                results[symbol_type][timeframe_name] = {}
                
                for range_name, days in date_ranges.items():
                    try:
                        end_date = datetime.now()
                        start_date = end_date - timedelta(days=days)
                        
                        if self.enhanced_api:
                            data = self.enhanced_api.get_historical_data(
                                symbol=symbol,
                                timeframe=timeframe_code,
                                start_date=start_date.strftime('%Y-%m-%d'),
                                end_date=end_date.strftime('%Y-%m-%d')
                            )
                            
                            if data and 'candles' in data and data['candles']:
                                bar_count = len(data['candles'])
                                results[symbol_type][timeframe_name][range_name] = bar_count
                                print(f"      📊 {range_name}: {bar_count} bars")
                            else:
                                results[symbol_type][timeframe_name][range_name] = 0
                                print(f"      ❌ {range_name}: No data")
                    except Exception as e:
                        results[symbol_type][timeframe_name][range_name] = f"Error: {str(e)[:30]}..."
                        print(f"      💥 {range_name}: Error")
                    
                    time.sleep(0.5)  # Rate limiting
        
        return results
    
    def generate_comprehensive_timeframe_guide(self, results):
        """Generate comprehensive timeframe guide for backtesting"""
        
        print("\n📋 COMPREHENSIVE TIMEFRAME GUIDE FOR BACKTESTING")
        print("=" * 80)
        
        # Theoretical calculations
        theoretical_bars = {
            '1m': {
                '1 Day': 375,      # 6.25 hours * 60 minutes
                '1 Week': 1875,    # 5 days * 375
                '1 Month': 8250,   # 22 trading days * 375
                '1 Year': 99000    # 264 trading days * 375
            },
            '5m': {
                '1 Day': 75,       # 375 / 5
                '1 Week': 375,     # 1875 / 5
                '1 Month': 1650,   # 8250 / 5
                '1 Year': 19800    # 99000 / 5
            },
            '15m': {
                '1 Day': 25,       # 375 / 15
                '1 Week': 125,     # 1875 / 15
                '1 Month': 550,    # 8250 / 15
                '1 Year': 6600     # 99000 / 15
            },
            '1H': {
                '1 Day': 6,        # 6.25 hours
                '1 Week': 31,      # 6.25 * 5
                '1 Month': 138,    # 6.25 * 22
                '1 Year': 1650     # 6.25 * 264
            },
            '1D': {
                '1 Week': 5,       # 5 trading days
                '1 Month': 22,     # 22 trading days
                '1 Year': 264,     # 264 trading days
                '5 Years': 1320    # 264 * 5
            }
        }
        
        print("\n📊 THEORETICAL VS ACTUAL DATA AVAILABILITY")
        print("-" * 60)
        
        # Market timing information
        print("\n🕐 INDIAN MARKET TRADING HOURS:")
        print("   📅 Trading Days: Monday to Friday")
        print("   ⏰ Equity Session: 9:15 AM to 3:30 PM (6 hours 15 minutes)")
        print("   ⏰ Pre-Market: 9:00 AM to 9:15 AM")
        print("   ⏰ Post-Market: 3:40 PM to 4:00 PM")
        print("   📊 Total Active Minutes: 375 minutes per day")
        
        # Timeframe recommendations
        timeframe_recommendations = {
            '1m (1 Minute)': {
                'best_for': 'Scalping, High-frequency strategies',
                'max_lookback': '30-90 days (due to data volume)',
                'typical_bars_per_day': 375,
                'backtesting_use': 'Short-term strategies, entry/exit optimization',
                'limitations': 'Large data volume, API rate limits'
            },
            '5m (5 Minutes)': {
                'best_for': 'Day trading, Intraday strategies',
                'max_lookback': '6 months to 1 year',
                'typical_bars_per_day': 75,
                'backtesting_use': 'Intraday backtesting, pattern recognition',
                'limitations': 'Moderate data volume'
            },
            '15m (15 Minutes)': {
                'best_for': 'Swing trading, Medium-term analysis',
                'max_lookback': '2-3 years',
                'typical_bars_per_day': 25,
                'backtesting_use': 'Multi-day strategies, trend analysis',
                'limitations': 'Good balance of detail and history'
            },
            '30m (30 Minutes)': {
                'best_for': 'Position trading, Trend analysis',
                'max_lookback': '3-5 years',
                'typical_bars_per_day': 13,
                'backtesting_use': 'Medium-term strategies',
                'limitations': 'Less granular than 15m'
            },
            '1H (1 Hour)': {
                'best_for': 'Position trading, Long-term analysis',
                'max_lookback': '5+ years',
                'typical_bars_per_day': 6,
                'backtesting_use': 'Long-term backtesting, weekly/monthly patterns',
                'limitations': 'Lower resolution for entry/exit timing'
            },
            '1D (Daily)': {
                'best_for': 'Long-term investing, Fundamental analysis',
                'max_lookback': '10+ years',
                'typical_bars_per_day': 1,
                'backtesting_use': 'Long-term strategies, portfolio backtesting',
                'limitations': 'No intraday information'
            },
            '1W (Weekly)': {
                'best_for': 'Long-term trends, Portfolio allocation',
                'max_lookback': '20+ years',
                'typical_bars_per_week': 1,
                'backtesting_use': 'Long-term trend analysis',
                'limitations': 'Very low resolution'
            },
            '1M (Monthly)': {
                'best_for': 'Long-term investing, Macro analysis',
                'max_lookback': '50+ years',
                'typical_bars_per_month': 1,
                'backtesting_use': 'Long-term portfolio strategies',
                'limitations': 'Extremely low resolution'
            }
        }
        
        print("\n📈 TIMEFRAME RECOMMENDATIONS FOR BACKTESTING")
        print("-" * 60)
        
        for timeframe, info in timeframe_recommendations.items():
            print(f"\n🎯 {timeframe}:")
            print(f"   📊 Best For: {info['best_for']}")
            print(f"   📅 Max Lookback: {info['max_lookback']}")
            print(f"   📈 Bars/Day: {info['typical_bars_per_day']}")
            print(f"   🧪 Backtesting Use: {info['backtesting_use']}")
            print(f"   ⚠️  Limitations: {info['limitations']}")
        
        # Data availability patterns
        print("\n📊 EXPECTED DATA AVAILABILITY PATTERNS")
        print("-" * 60)
        
        availability_patterns = {
            'Equity Stocks': {
                'data_since': '2010+ for major stocks',
                'best_timeframes': '1D, 1H, 15m',
                'limitations': 'Corporate actions may cause gaps'
            },
            'Indices': {
                'data_since': '2000+ for major indices',
                'best_timeframes': 'All timeframes available',
                'limitations': 'Very reliable data'
            },
            'ETFs': {
                'data_since': '2013+ (ETF introduction)',
                'best_timeframes': '1D, 1H, 15m',
                'limitations': 'Newer instrument class'
            },
            'Options': {
                'data_since': 'Current series only',
                'best_timeframes': '1m, 5m, 15m',
                'limitations': 'Limited to contract life'
            },
            'Futures': {
                'data_since': 'Current series + few expired',
                'best_timeframes': '1m, 5m, 15m, 1H',
                'limitations': 'Limited to contract life'
            },
            'Commodities': {
                'data_since': 'Varies by commodity',
                'best_timeframes': '1D, 1H',
                'limitations': 'Different trading hours'
            }
        }
        
        print("\n📋 DATA AVAILABILITY BY INSTRUMENT TYPE:")
        for instrument, info in availability_patterns.items():
            print(f"\n📈 {instrument}:")
            print(f"   📅 Data Since: {info['data_since']}")
            print(f"   ⭐ Best Timeframes: {info['best_timeframes']}")
            print(f"   ⚠️  Limitations: {info['limitations']}")
        
        # Backtesting strategy recommendations
        print("\n🧪 BACKTESTING STRATEGY RECOMMENDATIONS")
        print("-" * 60)
        
        strategy_recommendations = [
            {
                'strategy': 'Scalping Strategies',
                'timeframe': '1m',
                'lookback': '30-60 days',
                'reason': 'High-frequency data needed for entry/exit optimization'
            },
            {
                'strategy': 'Day Trading',
                'timeframe': '5m or 15m',
                'lookback': '6 months to 1 year',
                'reason': 'Balance between detail and sufficient historical data'
            },
            {
                'strategy': 'Swing Trading',
                'timeframe': '1H or 1D',
                'lookback': '2-5 years',
                'reason': 'Multi-day holds require longer historical validation'
            },
            {
                'strategy': 'Position Trading',
                'timeframe': '1D',
                'lookback': '5-10 years',
                'reason': 'Long-term trends require extensive historical data'
            },
            {
                'strategy': 'Options Strategies',
                'timeframe': '15m or 1H',
                'lookback': 'Current series + few past',
                'reason': 'Limited by option contract life'
            },
            {
                'strategy': 'Portfolio Strategies',
                'timeframe': '1D or 1W',
                'lookback': '10+ years',
                'reason': 'Long-term performance evaluation'
            }
        ]
        
        for rec in strategy_recommendations:
            print(f"\n🎯 {rec['strategy']}:")
            print(f"   ⏱️  Recommended Timeframe: {rec['timeframe']}")
            print(f"   📅 Lookback Period: {rec['lookback']}")
            print(f"   💡 Reason: {rec['reason']}")
        
        return timeframe_recommendations

def main():
    """Run historical data availability analysis"""
    
    print("🔍 HISTORICAL DATA AVAILABILITY ANALYSIS")
    print("=" * 70)
    print("🎯 Analyzing data availability for backtesting module")
    print("📊 Testing multiple timeframes and date ranges")
    print("=" * 70)
    
    analyzer = HistoricalDataAnalyzer()
    
    if analyzer.enhanced_api:
        # Run analysis
        print("\n⚡ Starting comprehensive timeframe analysis...")
        results = analyzer.analyze_timeframe_data_availability()
        
        # Generate guide
        recommendations = analyzer.generate_comprehensive_timeframe_guide(results)
        
        print("\n✅ ANALYSIS COMPLETED!")
        print("📋 Use this information for backtesting module design")
        print("🎯 Timeframe selection critical for strategy development")
        
    else:
        print("❌ Cannot run analysis - API not available")

if __name__ == "__main__":
    main()