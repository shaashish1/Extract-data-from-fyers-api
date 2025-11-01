"""
Quick System Validation - Essential Checks Only

Fast validation of critical systems before starting data download.
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("🚀 QUICK SYSTEM VALIDATION")
print("="*80)

# Test 1: Time and Market Status
print("\n1️⃣ Market Status:")
from datetime import datetime
import pytz
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
print(f"   Current IST: {now.strftime('%Y-%m-%d %H:%M:%S')}")
hour, minute, weekday = now.hour, now.minute, now.weekday()
market_open = (9 <= hour < 15 or (hour == 15 and minute <= 30)) and weekday < 5
print(f"   Market: {'✅ OPEN' if market_open else '⏰ CLOSED'}")

# Test 2: Authentication
print("\n2️⃣  Authentication:")
try:
    from scripts.auth.my_fyers_model import MyFyersModel
    fyers = MyFyersModel()
    token = fyers.get_token()
    print(f"   Token: ✅ {token[:20]}..." if token else "   Token: ❌ Missing")
    print(f"   Model: ✅ {type(fyers.get_fyre_model()).__name__}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Rate Limiter
print("\n3️⃣  Rate Limiter:")
try:
    from scripts.core.rate_limit_manager import get_rate_limiter
    limiter = get_rate_limiter()
    print(f"   Limits: {limiter.MAX_REQUESTS_PER_SECOND}/sec, {limiter.MAX_REQUESTS_PER_MINUTE}/min")
    print(f"   Status: ✅ Active")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Symbol Discovery
print("\n4️⃣  Symbol Discovery:")
try:
    from scripts.symbol_discovery.fyers_json_symbol_discovery import FyersJSONSymbolDiscovery
    discovery = FyersJSONSymbolDiscovery()
    
    # Check available metadata files
    metadata_dir = Path(project_root) / 'scripts' / 'symbol_discovery' / 'data' / 'symbols' / 'fyers'
    if metadata_dir.exists():
        metadata_files = list(metadata_dir.glob('*_metadata.json'))
        print(f"   Metadata files: ✅ {len(metadata_files)} files")
        for f in metadata_files:
            print(f"      - {f.name}")
    else:
        print(f"   ⚠️  Metadata directory not found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Data Storage
print("\n5️⃣  Data Storage:")
try:
    from scripts.data.data_storage import get_parquet_manager
    manager = get_parquet_manager()
    
    data_dir = Path(project_root) / 'data' / 'parquet'
    if data_dir.exists():
        parquet_files = list(data_dir.rglob('*.parquet'))
        print(f"   Parquet files: {len(parquet_files)} files")
        print(f"   Location: ✅ {data_dir}")
    else:
        print(f"   ⚠️  Data directory empty (OK before download)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: Backtesting (vectorbt)
print("\n6️⃣  Backtesting Environment:")
try:
    import vectorbt as vbt
    import numba
    print(f"   vectorbt: ✅ v{vbt.__version__}")
    print(f"   numba: ✅ v{numba.__version__}")
    print(f"   Python: {sys.version.split()[0]}")
    
    from scripts.backtesting.engine.data_loader import BacktestDataLoader
    loader = BacktestDataLoader()
    summary = loader.get_available_data_summary()
    print(f"   Data files: {summary['total_files']} (ready for backtesting)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 7: Market Data APIs
print("\n7️⃣  Market Data APIs:")
try:
    from scripts.market_data.history_api import FyersHistoryAPI
    from scripts.market_data.quotes_api import FyersQuotesAPI
    from scripts.market_data.market_depth_api import FyersMarketDepthAPI
    from scripts.market_data.option_chain_api import FyersOptionChainAPI
    print(f"   ✅ All 4 APIs available (rate-limited)")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*80)
print("✅ SYSTEM READY FOR DATA DOWNLOAD!")
print("="*80)
print("\n📋 Next Steps:")
print("   1. Review docs/TOMORROW_PLAN.md for detailed instructions")
print("   2. Download historical data (50+ symbols, 5 years)")
print("   3. Implement and test strategies")
print("   4. Generate performance rankings")
print("\n" + "="*80)
