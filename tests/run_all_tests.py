#!/usr/bin/env python3
"""
MASTER TEST EXECUTION
====================

Main entry point for running the complete Fyers platform test suite.
Executes comprehensive validation, testing, and reporting.

Usage:
    python run_all_tests.py                    # Run all tests
    python run_all_tests.py --validation-only  # System validation only
    python run_all_tests.py --quick            # Quick validation suite
    python run_all_tests.py --report           # Generate detailed reports

Author: Fyers Platform Development Team
Version: 1.0.0
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Rich imports
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

# Import our test framework
from tests.core.test_runner import EnterpriseTestRunner
from tests.core.test_validator import SystemValidator

def main():
    """Main test execution function."""
    parser = argparse.ArgumentParser(description="Fyers Platform Test Suite")
    parser.add_argument("--validation-only", action="store_true", 
                       help="Run system validation only")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick validation suite")
    parser.add_argument("--report", action="store_true",
                       help="Generate detailed reports")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    console = Console()
    
    # Display startup banner
    display_startup_banner(console)
    
    try:
        if args.validation_only:
            run_system_validation_only(console)
        elif args.quick:
            run_quick_validation(console)
        else:
            run_complete_test_suite(console, generate_reports=args.report)
            
    except KeyboardInterrupt:
        console.print("\n⚠️ Test execution interrupted by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Test execution failed: {str(e)}", style="red")
        sys.exit(1)

def display_startup_banner(console: Console):
    """Display startup banner."""
    banner_text = Text()
    banner_text.append("🧪 FYERS ENTERPRISE TEST SUITE\n", style="bold blue")
    banner_text.append("Algorithmic Trading Platform Validation\n\n", style="cyan")
    banner_text.append("📊 Platform Features:\n", style="yellow")
    banner_text.append("  • 156,586 Symbol Universe (NSE/BSE/MCX)\n", style="white")
    banner_text.append("  • 21 Production Scripts Organized\n", style="white")
    banner_text.append("  • Real-time WebSocket Streaming\n", style="white")
    banner_text.append("  • Enterprise-grade Architecture\n", style="white")
    banner_text.append("  • Comprehensive Testing Framework\n\n", style="white")
    banner_text.append(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
    
    panel = Panel.fit(banner_text, title="Test Suite Initialization", border_style="blue")
    console.print(panel)

def run_system_validation_only(console: Console):
    """Run system validation only."""
    console.print("\n🔍 Running System Validation Only", style="bold cyan")
    
    validator = SystemValidator(console)
    results = validator.run_complete_validation()
    
    # Generate validation report
    report_file = validator.generate_validation_report()
    
    console.print(f"\n✅ System validation completed", style="green")
    console.print(f"📋 Report: {report_file.relative_to(project_root)}", style="blue")

def run_quick_validation(console: Console):
    """Run quick validation suite."""
    console.print("\n⚡ Running Quick Validation Suite", style="bold yellow")
    
    # Quick system check
    validator = SystemValidator(console)
    console.print("\n🔍 System Health Check", style="cyan")
    
    quick_validations = [
        validator.validate_python_environment(),
        validator.validate_directory_structure(),
        validator.validate_production_scripts(),
    ]
    
    validator.validation_results = quick_validations
    summary = validator.display_validation_summary()
    
    # Quick script import test
    console.print("\n📦 Quick Import Test", style="cyan")
    runner = EnterpriseTestRunner(console)
    
    # Test just a few key imports
    key_scripts = [
        project_root / "scripts" / "auth" / "my_fyers_model.py",
        project_root / "scripts" / "symbol_discovery" / "comprehensive_symbol_discovery.py",
        project_root / "scripts" / "data" / "data_storage.py"
    ]
    
    import_results = []
    for script in key_scripts:
        if script.exists():
            try:
                # Quick syntax check
                with open(script, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(script), 'exec')
                console.print(f"  ✅ {script.name}", style="green")
                import_results.append(True)
            except Exception as e:
                console.print(f"  ❌ {script.name}: {str(e)}", style="red")
                import_results.append(False)
    
    success_rate = (sum(import_results) / len(import_results)) * 100
    console.print(f"\n⚡ Quick validation completed: {success_rate:.0f}% success rate", 
                 style="green" if success_rate > 80 else "yellow")

def run_complete_test_suite(console: Console, generate_reports: bool = True):
    """Run the complete test suite."""
    console.print("\n🚀 Running Complete Test Suite", style="bold green")
    
    # Phase 1: System Validation
    console.print("\n" + "="*60, style="blue")
    console.print("PHASE 1: SYSTEM VALIDATION", style="bold blue")
    console.print("="*60, style="blue")
    
    validator = SystemValidator(console)
    validation_results = validator.run_complete_validation()
    
    # Check if system is healthy enough to continue
    failed_validations = [r for r in validation_results if r.status == "failed"]
    if failed_validations:
        console.print(f"\n⚠️ System validation found {len(failed_validations)} critical issues", style="yellow")
        console.print("Continuing with test execution...", style="dim")
    
    # Phase 2: Comprehensive Testing
    console.print("\n" + "="*60, style="blue")
    console.print("PHASE 2: COMPREHENSIVE TESTING", style="bold blue")
    console.print("="*60, style="blue")
    
    runner = EnterpriseTestRunner(console)
    test_results = runner.run_complete_test_suite()
    
    # Phase 3: Final Summary
    console.print("\n" + "="*60, style="green")
    console.print("EXECUTION SUMMARY", style="bold green")
    console.print("="*60, style="green")
    
    # Combined results summary
    total_validations = len(validation_results)
    total_tests = len(test_results)
    
    validation_passed = len([r for r in validation_results if r.status == "passed"])
    tests_passed = len([r for r in test_results if r.status == "passed"])
    
    overall_success_rate = ((validation_passed + tests_passed) / (total_validations + total_tests)) * 100
    
    summary_text = Text()
    summary_text.append("🎯 EXECUTION COMPLETE\n\n", style="bold green")
    summary_text.append(f"📊 System Validations: {validation_passed}/{total_validations} passed\n", style="cyan")
    summary_text.append(f"🧪 Test Executions: {tests_passed}/{total_tests} passed\n", style="cyan")
    summary_text.append(f"📈 Overall Success Rate: {overall_success_rate:.1f}%\n\n", style="yellow")
    
    if overall_success_rate >= 90:
        summary_text.append("🏆 EXCELLENT - Platform ready for production!", style="bold green")
    elif overall_success_rate >= 75:
        summary_text.append("✅ GOOD - Platform ready with minor issues", style="green") 
    elif overall_success_rate >= 60:
        summary_text.append("⚠️ ACCEPTABLE - Review failed tests", style="yellow")
    else:
        summary_text.append("❌ ISSUES DETECTED - Address failures before deployment", style="red")
    
    summary_panel = Panel.fit(summary_text, title="Final Test Results", border_style="green")
    console.print(summary_panel)
    
    # Generate reports if requested
    if generate_reports:
        console.print("\n📋 Generating comprehensive reports...", style="blue")
        validation_report = validator.generate_validation_report()
        test_report = runner.generate_test_reports()
        
        console.print(f"✅ Validation report: {validation_report.name}", style="green")
        console.print(f"✅ Test report: {test_report.name}", style="green")

if __name__ == "__main__":
    main()