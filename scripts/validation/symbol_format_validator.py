#!/usr/bin/env python3
"""
Symbol Format Validator
========================

Validates NSE official CSV symbols match FYERS exchange format.

Features:
- Compare NSE symbols with FYERS format
- Validate symbol conversion accuracy
- Report mismatches and issues
- Test live symbol quotes from FYERS API

Usage:
    python ../validation/symbol_format_validator.py

Author: Fyers Trading Platform
Created: October 30, 2025
"""

import sys
from pathlib import Path
import pandas as pd
from typing import List, Dict, Set, Tuple
import logging
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..auth.my_fyers_model import MyFyersModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/symbol_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
console = Console()


class SymbolFormatValidator:
    """
    Validates NSE symbols match FYERS exchange format
    """
    
    def __init__(self):
        self.base_path = Path('data/consolidated_symbols')
        self.fyers = None
        self.validation_results = {
            'total_symbols': 0,
            'valid_symbols': 0,
            'invalid_symbols': 0,
            'format_mismatches': [],
            'api_failures': [],
            'success_rate': 0.0
        }
    
    def _init_fyers(self):
        """Initialize Fyers API connection"""
        try:
            console.print("[yellow]Initializing Fyers API...[/yellow]")
            self.fyers = MyFyersModel()
            console.print("[green]✓ Fyers API initialized successfully[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Failed to initialize Fyers API: {e}[/red]")
            return False
    
    def load_nse_symbols(self, category: str = 'nifty50') -> List[str]:
        """
        Load NSE symbols from CSV
        
        Args:
            category: Symbol category (nifty50, all_equities, etfs, etc.)
        
        Returns:
            List of NSE symbol names
        """
        csv_file = self.base_path / f"{category}_symbols.csv"
        
        if not csv_file.exists():
            logger.error(f"CSV file not found: {csv_file}")
            return []
        
        try:
            df = pd.read_csv(csv_file)
            symbols = df['symbol'].tolist()
            logger.info(f"Loaded {len(symbols)} symbols from {category}")
            return symbols
        except Exception as e:
            logger.error(f"Error loading symbols from {csv_file}: {e}")
            return []
    
    def load_fyers_format_symbols(self, category: str = 'all_equities') -> List[str]:
        """
        Load FYERS format symbols from text file
        
        Args:
            category: Symbol category
        
        Returns:
            List of FYERS format symbols (NSE:SYMBOL-EQ)
        """
        txt_file = self.base_path / f"fyers_format_{category}.txt"
        
        if not txt_file.exists():
            logger.warning(f"FYERS format file not found: {txt_file}")
            return []
        
        try:
            with open(txt_file, 'r') as f:
                symbols = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(symbols)} FYERS format symbols")
            return symbols
        except Exception as e:
            logger.error(f"Error loading FYERS symbols from {txt_file}: {e}")
            return []
    
    def nse_to_fyers_format(self, nse_symbol: str, exchange: str = 'NSE', suffix: str = 'EQ') -> str:
        """
        Convert NSE symbol to FYERS format
        
        Args:
            nse_symbol: NSE symbol name
            exchange: Exchange code (NSE, BSE, MCX)
            suffix: Instrument suffix (EQ, FUT, etc.)
        
        Returns:
            FYERS format symbol (e.g., NSE:RELIANCE-EQ)
        """
        return f"{exchange}:{nse_symbol}-{suffix}"
    
    def validate_symbol_format(self, nse_symbols: List[str], fyers_symbols: List[str]) -> Dict:
        """
        Validate NSE symbols match FYERS format
        
        Args:
            nse_symbols: List of NSE symbols
            fyers_symbols: List of FYERS format symbols
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'total_nse': len(nse_symbols),
            'total_fyers': len(fyers_symbols),
            'matched': 0,
            'unmatched_nse': [],
            'unmatched_fyers': [],
            'format_correct': True
        }
        
        # Convert NSE symbols to FYERS format
        expected_fyers = {self.nse_to_fyers_format(sym) for sym in nse_symbols}
        actual_fyers = set(fyers_symbols)
        
        # Find matches and mismatches
        matched = expected_fyers & actual_fyers
        unmatched_nse = expected_fyers - actual_fyers
        unmatched_fyers = actual_fyers - expected_fyers
        
        results['matched'] = len(matched)
        results['unmatched_nse'] = sorted(list(unmatched_nse))
        results['unmatched_fyers'] = sorted(list(unmatched_fyers))
        results['match_percentage'] = (len(matched) / len(nse_symbols) * 100) if nse_symbols else 0
        
        return results
    
    def test_fyers_api_symbol(self, fyers_symbol: str) -> Tuple[bool, str]:
        """
        Test if symbol is valid by fetching quote from FYERS API
        
        Args:
            fyers_symbol: FYERS format symbol
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not self.fyers:
            if not self._init_fyers():
                return False, "Fyers API not initialized"
        
        try:
            # Get quote for symbol
            data = {"symbols": fyers_symbol}
            response = self.fyers.quotes(data)
            
            if response and response.get('s') == 'ok':
                quote_data = response.get('d', [{}])[0]
                if quote_data and 'v' in quote_data:
                    ltp = quote_data['v'].get('lp', 0)
                    return True, f"Valid - LTP: {ltp}"
                else:
                    return False, "No quote data returned"
            else:
                error_msg = response.get('message', 'Unknown error')
                return False, f"API error: {error_msg}"
        
        except Exception as e:
            return False, f"Exception: {str(e)}"
    
    def validate_sample_with_api(self, symbols: List[str], sample_size: int = 10) -> Dict:
        """
        Validate a sample of symbols using FYERS API
        
        Args:
            symbols: List of FYERS format symbols
            sample_size: Number of symbols to test
        
        Returns:
            Dictionary with validation results
        """
        if not self._init_fyers():
            return {'error': 'Failed to initialize Fyers API'}
        
        # Take sample
        import random
        sample = random.sample(symbols, min(sample_size, len(symbols)))
        
        results = {
            'total_tested': len(sample),
            'valid': 0,
            'invalid': 0,
            'details': []
        }
        
        console.print(f"\n[cyan]Testing {len(sample)} sample symbols with FYERS API...[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Validating symbols...", total=len(sample))
            
            for symbol in sample:
                is_valid, message = self.test_fyers_api_symbol(symbol)
                
                results['details'].append({
                    'symbol': symbol,
                    'valid': is_valid,
                    'message': message
                })
                
                if is_valid:
                    results['valid'] += 1
                else:
                    results['invalid'] += 1
                
                progress.update(task, advance=1)
                time.sleep(0.5)  # Rate limiting
        
        results['success_rate'] = (results['valid'] / results['total_tested'] * 100) if results['total_tested'] > 0 else 0
        
        return results
    
    def run_full_validation(self, category: str = 'nifty50', test_api: bool = True) -> Dict:
        """
        Run complete validation for a category
        
        Args:
            category: Symbol category to validate
            test_api: Whether to test symbols with API
        
        Returns:
            Complete validation results
        """
        console.print(f"\n[bold cyan]═══ Symbol Format Validation for {category.upper()} ═══[/bold cyan]\n")
        
        # Load NSE symbols
        console.print("[yellow]1. Loading NSE symbols from CSV...[/yellow]")
        nse_symbols = self.load_nse_symbols(category)
        console.print(f"[green]✓ Loaded {len(nse_symbols)} NSE symbols[/green]")
        
        # Load FYERS format symbols
        console.print("\n[yellow]2. Loading FYERS format symbols...[/yellow]")
        fyers_category = 'all_equities' if category not in ['all_equities', 'etfs'] else category
        fyers_symbols = self.load_fyers_format_symbols(fyers_category)
        console.print(f"[green]✓ Loaded {len(fyers_symbols)} FYERS format symbols[/green]")
        
        # Validate format matching
        console.print("\n[yellow]3. Validating symbol format conversion...[/yellow]")
        format_results = self.validate_symbol_format(nse_symbols, fyers_symbols)
        
        # Display format validation results
        table = Table(title="Format Validation Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total NSE Symbols", str(format_results['total_nse']))
        table.add_row("Total FYERS Symbols", str(format_results['total_fyers']))
        table.add_row("Matched Symbols", str(format_results['matched']))
        table.add_row("Match Percentage", f"{format_results['match_percentage']:.2f}%")
        table.add_row("Unmatched NSE", str(len(format_results['unmatched_nse'])))
        table.add_row("Unmatched FYERS", str(len(format_results['unmatched_fyers'])))
        
        console.print(table)
        
        # Show sample of unmatched symbols
        if format_results['unmatched_nse']:
            console.print("\n[yellow]Sample of unmatched NSE symbols (first 10):[/yellow]")
            for sym in format_results['unmatched_nse'][:10]:
                console.print(f"  • {sym}")
        
        # Test with API if requested
        api_results = None
        if test_api and fyers_symbols:
            console.print("\n[yellow]4. Testing sample symbols with FYERS API...[/yellow]")
            
            # Convert NSE to FYERS format for testing
            test_symbols = [self.nse_to_fyers_format(sym) for sym in nse_symbols[:10]]
            api_results = self.validate_sample_with_api(test_symbols, sample_size=min(10, len(test_symbols)))
            
            # Display API validation results
            api_table = Table(title="API Validation Results")
            api_table.add_column("Metric", style="cyan")
            api_table.add_column("Value", style="green")
            
            api_table.add_row("Total Tested", str(api_results['total_tested']))
            api_table.add_row("Valid Symbols", str(api_results['valid']))
            api_table.add_row("Invalid Symbols", str(api_results['invalid']))
            api_table.add_row("Success Rate", f"{api_results['success_rate']:.2f}%")
            
            console.print(api_table)
            
            # Show details
            console.print("\n[yellow]Sample validation details:[/yellow]")
            for detail in api_results['details'][:5]:
                status = "[green]✓[/green]" if detail['valid'] else "[red]✗[/red]"
                console.print(f"  {status} {detail['symbol']}: {detail['message']}")
        
        # Compile final results
        final_results = {
            'category': category,
            'format_validation': format_results,
            'api_validation': api_results,
            'overall_status': 'PASS' if format_results['match_percentage'] > 90 else 'FAIL'
        }
        
        # Overall summary
        console.print(f"\n[bold]{'='*60}[/bold]")
        if final_results['overall_status'] == 'PASS':
            console.print(f"[bold green]✓ VALIDATION PASSED - {format_results['match_percentage']:.2f}% match rate[/bold green]")
        else:
            console.print(f"[bold red]✗ VALIDATION FAILED - {format_results['match_percentage']:.2f}% match rate[/bold red]")
        console.print(f"[bold]{'='*60}[/bold]\n")
        
        return final_results


