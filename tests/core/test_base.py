#!/usr/bin/env python3
"""
FYERS TEST BASE CLASS
====================

Enterprise-grade base class for all Fyers platform tests.
Provides common testing utilities, validation methods, and reporting.

Author: Fyers Platform Development Team
Version: 1.0.0
"""

import os
import sys
import unittest
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from unittest.mock import Mock, patch

# Rich imports for beautiful test output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.text import Text
from rich.tree import Tree

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

class FyersTestBase(unittest.TestCase):
    """
    Base test class for all Fyers platform tests.
    
    Provides:
    - Rich console output
    - Standardized test setup/teardown
    - Common validation utilities
    - Test result tracking
    - Mock/fixture management
    - Performance measurement
    """
    
    def __init__(self, methodName: str = 'runTest'):
        super().__init__(methodName)
        self.console = Console()
        self.test_results = {}
        self.start_time = None
        self.project_root = project_root
        self.scripts_path = project_root / "scripts"
        
        # Test configuration
        self.test_config = {
            "timeout": 30,  # seconds
            "retry_count": 3,
            "mock_api_calls": True,
            "validate_imports": True,
            "check_syntax": True,
            "performance_check": True
        }
        
        # Setup logging
        self.setup_test_logging()
    
    def setUp(self):
        """Setup for each test method."""
        self.start_time = datetime.now()
        test_name = self._testMethodName
        
        self.console.print(f"\n🧪 Starting: {test_name}", style="blue")
        self.console.print(f"⏰ Time: {self.start_time.strftime('%H:%M:%S')}", style="dim")
        
        # Initialize test-specific data
        self.test_data = {}
        self.mock_objects = {}
        
    def tearDown(self):
        """Cleanup after each test method."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        test_name = self._testMethodName
        
        # Store test results
        self.test_results[test_name] = {
            "start_time": self.start_time,
            "end_time": end_time,
            "duration": duration,
            "status": "completed"
        }
        
        self.console.print(f"✅ Completed: {test_name} ({duration:.2f}s)", style="green")
        
        # Cleanup mock objects
        for mock_obj in self.mock_objects.values():
            if hasattr(mock_obj, 'stop'):
                mock_obj.stop()
    
    def setup_test_logging(self):
        """Setup logging for test execution."""
        log_dir = self.project_root / "tests" / "reports"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"test_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(f"FyersTest.{self.__class__.__name__}")
    
    # ==================== VALIDATION UTILITIES ====================
    
    def validate_module_import(self, module_path: str, module_name: str = None) -> bool:
        """
        Validate that a module can be imported successfully.
        
        Args:
            module_path: Path to the module file
            module_name: Optional module name for import
            
        Returns:
            bool: True if import successful, False otherwise
        """
        try:
            if module_name is None:
                module_name = Path(module_path).stem
            
            # Add directory to path temporarily
            module_dir = str(Path(module_path).parent)
            if module_dir not in sys.path:
                sys.path.insert(0, module_dir)
            
            # Attempt import
            __import__(module_name)
            
            self.console.print(f"✅ Import successful: {module_name}", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Import failed: {module_name} - {str(e)}", style="red")
            self.logger.error(f"Module import failed: {module_path} - {e}")
            return False
    
    def validate_file_exists(self, file_path: Union[str, Path]) -> bool:
        """Validate that a file exists."""
        path_obj = Path(file_path)
        exists = path_obj.exists()
        
        if exists:
            self.console.print(f"✅ File exists: {path_obj.name}", style="green")
        else:
            self.console.print(f"❌ File missing: {file_path}", style="red")
            
        return exists
    
    def validate_directory_structure(self, base_path: Union[str, Path], 
                                   expected_dirs: List[str]) -> Dict[str, bool]:
        """Validate expected directory structure exists."""
        base_path = Path(base_path)
        results = {}
        
        for dir_name in expected_dirs:
            dir_path = base_path / dir_name
            exists = dir_path.exists() and dir_path.is_dir()
            results[dir_name] = exists
            
            if exists:
                self.console.print(f"✅ Directory exists: {dir_name}", style="green")
            else:
                self.console.print(f"❌ Directory missing: {dir_name}", style="red")
        
        return results
    
    def validate_python_syntax(self, file_path: Union[str, Path]) -> bool:
        """Validate Python file has correct syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            compile(source_code, str(file_path), 'exec')
            
            self.console.print(f"✅ Syntax valid: {Path(file_path).name}", style="green")
            return True
            
        except SyntaxError as e:
            self.console.print(f"❌ Syntax error: {Path(file_path).name} - Line {e.lineno}: {e.msg}", style="red")
            self.logger.error(f"Syntax error in {file_path}: {e}")
            return False
        except Exception as e:
            self.console.print(f"❌ Validation error: {Path(file_path).name} - {str(e)}", style="red")
            return False
    
    # ==================== MOCK AND FIXTURE UTILITIES ====================
    
    def create_mock_fyers_model(self) -> Mock:
        """Create a mock FyersModel for testing without API calls."""
        mock_fyers = Mock()
        
        # Mock common API responses
        mock_fyers.get_profile.return_value = {
            's': 'ok',
            'data': {
                'name': 'Test User',
                'email': 'test@example.com'
            }
        }
        
        mock_fyers.get_quotes.return_value = {
            's': 'ok',
            'd': [{
                'n': 'NSE:NIFTY50-INDEX',
                'lp': 19500.50,
                'ch': 150.25,
                'chp': 0.77
            }]
        }
        
        mock_fyers.history.return_value = {
            's': 'ok',
            'candles': [
                [1635724800, 19400.0, 19500.0, 19350.0, 19450.0, 1000000]
            ]
        }
        
        self.mock_objects['fyers_model'] = mock_fyers
        return mock_fyers
    
    def create_test_symbol_data(self, count: int = 10) -> List[Dict]:
        """Create test symbol data for validation."""
        test_symbols = []
        for i in range(count):
            symbol = {
                'symbol': f'NSE:TEST{i:03d}-EQ',
                'description': f'Test Symbol {i}',
                'lot_size': 1,
                'tick_size': 0.05,
                'segment': 'NSE'
            }
            test_symbols.append(symbol)
        
        return test_symbols
    
    # ==================== ASSERTION HELPERS ====================
    
    def assertModuleImports(self, module_path: str, msg: str = None):
        """Assert that a module imports successfully."""
        result = self.validate_module_import(module_path)
        if not result:
            raise AssertionError(msg or f"Module {module_path} failed to import")
    
    def assertFileExists(self, file_path: Union[str, Path], msg: str = None):
        """Assert that a file exists."""
        if not self.validate_file_exists(file_path):
            raise AssertionError(msg or f"File {file_path} does not exist")
    
    def assertValidPythonSyntax(self, file_path: Union[str, Path], msg: str = None):
        """Assert that a Python file has valid syntax."""
        if not self.validate_python_syntax(file_path):
            raise AssertionError(msg or f"File {file_path} has invalid Python syntax")
    
    # ==================== REPORTING UTILITIES ====================
    
    def generate_test_report(self) -> Table:
        """Generate a Rich table with test results."""
        table = Table(title="Test Execution Report")
        table.add_column("Test Name", style="cyan")
        table.add_column("Duration", style="green")
        table.add_column("Status", style="bold")
        
        for test_name, results in self.test_results.items():
            duration = f"{results['duration']:.2f}s"
            status = "✅ PASSED" if results['status'] == 'completed' else "❌ FAILED"
            table.add_row(test_name, duration, status)
        
        return table
    
    def print_test_summary(self):
        """Print a summary of test execution."""
        panel = Panel.fit(
            f"Test Summary\n"
            f"Total Tests: {len(self.test_results)}\n"
            f"Passed: {len([r for r in self.test_results.values() if r['status'] == 'completed'])}\n"
            f"Duration: {sum(r['duration'] for r in self.test_results.values()):.2f}s",
            title="Test Execution Summary",
            border_style="green"
        )
        self.console.print(panel)

# Utility functions for test discovery and execution
def discover_production_scripts(scripts_dir: Path) -> List[Path]:
    """Discover all production Python scripts in organized structure."""
    production_scripts = []
    
    # Define the organized script categories
    script_categories = ['auth', 'websocket', 'market_data', 'symbol_discovery', 'data', 'core']
    
    for category in script_categories:
        category_dir = scripts_dir / category
        if category_dir.exists():
            for script_file in category_dir.glob("*.py"):
                if script_file.name != "__init__.py":  # Skip __init__.py files
                    production_scripts.append(script_file)
    
    return production_scripts

def get_test_configuration() -> Dict[str, Any]:
    """Get test configuration settings."""
    return {
        "project_root": project_root,
        "scripts_path": project_root / "scripts",
        "test_data_path": project_root / "tests" / "fixtures",
        "test_reports_path": project_root / "tests" / "reports",
        "production_script_count": 21,
        "symbol_universe_size": 156586,
        "supported_markets": ["NSE", "BSE", "MCX"],
        "test_timeout": 30,
        "mock_api_calls": True
    }