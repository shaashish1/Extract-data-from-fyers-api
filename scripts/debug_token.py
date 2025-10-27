#!/usr/bin/env python3
"""
Token Analysis and Path Debugging
=================================

Analyze the token file and understand the authentication flow
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import configparser

# Add scripts directory to Python path for imports
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.append(str(script_dir))


def analyze_token_setup():
    """Analyze current token setup and paths"""
    print("🔍 TOKEN ANALYSIS & PATH DEBUGGING")
    print("=" * 60)
    
    # Read config
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'auth', 'credentials.ini')
    config.read(os.path.abspath(config_path))
    
    file_name = config['fyers']['file_name']
    print(f"📋 Config file name: {file_name}")
    
    # Check possible token locations
    current_dir = os.getcwd()
    script_dir = os.path.dirname(__file__)
    
    # Possible token paths
    token_paths = [
        file_name,  # Current working directory
        os.path.abspath(file_name),  # Absolute path from cwd
        os.path.abspath(os.path.join(script_dir, '..', 'auth', file_name))  # Auth directory
    ]
    
    print(f"\n📂 POSSIBLE TOKEN PATHS:")
    print("-" * 40)
    for i, path in enumerate(token_paths, 1):
        exists = os.path.exists(path)
        if exists:
            stat = os.stat(path)
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            size = stat.st_size
            print(f"{i}. {path}")
            print(f"   ✅ EXISTS | Modified: {mod_time} | Size: {size} bytes")
            
            # Read first 50 characters to check if it looks like a JWT
            try:
                with open(path, 'r') as f:
                    content = f.read().strip()
                    preview = content[:50] + "..." if len(content) > 50 else content
                    print(f"   📄 Preview: {preview}")
                    
                    # Basic JWT validation (should start with eyJ)
                    if content.startswith('eyJ'):
                        print(f"   ✅ Looks like JWT token")
                        
                        # Try to extract expiry from token (basic parsing)
                        parts = content.split('.')
                        if len(parts) >= 2:
                            try:
                                import base64
                                import json
                                
                                # Decode payload (add padding if needed)
                                payload = parts[1]
                                # Add padding if needed
                                payload += '=' * (4 - len(payload) % 4)
                                decoded = base64.b64decode(payload)
                                token_data = json.loads(decoded)
                                
                                iat = token_data.get('iat', 0)
                                exp = token_data.get('exp', 0)
                                
                                if iat:
                                    issued = datetime.fromtimestamp(iat)
                                    print(f"   🕐 Issued: {issued}")
                                    
                                if exp:
                                    expires = datetime.fromtimestamp(exp)
                                    now = datetime.now()
                                    print(f"   ⏰ Expires: {expires}")
                                    
                                    if expires > now:
                                        remaining = expires - now
                                        print(f"   ✅ Valid for: {remaining}")
                                    else:
                                        expired_since = now - expires
                                        print(f"   ❌ Expired since: {expired_since}")
                                        
                            except Exception as e:
                                print(f"   ⚠️  Could not decode token details: {e}")
                    else:
                        print(f"   ❌ Does not look like JWT token")
                        
            except Exception as e:
                print(f"   ❌ Could not read file: {e}")
        else:
            print(f"{i}. {path}")
            print(f"   ❌ DOES NOT EXIST")
    
    print(f"\n🔧 AUTHENTICATION FLOW:")
    print("-" * 40)
    print(f"Current working directory: {current_dir}")
    print(f"Script directory: {script_dir}")
    
    # Test MyFyersModel token loading
    try:
        from my_fyers_model import get_access_token
        print(f"\n🧪 Testing get_access_token() function...")
        token = get_access_token()
        print(f"✅ Token loaded successfully")
        print(f"📏 Token length: {len(token)} characters")
        print(f"📄 Token preview: {token[:50]}...")
        
        # Test which file was actually used
        print(f"\n🔍 Determining which token file was used...")
        
    except Exception as e:
        print(f"❌ Error testing token loading: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    analyze_token_setup()