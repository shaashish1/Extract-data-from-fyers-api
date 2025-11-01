#!/usr/bin/env python3
"""
Download Manager & Monitor
===========================

Simple script to manage and monitor bulk historical downloads.

Features:
- Start new downloads
- Resume failed downloads
- View download statistics
- Check progress
- Estimate completion time

Usage:
    # Start fresh download for all symbols, all timeframes
    python download_manager.py start
    
    # Start download for specific category
    python download_manager.py start --category nifty50
    
    # Resume failed downloads
    python download_manager.py resume
    
    # View statistics
    python download_manager.py status
    
    # Quick start (recommended for first run)
    python download_manager.py quick-start

Author: Fyers Trading Platform
Created: October 30, 2025
"""

import sys
import argparse
from pathlib import Path
import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import json
from datetime import datetime

console = Console()

class DownloadManager:
    """Manages bulk historical downloads"""
    
    def __init__(self):
        self.downloader_script = Path(__file__).parent / 'bulk_historical_downloader.py'
        self.status_file = Path('logs/download_status.json')
    
    def start_download(self, category: str = None, timeframe: str = None, workers: int = 10):
        """Start new download"""
        console.print(Panel.fit(
            "[bold cyan]Starting Bulk Historical Download[/bold cyan]\n"
            f"Category: {category or 'All'}\n"
            f"Timeframe: {timeframe or 'All'}\n"
            f"Workers: {workers}",
            box=box.DOUBLE
        ))
        
        cmd = [sys.executable, str(self.downloader_script), '--workers', str(workers)]
        
        if category:
            cmd.extend(['--category', category])
        if timeframe:
            cmd.extend(['--timeframe', timeframe])
        
        # Run the downloader
        subprocess.run(cmd)
    
    def resume_download(self, workers: int = 10):
        """Resume failed downloads"""
        console.print("[yellow]📥 Resuming failed downloads...[/yellow]")
        
        cmd = [sys.executable, str(self.downloader_script), '--resume', '--workers', str(workers)]
        subprocess.run(cmd)
    
    def show_status(self):
        """Show current download status"""
        if not self.status_file.exists():
            console.print("[yellow]⚠️  No download status found. Start a download first.[/yellow]")
            return
        
        with open(self.status_file, 'r') as f:
            status = json.load(f)
        
        stats = status.get('statistics', {})
        
        # Create statistics table
        table = Table(title="Download Status", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green", justify="right")
        table.add_column("Percentage", style="yellow", justify="right")
        
        total = stats.get('total', 0)
        completed = stats.get('completed', 0)
        failed = stats.get('failed', 0)
        pending = stats.get('pending', 0)
        
        table.add_row("Total Tasks", str(total), "100%")
        table.add_row(
            "Completed",
            str(completed),
            f"{completed/total*100:.1f}%" if total > 0 else "0%"
        )
        table.add_row(
            "Failed",
            str(failed),
            f"{failed/total*100:.1f}%" if total > 0 else "0%"
        )
        table.add_row(
            "Pending",
            str(pending),
            f"{pending/total*100:.1f}%" if total > 0 else "0%"
        )
        
        console.print("\n")
        console.print(table)
        
        # Show timing information
        started_at = status.get('started_at')
        updated_at = status.get('updated_at')
        
        if started_at and updated_at:
            start_time = datetime.fromisoformat(started_at)
            update_time = datetime.fromisoformat(updated_at)
            elapsed = update_time - start_time
            
            console.print(f"\n[cyan]Started:[/cyan] {started_at}")
            console.print(f"[cyan]Updated:[/cyan] {updated_at}")
            console.print(f"[cyan]Elapsed:[/cyan] {elapsed}")
            
            # Estimate remaining time
            if completed > 0 and pending > 0:
                avg_time_per_task = elapsed.total_seconds() / completed
                estimated_remaining = avg_time_per_task * pending
                hours = int(estimated_remaining // 3600)
                minutes = int((estimated_remaining % 3600) // 60)
                console.print(f"[yellow]Estimated Remaining:[/yellow] {hours}h {minutes}m")
        
        # Show recommendations
        if failed > 0:
            console.print(f"\n[yellow]💡 Tip: Run 'python download_manager.py resume' to retry {failed} failed tasks[/yellow]")
    
    def quick_start(self):
        """Quick start guide"""
        console.print(Panel.fit(
            "[bold cyan]Quick Start: Bulk Historical Download[/bold cyan]\n\n"
            "[green]Step 1:[/green] Start with a test run (Nifty 50, 1D only)\n"
            "  python download_manager.py start --category nifty50 --timeframe 1D\n\n"
            "[green]Step 2:[/green] Once successful, download all Nifty 50 timeframes\n"
            "  python download_manager.py start --category nifty50\n\n"
            "[green]Step 3:[/green] Download all symbols, all timeframes (FULL RUN)\n"
            "  python download_manager.py start\n\n"
            "[yellow]⚠️  Full download will take 24-48 hours for 8,686 symbols × 6 timeframes[/yellow]",
            box=box.DOUBLE
        ))
        
        # Ask user what they want to do
        console.print("\n[cyan]What would you like to do?[/cyan]")
        console.print("1. Test run (Nifty 50, 1D only) - ~5 minutes")
        console.print("2. Nifty 50 all timeframes - ~30 minutes")
        console.print("3. Full download (all symbols, all timeframes) - 24-48 hours")
        console.print("4. Exit")
        
        choice = console.input("\n[bold]Enter choice (1-4): [/bold]")
        
        if choice == '1':
            self.start_download(category='nifty50', timeframe='1D')
        elif choice == '2':
            self.start_download(category='nifty50')
        elif choice == '3':
            console.print("[yellow]⚠️  This will download ~52,000 files (8,686 symbols × 6 timeframes)[/yellow]")
            confirm = console.input("[bold]Are you sure? (yes/no): [/bold]")
            if confirm.lower() == 'yes':
                self.start_download()
            else:
                console.print("[red]Cancelled[/red]")
        elif choice == '4':
            console.print("[cyan]Goodbye![/cyan]")
        else:
            console.print("[red]Invalid choice[/red]")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Download Manager')
    parser.add_argument('action', choices=['start', 'resume', 'status', 'quick-start'],
                       help='Action to perform')
    parser.add_argument('--category', type=str, help='Category to download')
    parser.add_argument('--timeframe', type=str, choices=['1m', '5m', '15m', '30m', '60m', '1D'],
                       help='Timeframe to download')
    parser.add_argument('--workers', type=int, default=10, help='Number of workers (default: 10)')
    
    args = parser.parse_args()
    
    manager = DownloadManager()
    
    if args.action == 'start':
        manager.start_download(args.category, args.timeframe, args.workers)
    elif args.action == 'resume':
        manager.resume_download(args.workers)
    elif args.action == 'status':
        manager.show_status()
    elif args.action == 'quick-start':
        manager.quick_start()


if __name__ == '__main__':
    main()
