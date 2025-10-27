#!/usr/bin/env python3
"""
Quick Test Script - Demonstrates the reorganized project structure
Run this to verify all systems are working after directory restructure
"""
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test all core module imports"""
    print("🔧 Testing module imports...")
    
    try:
        from my_fyers_model import MyFyersModel
        print("  ✅ MyFyersModel")
        
        from scripts.data_storage import get_parquet_manager
        print("  ✅ Parquet Storage")
        
        from scripts.symbol_discovery import get_symbol_discovery
        print("  ✅ Symbol Discovery")
        
        from scripts.market_depth_storage import get_market_depth_manager
        print("  ✅ Market Depth Storage")
        
        from scripts.data_orchestrator import get_data_orchestrator
        print("  ✅ Data Orchestrator")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_api_connection():
    """Test Fyers API connection"""
    print("\n📡 Testing API connection...")
    
    try:
        from my_fyers_model import MyFyersModel
        fyers = MyFyersModel()
        
        quotes = fyers.get_quotes({'symbols': 'NSE:NIFTY50-INDEX'})
        if quotes.get('s') == 'ok':
            ltp = quotes['d'][0]['v']['lp']
            print(f"  ✅ API Working: Nifty50 = ₹{ltp}")
            return True
        else:
            print("  ❌ API call failed")
            return False
    except Exception as e:
        print(f"  ❌ API error: {e}")
        return False

def test_symbol_discovery():
    """Test symbol discovery system"""
    print("\n🔍 Testing symbol discovery...")
    
    try:
        from symbol_discovery import get_symbol_discovery
        discovery = get_symbol_discovery()
        
        nifty_symbols = discovery.get_nifty50_constituents()
        bank_symbols = discovery.get_banknifty_constituents()
        
        print(f"  ✅ Nifty50 stocks: {len(nifty_symbols)}")
        print(f"  ✅ BankNifty stocks: {len(bank_symbols)}")
        
        # Test loading universe
        universe = discovery.load_symbol_universe()
        if universe:
            total_categories = len([k for k, v in universe.items() if isinstance(v, list)])
            print(f"  ✅ Symbol universe: {total_categories} categories")
        
        return True
    except Exception as e:
        print(f"  ❌ Symbol discovery error: {e}")
        return False

def test_market_depth():
    """Test market depth collection"""
    print("\n📊 Testing market depth...")
    
    try:
        from market_depth_storage import get_market_depth_manager
        depth_manager = get_market_depth_manager()
        
        # Test getting market depth for a symbol
        depth = depth_manager.get_market_depth('NSE:HDFCBANK-EQ')
        if depth:
            parsed = depth_manager.parse_depth_data(depth)
            ltp = parsed.get('ltp', 0)
            spread = parsed.get('spread', 0)
            print(f"  ✅ HDFC Bank: LTP=₹{ltp}, Spread=₹{spread:.2f}")
            return True
        else:
            print("  ⚠️ Could not get market depth (market may be closed)")
            return True  # Not a failure if market is closed
    except Exception as e:
        print(f"  ❌ Market depth error: {e}")
        return False

def test_file_structure():
    """Test that files are in correct locations"""
    print("\n📁 Testing file structure...")
    
    import os
    from pathlib import Path
    
    # Check key files and directories
    checks = [
        ("../auth/credentials.ini", "Configuration file"),
        ("../auth/access_token.txt", "Access token"),
        ("../docs/", "Documentation directory"),
        ("../data/", "Data directory"),
        ("my_fyers_model.py", "Main API module"),
        ("symbol_discovery.py", "Symbol discovery module"),
        ("market_depth_storage.py", "Market depth module"),
        ("data_orchestrator.py", "Data orchestrator")
    ]
    
    all_good = True
    for file_path, description in checks:
        if os.path.exists(file_path):
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ Missing: {description}")
            all_good = False
    
    return all_good

def main():
    """Run comprehensive test suite"""
    print("🚀 Fyers Data Extraction System - Structure Test")
    print("=" * 60)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 Current Directory: scripts/")
    print()
    
    tests = [
        ("Module Imports", test_imports),
        ("File Structure", test_file_structure),
        ("API Connection", test_api_connection),
        ("Symbol Discovery", test_symbol_discovery),
        ("Market Depth", test_market_depth)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  💥 Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("🚀 Ready for comprehensive market data extraction!")
    else:
        print("⚠️  Some tests failed - check configuration and dependencies")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)