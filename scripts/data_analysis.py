#!/usr/bin/env python3
"""
Data Analysis and Utility Functions for Parquet Storage
Provides tools to analyze, export, and manage Parquet-stored market data
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
from data_storage import get_parquet_manager
from constants import option_symbols

# Initialize Parquet manager
parquet_manager = get_parquet_manager()

def analyze_data_coverage():
    """Analyze data coverage across all stored files"""
    print("📊 Data Coverage Analysis")
    print("=" * 50)
    
    available_data = parquet_manager.list_available_data()
    total_files = 0
    total_size_mb = 0
    
    coverage_report = []
    
    for category, files in available_data.items():
        print(f"\n📁 {category.title()} ({len(files)} files):")
        
        for file_stem in files:
            if '_' in file_stem:
                symbol_name, timeframe = file_stem.rsplit('_', 1)
                info = parquet_manager.get_data_info(symbol_name, timeframe)
                
                if info['exists']:
                    # Calculate days of coverage
                    start_date = pd.to_datetime(info['start_date'])
                    end_date = pd.to_datetime(info['end_date'])
                    days_coverage = (end_date - start_date).days
                    
                    coverage_report.append({
                        'category': category,
                        'symbol': symbol_name,
                        'timeframe': timeframe,
                        'rows': info['total_rows'],
                        'start_date': start_date,
                        'end_date': end_date,
                        'days_coverage': days_coverage,
                        'file_size_mb': info['file_size_mb']
                    })
                    
                    print(f"   📈 {file_stem:20}: {info['total_rows']:>8,} rows | "
                          f"{days_coverage:>4} days | {info['file_size_mb']:>6.1f} MB")
                    
                    total_files += 1
                    total_size_mb += info['file_size_mb']
    
    print(f"\n📋 Summary:")
    print(f"   Total files: {total_files}")
    print(f"   Total size: {total_size_mb:.1f} MB")
    
    return pd.DataFrame(coverage_report)

def export_to_csv(symbol_name, timeframe, output_dir="data/csv_exports", date_filter=None):
    """
    Export Parquet data to CSV format
    
    Args:
        symbol_name (str): Symbol name
        timeframe (str): Timeframe
        output_dir (str): Output directory for CSV files
        date_filter (tuple): (start_date, end_date) for filtering
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load data
    if date_filter:
        start_date, end_date = date_filter
        df = parquet_manager.load_data(symbol_name, timeframe, start_date, end_date)
    else:
        df = parquet_manager.load_data(symbol_name, timeframe)
    
    if df.empty:
        print(f"❌ No data found for {symbol_name}_{timeframe}")
        return
    
    # Export to CSV
    csv_filename = f"{symbol_name}_{timeframe}.csv"
    csv_path = output_path / csv_filename
    
    df.to_csv(csv_path, index=False)
    print(f"✅ Exported {len(df)} rows to {csv_path}")

