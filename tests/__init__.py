"""
FYERS ALGORITHMIC TRADING PLATFORM - TEST FRAMEWORK
==================================================

Enterprise-grade testing infrastructure for the comprehensive
Fyers trading platform with 156,586 symbols and real-time capabilities.

Test Categories:
- Unit Tests: Individual component validation
- Integration Tests: System-wide functionality 
- Validation Tests: Data integrity and API connectivity
- Performance Tests: Load and stress testing
- Mock Tests: Offline simulation and validation

Test Framework Features:
- Automated module import validation (21 production scripts)
- Authentication system testing
- Symbol discovery validation (subset of 156K symbols)
- Data storage and Parquet operations testing
- WebSocket connection testing (mock and live)
- Configuration and path validation
- Comprehensive reporting with Rich output
- CI/CD integration ready

Usage:
    python -m tests.run_all_tests
    python -m tests.unit.test_auth
    python -m tests.integration.test_websocket
"""

__version__ = "1.0.0"
__author__ = "Fyers Platform Development Team"

# Test framework metadata
TEST_FRAMEWORK_INFO = {
    "version": __version__,
    "platform_version": "156K Symbol Universe",
    "test_categories": [
        "unit", "integration", "validation", 
        "performance", "mock", "ci_cd"
    ],
    "production_scripts": 21,
    "symbol_universe_size": 156586,
    "supported_markets": ["NSE", "BSE", "MCX"],
    "testing_framework": "Enterprise-Grade Validation Suite"
}

# Export key testing utilities
from .core.test_base import FyersTestBase
from .core.test_runner import EnterpriseTestRunner
from .core.test_validator import SystemValidator

__all__ = [
    'FyersTestBase',
    'EnterpriseTestRunner', 
    'SystemValidator',
    'TEST_FRAMEWORK_INFO'
]