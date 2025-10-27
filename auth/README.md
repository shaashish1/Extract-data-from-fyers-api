# FYERS Token Generator

This script generates and saves FYERS access tokens dynamically for automated trading.

## Setup Instructions

### 1. Configure Credentials

Edit the `credentials.ini` file and replace the placeholder values with your actual FYERS credentials:

```ini
[FYERS_CREDENTIALS]
# Your FYERS username/client ID
user_name = YOUR_FYERS_USERNAME

# Your FYERS client ID (format: APP_ID-APP_TYPE)
client_id = YOUR_CLIENT_ID-100

# Your FYERS secret key
secret_key = YOUR_SECRET_KEY

# Your 4-digit PIN (split into individual digits)
pin1 = 1
pin2 = 2  
pin3 = 3
pin4 = 4

# TOTP secret key from FYERS app
totp_key = YOUR_TOTP_SECRET_KEY

# Redirect URI (your app's callback URL)
redirect_uri = https://your-redirect-uri.com
```

### 2. Install Dependencies

```bash
pip install requests pyotp configparser
```

### 3. Run the Script

```bash
python generate_token.py
```

The script will:
1. Verify your client ID
2. Generate TOTP automatically
3. Verify TOTP and PIN
4. Generate and save the access token to `access_token.txt`

## Token Usage

The generated token is saved as `access_token.txt` and is valid for 24 hours. You can read this file in your trading scripts:

```python
from pathlib import Path

# Read the token
token_file = Path("access_token.txt")
if token_file.exists():
    access_token = token_file.read_text().strip()
    print(f"Using token: {access_token[:20]}...")
else:
    print("Token file not found. Please run generate_token.py first.")
```

## Security Notes

- Never commit `credentials.ini` or `access_token.txt` to version control
- Both files are automatically ignored by `.gitignore`
- Regenerate tokens daily as they expire after 24 hours

## Troubleshooting

1. **Credential errors**: Verify all fields in `credentials.ini` are correct
2. **TOTP errors**: Ensure your TOTP secret key is valid and time is synchronized
3. **PIN errors**: Check that your 4-digit PIN is entered correctly
4. **Network errors**: Verify internet connection and FYERS API status