#!/usr/bin/env python3
"""
System Validation Report for Fyers API Data Extraction System
============================================================

This script validates all major components of the system and generates
a comprehensive report showing what's working and what needs attention.
"""

import os
import sys
import pandas as pd
from pathlib import Path
import time
from datetime import datetime

def print_header(title, symbol="🔍"):
    """Print a formatted header"""
    print(f"\n{symbol} {title}")
    print("=" * (len(title) + 4))

def print_status(item, status, details=""):
    """Print status with appropriate emoji"""
    emoji = "✅" if status else "❌" 
    print(f"   {emoji} {item}: {details}")

def validate_imports():
    """Validate all required imports"""
    print_header("Package Import Validation", "📦")
    
    imports = [
        ("pandas", "import pandas as pd"),
        ("numpy", "import numpy as np"),
        ("pyarrow", "import pyarrow as pa"),
        ("requests", "import requests"),
        ("fyers_apiv3", "from fyers_apiv3 import fyersModel"),
        ("aiohttp", "import aiohttp"),
        ("websocket-client", "import websocket"),
        ("matplotlib", "import matplotlib.pyplot as plt"),
        ("seaborn", "import seaborn as sns")
    ]
    
    results = {}
    for name, import_statement in imports:
        try:
            exec(import_statement)
            print_status(name, True, "✓ Available")
            results[name] = True
        except ImportError as e:
            print_status(name, False, f"❌ Missing: {e}")
            results[name] = False
    
    return results

def validate_core_modules():
    """Validate core system modules"""
    print_header("Core Module Validation", "🧩")
    
    modules = [
        "data_storage",
        "symbol_discovery", 
        "fyers_direct_discovery",
        "nse_data_fetcher",
        "index_constituents",
        "my_fyers_model",
        "constants"
    ]
    
    results = {}
    for module in modules:
        try:
            exec(f"from {module} import *")
            print_status(module, True, "✓ Importable")
            results[module] = True
        except Exception as e:
            print_status(module, False, f"❌ Error: {str(e)[:50]}")
            results[module] = False
    
    return results

def validate_data_storage():
    """Validate Parquet data storage system"""
    print_header("Data Storage Validation", "💾")
    
    try:
        from data_storage import get_parquet_manager
        manager = get_parquet_manager()
        
        # Check directory structure
        base_exists = os.path.exists(manager.base_data_dir)
        print_status("Base data directory", base_exists, str(manager.base_data_dir))
        
        # Check subdirectories
        subdirs = ["indices", "stocks", "options", "market_updates", "market_depth"]
        for subdir in subdirs:
            path = manager.base_data_dir / subdir
            exists = path.exists()
            print_status(f"{subdir} directory", exists, str(path))
        
        # Check existing data files
        indices_files = list((manager.base_data_dir / "indices").glob("*.parquet"))
        stocks_files = list((manager.base_data_dir / "stocks").glob("*.parquet"))
        options_files = list((manager.base_data_dir / "options").glob("*.parquet"))
        
        print_status("Indices data files", len(indices_files) > 0, f"{len(indices_files)} files")
        print_status("Stocks data files", len(stocks_files) > 0, f"{len(stocks_files)} files")
        print_status("Options data files", len(options_files) > 0, f"{len(options_files)} files")
        
        # Test data loading
        if indices_files:
            try:
                sample_file = indices_files[0]
                df = pd.read_parquet(sample_file)
                print_status("Data loading test", True, f"Loaded {df.shape[0]} rows from {sample_file.name}")
            except Exception as e:
                print_status("Data loading test", False, f"Failed: {str(e)[:50]}")
        
        return True
        
    except Exception as e:
        print_status("Data storage system", False, f"Failed: {str(e)[:50]}")
        return False

