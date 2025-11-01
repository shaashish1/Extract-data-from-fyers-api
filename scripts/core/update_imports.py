#!/usr/bin/env python3
"""
Import Path Updater for Reorganized Fyers Project Structure

This script updates all import statements and path references after the 
project reorganization to maintain compatibility.

Author: GitHub Copilot Assistant
Date: October 29, 2025
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Define the mapping of old import paths to new ones
IMPORT_MAPPINGS = {
    # Root level scripts moved to organized subdirectories
    "from scripts.analysis.analyze_comprehensive_discovery": "from scripts.analysis.analyze_comprehensive_discovery",
    "from scripts.analysis.analyze_existing_data": "from scripts.analysis.analyze_existing_data", 
    "from scripts.analysis.analyze_fyers_parquet": "from scripts.analysis.analyze_fyers_parquet",
    "from scripts.analysis.sector_analyzer": "from scripts.analysis.sector_analyzer",
    "from scripts.analysis.sector_classification": "from scripts.analysis.sector_classification",
    "from scripts.analysis.symbol_coverage_analysis": "from scripts.analysis.symbol_coverage_analysis",
    
    "from scripts.data_collection.download_bajfinance": "from scripts.data_collection.download_bajfinance",
    "from scripts.data_collection.download_complete_yahoo_history": "from scripts.data_collection.download_complete_yahoo_history",
    "from scripts.data_collection.download_expanded_yahoo_history": "from scripts.data_collection.download_expanded_yahoo_history", 
    "from scripts.data_collection.download_hybrid_fyers_yahoo": "from scripts.data_collection.download_hybrid_fyers_yahoo",
    "from scripts.data_collection.download_infy": "from scripts.data_collection.download_infy",
    "from scripts.data_collection.download_missing_symbols": "from scripts.data_collection.download_missing_symbols",
    "from scripts.data_collection.download_nifty200_complete": "from scripts.data_collection.download_nifty200_complete",
    
    "from scripts.strategies.strategy_ranker": "from scripts.strategies.strategy_ranker",
    "from scripts.strategies.strategy_runner": "from scripts.strategies.strategy_runner",
    
    "from scripts.validation.check_active_symbols": "from scripts.validation.check_active_symbols",
    "from scripts.validation.check_nifty50_match": "from scripts.validation.check_nifty50_match",
    "from scripts.validation.check_reset_time": "from scripts.validation.check_reset_time",
    "from scripts.validation.compare_symbols": "from scripts.validation.compare_symbols",
    "from scripts.validation.reconcile_symbols": "from scripts.validation.reconcile_symbols",
    "from scripts.validation.verify_complete_nifty50": "from scripts.validation.verify_complete_nifty50",
    "from scripts.validation.verify_yahoo_data": "from scripts.validation.verify_yahoo_data",
    "from scripts.validation.fix_nifty50_data": "from scripts.validation.fix_nifty50_data",
    
    # Import statements that reference the scripts/ subdirectories
    "import scripts.analysis.analyze_comprehensive_discovery": "import scripts.analysis.analyze_comprehensive_discovery",
    "import scripts.analysis.analyze_existing_data": "import scripts.analysis.analyze_existing_data",
    "import scripts.analysis.analyze_fyers_parquet": "import scripts.analysis.analyze_fyers_parquet",
    "import scripts.analysis.sector_analyzer": "import scripts.analysis.sector_analyzer",
    "import scripts.analysis.sector_classification": "import scripts.analysis.sector_classification",
    "import scripts.analysis.symbol_coverage_analysis": "import scripts.analysis.symbol_coverage_analysis",
    
    "import scripts.data_collection.download_bajfinance": "import scripts.data_collection.download_bajfinance",
    "import scripts.data_collection.download_complete_yahoo_history": "import scripts.data_collection.download_complete_yahoo_history",
    "import scripts.data_collection.download_expanded_yahoo_history": "import scripts.data_collection.download_expanded_yahoo_history",
    "import scripts.data_collection.download_hybrid_fyers_yahoo": "import scripts.data_collection.download_hybrid_fyers_yahoo",
    "import scripts.data_collection.download_infy": "import scripts.data_collection.download_infy", 
    "import scripts.data_collection.download_missing_symbols": "import scripts.data_collection.download_missing_symbols",
    "import scripts.data_collection.download_nifty200_complete": "import scripts.data_collection.download_nifty200_complete",
    
    "import scripts.strategies.strategy_ranker": "import scripts.strategies.strategy_ranker",
    "import scripts.strategies.strategy_runner": "import scripts.strategies.strategy_runner",
    
    "import scripts.validation.check_active_symbols": "import scripts.validation.check_active_symbols",
    "import scripts.validation.check_nifty50_match": "import scripts.validation.check_nifty50_match",
    "import scripts.validation.check_reset_time": "import scripts.validation.check_reset_time",
    "import scripts.validation.compare_symbols": "import scripts.validation.compare_symbols",
    "import scripts.validation.reconcile_symbols": "import scripts.validation.reconcile_symbols",
    "import scripts.validation.verify_complete_nifty50": "import scripts.validation.verify_complete_nifty50",
    "import scripts.validation.verify_yahoo_data": "import scripts.validation.verify_yahoo_data",
    "import scripts.validation.fix_nifty50_data": "import scripts.validation.fix_nifty50_data",
}

# Path adjustments for relative imports in moved scripts
RELATIVE_PATH_ADJUSTMENTS = {
    # Scripts moved from root to analysis/ need to adjust their relative imports
    "scripts/analysis/": {
        "from scripts.": "from ..",
        "import scripts.": "import ..", 
        "../scripts/": "../../",
        "scripts/": "../",
    },
    
    # Scripts moved from root to data_collection/ need path adjustments  
    "scripts/data_collection/": {
        "from scripts.": "from ..",
        "import scripts.": "import ..",
        "../scripts/": "../../", 
        "scripts/": "../",
    },
    
    # Scripts moved from root to strategies/ need path adjustments
    "scripts/strategies/": {
        "from scripts.": "from ..",
        "import scripts.": "import ..",
        "../scripts/": "../../",
        "scripts/": "../",
    },
    
    # Scripts moved from root to validation/ need path adjustments  
    "scripts/validation/": {
        "from scripts.": "from ..",
        "import scripts.": "import ..",
        "../scripts/": "../../",
        "scripts/": "../",
    }
}

def find_python_files(root_dir: str) -> List[str]:
    """Find all Python files in the project directory."""
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def update_imports_in_file(file_path: str) -> bool:
    """Update import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply general import mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Apply relative path adjustments based on current file location
        rel_path = os.path.relpath(file_path, os.getcwd()).replace('\\', '/')
        
        for path_prefix, adjustments in RELATIVE_PATH_ADJUSTMENTS.items():
            if rel_path.startswith(path_prefix):
                for old_path, new_path in adjustments.items():
                    content = content.replace(old_path, new_path)
                break
        
        # Write back only if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def update_all_imports(project_root: str) -> None:
    """Update imports in all Python files in the project."""
    print("🔧 Updating import statements after reorganization...")
    
    python_files = find_python_files(project_root)
    updated_files = []
    
    for file_path in python_files:
        if update_imports_in_file(file_path):
            updated_files.append(file_path)
    
    print(f"\n✅ Import update complete!")
    print(f"   📁 Scanned: {len(python_files)} Python files")
    print(f"   🔄 Updated: {len(updated_files)} files")
    
    if updated_files:
        print(f"\n📝 Updated files:")
        for file_path in updated_files[:10]:  # Show first 10
            rel_path = os.path.relpath(file_path, project_root)
            print(f"   • {rel_path}")
        
        if len(updated_files) > 10:
            print(f"   • ... and {len(updated_files) - 10} more files")

def main():
    """Main function to run the import updater."""
    # Get project root directory (where this script is run from)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    print("🚀 Fyers Project Import Path Updater")
    print(f"📂 Project root: {project_root}")
    print(f"🔍 Updating import paths after reorganization...\n")
    
    # Change to project root directory
    os.chdir(project_root)
    
    update_all_imports(project_root)
    
    print(f"\n🎉 Import path updates completed successfully!")
    print(f"💡 All scripts should now work with the new directory structure.")

if __name__ == "__main__":
    main()