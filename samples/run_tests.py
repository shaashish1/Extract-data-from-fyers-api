
# Add scripts directory to path for authentication
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from auth.my_fyers_model import MyFyersModel

#!/usr/bin/env python3
"""
🧪 Fyers WebSocket Live - Master Test Runner
==========================================

Comprehensive test suite runner for all FYERS API functionality.
Runs authentication, API, and WebSocket tests in sequence with
professional reporting and recommendations.

Author: Fyers WebSocket Live Project
Date: October 27, 2025
"""

import sys
import os
import subprocess
import importlib.util
from datetime import datetime
from pathlib import Path

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.prompt import Confirm
from rich.layout import Layout
import time

# Initialize Rich console
console = Console()

class MasterTestRunner:
    def __init__(self):
        """Initialize the master test runner."""
        self.samples_dir = Path(__file__).parent
        self.results = {}
        self.start_time = datetime.now()
        
    def run_authentication_test(self):
        """Test MyFyersModel authentication system."""
        console.print("🔐 Testing MyFyersModel Authentication...", style="blue")
        
        try:
            # Test our existing authentication system
            from scripts.auth.my_fyers_model import MyFyersModel
            
            # Initialize Fyers model (will auto-load token)
            fyers = MyFyersModel()
            
            # Test with a simple API call
            profile = fyers.get_profile()
            
            if profile and profile.get('s') == 'ok':
                return True, "MyFyersModel authentication working"
            else:
                return False, "Authentication failed - invalid token or credentials"
            
        except Exception as e:
            return False, f"Authentication test failed: {str(e)}"
    
    def run_api_test(self):
        """Run market data API test programmatically."""
        console.print("📊 Running Market Data API Test...", style="blue")
        
        try:
            # Import and run API tester
            api_file = self.samples_dir / "market_data" / "api_testing_suite.py"
            spec = importlib.util.spec_from_file_location("api_tester", api_file)
            api_module = importlib.util.module_from_spec(spec)
            
            sys.path.insert(0, str(api_file.parent))
            spec.loader.exec_module(api_module)
            
            # Run comprehensive test
            tester = api_module.MarketDataTester()
            result = tester.run_comprehensive_test()
            
            return result, "All API endpoints working"
            
        except Exception as e:
            return False, f"API test failed: {str(e)}"
    
    def run_websocket_test(self, duration=2):
        """Run basic WebSocket test programmatically."""
        console.print("⚡ Running WebSocket Streaming Test...", style="blue")
        
        try:
            # Import and run WebSocket tester
            ws_file = self.samples_dir / "websocket" / "basic_streaming_test.py"
            spec = importlib.util.spec_from_file_location("ws_tester", ws_file)
            ws_module = importlib.util.module_from_spec(spec)
            
            sys.path.insert(0, str(ws_file.parent))
            spec.loader.exec_module(ws_module)
            
            # Run WebSocket test with short duration
            tester = ws_module.EnhancedWebSocketTest()
            result = tester.run_test(duration_minutes=duration)
            
            return result, f"WebSocket streaming for {duration} minutes successful"
            
        except Exception as e:
            return False, f"WebSocket test failed: {str(e)}"
    
    def run_symbol_discovery_test(self):
        """Test symbol discovery system."""
        console.print("🔍 Testing Symbol Discovery System...", style="blue")
        
        try:
            # Import symbol discovery
            from scripts.symbol_discovery.comprehensive_symbol_discovery import ComprehensiveFyersDiscovery
            from scripts.auth.my_fyers_model import MyFyersModel
            
            # Test discovery
            fyers = MyFyersModel()
            discovery = ComprehensiveFyersDiscovery()
            
            # Quick test with limited symbols
            categories, df, all_symbols = discovery.discover_complete_universe()
            
            if len(all_symbols) > 100:
                return True, f"Symbol discovery working - found {len(all_symbols)} symbols"
            else:
                return False, "Symbol discovery found too few symbols"
                
        except Exception as e:
            return False, f"Symbol discovery test failed: {str(e)}"
    
    def create_test_report(self):
        """Create comprehensive test report."""
        runtime = datetime.now() - self.start_time
        
        # Overall status
        all_passed = all(result[0] for result in self.results.values())
        passed_count = sum(1 for result in self.results.values() if result[0])
        total_tests = len(self.results)
        
        # Create report table
        report_table = Table(title="🧪 Fyers WebSocket Live - Test Report")
        report_table.add_column("Test Component", style="cyan", width=25)
        report_table.add_column("Status", style="white", width=12)
        report_table.add_column("Result", style="blue", width=40)
        report_table.add_column("Details", style="yellow")
        
        for test_name, (passed, message) in self.results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            status_style = "green" if passed else "red"
            
            report_table.add_row(
                test_name,
                status,
                "Success" if passed else "Failed",
                message,
                style=status_style
            )
        
        # Summary statistics
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Total Tests", str(total_tests))
        stats_table.add_row("Passed", str(passed_count))
        stats_table.add_row("Failed", str(total_tests - passed_count))
        stats_table.add_row("Success Rate", f"{(passed_count/total_tests)*100:.1f}%")
        stats_table.add_row("Runtime", str(runtime).split('.')[0])
        stats_table.add_row("Test Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Overall result
        if all_passed:
            overall_status = "🎉 ALL TESTS PASSED"
            overall_style = "bold green"
            recommendation = "✅ Your FYERS WebSocket Live system is ready for production!"
        elif passed_count >= total_tests * 0.75:
            overall_status = "⚠️ MOST TESTS PASSED" 
            overall_style = "bold yellow"
            recommendation = "⚠️ Review failed tests before production use"
        else:
            overall_status = "❌ MULTIPLE FAILURES"
            overall_style = "bold red"
            recommendation = "❌ Fix critical issues before proceeding"
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(Panel(stats_table, title="📊 Test Statistics", border_style="blue"), size=8),
            Layout(report_table)
        )
        
        console.print(layout)
        console.print(f"\n{overall_status}", style=overall_style)
        console.print(f"{recommendation}", style=overall_style.replace("bold ", ""))
        
        return all_passed
    
    def run_comprehensive_tests(self):
        """Run all tests in sequence."""
        console.print("\n🚀 [bold blue]Fyers WebSocket Live - Comprehensive Test Suite[/bold blue]")
        console.print("Running complete system verification...\n")
        
        tests = [
            ("Authentication System", self.run_authentication_test, {}),
            ("Market Data APIs", self.run_api_test, {}),
            ("Symbol Discovery", self.run_symbol_discovery_test, {}),
            ("WebSocket Streaming", self.run_websocket_test, {"duration": 1})
        ]
        
        with Progress(console=console) as progress:
            main_task = progress.add_task("Running Tests...", total=len(tests))
            
            for test_name, test_func, kwargs in tests:
                progress.update(main_task, description=f"Running {test_name}...")
                
                try:
                    result, message = test_func(**kwargs)
                    self.results[test_name] = (result, message)
                    
                    status = "✅" if result else "❌"
                    console.print(f"{status} {test_name}: {message}", 
                                style="green" if result else "red")
                    
                except Exception as e:
                    self.results[test_name] = (False, f"Test error: {str(e)}")
                    console.print(f"❌ {test_name}: Test error", style="red")
                
                progress.advance(main_task)
                time.sleep(0.5)
        
        # Generate report
        console.print("\n" + "="*80)
        success = self.create_test_report()
        
        # Recommendations
        console.print("\n📋 [bold blue]Next Steps:[/bold blue]")
        
        if success:
            console.print("1. 🎯 [green]Run production scripts in scripts/ directory[/green]")
            console.print("2. 🔍 [green]Execute comprehensive symbol discovery (156K+ symbols)[/green]") 
            console.print("3. ⚡ [green]Start live WebSocket streaming for your portfolio[/green]")
            console.print("4. 📊 [green]Build custom analytics using the data storage system[/green]")
        else:
            console.print("1. 🔧 [yellow]Fix failed tests using individual sample scripts[/yellow]")
            console.print("2. 🔐 [yellow]Check credentials.ini and access_token.txt for auth issues[/yellow]")
            console.print("3. 📊 [yellow]Run samples/market_data/api_testing_suite.py for API issues[/yellow]")
            console.print("4. ⚡ [yellow]Test WebSocket with samples/websocket/basic_streaming_test.py[/yellow]")
        
        return success
    
    def run_interactive_mode(self):
        """Run tests in interactive mode with user choices."""
        console.print("""
        🧪 [bold blue]Fyers WebSocket Live - Interactive Test Suite[/bold blue]
        
        Choose your testing approach:
        • Quick comprehensive test (recommended for first-time setup)
        • Individual component testing (for troubleshooting)
        • Custom test configuration
        
        """)
        
        while True:
            console.print("\n📋 [bold blue]Test Options:[/bold blue]")
            console.print("1. 🚀 Run Complete Test Suite (Recommended)")
            console.print("2. 🔐 Authentication Test Only")
            console.print("3. 📊 Market Data API Test Only") 
            console.print("4. ⚡ WebSocket Streaming Test Only")
            console.print("5. 🔍 Symbol Discovery Test Only")
            console.print("6. 📚 Open Sample Scripts Guide")
            console.print("7. 🚪 Exit")
            
            from rich.prompt import Prompt
            choice = Prompt.ask("Enter your choice", choices=["1","2","3","4","5","6","7"], default="1")
            
            try:
                if choice == "1":
                    return self.run_comprehensive_tests()
                    
                elif choice == "2":
                    result, message = self.run_authentication_test()
                    console.print(f"Result: {message}", style="green" if result else "red")
                    
                elif choice == "3":
                    result, message = self.run_api_test()
                    console.print(f"Result: {message}", style="green" if result else "red")
                    
                elif choice == "4":
                    duration = int(Prompt.ask("Test duration (minutes)", default="2"))
                    result, message = self.run_websocket_test(duration)
                    console.print(f"Result: {message}", style="green" if result else "red")
                    
                elif choice == "5":
                    result, message = self.run_symbol_discovery_test()
                    console.print(f"Result: {message}", style="green" if result else "red")
                    
                elif choice == "6":
                    readme_path = self.samples_dir / "README.md"
                    console.print(f"📚 Sample guide: {readme_path}")
                    console.print("Open the README.md file for detailed instructions!")
                    
                elif choice == "7":
                    console.print("👋 Goodbye!", style="blue")
                    return True
                    
            except KeyboardInterrupt:
                console.print("\n⏹️ Test interrupted", style="yellow")
            except Exception as e:
                console.print(f"\n❌ Test error: {str(e)}", style="red")

def main():
    """Main function to run the test suite."""
    runner = MasterTestRunner()
    
    # Check if running with arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Automated mode
        success = runner.run_comprehensive_tests()
        sys.exit(0 if success else 1)
    else:
        # Interactive mode
        runner.run_interactive_mode()

if __name__ == "__main__":
    main()