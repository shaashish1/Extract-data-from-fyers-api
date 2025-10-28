# 🚫 NO MOCK DATA POLICY
**Critical Project Principle - Enforced Across All Development**

---

## ⚠️ **NEVER USE MOCK OR DUMMY CREDENTIALS**

This project uses **REAL credentials** everywhere - local development, CI/CD, testing, and production.

---

## 📋 **The Policy**

### ✅ **DO:**
1. **Commit real tokens** to git (`auth/access_token.txt`)
2. **Use actual Fyers API credentials** in all environments
3. **Test with live data** in GitHub Actions CI/CD
4. **Commit auth files** to repository
5. **Update tokens** when they expire (every 24 hours)

### ❌ **DON'T:**
1. **Create mock tokens** or dummy credentials
2. **Use environment variables** for secrets (adds complexity)
3. **Add auth files to .gitignore** (they should be tracked)
4. **Build mock/real switching logic** (unnecessary)
5. **Use fake data** for testing

---

## 🎯 **Rationale**

### 1. **Security Through Expiration** 🔒
- Fyers access tokens expire in **24 hours**
- Even if someone gets the token, it's useless after 24h
- Much safer than long-lived API keys

### 2. **Private Repository** 🔐
- Repository is **private** (no public exposure)
- Only authorized team members have access
- No risk of public credential leaks

### 3. **Real Data Testing** ✅
- CI/CD validates **actual API integration**
- Catches real-world issues immediately
- No "works in mock, fails in production" scenarios

### 4. **Production Parity** 🎯
- CI environment **identical to production**
- No environment-specific bugs
- What you test is what you deploy

### 5. **Simpler Architecture** 🚀
- No mock/real credential switching
- No environment variable management
- Less code = fewer bugs

---

## 🔄 **Token Management Workflow**

### Daily Operation:
```bash
# 1. Token expires after 24 hours
# 2. When you see authentication errors, regenerate:
python generate_token.py

# 3. Follow browser auth flow (manual step)
# Browser opens → Login to Fyers → Authorize app → Get auth code

# 4. Token automatically saved to auth/access_token.txt

# 5. Commit the new token
git add auth/access_token.txt
git commit -m "chore: refresh access token"
git push origin main

# 6. CI/CD automatically uses new token
```

### Token Lifetime:
- **Valid for:** 24 hours from generation
- **Update frequency:** Daily (or when expired)
- **Commit frequency:** Every time you regenerate
- **CI/CD impact:** Automatic (uses committed token)

---

## 🏗️ **Impact on Architecture**

### Before (Complex - Mock Data):
```
Local Dev → Uses real credentials
CI/CD → Uses mock credentials (different behavior!)
Production → Uses real credentials

Problems:
- 3 different credential sources
- Environment variable management
- Mock/real switching logic
- CI doesn't test real API
- Production bugs not caught in CI
```

### After (Simple - Real Data):
```
Local Dev → Uses auth/access_token.txt
CI/CD → Uses auth/access_token.txt (same file!)
Production → Uses auth/access_token.txt

Benefits:
- Single credential source
- No environment variables needed
- No switching logic
- CI tests real API
- Production parity guaranteed
```

---

## 📊 **CI/CD Integration**

### GitHub Actions Workflow:
```yaml
# System Validation Job
- name: 📦 Install Dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt

- name: 🔍 Run System Validation
  run: |
    echo "🔍 Running system validation with real credentials..."
    echo "ℹ️ Using committed auth files (tokens expire in 24 hours)"
    python tests/run_all_tests.py --validation-only

# NO mock credential creation
# NO environment variable secrets
# Just uses committed auth/access_token.txt
```

### What CI/CD Does:
1. ✅ Checks out repository (includes `auth/access_token.txt`)
2. ✅ Installs dependencies
3. ✅ Runs tests with **real Fyers API**
4. ✅ Validates actual integration
5. ✅ Reports real-world issues

### What CI/CD Doesn't Do:
1. ❌ Generate mock credentials
2. ❌ Use environment variables
3. ❌ Switch between mock/real
4. ❌ Test with fake data

---

## 🔐 **Security Considerations**

### Q: Isn't committing credentials dangerous?
**A:** No, because:
1. **24-hour expiration** - Token useless after 24h
2. **Private repository** - Only team access
3. **Read-only tokens** - Limited API permissions
4. **Audit trail** - Git history shows all token updates

### Q: What if someone steals the token?
**A:** Minimal risk:
1. **24-hour window** - Very short exposure
2. **Private repo required** - Need GitHub access first
3. **Limited scope** - Token only for market data, not trading
4. **Easy revocation** - Just regenerate and commit new token

