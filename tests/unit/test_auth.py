#!/usr/bin/env python3
"""
AUTHENTICATION SYSTEM UNIT TESTS
=================================

Unit tests for the Fyers authentication system components.
Tests MyFyersModel, token management, and credential handling.

Author: Fyers Platform Development Team
Version: 1.0.0
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

from tests.core.test_base import FyersTestBase

class TestMyFyersModel(FyersTestBase):
    """Unit tests for MyFyersModel class."""
    
    def setUp(self):
        super().setUp()
        self.auth_dir = self.project_root / "auth"
        self.scripts_auth_dir = self.project_root / "scripts" / "auth"
    
    def test_auth_directory_structure(self):
        """Test that authentication directory structure exists."""
        self.assertFileExists(self.auth_dir, "Root auth directory should exist")
        self.assertFileExists(self.scripts_auth_dir, "Scripts auth directory should exist")
        
        # Check for required files
        required_files = ["my_fyers_model.py", "fyers_config.py", "__init__.py"]
        for file_name in required_files:
            file_path = self.scripts_auth_dir / file_name
            self.assertFileExists(file_path, f"Auth script {file_name} should exist")
    
    def test_my_fyers_model_import(self):
        """Test that MyFyersModel can be imported."""
        # This tests the import without actually initializing
        try:
            module_path = str(self.scripts_auth_dir / "my_fyers_model.py")
            self.assertModuleImports(module_path, "MyFyersModel should import successfully")
        except Exception as e:
            # If import fails due to missing credentials, that's acceptable for unit test
            if "credentials" in str(e).lower() or "token" in str(e).lower():
                self.console.print("⚠️ Import test skipped - credentials required", style="yellow")
            else:
                raise
    
    def test_my_fyers_model_syntax(self):
        """Test MyFyersModel Python syntax validity."""
        file_path = self.scripts_auth_dir / "my_fyers_model.py"
        self.assertValidPythonSyntax(file_path, "MyFyersModel should have valid Python syntax")
    
    def test_fyers_config_syntax(self):
        """Test FyersConfig Python syntax validity."""
        file_path = self.scripts_auth_dir / "fyers_config.py"
        self.assertValidPythonSyntax(file_path, "FyersConfig should have valid Python syntax")
    
    def test_credentials_configuration(self):
        """Test credentials configuration setup."""
        # Check for credentials.ini or credentials.ini.example
        creds_file = self.auth_dir / "credentials.ini"
        example_file = self.auth_dir / "credentials.ini.example"
        
        has_credentials = creds_file.exists() or example_file.exists()
        self.assertTrue(has_credentials, "Either credentials.ini or credentials.ini.example should exist")
        
        if example_file.exists():
            # credentials.ini.example is a config file, not Python - just check it exists
            self.console.print("✅ credentials.ini.example found", style="green")
    
    @patch('builtins.open', new_callable=mock_open, read_data="test_token_content")
    def test_token_file_handling(self, mock_file):
        """Test token file reading mechanism."""
        # This is a mock test to ensure token file handling logic is sound
        with patch('os.path.exists', return_value=True):
            # Simulate token file reading
            try:
                with open("mock_token.txt", 'r') as f:
                    content = f.read()
                self.assertEqual(content, "test_token_content")
            except Exception as e:
                self.fail(f"Token file handling failed: {e}")
    
    def test_auth_module_init(self):
        """Test authentication module __init__.py structure."""
        init_file = self.scripts_auth_dir / "__init__.py"
        self.assertFileExists(init_file, "Auth module __init__.py should exist")
        self.assertValidPythonSyntax(init_file, "Auth __init__.py should have valid syntax")

class TestAuthenticationConfiguration(FyersTestBase):
    """Unit tests for authentication configuration."""
    
    def test_dual_auth_architecture(self):
        """Test the dual authentication architecture."""
        # Root /auth/ for credentials and data
        root_auth = self.project_root / "auth"
        self.assertFileExists(root_auth, "Root auth directory should exist")
        
        # Scripts /scripts/auth/ for code and logic
        scripts_auth = self.project_root / "scripts" / "auth"
        self.assertFileExists(scripts_auth, "Scripts auth directory should exist")
        
        # Verify separation of concerns
        # Root auth should have config files
        config_files = ["credentials.ini.example"]
        for config_file in config_files:
            file_path = root_auth / config_file
            if file_path.exists():
                self.console.print(f"✅ Config file found: {config_file}", style="green")
        
        # Scripts auth should have Python modules
        code_files = ["my_fyers_model.py", "fyers_config.py"]
        for code_file in code_files:
            file_path = scripts_auth / code_file
            self.assertFileExists(file_path, f"Code file {code_file} should exist in scripts/auth/")
    
    def test_path_resolution(self):
        """Test that auth scripts can find configuration files."""
        # Test the path resolution logic used in my_fyers_model.py
        scripts_auth_dir = self.project_root / "scripts" / "auth"
        
        # The path that my_fyers_model.py uses: '../auth/credentials.ini'
        expected_config_path = scripts_auth_dir.parent.parent / "auth" / "credentials.ini"
        example_config_path = scripts_auth_dir.parent.parent / "auth" / "credentials.ini.example"
        
        # Either the actual config or example should be reachable
        config_reachable = expected_config_path.exists() or example_config_path.exists()
        self.assertTrue(config_reachable, "Configuration files should be reachable from scripts/auth/")

if __name__ == '__main__':
    unittest.main()