def validate_symbol_discovery():
    """Validate symbol discovery systems"""
    print_header("Symbol Discovery Validation", "🎯")
    
    results = {}
    
    # Test Direct Fyers Discovery
    try:
        from fyers_direct_discovery import get_fyers_direct_discovery
        fyers_direct = get_fyers_direct_discovery()
        
        nifty50 = fyers_direct.get_nifty50_constituents()
        nifty100 = fyers_direct.get_nifty100_constituents()
        etfs = fyers_direct.get_popular_etfs()
        
        print_status("Direct Fyers - Nifty50", len(nifty50) > 0, f"{len(nifty50)} symbols")
        print_status("Direct Fyers - Nifty100", len(nifty100) > 0, f"{len(nifty100)} symbols")
        print_status("Direct Fyers - ETFs", len(etfs) > 0, f"{len(etfs)} symbols")
        
        results['fyers_direct'] = True
        
    except Exception as e:
        print_status("Direct Fyers Discovery", False, f"Failed: {str(e)[:50]}")
        results['fyers_direct'] = False
    
    # Test NSE Data Fetcher
    try:
        from nse_data_fetcher import get_nse_fetcher
        nse_fetcher = get_nse_fetcher()
        print_status("NSE Data Fetcher", True, "✓ Module loaded")
        results['nse_fetcher'] = True
        
    except Exception as e:
        print_status("NSE Data Fetcher", False, f"Failed: {str(e)[:50]}")
        results['nse_fetcher'] = False
    
    # Test Unified Symbol Discovery
    try:
        from symbol_discovery import SymbolDiscovery
        discovery = SymbolDiscovery()
        
        nifty50 = discovery.get_nifty50_constituents()
        etfs = discovery.get_etf_symbols()
        
        print_status("Unified Discovery - Nifty50", len(nifty50) > 0, f"{len(nifty50)} symbols")
        print_status("Unified Discovery - ETFs", len(etfs) > 0, f"{len(etfs)} symbols")
        
        results['unified_discovery'] = True
        
    except Exception as e:
        print_status("Unified Symbol Discovery", False, f"Failed: {str(e)[:50]}")
        results['unified_discovery'] = False
    
    # Test Index Constituents
    try:
        from index_constituents import get_nifty50_symbols, get_nifty100_symbols
        nifty50 = get_nifty50_symbols()
        nifty100 = get_nifty100_symbols()
        
        print_status("Index Constituents - Nifty50", len(nifty50) == 50, f"{len(nifty50)} symbols")
        print_status("Index Constituents - Nifty100", len(nifty100) == 100, f"{len(nifty100)} symbols")
        
        results['index_constituents'] = True
        
    except Exception as e:
        print_status("Index Constituents", False, f"Failed: {str(e)[:50]}")
        results['index_constituents'] = False
    
    return results

def validate_authentication():
    """Validate authentication setup"""
    print_header("Authentication Validation", "🔐")
    
    # Check credentials file
    cred_path = Path("../auth/credentials.ini")
    cred_exists = cred_path.exists()
    print_status("Credentials file", cred_exists, str(cred_path))
    
    # Check access token file
    token_path = Path("../auth/access_token.txt") 
    token_exists = token_path.exists()
    print_status("Access token file", token_exists, str(token_path))
    
    # Test Fyers model creation (without API calls)
    try:
        from my_fyers_model import MyFyersModel
        print_status("Fyers model class", True, "✓ Importable")
        model_available = True
    except Exception as e:
        print_status("Fyers model class", False, f"Failed: {str(e)[:50]}")
        model_available = False
    
    return {
        'credentials': cred_exists,
        'token': token_exists,
        'model': model_available
    }

def validate_websocket_setup():
    """Validate WebSocket setup"""
    print_header("WebSocket Setup Validation", "🌐")
    
    try:
        # Test WebSocket imports
        import websocket
        print_status("WebSocket client", True, "✓ Available")
        
        # Test WebSocket runner import
        from run_websocket import WebSocketDataCollector
        print_status("WebSocket runner class", True, "✓ Importable")
        
        return True
        
    except Exception as e:
        print_status("WebSocket setup", False, f"Failed: {str(e)[:50]}")
        return False