### Q: Why not use GitHub Secrets?
**A:** Unnecessary complexity:
1. **Secrets are for long-lived credentials** (we have 24h tokens)
2. **Adds environment variable management** (more code)
3. **Complicates local development** (need to set secrets)
4. **Breaks production parity** (different credential sources)

---

## 🧪 **Testing Strategy**

### Unit Tests:
```python
# Use real authentication
from scripts.auth.my_fyers_model import MyFyersModel

def test_authentication():
    fyers = MyFyersModel()  # Uses real auth/access_token.txt
    assert fyers.client is not None
    # Tests real API connection
```

### Integration Tests:
```python
# Use real market data
def test_market_data_fetch():
    fyers = MyFyersModel()
    data = fyers.history({
        'symbol': 'NSE:SBIN-EQ',
        'resolution': 'D',
        'date_format': '1'
    })
    assert len(data['candles']) > 0
    # Tests actual Fyers API response
```

### CI/CD Tests:
```bash
# Run with real credentials
python tests/run_all_tests.py --validation-only

# No mock setup needed
# Just uses committed auth files
```

---

## 📝 **Code Examples**

### ✅ **CORRECT - Real Credentials:**
```python
# scripts/auth/my_fyers_model.py
class MyFyersModel:
    def __init__(self):
        # Reads real token from committed file
        self.token_file = Path(__file__).parent.parent.parent / 'auth' / 'access_token.txt'
        with open(self.token_file, 'r') as f:
            self.access_token = f.read().strip()
```

### ❌ **WRONG - Mock Credentials:**
```python
# DON'T DO THIS
class MyFyersModel:
    def __init__(self, use_mock=False):
        if use_mock:
            self.access_token = "fake_token_for_testing"  # WRONG!
        else:
            # Load real token...
```

### ❌ **WRONG - Environment Variables:**
```python
# DON'T DO THIS
import os
class MyFyersModel:
    def __init__(self):
        self.access_token = os.getenv('FYERS_TOKEN')  # WRONG!
        # Adds complexity, breaks simplicity
```

---

## 🚀 **Developer Onboarding**

### New Developer Setup:
```bash
# 1. Clone repository
git clone https://github.com/shaashish1/Extract-data-from-fyers-api.git
cd Extract-data-from-fyers-api

# 2. Check existing token
cat auth/access_token.txt
# Token is already there from git!

# 3. If token expired, regenerate
python generate_token.py
# Follow browser auth flow

# 4. Commit new token (if you regenerated)
git add auth/access_token.txt
git commit -m "chore: refresh access token"
git push

# 5. Start developing
# All scripts automatically use committed token
```

**No additional setup needed!** Token is in repository, ready to use.

---

## 📈 **Monitoring & Maintenance**

### Token Expiration Monitoring:
```python
# Check token expiration
import jwt
import datetime

with open('auth/access_token.txt') as f:
    token = f.read().strip()
    
decoded = jwt.decode(token, options={"verify_signature": False})
exp_timestamp = decoded['exp']
exp_date = datetime.datetime.fromtimestamp(exp_timestamp)

print(f"Token expires: {exp_date}")
print(f"Hours remaining: {(exp_date - datetime.datetime.now()).total_seconds() / 3600:.1f}")
```

### Automated Token Refresh (Optional):
```bash
# Add to daily cron job
0 9 * * * cd /path/to/project && python generate_token.py --headless && git add auth/access_token.txt && git commit -m "chore: daily token refresh" && git push
```

---

## 🎯 **Summary**

### The Policy in One Sentence:
**Use real Fyers credentials everywhere, commit them to git, update daily when expired.**

### Key Benefits:
1. ✅ **Security through expiration** (24h tokens)
2. ✅ **Simplicity** (single credential source)
3. ✅ **Production parity** (CI matches production)
4. ✅ **Real testing** (validates actual API)
5. ✅ **Team efficiency** (no credential management)

### What This Prevents:
1. ❌ Mock/real switching bugs
2. ❌ Environment variable complexity
3. ❌ "Works in dev, fails in production"
4. ❌ Credential management overhead
5. ❌ False sense of security with long-lived secrets

---

## 📚 **Related Documentation**
- [CI/CD Pipeline Guide](./CI_CD_PIPELINE_GUIDE.md) - How CI/CD uses real credentials
- [Copilot Instructions](../.github/copilot-instructions.md) - Development guidelines
- [Authentication Guide](../README.md#authentication) - Token generation process

---

**Policy Status:** ✅ **ACTIVE AND ENFORCED**  
**Last Updated:** October 28, 2025  
**Applies To:** All developers, CI/CD, testing, production  
**Exceptions:** None - This is a fundamental architectural decision
