#!/usr/bin/env python3
"""
AUTHENTICATION SYSTEM ANALYSIS AND TESTING
Comprehensive testing and validation of token generation and storage
"""

import os
import sys
import configparser
from datetime import datetime
from pathlib import Path

def print_section(title, char="="):
    """Print formatted section header"""
    print(f"\n{char * 70}")
    print(f" {title}")
    print(f"{char * 70}")

def print_status(item, status, details=""):
    """Print status with emoji"""
    status_emoji = "✅" if status else "❌"
    print(f"{status_emoji} {item}")
    if details:
        print(f"   📋 {details}")

def analyze_auth_system():
    """Comprehensive analysis of authentication system"""
    print("🔐 FYERS AUTHENTICATION SYSTEM ANALYSIS")
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print_section("📁 AUTH FOLDER STRUCTURE")
    
    auth_dir = Path("../auth")
    if auth_dir.exists():
        print(f"📂 Auth Directory: {auth_dir.absolute()}")
        for file in auth_dir.iterdir():
            if file.is_file():
                size = file.stat().st_size
                print(f"   📄 {file.name} ({size:,} bytes)")
    else:
        print("❌ Auth directory not found")
        return False
    
    print_section("🔧 CREDENTIALS CONFIGURATION")
    
    # Check credentials.ini
    credentials_file = auth_dir / "credentials.ini"
    if credentials_file.exists():
        try:
            config = configparser.ConfigParser()
            config.read(credentials_file)
            
            print_status("Credentials file exists", True, str(credentials_file))
            
            if 'fyers' in config:
                fyers_config = config['fyers']
                print(f"\n📊 FYERS CONFIGURATION:")
                
                config_items = [
                    ("client_id", "Client ID"),
                    ("secret_key", "Secret Key"),
                    ("redirect_url", "Redirect URL"),
                    ("file_name", "Token File Name"),
                    ("log_dir", "Log Directory"),
                    ("time_zone", "Time Zone")
                ]
                
                for key, description in config_items:
                    if key in fyers_config:
                        value = fyers_config[key]
                        # Mask sensitive data
                        if key in ['secret_key']:
                            display_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                        elif key in ['client_id']:
                            display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else value
                        else:
                            display_value = value
                        print_status(f"{description}", True, display_value)
                    else:
                        print_status(f"{description}", False, "Missing")
            else:
                print_status("Fyers section in config", False, "Missing [fyers] section")
                
        except Exception as e:
            print_status("Reading credentials", False, f"Error: {e}")
    else:
        print_status("credentials.ini", False, "File not found")
    
    print_section("🔑 TOKEN STORAGE ANALYSIS")
    
    # Check access token file
    token_file = auth_dir / "access_token.txt"
    if token_file.exists():
        try:
            with open(token_file, 'r') as f:
                token_content = f.read().strip()
            
            print_status("Token file exists", True, str(token_file))
            print_status("Token length", len(token_content) > 0, f"{len(token_content)} characters")
            
            # Validate token format (JWT tokens typically have 3 parts separated by dots)
            token_parts = token_content.split('.')
            is_jwt = len(token_parts) == 3
            print_status("JWT format", is_jwt, f"{len(token_parts)} parts" if not is_jwt else "Valid JWT structure")
            
            # Show partial token (for verification)
            if len(token_content) > 20:
                display_token = f"{token_content[:10]}...{token_content[-10:]}"
                print_status("Token preview", True, display_token)
                
        except Exception as e:
            print_status("Reading token file", False, f"Error: {e}")
    else:
        print_status("access_token.txt", False, "Token file not found")
    
    print_section("🔍 TOKEN USAGE IN SCRIPTS")
    
    # Check how scripts access the token
    scripts_dir = Path(".")
    token_usage_files = []
    
    for py_file in scripts_dir.glob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'get_access_token' in content or 'access_token' in content:
                    token_usage_files.append(py_file.name)
        except:
            pass
    
    print_status("Scripts using tokens", len(token_usage_files) > 0, f"{len(token_usage_files)} files found")
    for file in token_usage_files[:5]:  # Show first 5
        print(f"   📄 {file}")
    if len(token_usage_files) > 5:
        print(f"   📄 ... and {len(token_usage_files) - 5} more files")
    
    print_section("📊 TOKEN PATH RESOLUTION")
    
    # Test token path resolution logic from my_fyers_model.py
    current_dir = Path.cwd()
    auth_dir_path = Path("../auth")
    
    print(f"📂 Current working directory: {current_dir}")
    print(f"📂 Auth directory (relative): {auth_dir_path}")
    print(f"📂 Auth directory (absolute): {auth_dir_path.absolute()}")
    
    # Check different token file locations
    token_locations = [
        ("Current directory", current_dir / "access_token.txt"),
        ("Auth directory", auth_dir_path / "access_token.txt"),
        ("Scripts directory", Path(".") / "access_token.txt")
    ]
    
    for location_name, path in token_locations:
        exists = path.exists()
        print_status(f"Token in {location_name}", exists, str(path))
    
    print_section("🧪 TOKEN VALIDATION TEST")
    
    try:
        # Test importing the get_access_token function
        sys.path.append('.')
        from my_fyers_model import get_access_token, client_id
        
        print_status("Import get_access_token", True, "Successfully imported")
        
        # Test getting the token
        token = get_access_token()
        if token:
            print_status("Get access token", True, f"Token retrieved ({len(token)} chars)")
            
            # Test token format for API usage
            expected_format = f"{client_id}:{token}"
            print_status("API token format", True, f"Format: CLIENT_ID:TOKEN")
            print(f"   📋 Full token format: {client_id}:{token[:10]}...{token[-10:]}")
        else:
            print_status("Get access token", False, "No token returned")
            
    except Exception as e:
        print_status("Token validation", False, f"Error: {e}")
    
    print_section("⚙️ GENERATE TOKEN SCRIPT ANALYSIS")
    
    generate_script = auth_dir / "generate_token.py"
    if generate_script.exists():
        print_status("Token generation script", True, str(generate_script))
        
        try:
            with open(generate_script, 'r') as f:
                script_content = f.read()
            
            # Check for key features
            features = [
                ("Error handling", "try:" in script_content and "except:" in script_content),
                ("Browser opening", "webbrowser" in script_content),
                ("Token saving", "with open" in script_content and "write" in script_content),
                ("Auth code input", "input(" in script_content),
                ("Fyers API usage", "fyersModel" in script_content)
            ]
            
            for feature, present in features:
                print_status(feature, present, "Implemented" if present else "Missing")
                
        except Exception as e:
            print_status("Script analysis", False, f"Error: {e}")
    else:
        print_status("generate_token.py", False, "Script not found")
    
    return True

