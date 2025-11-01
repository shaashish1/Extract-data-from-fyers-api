#!/usr/bin/env python3
"""
Quick real-time sanity check:
- Preflight auth (profile)
- Fetch quotes for a handful of symbols
- Exit 0 on success, 1 on failure
"""
import sys
import json
from pathlib import Path

# Ensure project root is on sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.auth.my_fyers_model import MyFyersModel
from scripts.realtime.fyers_realtime import get_realtime_manager


def main() -> int:
    fy = MyFyersModel()
    check = fy.preflight_auth_check()
    if not isinstance(check, dict) or check.get('s') != 'ok':
        print(f"⚠️  Auth preflight reported an issue: {check}")
        print("➡️  Proceeding to try quotes anyway for a precise error message...")

    mgr = get_realtime_manager(symbols=["NSE:SBIN-EQ"])  # keep it minimal for validation
    try:
        quotes = mgr.fetch_quotes_once()
        print(f"✅ Real-time quote check OK. Symbols returned: {len(quotes)}")
        # Print a few entries
        for k in list(quotes.keys())[:5]:
            print(f"  {k}: {json.dumps(quotes[k])}")
        return 0
    except Exception as e:
        print(f"❌ Real-time quote check failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
