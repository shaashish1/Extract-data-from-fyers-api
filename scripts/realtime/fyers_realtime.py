#!/usr/bin/env python3
"""
FR-lite real-time quotes/depth manager using MyFyersModel
- No Kafka/REST; simple in-process loop to validate auth and stream data
- Default symbol universe: from data/consolidated_symbols/nifty50_symbols.csv (if present), else a small fallback list
"""
import os
import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import sys
from pathlib import Path
import pandas as pd

# Ensure project root for nested imports when run directly
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Project imports
from scripts.auth.my_fyers_model import MyFyersModel

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FyersRealtimeManager:
    def __init__(self, symbols: Optional[List[str]] = None):
        self.fy = MyFyersModel()
        self.client = self.fy.get_fyre_model()
        self.symbols = symbols or self._load_default_symbols()
        self.latest_quotes: Dict[str, Dict[str, Any]] = {}
        self.latest_depth: Dict[str, Dict[str, Any]] = {}

    def _load_default_symbols(self) -> List[str]:
        """Load NSE symbols (without -EQ suffix) and map to Fyers format NSE:SYMBOL-EQ."""
        csv_path = Path('data/consolidated_symbols/nifty50_symbols.csv')
        symbols: List[str] = []
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                if 'symbol' in df.columns:
                    base = [str(s) for s in df['symbol'].dropna().unique().tolist()][:25]
                    symbols = [f"NSE:{s}-EQ" for s in base]
                    logger.info(f"Loaded {len(symbols)} symbols from {csv_path}")
            except Exception as e:
                logger.warning(f"Failed to read {csv_path}: {e}")
        if not symbols:
            # Fallback small list
            base = ["SBIN", "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "KOTAKBANK", "AXISBANK"]
            symbols = [f"NSE:{s}-EQ" for s in base]
            logger.info(f"Using fallback symbols: {symbols}")
        return symbols

    def fetch_quotes_once(self) -> Dict[str, Dict[str, Any]]:
        """Fetch quotes for the configured symbols once; returns symbol->data map."""
        data = {"symbols": ",".join(self.symbols)}
        resp = self.client.quotes(data=data)
        out: Dict[str, Dict[str, Any]] = {}
        if isinstance(resp, dict) and resp.get('s') == 'ok':
            for item in resp.get('d', []):
                n = item.get('n')  # e.g., NSE:SBIN-EQ
                v = item.get('v', {})
                out[n] = {
                    'ltp': v.get('ltp'),
                    'vol_traded_today': v.get('vol_traded_today'),
                    'per_change': v.get('per_change'),
                    'change': v.get('change'),
                    'open': v.get('open_price'),
                    'high': v.get('high_price'),
                    'low': v.get('low_price'),
                    'prev_close': v.get('prev_close_price'),
                }
            self.latest_quotes = out
        else:
            raise RuntimeError(f"Quotes error: {resp}")
        return out

    def fetch_depth_for(self, symbol: str) -> Dict[str, Any]:
        """Fetch market depth for a single symbol."""
        data = {"symbol": symbol, "ohlcv_flag": "1"}
        resp = self.client.depth(data=data)
        if isinstance(resp, dict) and resp.get('s') == 'ok':
            self.latest_depth[symbol] = resp
            return resp
        raise RuntimeError(f"Depth error for {symbol}: {resp}")

    def stream_loop(self, interval_sec: int = 2, rounds: Optional[int] = None):
        """Continuously fetch quotes; optionally limit to a number of rounds."""
        i = 0
        while True:
            i += 1
            try:
                q = self.fetch_quotes_once()
                sample = list(q.items())[:5]
                logger.info(f"Quotes sample: {json.dumps(sample, default=str)[:300]}...")
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                # If -16/-17 comes inside the response, fetch_quotes_once will raise; stop
                break
            if rounds is not None and i >= rounds:
                break
            time.sleep(interval_sec)


def get_realtime_manager(symbols: Optional[List[str]] = None) -> FyersRealtimeManager:
    return FyersRealtimeManager(symbols)
