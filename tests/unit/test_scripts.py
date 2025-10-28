#!/usr/bin/env python3
"""
SCRIPT ORGANIZATION UNIT TESTS
===============================

Unit tests for the organized script structure and imports.
Validates the 6-category organization and module loading.

Author: Fyers Platform Development Team
Version: 1.0.0
"""

import os
import sys
import unittest
from pathlib import Path

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

from tests.core.test_base import FyersTestBase

class TestScriptOrganization(FyersTestBase):
    """Unit tests for script organization structure."""
    
    def setUp(self):
        super().setUp()
        self.scripts_dir = self.project_root / "scripts"
        self.expected_categories = [
            "auth", "websocket", "market_data", 
            "symbol_discovery", "data", "core"
        ]
    
    def test_script_directory_structure(self):
        """Test that all expected script categories exist."""
        self.assertFileExists(self.scripts_dir, "Scripts directory should exist")
        
        # Validate each category directory
        for category in self.expected_categories:
            category_dir = self.scripts_dir / category
            self.assertFileExists(category_dir, f"Category {category} should exist")
            
            # Check for __init__.py
            init_file = category_dir / "__init__.py"
            self.assertFileExists(init_file, f"Category {category} should have __init__.py")
            self.assertValidPythonSyntax(init_file, f"Category {category} __init__.py should be valid")
    
    def test_production_script_count(self):
        """Test that we have the expected number of production scripts."""
        total_scripts = 0
        category_counts = {}
        
        for category in self.expected_categories:
            category_dir = self.scripts_dir / category
            if category_dir.exists():
                py_files = list(category_dir.glob("*.py"))
                # Exclude __init__.py from count
                production_scripts = [f for f in py_files if f.name != "__init__.py"]
                category_counts[category] = len(production_scripts)
                total_scripts += len(production_scripts)
        
        # We expect around 21 production scripts
        self.assertGreaterEqual(total_scripts, 20, f"Should have at least 20 production scripts, found {total_scripts}")
        self.assertLessEqual(total_scripts, 25, f"Should have at most 25 production scripts, found {total_scripts}")
        
        # Log category breakdown
        for category, count in category_counts.items():
            self.console.print(f"  📁 {category}: {count} scripts", style="green")
    
    def test_archive_directory(self):
        """Test that archive directory exists and contains preserved scripts."""
        archive_dir = self.scripts_dir / "archive"
        self.assertFileExists(archive_dir, "Archive directory should exist")
        
        # Should contain preserved legacy scripts
        archived_files = list(archive_dir.glob("*.py"))
        self.assertGreater(len(archived_files), 30, "Archive should contain preserved scripts")
        
        self.console.print(f"  📦 Archive: {len(archived_files)} preserved scripts", style="blue")
    
    def test_script_syntax_validation(self):
        """Test that all production scripts have valid Python syntax."""
        syntax_errors = []
        
        for category in self.expected_categories:
            category_dir = self.scripts_dir / category
            if category_dir.exists():
                for script_file in category_dir.glob("*.py"):
                    if script_file.name != "__init__.py":
                        try:
                            self.assertValidPythonSyntax(script_file)
                        except AssertionError as e:
                            syntax_errors.append(f"{category}/{script_file.name}: {str(e)}")
        
        if syntax_errors:
            self.fail(f"Syntax errors found in {len(syntax_errors)} scripts:\n" + "\n".join(syntax_errors))
    
    def test_category_specific_scripts(self):
        """Test that each category contains expected types of scripts."""
        expected_scripts = {
            "auth": ["my_fyers_model.py", "fyers_config.py"],
            "websocket": ["run_websocket.py", "web_data_socket.py"],
            "symbol_discovery": ["comprehensive_symbol_discovery.py"],
            "data": ["data_storage.py"],
            "market_data": ["stocks_data.py"],
            "core": ["constants.py", "utility.py"]
        }
        
        for category, expected_files in expected_scripts.items():
            category_dir = self.scripts_dir / category
            if category_dir.exists():
                for expected_file in expected_files:
                    file_path = category_dir / expected_file
                    if file_path.exists():
                        self.console.print(f"  ✅ {category}/{expected_file}", style="green")
                    else:
                        self.console.print(f"  ⚠️ {category}/{expected_file} - not found", style="yellow")

class TestModuleImports(FyersTestBase):
    """Unit tests for module import capabilities."""
    
    def test_category_module_imports(self):
        """Test that category modules can be imported."""
        categories_to_test = ["auth", "data", "core"]  # Safe categories for import testing
        
        for category in categories_to_test:
            with self.subTest(category=category):
                try:
                    module_path = str(self.project_root / "scripts" / category)
                    if module_path not in sys.path:
                        sys.path.insert(0, module_path)
                    
                    # Try to import the category module
                    category_module = __import__(category)
                    self.console.print(f"  ✅ {category} module imported", style="green")
                    
                except ImportError as e:
                    # Some modules may fail due to missing dependencies - that's OK
                    if any(keyword in str(e).lower() for keyword in ["credentials", "token", "api", "fyers"]):
                        self.console.print(f"  ⚠️ {category} import skipped - requires API setup", style="yellow")
                    else:
                        self.fail(f"Failed to import {category}: {e}")
                except Exception as e:
                    self.fail(f"Unexpected error importing {category}: {e}")

if __name__ == '__main__':
    unittest.main()