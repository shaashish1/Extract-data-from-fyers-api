#!/usr/bin/env python3
"""
Symbol Format Validator
========================

Validates that NSE official CSV symbols match FYERS exchange format.

This script:
1. Loads NSE symbols from consolidated_symbols/*.csv
2. Converts them to FYERS format (NSE:SYMBOL-EQ)
3. Validates against FYERS API by fetching quotes
4. Reports mismatches and validation results

Usage:
    python ../validation/validate_symbol_formats.py
    python ../validation/validate_symbol_formats.py --category nifty50
    python ../validation/validate_symbol_formats.py --sample 10

Author: Fyers Trading Platform
Created: October 30, 2025
"""

import sys
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
import time
import argparse
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ..auth.my_fyers_model import MyFyersModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()


class SymbolFormatValidator:
    """
    Validates NSE symbols against FYERS format
    """
    
    def __init__(self):
        self.fyers = MyFyersModel()
        self.consolidated_path = project_root / 'data' / 'consolidated_symbols'
        self.results = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'errors': []
        }
    
    def nse_to_fyers_format(self, nse_symbol: str) -> str:
        """
        Convert NSE symbol to FYERS format
        
        Args:
            nse_symbol: NSE symbol (e.g., 'RELIANCE', 'BAJAJ-AUTO')
        
        Returns:
            FYERS format symbol (e.g., 'NSE:RELIANCE-EQ', 'NSE:BAJAJ-AUTO-EQ')
        """
        return f"NSE:{nse_symbol}-EQ"
    
    def validate_symbol_with_fyers(self, fyers_symbol: str) -> Tuple[bool, str]:
        """
        Validate symbol by fetching quote from FYERS API
        
        Args:
            fyers_symbol: FYERS format symbol
        
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            data = {
                "symbols": fyers_symbol
            }
            response = self.fyers.quotes(data)
            
            if response and 'd' in response:
                symbol_data = response['d'][0]
                
                # Check if we got valid data
                if 'v' in symbol_data and 'lp' in symbol_data['v']:
                    return True, f"Valid - LTP: {symbol_data['v']['lp']}"
                else:
                    return False, "No price data available"
            else:
                return False, "Invalid response from FYERS"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def load_symbols_from_csv(self, csv_file: Path) -> List[str]:
        """
        Load symbols from CSV file
        
        Args:
            csv_file: Path to CSV file
        
        Returns:
            List of symbol names
        """
        try:
            df = pd.read_csv(csv_file)
            
            # Try different column names
            if 'symbol' in df.columns:
                return df['symbol'].tolist()
            elif 'SYMBOL' in df.columns:
                return df['SYMBOL'].tolist()
            elif 'Symbol' in df.columns:
                return df['Symbol'].tolist()
            else:
                # Use first column
                return df.iloc[:, 0].tolist()
        
        except Exception as e:
            logger.error(f"Error loading {csv_file}: {e}")
            return []
    
    def validate_category(self, category: str, sample_size: int = None) -> Dict:
        """
        Validate all symbols in a category
        
        Args:
            category: Category name (e.g., 'nifty50', 'etfs')
            sample_size: Optional sample size for testing
        
        Returns:
            Dictionary with validation results
        """
        csv_file = self.consolidated_path / f"{category}_symbols.csv"
        
        if not csv_file.exists():
            return {'error': f'File not found: {csv_file}'}
        
        console.print(f"\n[bold cyan]Validating {category}...[/bold cyan]")
        
        # Load symbols
        nse_symbols = self.load_symbols_from_csv(csv_file)
        
        if sample_size:
            nse_symbols = nse_symbols[:sample_size]
        
        results = {
            'category': category,
            'total': len(nse_symbols),
            'valid': 0,
            'invalid': 0,
            'errors': [],
            'valid_symbols': [],
            'invalid_symbols': []
        }
        
        # Progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task(
                f"Validating {category}...",
                total=len(nse_symbols)
            )
            
            for nse_symbol in nse_symbols:
                # Convert to FYERS format
                fyers_symbol = self.nse_to_fyers_format(nse_symbol)
                
                # Validate with FYERS API
                is_valid, message = self.validate_symbol_with_fyers(fyers_symbol)
                
                if is_valid:
                    results['valid'] += 1
                    results['valid_symbols'].append({
                        'nse': nse_symbol,
                        'fyers': fyers_symbol,
                        'message': message
                    })
                else:
                    results['invalid'] += 1
                    results['invalid_symbols'].append({
                        'nse': nse_symbol,
                        'fyers': fyers_symbol,
                        'message': message
                    })
                    results['errors'].append(f"{nse_symbol} -> {fyers_symbol}: {message}")
                
                progress.update(task, advance=1)
                
                # Rate limiting
                time.sleep(0.1)  # 10 requests per second
        
        return results
    
    def validate_all_categories(self, sample_size: int = None) -> Dict:
        """
        Validate all symbol categories
        
        Args:
            sample_size: Optional sample size per category
        
        Returns:
            Dictionary with all validation results
        """
        categories = [
            'nifty50',
            'nifty_bank',
            'nifty100',
            'nifty200',
            'etfs',
            'all_equities'
        ]
        
        all_results = {}
        
        for category in categories:
            csv_file = self.consolidated_path / f"{category}_symbols.csv"
            if csv_file.exists():
                results = self.validate_category(category, sample_size)
                all_results[category] = results
                
                # Update global results
                self.results['total'] += results['total']
                self.results['valid'] += results['valid']
                self.results['invalid'] += results['invalid']
        
        return all_results
    
    def display_results(self, results: Dict):
        """
        Display validation results in a table
        
        Args:
            results: Validation results dictionary
        """
        console.print("\n[bold green]Validation Results[/bold green]")
        
        # Summary table
        table = Table(title="Summary")
        table.add_column("Category", style="cyan")
        table.add_column("Total", justify="right", style="yellow")
        table.add_column("Valid", justify="right", style="green")
        table.add_column("Invalid", justify="right", style="red")
        table.add_column("Success Rate", justify="right", style="magenta")
        
        for category, result in results.items():
            if 'error' not in result:
                success_rate = (result['valid'] / result['total'] * 100) if result['total'] > 0 else 0
                table.add_row(
                    category,
                    str(result['total']),
                    str(result['valid']),
                    str(result['invalid']),
                    f"{success_rate:.1f}%"
                )
        
        console.print(table)
        
        # Invalid symbols table
        for category, result in results.items():
            if 'error' not in result and result['invalid'] > 0:
                console.print(f"\n[bold red]Invalid Symbols in {category}:[/bold red]")
                
                invalid_table = Table()
                invalid_table.add_column("NSE Symbol", style="cyan")
                invalid_table.add_column("FYERS Format", style="yellow")
                invalid_table.add_column("Message", style="red")
                
                for invalid in result['invalid_symbols'][:10]:  # Show first 10
                    invalid_table.add_row(
                        invalid['nse'],
                        invalid['fyers'],
                        invalid['message']
                    )
                
                if result['invalid'] > 10:
                    console.print(f"[dim]...and {result['invalid'] - 10} more[/dim]")
                
                console.print(invalid_table)
    
    def save_results(self, results: Dict, output_file: str = 'symbol_validation_results.json'):
        """
        Save validation results to JSON file
        
        Args:
            results: Validation results
            output_file: Output file name
        """
        import json
        
        output_path = project_root / 'logs' / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        console.print(f"\n[green]Results saved to: {output_path}[/green]")


def main():
    parser = argparse.ArgumentParser(description='Validate symbol format compatibility')
    parser.add_argument('--category', type=str, help='Specific category to validate')
    parser.add_argument('--sample', type=int, help='Sample size for testing')
    parser.add_argument('--save', action='store_true', help='Save results to JSON')
    
    args = parser.parse_args()
    
    validator = SymbolFormatValidator()
    
    console.print("[bold cyan]Symbol Format Validator[/bold cyan]")
    console.print("Validating NSE symbols against FYERS exchange format...\n")
    
    if args.category:
        # Validate single category
        results = {args.category: validator.validate_category(args.category, args.sample)}
    else:
        # Validate all categories
        results = validator.validate_all_categories(args.sample)
    
    # Display results
    validator.display_results(results)
    
    # Save if requested
    if args.save:
        validator.save_results(results)
    
    # Final summary
    console.print(f"\n[bold]Overall Results:[/bold]")
    console.print(f"Total symbols validated: [yellow]{validator.results['total']}[/yellow]")
    console.print(f"Valid symbols: [green]{validator.results['valid']}[/green]")
    console.print(f"Invalid symbols: [red]{validator.results['invalid']}[/red]")
    
    if validator.results['total'] > 0:
        success_rate = validator.results['valid'] / validator.results['total'] * 100
        console.print(f"Success rate: [magenta]{success_rate:.2f}%[/magenta]")


if __name__ == '__main__':
    main()
