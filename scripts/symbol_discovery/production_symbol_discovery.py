#!/usr/bin/env python3
"""
Production-Ready NSE Symbol Discovery System
Combines manual NSE CSVs + FYERS data + smart categorization

Author: Ashish
Date: October 29, 2025
"""

import pandas as pd
import requests
from pathlib import Path
from typing import Dict, Set, List
from rich.console import Console
from rich.table import Table
from rich import box
import time

console = Console()


class ProductionSymbolDiscovery:
    """
    Production-grade symbol discovery combining:
    1. Manual NSE CSV downloads (stored in data/nse_symbols/)
    2. FYERS CSV data (NSE_CM + NSE_FO)
    3. Smart categorization and validation
    """
    
    def __init__(self):
        # Directories
        self.nse_data_dir = Path("data/nse_symbols")
        self.nse_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.nse_data_input_dir = Path("data/nse_data_input_csv")  # New NSE CSV format
        
        self.fyers_data_dir = Path("data/fyers_symbols")
        self.fyers_data_dir.mkdir(parents=True, exist_ok=True)
        
        # NSE CSV files (manually downloaded) - old format
        self.nse_files = {
            'nifty50': 'NIFTY_50.csv',
            'nifty100': 'NIFTY_100.csv',
            'nifty200': 'NIFTY_200.csv',
            'nifty_midcap50': 'NIFTY_MIDCAP_50.csv',
            'nifty_midcap100': 'NIFTY_MIDCAP_100.csv',
        }
        
        # New NSE CSV format files
        self.nse_new_files = {
            'nifty50': 'MW-NIFTY-50-29-Oct-2025.csv',
            'nifty100': 'MW-NIFTY-100-29-Oct-2025.csv',
            'nifty200': 'MW-NIFTY-200-29-Oct-2025.csv',
            'nifty_bank': 'MW-NIFTY-BANK-29-Oct-2025.csv',
            'nifty_financial': 'MW-NIFTY-FINANCIAL-SERVICES-29-Oct-2025.csv',
            'nifty_next50': 'MW-NIFTY-NEXT-50-29-Oct-2025.csv',
            'nifty_midcap_select': 'MW-NIFTY-MIDCAP-SELECT-29-Oct-2025.csv',
            'nifty_smallcap100': 'MW-NIFTY-SMALLCAP-100-29-Oct-2025.csv',
            'etfs': 'MW-ETF-29-Oct-2025.csv',
            'fo_stocks': 'MW-FO-stock_opt-29-Oct-2025.csv'
        }
        
        # FYERS endpoints
        self.FYERS_ENDPOINTS = {
            'NSE_CM': 'https://public.fyers.in/sym_details/NSE_CM.csv',
            'NSE_FO': 'https://public.fyers.in/sym_details/NSE_FO.csv',
        }
        
        # Symbol storage
        self.symbols = {
            'nifty50': set(),
            'nifty100': set(),
            'nifty200': set(),
            'nifty_midcap50': set(),
            'nifty_midcap100': set(),
            'nifty_bank': set(),
            'nifty_financial': set(),
            'nifty_next50': set(),
            'nifty_midcap_select': set(),
            'nifty_smallcap100': set(),
            'etfs': set(),
            'fo_stocks': set(),
            'nse_cm_all': set(),
            'nse_fo_equities': set(),
            'all_equities': set()
        }
    
    def load_nse_manual_csvs(self):
        """Load manually downloaded NSE CSVs"""
        console.print("\n[bold cyan]📂 Loading Manual NSE CSVs[/bold cyan]")
        console.rule()
        
        for category, filename in self.nse_files.items():
            filepath = self.nse_data_dir / filename
            
            if filepath.exists():
                try:
                    df = pd.read_csv(filepath)
                    # NSE CSVs have 'symbol' or 'SYMBOL' column
                    symbol_col = 'symbol' if 'symbol' in df.columns else 'SYMBOL'
                    symbols = set(df[symbol_col].dropna().astype(str).str.strip())
                    
                    # Filter out index names (NSE includes them in the CSV)
                    index_names = {'NIFTY 50', 'NIFTY 100', 'NIFTY 200', 'NIFTY MIDCAP 50', 'NIFTY MIDCAP 100', 
                                   'NIFTY50', 'NIFTY100', 'NIFTY200', 'NIFTYMIDCAP50', 'NIFTYMIDCAP100'}
                    symbols = {s for s in symbols if s not in index_names and not s.startswith('Nifty')}
                    
                    self.symbols[category] = symbols
                    console.print(f"[green]✅ {category}: {len(symbols)} symbols from {filename}[/green]")
                except Exception as e:
                    console.print(f"[red]❌ Error loading {filename}: {e}[/red]")
            else:
                console.print(f"[yellow]⚠️ {filename} not found. Please download manually.[/yellow]")
    
    def load_nse_new_format_csvs(self):
        """Load NSE CSVs in new format (MW-*.csv from data/nse_data_input_csv)"""
        console.print("\n[bold cyan]📂 Loading New Format NSE CSVs[/bold cyan]")
        console.rule()
        
        for category, filename in self.nse_new_files.items():
            filepath = self.nse_data_input_dir / filename
            
            if filepath.exists():
                try:
                    # Read CSV with special handling for NSE format
                    df = pd.read_csv(filepath, skiprows=0)
                    
                    # Find the symbol column (first column with "SYMBOL" in header)
                    symbol_col = None
                    for col in df.columns:
                        if 'SYMBOL' in str(col).upper():
                            symbol_col = col
                            break
                    
                    if symbol_col is None:
                        console.print(f"[yellow]⚠️ No SYMBOL column found in {filename}[/yellow]")
                        continue
                    
                    # Extract symbols and clean
                    symbols = set(df[symbol_col].dropna().astype(str).str.strip())
                    
                    # Remove empty strings, whitespace-only entries, and index names
                    # Filter out common index names that appear in NSE CSVs
                    index_names = {
                        'NIFTY 50', 'NIFTY 100', 'NIFTY 200', 'NIFTY BANK', 
                        'NIFTY FINANCIAL SERVICES', 'NIFTY NEXT 50',
                        'NIFTY MIDCAP SELECT', 'NIFTY SMALLCAP 100',
                        'NIFTY50', 'NIFTY100', 'NIFTY200', 'NIFTYBANK',
                        'Symbol', 'SYMBOL'  # Header values that might leak through
                    }
                    symbols = {s for s in symbols if s and not s.isspace() 
                              and s not in index_names 
                              and not s.startswith('Nifty')
                              and not s.startswith('NIFTY')
                              and not s.upper().startswith('SYMBOL')}
                    
                    self.symbols[category] = symbols
                    console.print(f"[green]✅ {category}: {len(symbols)} symbols from {filename}[/green]")
                    
                except Exception as e:
                    console.print(f"[red]❌ Error loading {filename}: {e}[/red]")
            else:
                console.print(f"[yellow]⚠️ {filename} not found in {self.nse_data_input_dir}[/yellow]")
    
    def download_fyers_csvs(self):
        """Download FYERS symbol CSVs"""
        console.print("\n[bold cyan]📥 Downloading FYERS CSVs[/bold cyan]")
        console.rule()
        
        for segment, url in self.FYERS_ENDPOINTS.items():
            try:
                console.print(f"[cyan]Downloading {segment}...[/cyan]")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Save to disk
                filepath = self.fyers_data_dir / f"{segment}.csv"
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                console.print(f"[green]✅ {segment} saved to {filepath}[/green]")
                time.sleep(1)
                
            except Exception as e:
                console.print(f"[red]❌ Failed to download {segment}: {e}[/red]")
    
    def process_fyers_nse_cm(self):
        """Process NSE_CM for all cash market symbols"""
        console.print("\n[bold cyan]🔄 Processing FYERS NSE_CM[/bold cyan]")
        console.rule()
        
        filepath = self.fyers_data_dir / 'NSE_CM.csv'
        if not filepath.exists():
            console.print("[red]❌ NSE_CM.csv not found[/red]")
            return
        
        try:
            df = pd.read_csv(filepath, header=None)
            # Column 13 = base_symbol
            symbols = set(df.iloc[:, 13].dropna().astype(str))
            symbols = {s for s in symbols if s != 'nan'}
            
            self.symbols['nse_cm_all'] = symbols
            console.print(f"[green]✅ NSE_CM: {len(symbols)} symbols[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error processing NSE_CM: {e}[/red]")
    
    def process_fyers_nse_fo(self):
        """Extract equity symbols from NSE_FO (ignore derivative contracts)"""
        console.print("\n[bold cyan]⚡ Extracting Equities from NSE_FO[/bold cyan]")
        console.rule()
        
        filepath = self.fyers_data_dir / 'NSE_FO.csv'
        if not filepath.exists():
            console.print("[red]❌ NSE_FO.csv not found[/red]")
            return
        
        try:
            df = pd.read_csv(filepath, header=None)
            
            # Column 13 = base_symbol
            # Get unique base symbols (these are the underlying equities)
            all_base_symbols = set(df.iloc[:, 13].dropna().astype(str))
            all_base_symbols = {s for s in all_base_symbols if s != 'nan'}
            
            # Filter: Only symbols not in NSE_CM (F&O exclusives like TATAMOTORS)
            fo_exclusive = all_base_symbols - self.symbols['nse_cm_all']
            
            self.symbols['nse_fo_equities'] = all_base_symbols
            console.print(f"[green]✅ NSE_FO unique equities: {len(all_base_symbols)}[/green]")
            console.print(f"[yellow]   F&O exclusive (not in CM): {len(fo_exclusive)}[/yellow]")
            
            if fo_exclusive:
                console.print(f"[dim]   Examples: {', '.join(sorted(list(fo_exclusive))[:10])}[/dim]")
            
        except Exception as e:
            console.print(f"[red]❌ Error processing NSE_FO: {e}[/red]")
    
    def merge_all_equities(self):
        """Merge CM + FO for complete equity universe"""
        console.print("\n[bold cyan]🔗 Merging Complete Equity Universe[/bold cyan]")
        console.rule()
        
        # Combine NSE_CM + NSE_FO equities
        self.symbols['all_equities'] = (
            self.symbols['nse_cm_all'] | 
            self.symbols['nse_fo_equities']
        )
        
        console.print(f"[green]✅ Total unique equities: {len(self.symbols['all_equities'])}[/green]")
        console.print(f"[dim]   = {len(self.symbols['nse_cm_all'])} (CM) + {len(self.symbols['nse_fo_equities'] - self.symbols['nse_cm_all'])} (FO exclusive)[/dim]")
    
    def validate_nifty_indices(self):
        """Validate Nifty50/100/200 against discovered symbols"""
        console.print("\n")
        console.rule("[bold yellow]🔍 NIFTY INDEX VALIDATION[/bold yellow]")
        
        validation_table = Table(
            title="📊 Nifty Index Validation",
            box=box.ROUNDED,
            title_style="bold cyan"
        )
        
        validation_table.add_column("Index", style="bold blue", width=20)
        validation_table.add_column("From NSE CSV", justify="right", style="green", width=15)
        validation_table.add_column("In CM", justify="right", style="yellow", width=10)
        validation_table.add_column("In FO", justify="right", style="yellow", width=10)
        validation_table.add_column("Missing", justify="right", style="red", width=10)
        
        indices_to_check = {
            'nifty50': ('Nifty 50', 50),
            'nifty100': ('Nifty 100', 100),
            'nifty200': ('Nifty 200', 200),
        }
        
        for key, (name, expected) in indices_to_check.items():
            nse_symbols = self.symbols.get(key, set())
            nse_count = len(nse_symbols)
            
            # Check how many are in CM
            in_cm = len(nse_symbols & self.symbols['nse_cm_all'])
            
            # Check how many are in FO
            in_fo = len(nse_symbols & self.symbols['nse_fo_equities'])
            
            # Missing from both
            missing = nse_symbols - self.symbols['all_equities']
            missing_count = len(missing)
            
            validation_table.add_row(
                name,
                str(nse_count),
                str(in_cm),
                str(in_fo),
                str(missing_count) if missing_count > 0 else "✅ 0"
            )
            
            # Show missing symbols
            if missing:
                console.print(f"\n[red]⚠️ {name} Missing Symbols:[/red]")
                for sym in sorted(missing):
                    console.print(f"   • {sym}")
        
        console.print(validation_table)
    
    def display_summary(self):
        """Display comprehensive summary"""
        console.print("\n")
        console.rule("[bold green]📊 DISCOVERY SUMMARY[/bold green]")
        
        summary_table = Table(
            title="🎯 Symbol Discovery Results",
            box=box.ROUNDED,
            title_style="bold cyan"
        )
        
        summary_table.add_column("Category", style="bold blue", width=25)
        summary_table.add_column("Symbols", justify="right", style="bold yellow", width=12)
        summary_table.add_column("Source", style="green", width=20)
        
        # NSE Manual CSVs
        summary_table.add_row("", "", "", style="dim")
        summary_table.add_row("[bold]NSE Index Constituents[/bold]", "", "", style="cyan")
        summary_table.add_row("Nifty 50", str(len(self.symbols.get('nifty50', set()))), "NSE Manual CSV")
        summary_table.add_row("Nifty 100", str(len(self.symbols.get('nifty100', set()))), "NSE Manual CSV")
        summary_table.add_row("Nifty 200", str(len(self.symbols.get('nifty200', set()))), "NSE Manual CSV")
        summary_table.add_row("Nifty Bank", str(len(self.symbols.get('nifty_bank', set()))), "NSE Manual CSV")
        summary_table.add_row("Nifty Financial", str(len(self.symbols.get('nifty_financial', set()))), "NSE Manual CSV")
        summary_table.add_row("Nifty Next 50", str(len(self.symbols.get('nifty_next50', set()))), "NSE Manual CSV")
        summary_table.add_row("Midcap Select", str(len(self.symbols.get('nifty_midcap_select', set()))), "NSE Manual CSV")
        summary_table.add_row("Smallcap 100", str(len(self.symbols.get('nifty_smallcap100', set()))), "NSE Manual CSV")
        
        # ETFs & F&O Stocks
        summary_table.add_row("", "", "", style="dim")
        summary_table.add_row("ETFs", str(len(self.symbols.get('etfs', set()))), "NSE Manual CSV")
        summary_table.add_row("F&O Stocks", str(len(self.symbols.get('fo_stocks', set()))), "NSE Manual CSV")
        
        # FYERS Data
        summary_table.add_row("", "", "", style="dim")
        summary_table.add_row("[bold]FYERS Complete Data[/bold]", "", "", style="cyan")
        summary_table.add_row("NSE Cash Market (CM)", str(len(self.symbols['nse_cm_all'])), "FYERS CSV")
        summary_table.add_row("NSE F&O Equities", str(len(self.symbols['nse_fo_equities'])), "FYERS CSV")
        
        # Combined
        summary_table.add_row("", "", "", style="dim")
        summary_table.add_row("[bold]Total Equities (CM+FO)[/bold]", 
                             str(len(self.symbols['all_equities'])), 
                             "Combined", 
                             style="bold green")
        
        console.print(summary_table)
    
    def save_consolidated_data(self):
        """Save all discovered symbols to files"""
        console.print("\n[bold cyan]💾 Saving Consolidated Data[/bold cyan]")
        console.rule()
        
        output_dir = Path("data/consolidated_symbols")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for category, symbols in self.symbols.items():
            if symbols:
                df = pd.DataFrame({'symbol': sorted(list(symbols))})
                
                # Save as CSV
                csv_path = output_dir / f'{category}_symbols.csv'
                df.to_csv(csv_path, index=False)
                
                # Save as Parquet
                parquet_path = output_dir / f'{category}_symbols.parquet'
                df.to_parquet(parquet_path, index=False)
                
                console.print(f"[green]✅ Saved {category}: {len(symbols)} symbols[/green]")
        
        console.print(f"\n[green]📁 Output directory: {output_dir}[/green]")
    
    def generate_fyers_format_symbols(self):
        """Generate Fyers-format symbols (NSE:SYMBOL-EQ)"""
        console.print("\n[bold cyan]🔧 Generating Fyers Format Symbols[/bold cyan]")
        console.rule()
        
        # Generate Fyers format for all equities
        fyers_equities = [f"NSE:{s}-EQ" for s in sorted(self.symbols['all_equities'])]
        output_path = Path("data/consolidated_symbols/fyers_format_all_equities.txt")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(fyers_equities))
        
        console.print(f"[green]✅ Generated {len(fyers_equities)} Fyers-format equity symbols[/green]")
        console.print(f"[green]💾 Saved to: {output_path}[/green]")
        
        # Generate Fyers format for ETFs
        if self.symbols.get('etfs'):
            fyers_etfs = [f"NSE:{s}-EQ" for s in sorted(self.symbols['etfs'])]
            etf_output_path = Path("data/consolidated_symbols/fyers_format_etfs.txt")
            
            with open(etf_output_path, 'w') as f:
                f.write('\n'.join(fyers_etfs))
            
            console.print(f"[green]✅ Generated {len(fyers_etfs)} Fyers-format ETF symbols[/green]")
            console.print(f"[green]💾 Saved to: {etf_output_path}[/green]")
        
        console.print(f"\n[dim]Sample equity symbols (first 5):[/dim]")
        for sym in fyers_equities[:5]:
            console.print(f"   {sym}")
        
        if self.symbols.get('etfs'):
            console.print(f"\n[dim]Sample ETF symbols (first 5):[/dim]")
            for sym in fyers_etfs[:5]:
                console.print(f"   {sym}")
    
    def run_discovery(self):
        """Main discovery workflow"""
        console.print("\n[bold yellow]🚀 Production Symbol Discovery System[/bold yellow]")
        console.print("[dim]Combines manual NSE CSVs + FYERS data[/dim]\n")
        
        # Step 1: Load new format NSE CSVs (includes ETFs, multiple indices)
        self.load_nse_new_format_csvs()
        
        # Step 2: Download FYERS data
        self.download_fyers_csvs()
        
        # Step 3: Process FYERS NSE_CM
        self.process_fyers_nse_cm()
        
        # Step 4: Extract NSE_FO equities
        self.process_fyers_nse_fo()
        
        # Step 5: Merge all equities
        self.merge_all_equities()
        
        # Step 6: Validate Nifty indices
        self.validate_nifty_indices()
        
        # Step 7: Display summary
        self.display_summary()
        
        # Step 8: Save consolidated data
        self.save_consolidated_data()
        
        # Step 9: Generate Fyers format
        self.generate_fyers_format_symbols()
        
        console.print("\n[bold green]✅ Symbol Discovery Complete![/bold green]")


def main():
    """Entry point"""
    try:
        discovery = ProductionSymbolDiscovery()
        discovery.run_discovery()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Discovery interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