def create_price_chart(symbol_name, timeframe, days_back=30, save_chart=True):
    """
    Create price chart for a symbol
    
    Args:
        symbol_name (str): Symbol name
        timeframe (str): Timeframe
        days_back (int): Number of days to show
        save_chart (bool): Whether to save the chart
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Load data
    df = parquet_manager.load_data(
        symbol_name, 
        timeframe, 
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    if df.empty:
        print(f"❌ No data found for {symbol_name}_{timeframe}")
        return
    
    # Create chart
    plt.figure(figsize=(12, 6))
    
    # Plot OHLC data
    plt.subplot(2, 1, 1)
    plt.plot(df['timestamp'], df['close'], label='Close Price', color='blue', linewidth=1)
    plt.fill_between(df['timestamp'], df['low'], df['high'], alpha=0.3, color='gray', label='High-Low Range')
    plt.title(f"{symbol_name.upper()} - {timeframe} ({days_back} days)")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot volume
    plt.subplot(2, 1, 2)
    plt.bar(df['timestamp'], df['volume'], alpha=0.7, color='orange', width=0.8)
    plt.ylabel("Volume")
    plt.xlabel("Date")
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_chart:
        charts_dir = Path("data/charts")
        charts_dir.mkdir(parents=True, exist_ok=True)
        chart_path = charts_dir / f"{symbol_name}_{timeframe}_{days_back}d.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"📊 Chart saved to {chart_path}")
    
    plt.show()

def get_data_statistics(symbol_name, timeframe):
    """
    Get statistical summary of data
    
    Args:
        symbol_name (str): Symbol name  
        timeframe (str): Timeframe
        
    Returns:
        dict: Statistical summary
    """
    df = parquet_manager.load_data(symbol_name, timeframe)
    
    if df.empty:
        return {"error": "No data found"}
    
    # Calculate statistics
    stats = {
        "symbol": symbol_name,
        "timeframe": timeframe,
        "total_rows": len(df),
        "date_range": {
            "start": df['timestamp'].min(),
            "end": df['timestamp'].max(),
            "days": (df['timestamp'].max() - df['timestamp'].min()).days
        },
        "price_stats": {
            "current_price": df['close'].iloc[-1],
            "min_price": df['close'].min(),
            "max_price": df['close'].max(),
            "mean_price": df['close'].mean(),
            "std_price": df['close'].std()
        },
        "volume_stats": {
            "total_volume": df['volume'].sum(),
            "avg_volume": df['volume'].mean(),
            "max_volume": df['volume'].max()
        },
        "returns": {
            "total_return_pct": ((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100,
            "daily_return_std": df['close'].pct_change().std() * 100
        }
    }
    
    return stats

def compare_symbols(symbols_list, timeframe='1D', days_back=90):
    """
    Compare multiple symbols performance
    
    Args:
        symbols_list (list): List of symbol names
        timeframe (str): Timeframe to compare
        days_back (int): Number of days to analyze
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    comparison_data = {}
    
    for symbol in symbols_list:
        df = parquet_manager.load_data(
            symbol, 
            timeframe,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if not df.empty:
            # Normalize prices to start at 100 for comparison
            normalized_prices = (df['close'] / df['close'].iloc[0]) * 100
            comparison_data[symbol] = {
                'timestamp': df['timestamp'],
                'normalized_price': normalized_prices,
                'return_pct': ((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100
            }
    
    if not comparison_data:
        print("❌ No data found for any symbols")
        return
    
    # Create comparison chart
    plt.figure(figsize=(12, 8))
    
    for symbol, data in comparison_data.items():
        plt.plot(data['timestamp'], data['normalized_price'], 
                label=f"{symbol} ({data['return_pct']:.1f}%)", linewidth=2)
    
    plt.title(f"Symbol Performance Comparison - {timeframe} ({days_back} days)")
    plt.ylabel("Normalized Price (Base = 100)")
    plt.xlabel("Date")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save chart
    charts_dir = Path("data/charts")
    charts_dir.mkdir(parents=True, exist_ok=True)
    chart_path = charts_dir / f"comparison_{timeframe}_{days_back}d.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"📊 Comparison chart saved to {chart_path}")
    
    plt.show()
    
    # Print performance summary
    print(f"\n📊 Performance Summary ({days_back} days):")
    for symbol, data in comparison_data.items():
        print(f"   {symbol:12}: {data['return_pct']:>6.1f}%")

def backup_data(backup_dir="data/backups"):
    """Create backup of all Parquet data"""
    import shutil
    from datetime import datetime
    
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"parquet_backup_{timestamp}"
    backup_full_path = backup_path / backup_name
    
    # Copy entire parquet directory
    shutil.copytree(parquet_manager.base_data_dir, backup_full_path)
    
    print(f"💾 Backup created: {backup_full_path}")
    return backup_full_path

if __name__ == "__main__":
    print("🔧 Parquet Data Analysis Utilities")
    print("=" * 40)
    
    # Run data coverage analysis
    coverage_df = analyze_data_coverage()
    
    # Example usage of other functions
    print("\n💡 Example Usage:")
    print("   analyze_data_coverage()")
    print("   export_to_csv('nifty50', '1D')")
    print("   create_price_chart('nifty50', '1D', days_back=30)")
    print("   get_data_statistics('nifty50', '1D')")
    print("   compare_symbols(['nifty50', 'niftybank'], '1D')")
    print("   backup_data()")