def generate_performance_test():
    """Test performance of symbol discovery methods"""
    print_header("Performance Testing", "⚡")
    
    try:
        from fyers_direct_discovery import get_fyers_direct_discovery
        from symbol_discovery import SymbolDiscovery
        
        # Test Direct Fyers performance
        start_time = time.time()
        fyers_direct = get_fyers_direct_discovery()
        nifty50 = fyers_direct.get_nifty50_constituents()
        etfs = fyers_direct.get_popular_etfs()
        direct_time = time.time() - start_time
        
        print_status("Direct Fyers speed", True, f"{direct_time:.2f}s ({len(nifty50)+len(etfs)} symbols)")
        
        # Test Unified Discovery performance  
        start_time = time.time()
        discovery = SymbolDiscovery()
        nifty50_unified = discovery.get_nifty50_constituents()
        etfs_unified = discovery.get_etf_symbols()
        unified_time = time.time() - start_time
        
        print_status("Unified Discovery speed", True, f"{unified_time:.2f}s ({len(nifty50_unified)+len(etfs_unified)} symbols)")
        
        # Performance comparison
        if direct_time > 0:
            improvement = ((unified_time - direct_time) / direct_time) * 100
            print_status("Performance improvement", direct_time < unified_time, f"Direct is {abs(improvement):.1f}% {'faster' if improvement > 0 else 'slower'}")
        
        return True
        
    except Exception as e:
        print_status("Performance testing", False, f"Failed: {str(e)[:50]}")
        return False

def validate_data_analysis():
    """Validate data analysis capabilities"""
    print_header("Data Analysis Validation", "📊")
    
    try:
        from data_analysis import analyze_data_coverage
        print_status("Data analysis module", True, "✓ Importable")
        
        # Test if we can analyze existing data
        analyze_data_coverage()
        print_status("Data coverage analysis", True, "✓ Executed")
        
        return True
        
    except Exception as e:
        print_status("Data analysis", False, f"Failed: {str(e)[:50]}")
        return False

def main():
    """Run complete system validation"""
    print("🚀 Fyers API Data Extraction System Validation")
    print("=" * 60)
    print(f"📅 Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    print(f"📁 Working Directory: {os.getcwd()}")
    
    # Run all validations
    results = {}
    
    results['imports'] = validate_imports()
    results['modules'] = validate_core_modules()
    results['storage'] = validate_data_storage()
    results['symbols'] = validate_symbol_discovery()
    results['auth'] = validate_authentication()
    results['websocket'] = validate_websocket_setup()
    results['performance'] = generate_performance_test()
    results['analysis'] = validate_data_analysis()
    
    # Generate summary
    print_header("Validation Summary", "📋")
    
    total_checks = 0
    passed_checks = 0
    
    for category, category_results in results.items():
        if isinstance(category_results, dict):
            for check, status in category_results.items():
                total_checks += 1
                if status:
                    passed_checks += 1
        elif isinstance(category_results, bool):
            total_checks += 1
            if category_results:
                passed_checks += 1
    
    success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    print_status("Overall Success Rate", success_rate >= 80, f"{passed_checks}/{total_checks} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("\n🎉 System Status: EXCELLENT - Ready for production use!")
    elif success_rate >= 80:
        print("\n✅ System Status: GOOD - Ready with minor issues to address")
    elif success_rate >= 60:
        print("\n⚠️  System Status: NEEDS ATTENTION - Some components need fixing")
    else:
        print("\n❌ System Status: CRITICAL - Major issues need resolution")
    
    print("\n💡 Next Steps:")
    print("   • For authentication issues: Setup Fyers API credentials")
    print("   • For missing data: Run scripts/stocks_data.py")
    print("   • For real-time testing: Run scripts/run_websocket.py")
    print("   • For NSE integration: Test scripts/nse_symbol_demo.py")
    
    return results

if __name__ == "__main__":
    main()