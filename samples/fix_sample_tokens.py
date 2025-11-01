#!/usr/bin/env python3
"""
🔧 Sample Scripts Access Token Fixer
====================================

This script fixes all sample scripts to use the real access token
from our authentication system instead of dummy tokens.

Author: Fyers WebSocket Live Project
Date: October 29, 2025
"""

import os
import sys
import re
from pathlib import Path

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

console = Console()

class SampleScriptsFixer:
    def __init__(self):
        """Initialize the sample scripts fixer."""
        self.samples_dir = Path(__file__).parent
        self.project_root = self.samples_dir.parent
        self.fixed_files = []
        self.skipped_files = []
        
        # Get real access token
        self.real_token = self.get_real_access_token()
        self.client_id = self.get_client_id()
        
    def get_real_access_token(self):
        """Get the real access token from auth directory."""
        try:
            token_path = self.project_root / "auth" / "access_token.txt"
            with open(token_path, 'r') as f:
                token = f.read().strip()
            console.print(f"✅ Found real access token: {token[:20]}...", style="green")
            return token
        except Exception as e:
            console.print(f"❌ Could not read access token: {e}", style="red")
            return None
    
    def get_client_id(self):
        """Get the real client ID from credentials."""
        try:
            import configparser
            config = configparser.ConfigParser()
            config_path = self.project_root / "auth" / "credentials.ini"
            config.read(config_path)
            client_id = config['fyers']['client_id']
            console.print(f"✅ Found client ID: {client_id}", style="green")
            return client_id
        except Exception as e:
            console.print(f"❌ Could not read client ID: {e}", style="red")
            return None
    
    def find_python_files(self):
        """Find all Python files in samples directory."""
        python_files = []
        for root, dirs, files in os.walk(self.samples_dir):
            for file in files:
                if file.endswith('.py') and file != 'fix_sample_tokens.py':
                    python_files.append(Path(root) / file)
        return python_files
    
    def fix_file(self, file_path):
        """Fix access token and authentication in a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes_made = False
            
            # Pattern 1: Direct token assignment with dummy tokens
            dummy_token_patterns = [
                r'access_token\s*=\s*["\']eyJ0eXXXXXXXX2c5-Y3RgS8wR14g["\']',
                r'access_token\s*=\s*["\']XCXXXXXXM-100:eyJ0tHfZNSBoLo["\']',
                r'access_token\s*=\s*["\'][^"\']*XXXXX[^"\']*["\']',
                r'token\s*=\s*["\']eyJ0eXXXXXXXX2c5-Y3RgS8wR14g["\']'
            ]
            
            for pattern in dummy_token_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, f'access_token = "{self.real_token}"', content)
                    changes_made = True
            
            # Pattern 2: Direct client_id assignment with dummy values
            dummy_client_patterns = [
                r'client_id\s*=\s*["\']XC4XXXXM-100["\']',
                r'client_id\s*=\s*["\']XCXXXXXXM-100["\']'
            ]
            
            for pattern in dummy_client_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, f'client_id = "{self.client_id}"', content)
                    changes_made = True
            
            # Pattern 3: Files that read from access_token.txt
            if 'access_token.txt' in content or 'fyers_access_token.txt' in content:
                # Add import for our authentication system
                if 'from my_fyers_model import MyFyersModel' not in content:
                    # Add import at the top
                    import_line = """
# Add scripts directory to path for authentication
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from auth.my_fyers_model import MyFyersModel

"""
                    content = import_line + content
                    changes_made = True
                
                # Replace token reading with our system
                token_read_patterns = [
                    r'access_token\s*=\s*open\(["\'][^"\']*access_token\.txt["\'][^)]*\)\.read\(\)[^\\n]*',
                    r'with\s+open\(["\'][^"\']*access_token\.txt["\'][^)]*\)[^:]*:[^\\n]*\\n[^\\n]*access_token[^\\n]*'
                ]
                
                for pattern in token_read_patterns:
                    if re.search(pattern, content):
                        replacement = """# Get access token from our authentication system
fyers_auth = MyFyersModel()
access_token = fyers_auth.get_access_token()"""
                        content = re.sub(pattern, replacement, content)
                        changes_made = True
            
            # Pattern 4: Add proper imports for scripts that use MyFyersModel
            if 'MyFyersModel' in content and 'from scripts.auth.my_fyers_model import MyFyersModel' not in content:
                if 'from my_fyers_model import MyFyersModel' not in content:
                    # Fix import path
                    content = content.replace(
                        'from my_fyers_model import MyFyersModel',
                        'from scripts.auth.my_fyers_model import MyFyersModel'
                    )
                    changes_made = True
            
            # Save changes if any were made
            if changes_made:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(file_path)
                return True, "Fixed dummy tokens and authentication"
            else:
                self.skipped_files.append(file_path)
                return False, "No dummy tokens found"
                
        except Exception as e:
            return False, f"Error processing file: {str(e)}"
    
    def run_comprehensive_fix(self):
        """Run comprehensive fix on all sample files."""
        console.print("🔧 Starting Sample Scripts Token Fix...", style="blue bold")
        
        if not self.real_token or not self.client_id:
            console.print("❌ Cannot proceed without real credentials", style="red")
            return False
        
        python_files = self.find_python_files()
        console.print(f"📁 Found {len(python_files)} Python files to check", style="blue")
        
        results_table = Table(title="Sample Scripts Fix Results")
        results_table.add_column("File", style="cyan")
        results_table.add_column("Status", style="green")
        results_table.add_column("Details", style="yellow")
        
        for file_path in track(python_files, description="Fixing files..."):
            relative_path = file_path.relative_to(self.samples_dir)
            success, message = self.fix_file(file_path)
            
            status = "✅ Fixed" if success else "⏭️ Skipped"
            results_table.add_row(str(relative_path), status, message)
        
        console.print(results_table)
        
        # Summary
        summary_panel = Panel(
            f"""
🎯 **Fix Summary:**
✅ Files Fixed: {len(self.fixed_files)}
⏭️ Files Skipped: {len(self.skipped_files)}
📁 Total Files: {len(python_files)}

🔑 **Credentials Used:**
• Client ID: {self.client_id}
• Token: {self.real_token[:20]}...
            """.strip(),
            title="Sample Scripts Fix Complete",
            border_style="green"
        )
        console.print(summary_panel)
        
        return len(self.fixed_files) > 0

def main():
    """Main execution function."""
    fixer = SampleScriptsFixer()
    success = fixer.run_comprehensive_fix()
    
    if success:
        console.print("\\n🎉 Sample scripts have been updated with real credentials!", style="green bold")
        console.print("🚀 You can now run the samples to test symbol discovery and API functionality.", style="blue")
    else:
        console.print("\\n⚠️ No files were fixed. Check if credentials are available.", style="yellow")

if __name__ == "__main__":
    main()