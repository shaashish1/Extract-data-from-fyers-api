#!/usr/bin/env python3
"""
SYSTEM VALIDATOR
===============

Comprehensive system validation for the Fyers Algorithmic Trading Platform.
Validates configuration, dependencies, file structure, and system health.

Author: Fyers Platform Development Team
Version: 1.0.0
"""

import os
import sys
import subprocess
import importlib
import platform
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Rich imports
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

@dataclass
class ValidationResult:
    """Validation result structure."""
    component: str
    status: str  # "passed", "failed", "warning"
    message: str
    details: str = ""
    timestamp: datetime = None

class SystemValidator:
    """
    Comprehensive system validator for the Fyers platform.
    
    Validates:
    - Python environment and dependencies
    - Project directory structure
    - Configuration files
    - Script organization and imports
    - Data directory structure
    - Git repository status
    - System requirements
    """
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.project_root = project_root
        self.validation_results: List[ValidationResult] = []
        
        # Expected project structure
        self.expected_structure = {
            "directories": [
                "auth", "data", "scripts", "samples", "tests", "logs",
                "data/parquet", "data/market_depth", 
                "scripts/auth", "scripts/websocket", "scripts/market_data",
                "scripts/symbol_discovery", "scripts/data", "scripts/core",
                "tests/unit", "tests/integration", "tests/fixtures", "tests/reports"
            ],
            "files": [
                "README.md", "requirements.txt", ".gitignore",
                "auth/credentials.ini.example", 
                "scripts/__init__.py",
                "tests/__init__.py"
            ]
        }
        
        # Required Python packages
        self.required_packages = [
            "pandas", "numpy", "pyarrow", "requests", "configparser",
            "rich", "fyers-apiv3", "pytz", "websocket-client"
        ]
    
    def validate_python_environment(self) -> ValidationResult:
        """Validate Python version and environment."""
        try:
            python_version = platform.python_version()
            major, minor = map(int, python_version.split('.')[:2])
            
            if major >= 3 and minor >= 8:
                return ValidationResult(
                    component="Python Environment",
                    status="passed",
                    message=f"Python {python_version} - Compatible",
                    timestamp=datetime.now()
                )
            else:
                return ValidationResult(
                    component="Python Environment", 
                    status="warning",
                    message=f"Python {python_version} - Consider upgrading to 3.8+",
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            return ValidationResult(
                component="Python Environment",
                status="failed", 
                message=f"Failed to validate Python: {str(e)}",
                timestamp=datetime.now()
            )
    
    def validate_dependencies(self) -> ValidationResult:
        """Validate required Python packages."""
        missing_packages = []
        installed_packages = []
        
        for package in self.required_packages:
            try:
                importlib.import_module(package.replace('-', '_'))
                installed_packages.append(package)
            except ImportError:
                missing_packages.append(package)
        
        if not missing_packages:
            return ValidationResult(
                component="Dependencies",
                status="passed",
                message=f"All {len(self.required_packages)} required packages installed",
                details=f"Installed: {', '.join(installed_packages)}",
                timestamp=datetime.now()
            )
        else:
            return ValidationResult(
                component="Dependencies",
                status="failed",
                message=f"Missing packages: {', '.join(missing_packages)}",
                details=f"Install with: pip install {' '.join(missing_packages)}",
                timestamp=datetime.now()
            )
    
    def validate_directory_structure(self) -> ValidationResult:
        """Validate project directory structure."""
        missing_dirs = []
        existing_dirs = []
        
        for dir_path in self.expected_structure["directories"]:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                existing_dirs.append(dir_path)
            else:
                missing_dirs.append(dir_path)
        
        if not missing_dirs:
            return ValidationResult(
                component="Directory Structure",
                status="passed",
                message=f"All {len(self.expected_structure['directories'])} directories present",
                details=f"Validated: {len(existing_dirs)} directories",
                timestamp=datetime.now()
            )
        else:
            return ValidationResult(
                component="Directory Structure",
                status="warning",
                message=f"Missing directories: {', '.join(missing_dirs)}",
                details=f"Present: {len(existing_dirs)}, Missing: {len(missing_dirs)}",
                timestamp=datetime.now()
            )
    
    def validate_configuration_files(self) -> ValidationResult:
        """Validate configuration files."""
        config_status = []
        
        # Check credentials configuration
        auth_dir = self.project_root / "auth"
        if (auth_dir / "credentials.ini").exists():
            config_status.append("✅ credentials.ini found")
        elif (auth_dir / "credentials.ini.example").exists():
            config_status.append("⚠️ credentials.ini.example found (setup required)")
        else:
            config_status.append("❌ No credentials configuration found")
        
        # Check access token
        if (auth_dir / "access_token.txt").exists():
            config_status.append("✅ access_token.txt found")
        else:
            config_status.append("⚠️ access_token.txt not found (will be generated)")
        
        # Check requirements.txt
        if (self.project_root / "requirements.txt").exists():
            config_status.append("✅ requirements.txt found")
        else:
            config_status.append("⚠️ requirements.txt missing")
        
        failed_configs = [s for s in config_status if s.startswith("❌")]
        warning_configs = [s for s in config_status if s.startswith("⚠️")]
        
        if failed_configs:
            status = "failed"
            message = f"Critical configuration issues: {len(failed_configs)}"
        elif warning_configs:
            status = "warning"
            message = f"Configuration warnings: {len(warning_configs)}"
        else:
            status = "passed"
            message = "All configuration files validated"
        
        return ValidationResult(
            component="Configuration Files",
            status=status,
            message=message,
            details="\n".join(config_status),
            timestamp=datetime.now()
        )
    
    def validate_production_scripts(self) -> ValidationResult:
        """Validate production script organization."""
        scripts_dir = self.project_root / "scripts"
        expected_categories = ["auth", "websocket", "market_data", "symbol_discovery", "data", "core"]
        
        script_count = 0
        category_status = []
        
        for category in expected_categories:
            category_dir = scripts_dir / category
            if category_dir.exists():
                py_files = list(category_dir.glob("*.py"))
                # Exclude __init__.py from count
                actual_scripts = [f for f in py_files if f.name != "__init__.py"]
                script_count += len(actual_scripts)
                category_status.append(f"✅ {category}: {len(actual_scripts)} scripts")
            else:
                category_status.append(f"❌ {category}: directory missing")
        
        # Check for archive directory
        archive_dir = scripts_dir / "archive"
        if archive_dir.exists():
            archived_files = list(archive_dir.glob("*.py"))
            category_status.append(f"📁 archive: {len(archived_files)} preserved scripts")
        
        if script_count >= 20:  # Expected ~21 production scripts
            status = "passed"
            message = f"Production scripts organized: {script_count} scripts"
        else:
            status = "warning"
            message = f"Script organization incomplete: {script_count} scripts found"
        
        return ValidationResult(
            component="Production Scripts",
            status=status,
            message=message,
            details="\n".join(category_status),
            timestamp=datetime.now()
        )
    
    def validate_data_structure(self) -> ValidationResult:
        """Validate data directory structure and files."""
        data_dir = self.project_root / "data"
        data_status = []
        
        # Check parquet directory
        parquet_dir = data_dir / "parquet"
        if parquet_dir.exists():
            subdirs = ["symbols", "fyers_symbols"]
            for subdir in subdirs:
                subdir_path = parquet_dir / subdir
                if subdir_path.exists():
                    files = list(subdir_path.glob("*.json"))
                    data_status.append(f"✅ {subdir}: {len(files)} files")
                else:
                    data_status.append(f"⚠️ {subdir}: directory missing")
        else:
            data_status.append("❌ parquet directory missing")
        
        # Check market_depth directory
        depth_dir = data_dir / "market_depth"
        if depth_dir.exists():
            depth_files = list(depth_dir.glob("*.json"))
            data_status.append(f"✅ market_depth: {len(depth_files)} files")
        else:
            data_status.append("⚠️ market_depth: directory missing")
        
        failed_items = [s for s in data_status if s.startswith("❌")]
        if failed_items:
            status = "warning"
            message = f"Data structure issues: {len(failed_items)}"
        else:
            status = "passed"
            message = "Data structure validated"
        
        return ValidationResult(
            component="Data Structure",
            status=status,
            message=message,
            details="\n".join(data_status),
            timestamp=datetime.now()
        )
    
    def validate_samples_framework(self) -> ValidationResult:
        """Validate samples testing framework."""
        samples_dir = self.project_root / "samples"
        
        if not samples_dir.exists():
            return ValidationResult(
                component="Samples Framework",
                status="failed",
                message="Samples directory missing",
                timestamp=datetime.now()
            )
        
        # Check for master test runner
        master_runner = samples_dir / "run_tests.py"
        if not master_runner.exists():
            return ValidationResult(
                component="Samples Framework",
                status="warning",
                message="Master test runner missing",
                timestamp=datetime.now()
            )
        
        # Count sample categories
        sample_categories = []
        for item in samples_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                py_files = list(item.glob("**/*.py"))
                sample_categories.append(f"{item.name}: {len(py_files)} samples")
        
        return ValidationResult(
            component="Samples Framework",
            status="passed",
            message=f"Samples framework validated: {len(sample_categories)} categories",
            details="\n".join(sample_categories),
            timestamp=datetime.now()
        )
    
    def validate_git_status(self) -> ValidationResult:
        """Validate Git repository status."""
        try:
            # Check if git is available
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            
            # Check if we're in a git repository
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                if result.stdout.strip():
                    return ValidationResult(
                        component="Git Repository",
                        status="warning",
                        message="Uncommitted changes detected",
                        details="Run 'git status' to see changes",
                        timestamp=datetime.now()
                    )
                else:
                    return ValidationResult(
                        component="Git Repository",
                        status="passed",
                        message="Repository clean - all changes committed",
                        timestamp=datetime.now()
                    )
            else:
                return ValidationResult(
                    component="Git Repository",
                    status="warning",
                    message="Not a git repository or git error",
                    timestamp=datetime.now()
                )
                
        except FileNotFoundError:
            return ValidationResult(
                component="Git Repository",
                status="warning",
                message="Git not installed or not in PATH",
                timestamp=datetime.now()
            )
        except Exception as e:
            return ValidationResult(
                component="Git Repository",
                status="warning",
                message=f"Git validation failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    def run_complete_validation(self) -> List[ValidationResult]:
        """Run complete system validation."""
        self.console.print("🔍 Starting System Validation", style="bold blue")
        self.console.print("=" * 50, style="blue")
        
        validations = [
            ("Python Environment", self.validate_python_environment),
            ("Dependencies", self.validate_dependencies),
            ("Directory Structure", self.validate_directory_structure),
            ("Configuration Files", self.validate_configuration_files),
            ("Production Scripts", self.validate_production_scripts),
            ("Data Structure", self.validate_data_structure),
            ("Samples Framework", self.validate_samples_framework),
            ("Git Repository", self.validate_git_status)
        ]
        
        with Progress(console=self.console) as progress:
            task = progress.add_task("Validating system components...", total=len(validations))
            
            for name, validation_func in validations:
                self.console.print(f"\n🔍 Validating: {name}", style="cyan")
                result = validation_func()
                self.validation_results.append(result)
                
                # Display immediate result
                status_style = "green" if result.status == "passed" else "yellow" if result.status == "warning" else "red"
                status_icon = "✅" if result.status == "passed" else "⚠️" if result.status == "warning" else "❌"
                
                self.console.print(f"  {status_icon} {result.message}", style=status_style)
                if result.details:
                    for detail in result.details.split('\n'):
                        if detail.strip():
                            self.console.print(f"    {detail}", style="dim")
                
                progress.update(task, advance=1)
        
        self.display_validation_summary()
        return self.validation_results
    
    def display_validation_summary(self):
        """Display validation summary."""
        # Count results by status
        passed = len([r for r in self.validation_results if r.status == "passed"])
        warnings = len([r for r in self.validation_results if r.status == "warning"])
        failed = len([r for r in self.validation_results if r.status == "failed"])
        total = len(self.validation_results)
        
        # Create summary table
        table = Table(title="System Validation Summary")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Message", style="white")
        
        for result in self.validation_results:
            status_icon = "✅" if result.status == "passed" else "⚠️" if result.status == "warning" else "❌"
            status_text = f"{status_icon} {result.status.upper()}"
            table.add_row(result.component, status_text, result.message)
        
        self.console.print("\n")
        self.console.print(table)
        
        # Summary panel
        summary_text = Text()
        summary_text.append(f"📊 Total Validations: {total}\n", style="cyan")
        summary_text.append(f"✅ Passed: {passed}\n", style="green")
        summary_text.append(f"⚠️ Warnings: {warnings}\n", style="yellow")
        summary_text.append(f"❌ Failed: {failed}\n", style="red")
        
        if failed == 0:
            overall_status = "SYSTEM HEALTHY" if warnings == 0 else "SYSTEM READY (with warnings)"
            status_style = "green" if warnings == 0 else "yellow"
        else:
            overall_status = "SYSTEM ISSUES DETECTED"
            status_style = "red"
        
        summary_text.append(f"\n🎯 Overall Status: {overall_status}", style=status_style)
        
        summary_panel = Panel.fit(summary_text, title="Validation Summary", border_style=status_style)
        self.console.print("\n")
        self.console.print(summary_panel)
        
        return {
            "total": total,
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "overall_status": overall_status
        }
    
    def generate_validation_report(self) -> Path:
        """Generate detailed validation report."""
        reports_dir = self.project_root / "tests" / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"system_validation_{timestamp}.json"
        
        report_data = {
            "validation_info": {
                "timestamp": datetime.now().isoformat(),
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "project_root": str(self.project_root)
            },
            "validation_results": [
                {
                    "component": r.component,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None
                }
                for r in self.validation_results
            ],
            "summary": self.display_validation_summary()
        }
        
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.console.print(f"\n📋 Validation report saved: {report_file.relative_to(self.project_root)}", style="green")
        return report_file