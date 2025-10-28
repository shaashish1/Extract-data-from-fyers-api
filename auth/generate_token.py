"""
FYERS Token Generator
Generates and saves FYERS access token dynamically.
Token valid for 24 hours.

Usage: python generate_token.py
"""
import json
import requests
import pyotp
import hashlib
from urllib import parse
import sys
import configparser
from pathlib import Path

def load_credentials():
    """Load credentials from credentials.ini file"""
    config = configparser.ConfigParser()
    credentials_file = Path(__file__).parent / "credentials.ini"
    
    if not credentials_file.exists():
        print("ERROR: credentials.ini not found in the same directory")
        print(f"Expected location: {credentials_file}")
        sys.exit(1)
    
    try:
        config.read(credentials_file)
        return config['FYERS_CREDENTIALS']
    except Exception as e:
        print(f"ERROR: Failed to read credentials.ini: {e}")
        sys.exit(1)

# API Endpoints
BASE_URL = "https://api-t2.fyers.in/vagator/v2"
BASE_URL_2 = "https://api-t1.fyers.in/api/v3"
URL_VERIFY_CLIENT_ID = BASE_URL + "/send_login_otp"
URL_VERIFY_TOTP = BASE_URL + "/verify_otp"
URL_VERIFY_PIN = BASE_URL + "/verify_pin"
URL_TOKEN = BASE_URL_2 + "/token"
URL_VALIDATE_AUTH_CODE = BASE_URL_2 + "/validate-authcode"

SUCCESS = 1
ERROR = -1

# Load credentials from credentials.ini
credentials = load_credentials()
CLIENT_ID = credentials['user_name']
PIN = f"{credentials['pin1']}{credentials['pin2']}{credentials['pin3']}{credentials['pin4']}"
APP_ID = credentials['client_id'].split("-")[0]
APP_TYPE = credentials['client_id'].split("-")[1]
APP_SECRET = credentials['secret_key']
TOTP_SECRET_KEY = credentials['totp_key']
REDIRECT_URI = credentials['redirect_uri']


def verify_client_id(client_id):
    """Step 1: Verify Client ID and Get Request Key"""
    try:
        payload = {"fy_id": client_id, "app_id": "2"}
        result_string = requests.post(url=URL_VERIFY_CLIENT_ID, json=payload)

        if result_string.status_code != 200:
            return [ERROR, result_string.text]

        result = json.loads(result_string.text)
        request_key = result["request_key"]
        return [SUCCESS, request_key]
    
    except Exception as e:
        return [ERROR, str(e)]
    

def generate_totp(secret):
    """Step 2: Generate TOTP"""
    try:
        generated_totp = pyotp.TOTP(secret).now()
        return [SUCCESS, generated_totp]
    except Exception as e:
        return [ERROR, str(e)]


def verify_totp(request_key, totp):
    """Step 3: Verify TOTP and Get New Request Key"""
    try:
        payload = {"request_key": request_key, "otp": totp}
        result_string = requests.post(url=URL_VERIFY_TOTP, json=payload)

        if result_string.status_code != 200:
            return [ERROR, result_string.text]

        result = json.loads(result_string.text)
        request_key = result["request_key"]
        return [SUCCESS, request_key]
    
    except Exception as e:
        return [ERROR, str(e)]


def verify_PIN(request_key, pin):
    """Step 4: Verify PIN and Get Access Token"""
    try:
        payload = {"request_key": request_key, "identity_type": "pin", "identifier": pin}
        result_string = requests.post(url=URL_VERIFY_PIN, json=payload)

        if result_string.status_code != 200:
            return [ERROR, result_string.text]

        result = json.loads(result_string.text)
        access_token = result["data"]["access_token"]
        return [SUCCESS, access_token]
    
    except Exception as e:
        return [ERROR, str(e)]


