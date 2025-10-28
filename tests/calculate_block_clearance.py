"""
Calculate Fyers API Rate Limit Block Clearance Time
==================================================
Blocks clear at midnight IST (Indian Standard Time = UTC+5:30)
"""

from datetime import datetime, timedelta
import pytz

# Current time
now = datetime.now()

# IST timezone
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)

# Next midnight IST
midnight_ist = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
if now_ist.time() > midnight_ist.time():
    midnight_ist = midnight_ist + timedelta(days=1)

# Time remaining
time_until_clear = midnight_ist - now_ist

print("="*80)
print("Fyers API Rate Limit Block Clearance Calculator")
print("="*80)
print(f"\n📅 Current time (IST): {now_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"🕛 Next midnight (IST): {midnight_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"⏰ Time until block clears: {time_until_clear}")

hours, remainder = divmod(time_until_clear.seconds, 3600)
minutes, seconds = divmod(remainder, 60)
print(f"   = {hours} hours, {minutes} minutes, {seconds} seconds")

if time_until_clear.total_seconds() < 3600:  # Less than 1 hour
    print(f"\n✅ Block clears soon! Only {minutes} minutes remaining.")
elif time_until_clear.total_seconds() < 7200:  # Less than 2 hours
    print(f"\n⏰ Block clears in about {hours} hour(s). Not too long!")
else:
    print(f"\n⏳ Still {hours}+ hours until block clears. Consider:")
    print("   - Generating new token (may or may not work)")
    print("   - Testing symbol discovery (doesn't count toward rate limit)")
    print("   - Working on other parts of the project")
