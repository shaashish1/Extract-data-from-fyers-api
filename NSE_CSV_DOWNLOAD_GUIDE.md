# NSE Symbol CSV Download Instructions

## Quick 5-Minute Manual Download Process

### Step 1: Create Directory
```bash
mkdir -p data/nse_symbols
cd data/nse_symbols
```

### Step 2: Download NSE Index CSVs

You can download these files from NSE Archives or use the provided Python script.

#### Option A: Direct URLs (NSE Archives)
```
# Nifty indices
https://archives.nseindia.com/content/indices/ind_nifty50list.csv
https://archives.nseindia.com/content/indices/ind_nifty100list.csv
https://archives.nseindia.com/content/indices/ind_nifty200list.csv
https://archives.nseindia.com/content/indices/ind_niftymidcap50list.csv
https://archives.nseindia.com/content/indices/ind_niftymidcap100list.csv

# ETFs
https://archives.nseindia.com/content/fo/etf_list.csv
```

#### Option B: Use Provided Script
Save the attached `nse_fyers_data_fetch.py` and run:
```bash
python nse_fyers_data_fetch.py
```

### Step 3: Rename Files (if needed)
The script expects these exact filenames in `data/nse_symbols/`:
- `NIFTY_50.csv`
- `NIFTY_100.csv`
- `NIFTY_200.csv`
- `NIFTY_MIDCAP_50.csv`
- `NIFTY_MIDCAP_100.csv`
- `ETFs.csv`

### Step 4: Verify Files
```bash
ls -lh data/nse_symbols/
```

You should see 6 CSV files.

---

## Quick Download Script (5 minutes)

Save this as `quick_nse_download.py`:

```python
import requests
import pandas as pd
import time
from pathlib import Path

# NSE session initialization
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

session = requests.Session()
session.get('https://www.nseindia.com', headers=headers)
time.sleep(2)

# Output directory
output_dir = Path("data/nse_symbols")
output_dir.mkdir(parents=True, exist_ok=True)

# Index URLs
indices = {
    "NIFTY_50": "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050",
    "NIFTY_100": "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20100",
    "NIFTY_200": "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200",
    "NIFTY_MIDCAP_50": "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20MIDCAP%2050",
    "NIFTY_MIDCAP_100": "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20MIDCAP%20100",
}

# Download indices
for name, url in indices.items():
    try:
        response = session.get(url, headers=headers)
        data = response.json().get("data", [])
        df = pd.DataFrame(data)[["symbol"]]
        
        output_path = output_dir / f"{name}.csv"
        df.to_csv(output_path, index=False)
        print(f"✅ Downloaded {name}: {len(df)} symbols")
        time.sleep(1)
    except Exception as e:
        print(f"❌ Failed {name}: {e}")

# Download ETFs from archive
try:
    etf_url = "https://archives.nseindia.com/content/fo/etf_list.csv"
    etf_df = pd.read_csv(etf_url)
    etf_output = output_dir / "ETFs.csv"
    etf_df[["SYMBOL"]].rename(columns={"SYMBOL": "symbol"}).to_csv(etf_output, index=False)
    print(f"✅ Downloaded ETFs: {len(etf_df)} symbols")
except Exception as e:
    print(f"❌ Failed ETFs: {e}")

print(f"\n✅ All files saved to: {output_dir}")
```

Run it:
```bash
python quick_nse_download.py
```

---

## File Structure After Download

```
data/
└── nse_symbols/
    ├── NIFTY_50.csv          (50 symbols)
    ├── NIFTY_100.csv         (100 symbols)
    ├── NIFTY_200.csv         (200 symbols)
    ├── NIFTY_MIDCAP_50.csv   (50 symbols)
    ├── NIFTY_MIDCAP_100.csv  (100 symbols)
    └── ETFs.csv              (varies, ~200-300)
```

---

## Next Step

After downloading NSE CSVs, run the production discovery:
```bash
python scripts/symbol_discovery/production_symbol_discovery.py
```

This will:
1. ✅ Load your manual NSE CSVs
2. ✅ Download FYERS NSE_CM + NSE_FO
3. ✅ Extract F&O equity symbols (TATAMOTORS, etc.)
4. ✅ Merge for complete equity universe
5. ✅ Validate Nifty50/100/200 counts
6. ✅ Save consolidated data

---

## Manual Download (Backup Method)

If scripts fail, manually download from NSE website:

1. Visit: https://www.nseindia.com/market-data/live-equity-market
2. Select index (Nifty 50, Nifty 100, etc.)
3. Click "Download" button → CSV
4. Save to `data/nse_symbols/` with correct filename

---

## Frequency of Updates

- **Nifty indices**: Update every 6 months (or when you notice changes)
- **ETFs**: Update quarterly
- **FYERS data**: Downloaded automatically (always latest)

**Total time investment: 5 minutes every 6 months** 🎯