def token(client_id, app_id, redirect_uri, app_type, access_token):
    """Step 5: Get Auth Code or Final Token (API V3)"""
    try:
        payload = {
            "fyers_id": client_id,
            "app_id": app_id,
            "redirect_uri": redirect_uri,
            "appType": app_type,
            "code_challenge": "",
            "state": "sample_state",
            "scope": "",
            "nonce": "",
            "response_type": "code",
            "create_cookie": True
        }
        headers = {'Authorization': f'Bearer {access_token}'}
        result_string = requests.post(url=URL_TOKEN, json=payload, headers=headers)

        result = json.loads(result_string.text)
        
        # Handle both old (308 redirect) and new (200 OK) response formats
        if result_string.status_code == 308:
            # Old format: 308 redirect with Url containing auth_code
            url = result["Url"]
            auth_code = parse.parse_qs(parse.urlparse(url).query)['auth_code'][0]
            return [SUCCESS, auth_code]
        
        elif result_string.status_code == 200 and result.get('s') == 'ok':
            # New format: 200 OK with data.auth containing the token directly
            if 'data' in result and 'auth' in result['data']:
                # The 'auth' field IS the access token - no need for validate_authcode step
                final_token = result['data']['auth']
                return [SUCCESS, final_token]
            # Fallback: check for redirectUrl with auth_code
            elif 'data' in result and 'redirectUrl' in result['data']:
                url = result['data']['redirectUrl']
                parsed_url = parse.urlparse(url)
                query_params = parse.parse_qs(parsed_url.query)
                if 'auth_code' in query_params:
                    auth_code = query_params['auth_code'][0]
                    return [SUCCESS, auth_code]
                else:
                    return [ERROR, f"No auth_code in redirectUrl: {url}"]
            else:
                return [ERROR, f"Unexpected response format: {result_string.text}"]
        else:
            return [ERROR, result_string.text]
    
    except Exception as e:
        return [ERROR, str(e)]


def validate_authcode(client_id, app_secret, auth_code):
    """Step 6: Convert Auth Code to Access Token (when needed)"""
    try:
        payload = {
            "grant_type": "authorization_code",
            "appIdHash": hashlib.sha256(client_id.encode()).hexdigest(),
            "code": auth_code
        }
        headers = {'Authorization': f'Basic {app_secret}'}
        result_string = requests.post(url=URL_VALIDATE_AUTH_CODE, json=payload, headers=headers)

        if result_string.status_code != 200:
            return [ERROR, result_string.text]

        result = json.loads(result_string.text)
        access_token = result["access_token"]
        return [SUCCESS, access_token]
    
    except Exception as e:
        return [ERROR, str(e)]


def save_token_to_file(token, filename="access_token.txt"):
    """Save the access token to a file with UTF-8 encoding (no BOM)"""
    try:
        token_file = Path(__file__).parent / filename
        # CRITICAL: Use UTF-8 encoding without BOM to prevent token corruption
        token_file.write_text(token, encoding='utf-8')
        print(f"✅ Token saved to {token_file}")
        print(f"📏 Token length: {len(token)} characters")
        print(f"🔑 Token preview: {token[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Error saving token: {e}")
        return False


def main():
    """Main function to generate and save FYERS token"""
    print("🚀 Starting FYERS token generation...")
    
    # Step 1: Verify Client ID
    print("Step 1: Verifying Client ID...")
    result = verify_client_id(CLIENT_ID)
    if result[0] == ERROR:
        print(f"❌ Error verifying client ID: {result[1]}")
        return
    request_key = result[1]
    print("✅ Client ID verified")

    # Step 2: Generate TOTP
    print("Step 2: Generating TOTP...")
    result = generate_totp(TOTP_SECRET_KEY)
    if result[0] == ERROR:
        print(f"❌ Error generating TOTP: {result[1]}")
        return
    totp = result[1]
    print("✅ TOTP generated")

    # Step 3: Verify TOTP
    print("Step 3: Verifying TOTP...")
    result = verify_totp(request_key, totp)
    if result[0] == ERROR:
        print(f"❌ Error verifying TOTP: {result[1]}")
        return
    request_key = result[1]
    print("✅ TOTP verified")

    # Step 4: Verify PIN
    print("Step 4: Verifying PIN...")
    result = verify_PIN(request_key, PIN)
    if result[0] == ERROR:
        print(f"❌ Error verifying PIN: {result[1]}")
        return
    access_token = result[1]
    print("✅ PIN verified")

    # Step 5: Get final token
    print("Step 5: Getting final token...")
    result = token(CLIENT_ID, APP_ID, REDIRECT_URI, APP_TYPE, access_token)
    if result[0] == ERROR:
        print(f"❌ Error getting token: {result[1]}")
        return
    
    token_or_auth_code = result[1]
    
    # Check if we got a final token or need to validate auth code
    if len(token_or_auth_code) > 50:  # Likely a final token
        final_token = token_or_auth_code
        print("✅ Final token received directly")
    else:  # Likely an auth code that needs validation
        print("Step 6: Validating auth code...")
        result = validate_authcode(CLIENT_ID, APP_SECRET, token_or_auth_code)
        if result[0] == ERROR:
            print(f"❌ Error validating auth code: {result[1]}")
            return
        final_token = result[1]
        print("✅ Auth code validated")

    # Save token to file
    print("Step 7: Saving token...")
    if save_token_to_file(final_token):
        print(f"🎉 Token generation completed successfully!")
        print(f"💡 Token is valid for 24 hours")
        print(f"📁 Token saved as: access_token.txt")
    else:
        print("❌ Failed to save token to file")


if __name__ == "__main__":
    main()