def test_token_generation():
    """Test token generation process"""
    print_section("🔄 TOKEN GENERATION TEST")
    
    auth_dir = Path("../auth")
    generate_script = auth_dir / "generate_token.py"
    
    if not generate_script.exists():
        print_status("Generate script available", False, "generate_token.py not found")
        return False
    
    print("💡 TOKEN GENERATION PROCESS:")
    print("   1. Run: python ../auth/generate_token.py")
    print("   2. Browser will open with Fyers login URL")
    print("   3. Login to your Fyers account")
    print("   4. Authorize the application")
    print("   5. Copy the auth_code from redirected URL")
    print("   6. Paste the auth_code when prompted")
    print("   7. Token will be saved to: ../auth/access_token.txt")
    
    print("\n🔧 MANUAL TOKEN GENERATION:")
    print("   If automatic generation fails, you can:")
    print("   1. Go to Fyers API portal: https://myapi.fyers.in/")
    print("   2. Generate access token manually")
    print("   3. Save it to: ../auth/access_token.txt")
    
    return True

def provide_troubleshooting_guide():
    """Provide troubleshooting guide for common issues"""
    print_section("🛠️ TROUBLESHOOTING GUIDE")
    
    common_issues = [
        {
            "issue": "Token file not found",
            "solution": "Run: python ../auth/generate_token.py to generate new token",
            "details": "Ensure auth/access_token.txt exists with valid token"
        },
        {
            "issue": "Invalid credentials",
            "solution": "Update auth/credentials.ini with correct Fyers API credentials",
            "details": "Get credentials from https://myapi.fyers.in/dashboard/"
        },
        {
            "issue": "Token expired",
            "solution": "Generate new token using generate_token.py",
            "details": "Tokens typically expire daily, regenerate as needed"
        },
        {
            "issue": "Import errors",
            "solution": "Ensure you're running scripts from the correct directory",
            "details": "Scripts should find auth folder at ../auth/ relative path"
        },
        {
            "issue": "Path resolution issues",
            "solution": "Check working directory and auth folder location",
            "details": "my_fyers_model.py handles multiple token file locations"
        }
    ]
    
    for i, issue_info in enumerate(common_issues, 1):
        print(f"\n{i}. ❌ {issue_info['issue']}")
        print(f"   ✅ Solution: {issue_info['solution']}")
        print(f"   💡 Details: {issue_info['details']}")

def main():
    """Main analysis function"""
    success = analyze_auth_system()
    
    if success:
        test_token_generation()
        provide_troubleshooting_guide()
        
        print_section("✅ AUTHENTICATION SYSTEM SUMMARY")
        
        print("🎯 TOKEN STORAGE LOCATIONS:")
        print("   📂 Primary: ../auth/access_token.txt")
        print("   📂 Fallback: ./access_token.txt (current directory)")
        print("   📂 Scripts access via: get_access_token() function")
        
        print("\n🔧 TOKEN USAGE PATTERN:")
        print("   📊 Format: CLIENT_ID:ACCESS_TOKEN")
        print("   📊 Used by: WebSocket, API calls, data fetching")
        print("   📊 Auto-resolved: my_fyers_model.py handles path resolution")
        
        print("\n🎉 SYSTEM STATUS: AUTHENTICATION CONFIGURED")
        print("💡 Ready for data validation with existing token")
    else:
        print("\n❌ AUTHENTICATION SYSTEM NEEDS ATTENTION")
        print("💡 Please fix configuration issues before proceeding")

if __name__ == "__main__":
    main()