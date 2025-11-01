# 📊 Bulk Historical Data Download System

Complete system for downloading 5 years of historical data for all symbols across multiple timeframes.

## 🚀 Quick Start

### Option 1: Interactive Quick Start (Recommended)
```bash
python scripts/market_data/download_manager.py quick-start
```

### Option 2: Command Line

**Test Run (Nifty 50, Daily data only - ~5 minutes)**
```bash
python scripts/market_data/download_manager.py start --category nifty50 --timeframe 1D
```

**Download Nifty 50 All Timeframes (~30 minutes)**
```bash
python scripts/market_data/download_manager.py start --category nifty50
```

**Full Download (All symbols, All timeframes - 24-48 hours)**
```bash
python scripts/market_data/download_manager.py start
```

## 📁 Data Organization

Data is stored in month-wise folders for efficient querying:

```
data/parquet/
├── nifty50/
│   ├── RELIANCE/
│   │   ├── 1D/
│   │   │   ├── 2020/
│   │   │   │   ├── 01/
│   │   │   │   │   └── RELIANCE_1D_2020_01.parquet
│   │   │   │   ├── 02/
│   │   │   │   │   └── RELIANCE_1D_2020_02.parquet
│   │   │   │   └── ...
│   │   │   ├── 2021/...
│   │   │   ├── 2022/...
│   │   │   ├── 2023/...
│   │   │   ├── 2024/...
│   │   │   └── 2025/...
│   │   ├── 1m/
│   │   │   └── (same structure)
│   │   ├── 5m/
│   │   ├── 15m/
│   │   ├── 30m/
│   │   └── 60m/
│   ├── TCS/
│   └── ...
├── etfs/
├── all_equities/
└── ...
```

## ⚙️ Features

### ✅ Comprehensive Coverage
- **Symbols:** All 8,686 equities + 273 ETFs + indices
- **Timeframes:** 1m, 5m, 15m, 30m, 60m, 1D
- **History:** 5 years of data
- **Total Files:** ~52,000 Parquet files

### ✅ Smart Downloading
- **Parallel Processing:** 10 concurrent downloads (configurable)
- **Rate Limiting:** Respects Fyers API limits automatically
- **Auto-Retry:** Failed downloads are tracked and can be retried
- **Resume Capability:** Can resume interrupted downloads
- **Progress Tracking:** Real-time progress with Rich console

### ✅ Organized Storage
- **Month-wise Folders:** Easy querying by date range
- **Parquet Format:** 10x faster than CSV, compressed
- **Standardized Schema:** timestamp, open, high, low, close, volume

## 📊 Download Statistics

### Estimated Download Times

| Category | Symbols | Total Files | Estimated Time |
|----------|---------|-------------|----------------|
| Nifty 50 (1D only) | 50 | 50 | ~5 minutes |
| Nifty 50 (all timeframes) | 50 | 300 | ~30 minutes |
| All Equities (1D only) | 8,686 | 8,686 | ~8 hours |
| **Full Download** | **8,959** | **~52,000** | **24-48 hours** |

*Times assume stable internet and no API throttling*

### Storage Requirements

| Data Type | Size per Symbol | Total Size |
|-----------|----------------|------------|
| 1D data | ~50 KB | ~450 MB |
| 1m data | ~500 KB | ~4.5 GB |
| All timeframes | ~1 MB | **~9 GB** |

**Total Estimated Storage:** ~9-10 GB for complete 5-year dataset

## 🔧 Advanced Usage

### Download Specific Category
```bash
# ETFs only
python scripts/market_data/download_manager.py start --category etfs

# Bank Nifty constituents
python scripts/market_data/download_manager.py start --category nifty_bank
```

### Download Specific Timeframe
```bash
# Daily data only (fastest, smallest)
python scripts/market_data/download_manager.py start --timeframe 1D

# Intraday data only
python scripts/market_data/download_manager.py start --timeframe 5m
```

### Adjust Worker Count
```bash
# More workers (faster but more API calls)
python scripts/market_data/download_manager.py start --workers 20

# Fewer workers (slower but gentler on API)
python scripts/market_data/download_manager.py start --workers 5
```

### Resume Failed Downloads
```bash
python scripts/market_data/download_manager.py resume
```

### Check Download Status
```bash
python scripts/market_data/download_manager.py status
```

## 📈 Using the Downloaded Data

### Load Data by Month
```python
import pandas as pd
from pathlib import Path

# Load specific month
file_path = Path('data/parquet/nifty50/RELIANCE/1D/2024/10/RELIANCE_1D_2024_10.parquet')
df = pd.read_parquet(file_path)

print(df.head())
```

