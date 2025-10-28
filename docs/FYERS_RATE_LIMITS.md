# Fyers API Rate Limits - Critical Information

## ⚠️ **CRITICAL: Rate Limit Policy**

Fyers has **strict rate limits** that can block your account for the **entire day** if violated.

## 📊 **Official Rate Limits**

| Timeframe    | Limit     | Notes                                      |
|--------------|-----------|-------------------------------------------|
| **Per Second** | 10 requests | Exceed = immediate 429 error             |
| **Per Minute** | 200 requests | Exceed = 429 error + violation count    |
| **Per Day**    | 100,000 requests | Very high - unlikely to hit            |

## 🚨 **THE CRITICAL RULE**

**If you exceed the per-minute limit MORE THAN 3 TIMES in a single day:**
- ❌ **You will be BLOCKED until MIDNIGHT (IST)**
- ❌ **No API calls will work (even valid ones)**
- ❌ **Generating a new token MAY NOT help**
- ❌ **You must wait until the next day**

## ✅ **Safe Request Patterns**

### **Conservative (Recommended)**
- **1 request per second** = 60 requests/minute
- Safe margin: 140 requests/minute below limit
- **Use this for production**

### **Moderate**
- **5 requests per second** = up to 150 requests/minute  
- Safe margin: 50 requests/minute below limit
- Use for batch operations

### **Maximum (Risky)**
- **10 requests per second** = 200 requests/minute
- No margin for error
- ⚠️ Any spike = violation

## 🛡️ **Our Implementation**

All market data API scripts use **1-second delays**:
```python
time.sleep(1.0)  # 1 second between requests = 60/min (safe)
```

### **Retry Strategy**
When 429 error occurs:
1. **Wait 60 seconds** (full minute to reset counter)
2. **Retry once**
3. **If still fails**: Assume daily block, stop trying

## 📋 **HTTP Status Codes**

| Code | Meaning                    | Action Required                          |
|------|----------------------------|------------------------------------------|
| 200  | Success                    | Continue normal operation                 |
| 400  | Bad request                | Check parameters                         |
| 401  | Authorization error        | Check credentials                        |
| 403  | Permission error           | Check API permissions                    |
| 429  | **Rate limit exceeded**    | **STOP! Wait 60s, then retry once**      |
| 500  | Internal server error      | Wait and retry                           |

## 🔧 **Common API Error Codes**

| Code  | Description                              | Solution                              |
|-------|------------------------------------------|---------------------------------------|
| -8    | Token expired                            | Generate new token                    |
| -15   | Invalid token                            | Check token format                    |
| -16   | Cannot authenticate token                | Regenerate token                      |
| -17   | Token invalid or expired                 | Generate new token                    |
| -50   | Invalid parameters                       | Check API documentation               |
| -300  | Invalid symbol                           | Verify symbol format (e.g., NSE:SBIN-EQ) |
| -429  | **Rate limit exceeded**                  | **CRITICAL: Daily block risk**        |

## 🎯 **Best Practices**

### **1. Always Add Delays**
```python
import time

# Before EVERY API call
time.sleep(1.0)  # Minimum 1 second
response = fyers.get_fyre_model().quotes(data=data)
```

### **2. Batch Processing**
```python
# Split large requests into batches
MAX_SYMBOLS = 50  # Fyers quotes API limit
for i in range(0, len(symbols), MAX_SYMBOLS):
    batch = symbols[i:i+MAX_SYMBOLS]
    response = get_quotes(batch)
    time.sleep(1.0)  # CRITICAL: delay between batches
```

### **3. Handle 429 Gracefully**
```python
if response.get('code') == 429:
    logger.error("Rate limit exceeded! Waiting 60 seconds...")
    time.sleep(60.0)  # Full minute
    response = retry_request()  # One retry only
    if response.get('code') == 429:
        logger.error("Still blocked - daily limit violated?")
        sys.exit(1)  # Stop execution
```

