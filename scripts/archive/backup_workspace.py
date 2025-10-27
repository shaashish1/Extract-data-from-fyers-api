#!/usr/bin/env python3
"""
🚀 FYERS PROJECT WORKSPACE BACKUP SYSTEM
Professional-grade backup utility for the comprehensive FYERS API project

Features:
- Complete project structure backup with timestamps
- Selective backup of critical files vs full workspace
- Compression with detailed manifest
- Verification and integrity checks
- Rich progress reporting with colorful output

Usage:
    python backup_workspace.py [--mode=quick|full|critical]
"""

import os
import sys
import json
import shutil
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import tempfile

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich import box

console = Console()

class FyersProjectBackup:
    """
    🎯 COMPREHENSIVE PROJECT BACKUP SYSTEM
    
    Handles complete workspace backup with intelligent file selection,
    compression, verification, and detailed reporting.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent
        self.backup_root = self.project_root / "backups"
        self.backup_root.mkdir(exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define critical files for quick backup
        self.critical_files = {
            "Core Scripts": [
                "scripts/comprehensive_symbol_discovery.py",
                "scripts/my_fyers_model.py", 
                "scripts/data_storage.py",
                "scripts/run_websocket.py",
                "scripts/fyers_config.py",
                "scripts/index_constituents.py"
            ],
            "Configuration": [
                "auth/credentials.ini",
                "requirements.txt",
                "README.md",
                "project_summary.py"
            ],
            "Data Outputs": [
                "scripts/data/parquet/fyers_symbols/fyers_symbols_20251027_161130.parquet"
            ],
            "Documentation": [
                "README.md",
                "SYSTEM_UPDATES_COMPLETED.md",
                "docs/README.md"
            ]
        }
        
        # Files to exclude from full backup
        self.exclude_patterns = {
            "__pycache__",
            ".git",
            ".venv", 
            "node_modules",
            "*.pyc",
            "*.log",
            ".vscode/settings.json",
            "auth/access_token.txt"  # Security: Don't backup active tokens
        }
    
    def create_critical_backup(self) -> str:
        """
        🎯 CRITICAL FILES BACKUP
        
        Creates a compact backup with only essential files
        """
        backup_name = f"fyers_critical_backup_{self.timestamp}.zip"
        backup_path = self.backup_root / backup_name
        
        console.print("📦 [bold cyan]Creating Critical Files Backup[/bold cyan]")
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as backup_zip:
            file_count = 0
            total_size = 0
            
            with Progress() as progress:
                task = progress.add_task("[green]Backing up critical files...", total=100)
                
                for category, files in self.critical_files.items():
                    progress.update(task, description=f"[green]Processing {category}...")
                    
                    for file_path in files:
                        full_path = self.project_root / file_path
                        
                        if full_path.exists():
                            # Add file to zip
                            backup_zip.write(full_path, file_path)
                            file_count += 1
                            total_size += full_path.stat().st_size
                            
                            console.print(f"  ✅ {file_path}")
                        else:
                            console.print(f"  ⚠️ {file_path} [dim](not found)[/dim]")
                    
                    progress.advance(task, 100 // len(self.critical_files))
        
        # Create manifest
        manifest = {
            "backup_type": "critical",
            "timestamp": self.timestamp,
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "categories": self.critical_files,
            "backup_file": backup_name
        }
        
        manifest_path = self.backup_root / f"critical_manifest_{self.timestamp}.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        console.print(f"\n✅ [bold green]Critical backup created:[/bold green] {backup_name}")
        console.print(f"📊 Files: {file_count}, Size: {manifest['total_size_mb']} MB")
        
        return str(backup_path)
    
    def create_full_backup(self) -> str:
        """
        🚀 COMPLETE WORKSPACE BACKUP
        
        Creates a full backup of the entire project workspace
        """
        backup_name = f"fyers_full_backup_{self.timestamp}.zip"
        backup_path = self.backup_root / backup_name
        
        console.print("🌍 [bold blue]Creating Full Workspace Backup[/bold blue]")
        
        # Count files first
        all_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_root)
                
                if not self._should_exclude(str(rel_path)):
                    all_files.append((file_path, rel_path))
        
        console.print(f"📊 Found {len(all_files)} files to backup")
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as backup_zip:
            total_size = 0
            
            with Progress() as progress:
                task = progress.add_task("[blue]Creating full backup...", total=len(all_files))
                
                for file_path, rel_path in all_files:
                    try:
                        backup_zip.write(file_path, rel_path)
                        total_size += file_path.stat().st_size
                        progress.advance(task)
                        
                        if len(all_files) < 50:  # Show details for smaller backups
                            console.print(f"  ✅ {rel_path}")
                            
                    except Exception as e:
                        console.print(f"  ❌ Failed to backup {rel_path}: {e}")
        
        # Create manifest
        manifest = {
            "backup_type": "full",
            "timestamp": self.timestamp,
            "file_count": len(all_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "excluded_patterns": list(self.exclude_patterns),
            "backup_file": backup_name
        }
        
        manifest_path = self.backup_root / f"full_manifest_{self.timestamp}.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        console.print(f"\n✅ [bold green]Full backup created:[/bold green] {backup_name}")
        console.print(f"📊 Files: {len(all_files)}, Size: {manifest['total_size_mb']} MB")
        
        return str(backup_path)
    
    def create_data_backup(self) -> str:
        """
        📊 DATA FILES BACKUP
        
        Creates backup of all data files (Parquet, JSON, etc.)
        """
        backup_name = f"fyers_data_backup_{self.timestamp}.zip"
        backup_path = self.backup_root / backup_name
        
        console.print("📊 [bold yellow]Creating Data Files Backup[/bold yellow]")
        
        data_dirs = [
            "scripts/data",
            "data",
            "auth" # Include auth for config (but exclude tokens)
        ]
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as backup_zip:
            file_count = 0
            total_size = 0
            
            for data_dir in data_dirs:
                full_dir = self.project_root / data_dir
                if not full_dir.exists():
                    continue
                
                console.print(f"📁 Processing {data_dir}...")
                
                for root, dirs, files in os.walk(full_dir):
                    for file in files:
                        file_path = Path(root) / file
                        rel_path = file_path.relative_to(self.project_root)
                        
                        # Skip sensitive files
                        if "access_token" in file or file.endswith('.log'):
                            continue
                        
                        backup_zip.write(file_path, rel_path)
                        file_count += 1
                        total_size += file_path.stat().st_size
                        console.print(f"  ✅ {rel_path}")
        
        manifest = {
            "backup_type": "data",
            "timestamp": self.timestamp,
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "data_directories": data_dirs,
            "backup_file": backup_name
        }
        
        manifest_path = self.backup_root / f"data_manifest_{self.timestamp}.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        console.print(f"\n✅ [bold green]Data backup created:[/bold green] {backup_name}")
        console.print(f"📊 Files: {file_count}, Size: {manifest['total_size_mb']} MB")
        
        return str(backup_path)
    
    def _should_exclude(self, path: str) -> bool:
        """Check if a file/directory should be excluded"""
        path_lower = path.lower()
        
        for pattern in self.exclude_patterns:
            if pattern.startswith("*."):
                # Extension pattern
                if path_lower.endswith(pattern[1:]):
                    return True
            else:
                # Directory or filename pattern
                if pattern in path_lower:
                    return True
        
        return False
    
    def verify_backup(self, backup_path: str) -> bool:
        """Verify backup integrity"""
        console.print(f"🔍 [bold cyan]Verifying backup: {Path(backup_path).name}[/bold cyan]")
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as backup_zip:
                # Test the archive
                bad_files = backup_zip.testzip()
                
                if bad_files is None:
                    file_count = len(backup_zip.namelist())
                    console.print(f"✅ [green]Backup verified successfully[/green]")
                    console.print(f"📊 Contains {file_count} files")
                    return True
                else:
                    console.print(f"❌ [red]Backup verification failed: {bad_files}[/red]")
                    return False
                    
        except Exception as e:
            console.print(f"❌ [red]Backup verification error: {e}[/red]")
            return False
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_root.glob("*.zip"):
            manifest_file = backup_file.with_suffix('').with_suffix('') / f"_manifest_{backup_file.stem.split('_')[-1]}.json"
            
            # Try to find corresponding manifest
            manifest_files = list(self.backup_root.glob(f"*manifest*{backup_file.stem.split('_')[-1]}.json"))
            
            backup_info = {
                "file": backup_file.name,
                "path": str(backup_file),
                "size_mb": round(backup_file.stat().st_size / 1024 / 1024, 2),
                "created": datetime.fromtimestamp(backup_file.stat().st_mtime),
                "manifest": manifest_files[0].name if manifest_files else None
            }
            
            backups.append(backup_info)
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def print_backup_summary(self):
        """Print a summary of all backups"""
        backups = self.list_backups()
        
        if not backups:
            console.print("📁 [yellow]No backups found[/yellow]")
            return
        
        table = Table(title="🗄️ [bold blue]Available Backups[/bold blue]", box=box.ROUNDED)
        table.add_column("Backup File", style="cyan")
        table.add_column("Size (MB)", justify="right", style="yellow")
        table.add_column("Created", style="green")
        table.add_column("Manifest", style="dim")
        
        for backup in backups:
            table.add_row(
                backup['file'],
                f"{backup['size_mb']:.1f}",
                backup['created'].strftime("%Y-%m-%d %H:%M"),
                backup['manifest'] or "❌"
            )
        
        console.print(table)

def main():
    """Main backup interface"""
    console.print("\n")
    console.print(Panel.fit("🚀 [bold blue]FYERS PROJECT WORKSPACE BACKUP SYSTEM[/bold blue] 🚀",
                           style="bright_cyan", box=box.DOUBLE))
    
    backup_system = FyersProjectBackup()
    
    # Show current backups
    console.print("\n📋 [bold]Current Backups:[/bold]")
    backup_system.print_backup_summary()
    
    # Interactive menu
    console.print("\n[bold]Choose backup type:[/bold]")
    console.print("1. 📦 Critical Files Only (Fast - Essential files)")
    console.print("2. 📊 Data Files Only (Parquet, configs)")
    console.print("3. 🌍 Full Workspace (Complete backup)")
    console.print("4. 🔄 All Types (Critical + Data + Full)")
    console.print("5. 📋 List Existing Backups")
    console.print("6. ❌ Exit")
    
    choice = console.input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        backup_path = backup_system.create_critical_backup()
        backup_system.verify_backup(backup_path)
        
    elif choice == "2":
        backup_path = backup_system.create_data_backup()
        backup_system.verify_backup(backup_path)
        
    elif choice == "3":
        backup_path = backup_system.create_full_backup()
        backup_system.verify_backup(backup_path)
        
    elif choice == "4":
        console.print("🚀 [bold]Creating all backup types...[/bold]")
        
        # Critical
        critical_path = backup_system.create_critical_backup()
        backup_system.verify_backup(critical_path)
        
        # Data
        data_path = backup_system.create_data_backup()
        backup_system.verify_backup(data_path)
        
        # Full
        full_path = backup_system.create_full_backup()
        backup_system.verify_backup(full_path)
        
        console.print("\n🎉 [bold green]All backups completed successfully![/bold green]")
        
    elif choice == "5":
        backup_system.print_backup_summary()
        
    elif choice == "6":
        console.print("👋 [bold]Goodbye![/bold]")
        return
    
    else:
        console.print("❌ [red]Invalid choice[/red]")
        return
    
    # Final summary
    console.print(f"\n📁 [bold]Backup location:[/bold] {backup_system.backup_root}")
    console.print("✅ [bold green]Backup process completed![/bold green]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n⚠️ [yellow]Backup interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n❌ [red]Backup failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")