### Load Date Range
```python
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_date_range(symbol, timeframe, start_date, end_date):
    """Load data for a date range"""
    base_path = Path(f'data/parquet/nifty50/{symbol}/{timeframe}')
    
    all_data = []
    
    # Iterate through years and months
    for year in range(start_date.year, end_date.year + 1):
        for month in range(1, 13):
            # Skip months outside range
            if (year == start_date.year and month < start_date.month):
                continue
            if (year == end_date.year and month > end_date.month):
                continue
            
            file_path = base_path / str(year) / f"{month:02d}" / f"{symbol}_{timeframe}_{year}_{month:02d}.parquet"
            
            if file_path.exists():
                df = pd.read_parquet(file_path)
                all_data.append(df)
    
    # Combine all data
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined['date'] = pd.to_datetime(combined['timestamp'], unit='s')
        
        # Filter to exact date range
        combined = combined[
            (combined['date'] >= start_date) & 
            (combined['date'] <= end_date)
        ]
        
        return combined.sort_values('timestamp')
    
    return pd.DataFrame()

# Example usage
start = datetime(2024, 1, 1)
end = datetime(2024, 12, 31)
df = load_date_range('RELIANCE', '1D', start, end)
print(f"Loaded {len(df)} records")
```

### Create Data Loading Utility
```python
# Save this as scripts/data/data_loader.py
from pathlib import Path
import pandas as pd
from datetime import datetime

class HistoricalDataLoader:
    """Utility to load historical data from Parquet files"""
    
    def __init__(self, base_path='data/parquet'):
        self.base_path = Path(base_path)
    
    def load_symbol(self, category, symbol, timeframe, start_date=None, end_date=None):
        """Load data for a symbol"""
        symbol_path = self.base_path / category / symbol / timeframe
        
        if not symbol_path.exists():
            raise FileNotFoundError(f"No data found for {symbol}")
        
        all_data = []
        
        # Get all Parquet files
        for file in symbol_path.rglob('*.parquet'):
            df = pd.read_parquet(file)
            all_data.append(df)
        
        if not all_data:
            return pd.DataFrame()
        
        # Combine all data
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
        combined['date'] = pd.to_datetime(combined['timestamp'], unit='s')
        
        # Filter by date range if specified
        if start_date:
            combined = combined[combined['date'] >= start_date]
        if end_date:
            combined = combined[combined['date'] <= end_date]
        
        return combined
    
    def get_available_symbols(self, category):
        """Get list of available symbols in a category"""
        category_path = self.base_path / category
        if not category_path.exists():
            return []
        
        return [d.name for d in category_path.iterdir() if d.is_dir()]

# Usage example
loader = HistoricalDataLoader()

# Load all available data for a symbol
df = loader.load_symbol('nifty50', 'RELIANCE', '1D')

# Load specific date range
start = datetime(2024, 1, 1)
end = datetime(2024, 12, 31)
df_2024 = loader.load_symbol('nifty50', 'RELIANCE', '1D', start, end)

# Get list of available symbols
symbols = loader.get_available_symbols('nifty50')
print(f"Available symbols: {len(symbols)}")
```

## 🔍 Monitoring Downloads

### Real-time Progress
The bulk downloader shows real-time progress with:
- Current task being processed
- Completed/Failed/Pending counts
- Progress bar
- Time elapsed and remaining

### Download Logs
Check `logs/bulk_download.log` for detailed download logs:
```bash
tail -f logs/bulk_download.log
```

### Status File
Download status is saved in `logs/download_status.json`:
```json
{
  "tasks": {
    "RELIANCE_1D": {
      "symbol": "RELIANCE",
      "category": "nifty50",
      "timeframe": "1D",
      "status": "completed",
      "downloaded_months": 60,
      "total_months": 60
    }
  },
  "statistics": {
    "total": 300,
    "completed": 250,
    "failed": 5,
    "pending": 45
  }
}
```

## ⚠️ Troubleshooting

### API Rate Limit Errors
If you get rate limit errors:
1. Reduce worker count: `--workers 5`
2. The rate limiter will automatically slow down
3. Resume with `python download_manager.py resume`

### Disk Space Issues
Monitor disk space during download:
```bash
# Linux/Mac
df -h data/

# Windows
Get-PSDrive C
```

### Failed Downloads
Check failed tasks and retry:
```bash
python scripts/market_data/download_manager.py status
python scripts/market_data/download_manager.py resume
```

## 📝 Best Practices

1. **Start Small:** Test with Nifty 50 before full download
2. **Monitor Progress:** Check status regularly during large downloads
3. **Backup Data:** Backup the `data/parquet` folder after complete downloads
4. **Incremental Updates:** Use `scripts/data/update_tables.py` for daily updates
5. **Validate Data:** Spot-check random files to ensure data quality

## 🚀 Next Steps

After downloading data:

1. **Backtesting:** Use the data for strategy backtesting
2. **Analysis:** Perform technical analysis on historical data
3. **Visualization:** Create charts and dashboards
4. **Live Trading:** Combine with WebSocket for real-time + historical analysis

## 📞 Support

For issues or questions:
- Check `logs/bulk_download.log` for errors
- Review `PROJECT_REVIEW_AND_GAPS.md` for system overview
- Check Fyers API documentation for API limits