### **4. Track Request Count**
```python
class RateLimitTracker:
    def __init__(self):
        self.requests_this_minute = 0
        self.last_reset = time.time()
    
    def check_and_wait(self):
        # Reset counter every minute
        if time.time() - self.last_reset > 60:
            self.requests_this_minute = 0
            self.last_reset = time.time()
        
        # If approaching limit, wait
        if self.requests_this_minute >= 150:  # 50 below limit
            wait_time = 60 - (time.time() - self.last_reset)
            if wait_time > 0:
                time.sleep(wait_time)
                self.requests_this_minute = 0
                self.last_reset = time.time()
        
        self.requests_this_minute += 1
```

## 🆘 **If You Get Blocked**

### **Symptoms**
- All API calls return 429 error
- Retry after 60+ seconds still fails
- Different symbols/APIs all fail

### **Diagnosis**
1. Check token age: `ls -l auth/access_token.txt`
   - If > 24 hours old → Token expired (generate new)
   - If < 24 hours old → Likely daily block

2. Check current time vs midnight IST
   - Block clears at **00:00 IST (UTC+5:30)**

### **Solutions (in order)**

1. **Wait until midnight IST**
   - Most reliable solution
   - Block automatically clears

2. **Generate new token**
   ```bash
   cd auth
   python generate_token.py
   ```
   - May work if block is token-specific
   - May NOT work if block is IP-based

3. **Use different credentials**
   - Different Fyers account
   - Different API app ID
   - Last resort only

## 📅 **Token Management**

### **Token Lifespan**
- Tokens expire every **24 hours**
- Generate new token daily if running automated scripts

### **Token Generation**
```bash
cd auth
python generate_token.py
# Follow browser authentication
# Token saved to auth/access_token.txt
```

### **Check Token Age**
```powershell
# Windows PowerShell
Get-Item auth\access_token.txt | Select-Object Name, LastWriteTime

# If LastWriteTime > 24 hours ago → Regenerate
```

## 🎓 **Permission Requirements**

Ensure your Fyers API app has correct permissions:

| Permission Template      | Includes                                  |
|-------------------------|------------------------------------------|
| **Basic**               | Profile, Logout                          |
| **Transactions Info**   | Basic + Orders, Positions, Trades, etc.  |
| **Order Placement**     | Transactions + Place/Modify/Cancel       |
| **Market Data**         | All + Historical, Depth, Quotes          |

**For this project**: Use **Market Data** permission template.

## 📊 **Monitoring Rate Limits**

Create a monitoring script:
```python
import time
from datetime import datetime

class FyersRateLimitMonitor:
    def __init__(self):
        self.requests_today = 0
        self.requests_this_minute = []
        self.violations_today = 0
    
    def log_request(self):
        now = time.time()
        self.requests_today += 1
        self.requests_this_minute.append(now)
        
        # Clean old requests (> 1 minute ago)
        self.requests_this_minute = [
            r for r in self.requests_this_minute 
            if now - r < 60
        ]
        
        # Check for violation
        if len(self.requests_this_minute) > 200:
            self.violations_today += 1
            print(f"⚠️ VIOLATION {self.violations_today}/3")
            if self.violations_today >= 3:
                print("🚨 CRITICAL: Daily block imminent!")
                return False
        
        return True
    
    def get_stats(self):
        return {
            'requests_today': self.requests_today,
            'requests_this_minute': len(self.requests_this_minute),
            'violations_today': self.violations_today,
            'safe': self.violations_today < 3
        }
```

## 🔗 **Related Documentation**

- [Fyers API Documentation](https://myapi.fyers.in/docsv3)
- [Authentication Guide](./AUTHENTICATION.md)
- [Market Data API Reference](./MARKET_DATA_APIs.md)

## 📝 **Changelog**

- **2025-10-28**: Initial documentation based on official Fyers rate limits
- **Rate limits confirmed**: 10/sec, 200/min, 100k/day
- **Daily block policy**: 3 violations = blocked until midnight
