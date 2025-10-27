#!/usr/bin/env python3
"""
QUICK PROJECT BACKUP - Immediate backup of critical FYERS project files

This script creates an instant backup of the most important project files
without requiring user interaction.
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def quick_backup():
    """Create immediate backup of critical files"""
    project_root = Path(__file__).parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create backup directory
    backup_dir = project_root / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    backup_file = backup_dir / f"fyers_project_backup_{timestamp}.zip"
    
    # Critical files to backup
    critical_files = [
        # Core scripts
        "scripts/comprehensive_symbol_discovery.py",
        "scripts/my_fyers_model.py",
        "scripts/data_storage.py", 
        "scripts/run_websocket.py",
        "scripts/index_constituents.py",
        "scripts/fyers_config.py",
        
        # Configuration
        "README.md",
        "requirements.txt",
        "project_summary.py",
        "auth/credentials.ini",
        
        # Latest data discovery
        "scripts/data/parquet/fyers_symbols/fyers_symbols_20251027_161130.parquet",
        
        # Documentation
        "SYSTEM_UPDATES_COMPLETED.md"
    ]
    
    print(f"🚀 Creating quick backup: {backup_file.name}")
    
    with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
        backed_up = 0
        total_size = 0
        
        for file_path in critical_files:
            full_path = project_root / file_path
            
            if full_path.exists():
                zip_file.write(full_path, file_path)
                size = full_path.stat().st_size
                total_size += size
                backed_up += 1
                print(f"  ✅ {file_path} ({size:,} bytes)")
            else:
                print(f"  ⚠️ {file_path} (not found)")
    
    print(f"\n✅ Backup completed!")
    print(f"📊 Files backed up: {backed_up}")
    print(f"📦 Total size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    print(f"📁 Location: {backup_file}")
    
    return str(backup_file)

if __name__ == "__main__":
    quick_backup()