def main():
    """Main execution"""
    validator = SymbolFormatValidator()
    
    # Validate different categories
    categories = ['nifty50', 'nifty100', 'nifty200', 'etfs']
    
    all_results = {}
    
    for category in categories:
        try:
            results = validator.run_full_validation(category, test_api=(category == 'nifty50'))
            all_results[category] = results
        except Exception as e:
            console.print(f"[red]Error validating {category}: {e}[/red]")
            logger.error(f"Error validating {category}: {e}", exc_info=True)
    
    # Final summary
    console.print("\n[bold cyan]═══ OVERALL VALIDATION SUMMARY ═══[/bold cyan]\n")
    
    summary_table = Table()
    summary_table.add_column("Category", style="cyan")
    summary_table.add_column("NSE Symbols", style="yellow")
    summary_table.add_column("Match %", style="green")
    summary_table.add_column("Status", style="bold")
    
    for category, results in all_results.items():
        if 'format_validation' in results:
            fmt = results['format_validation']
            status = "✓ PASS" if results['overall_status'] == 'PASS' else "✗ FAIL"
            status_style = "green" if results['overall_status'] == 'PASS' else "red"
            
            summary_table.add_row(
                category.upper(),
                str(fmt['total_nse']),
                f"{fmt['match_percentage']:.2f}%",
                f"[{status_style}]{status}[/{status_style}]"
            )
    
    console.print(summary_table)
    console.print()


if __name__ == '__main__':
    main()
