"""
Fyers API Rate Limit Manager
=============================
Global rate limit protection to prevent API blocks.

Fyers Rate Limits:
- Per Second: 10 requests (we use max 5 for safety)
- Per Minute: 200 requests (we use max 150 for safety)
- Per Day: 100,000 requests (tracked but unlikely to hit)
- CRITICAL: 3 violations/day = BLOCKED UNTIL MIDNIGHT IST

Features:
- Automatic request throttling
- Violation tracking and prevention
- Thread-safe implementation
- Automatic cooldown periods
- Daily block prevention

Created: October 28, 2025
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RateLimitManager:
    """
    Thread-safe rate limit manager for Fyers API.
    
    Usage:
        from scripts.core.rate_limit_manager import get_rate_limiter
        
        limiter = get_rate_limiter()
        
        # Before making any API call
        limiter.wait_if_needed()
        response = fyers.get_fyre_model().quotes(data=data)
        limiter.record_request()
    """
    
    # Fyers API Limits
    MAX_REQUESTS_PER_SECOND = 5  # Conservative (actual: 10)
    MAX_REQUESTS_PER_MINUTE = 150  # Conservative (actual: 200)
    MAX_REQUESTS_PER_DAY = 90000  # Conservative (actual: 100,000)
    MAX_VIOLATIONS_PER_DAY = 2  # Block at 3, stop at 2 for safety
    
    def __init__(self):
        """Initialize the rate limit manager."""
        self._lock = threading.Lock()
        
        # Request tracking
        self._requests_per_second = []  # List of timestamps
        self._requests_per_minute = []
        self._requests_per_day = []
        
        # Violation tracking
        self._violations_today = 0
        self._last_violation_time = None
        self._daily_reset_time = self._get_next_midnight_ist()
        
        # Statistics
        self._total_requests = 0
        self._total_waits = 0
        self._total_wait_time = 0.0
        
        logger.info("Rate Limit Manager initialized")
        logger.info(f"Limits: {self.MAX_REQUESTS_PER_SECOND}/sec, "
                   f"{self.MAX_REQUESTS_PER_MINUTE}/min, "
                   f"{self.MAX_REQUESTS_PER_DAY}/day")
    
    def _get_next_midnight_ist(self) -> datetime:
        """Get next midnight IST for daily reset."""
        try:
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = datetime.now(ist)
            midnight = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
            if now_ist >= midnight:
                midnight += timedelta(days=1)
            return midnight
        except ImportError:
            # Fallback if pytz not available
            now = datetime.now()
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            midnight += timedelta(days=1)
            # Approximate IST adjustment (UTC+5:30)
            return midnight - timedelta(hours=5, minutes=30)
    
    def _clean_old_requests(self):
        """Remove old request timestamps outside tracking windows."""
        now = time.time()
        
        # Keep only last 1 second
        self._requests_per_second = [
            t for t in self._requests_per_second 
            if now - t < 1.0
        ]
        
        # Keep only last 60 seconds
        self._requests_per_minute = [
            t for t in self._requests_per_minute 
            if now - t < 60.0
        ]
        
        # Reset daily counter if past midnight IST
        try:
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            now_dt = datetime.now(ist)
        except ImportError:
            # Fallback without timezone awareness
            now_dt = datetime.now()
            if hasattr(self._daily_reset_time, 'tzinfo') and self._daily_reset_time.tzinfo:
                # Remove timezone from reset time for comparison
                self._daily_reset_time = self._daily_reset_time.replace(tzinfo=None)
        
        if now_dt >= self._daily_reset_time:
            logger.info("Daily reset triggered - clearing counters")
            self._requests_per_day = []
            self._violations_today = 0
            self._daily_reset_time = self._get_next_midnight_ist()
    
    def _get_current_rates(self) -> dict:
        """Get current request rates."""
        self._clean_old_requests()
        return {
            'per_second': len(self._requests_per_second),
            'per_minute': len(self._requests_per_minute),
            'per_day': len(self._requests_per_day),
            'violations': self._violations_today
        }
    
    def _calculate_wait_time(self) -> float:
        """
        Calculate how long to wait before next request.
        
        Returns:
            Wait time in seconds (0 if safe to proceed)
        """
        rates = self._get_current_rates()
        wait_times = []
        
        # Check per-second limit
        if rates['per_second'] >= self.MAX_REQUESTS_PER_SECOND:
            # Wait until oldest request in this second expires
            oldest = min(self._requests_per_second)
            wait_for_second = 1.0 - (time.time() - oldest)
            if wait_for_second > 0:
                wait_times.append(wait_for_second)
                logger.debug(f"Per-second limit reached ({rates['per_second']}/{self.MAX_REQUESTS_PER_SECOND})")
        
        # Check per-minute limit
        if rates['per_minute'] >= self.MAX_REQUESTS_PER_MINUTE:
            # Wait until oldest request in this minute expires
            oldest = min(self._requests_per_minute)
            wait_for_minute = 60.0 - (time.time() - oldest)
            if wait_for_minute > 0:
                wait_times.append(wait_for_minute)
                logger.warning(f"⚠️ Per-minute limit reached ({rates['per_minute']}/{self.MAX_REQUESTS_PER_MINUTE})")
                logger.warning(f"Waiting {wait_for_minute:.1f}s for cooldown...")
        
        # Check daily limit
        if rates['per_day'] >= self.MAX_REQUESTS_PER_DAY:
            logger.error(f"🚨 DAILY LIMIT REACHED ({rates['per_day']}/{self.MAX_REQUESTS_PER_DAY})!")
            logger.error("Waiting until midnight IST for reset...")
            time_until_midnight = (self._daily_reset_time - datetime.now()).total_seconds()
            wait_times.append(max(0, time_until_midnight))
        
        # Check violations
        if rates['violations'] >= self.MAX_VIOLATIONS_PER_DAY:
            logger.error(f"🚨 VIOLATION LIMIT REACHED ({rates['violations']}/{self.MAX_VIOLATIONS_PER_DAY})!")
            logger.error("⛔ STOPPING to prevent daily block!")
            raise RuntimeError(
                f"Rate limit violations: {rates['violations']}/{self.MAX_VIOLATIONS_PER_DAY}. "
                "Stopping to prevent Fyers API daily block. Wait until midnight IST."
            )
        
        return max(wait_times) if wait_times else 0.0
    
    def wait_if_needed(self, min_delay: float = 0.2) -> float:
        """
        Wait if necessary to stay within rate limits.
        
        Args:
            min_delay: Minimum delay between requests (default: 0.2s = 5 req/sec)
        
        Returns:
            Actual wait time in seconds
        """
        with self._lock:
            # Calculate required wait time
            wait_time = self._calculate_wait_time()
            
            # Apply minimum delay (conservative rate limiting)
            wait_time = max(wait_time, min_delay)
            
            if wait_time > 0:
                self._total_waits += 1
                self._total_wait_time += wait_time
                
                if wait_time > 1.0:
                    logger.info(f"⏰ Rate limit protection: waiting {wait_time:.1f}s")
                
                time.sleep(wait_time)
            
            return wait_time
    
    def record_request(self, success: bool = True):
        """
        Record a request after it's made.
        
        Args:
            success: Whether the request was successful (False if got 429)
        """
        with self._lock:
            now = time.time()
            
            self._requests_per_second.append(now)
            self._requests_per_minute.append(now)
            self._requests_per_day.append(now)
            self._total_requests += 1
            
            if not success:
                # Got 429 error - record violation
                self._violations_today += 1
                self._last_violation_time = datetime.now()
                
                logger.error(f"🚨 RATE LIMIT VIOLATION #{self._violations_today}")
                logger.error(f"⚠️ Warning: {3 - self._violations_today} violations remaining before daily block!")
                
                if self._violations_today >= self.MAX_VIOLATIONS_PER_DAY:
                    logger.error("⛔ Maximum violations reached - stopping execution")
    
    def get_statistics(self) -> dict:
        """Get current statistics."""
        with self._lock:
            rates = self._get_current_rates()
            
            try:
                import pytz
                ist = pytz.timezone('Asia/Kolkata')
                now_dt = datetime.now(ist)
            except ImportError:
                now_dt = datetime.now()
                if hasattr(self._daily_reset_time, 'tzinfo') and self._daily_reset_time.tzinfo:
                    self._daily_reset_time = self._daily_reset_time.replace(tzinfo=None)
            
            time_until_midnight = (self._daily_reset_time - now_dt).total_seconds()
            hours_until_midnight = time_until_midnight / 3600
            
            return {
                'total_requests': self._total_requests,
                'total_waits': self._total_waits,
                'total_wait_time': self._total_wait_time,
                'current_rates': rates,
                'limits': {
                    'per_second': self.MAX_REQUESTS_PER_SECOND,
                    'per_minute': self.MAX_REQUESTS_PER_MINUTE,
                    'per_day': self.MAX_REQUESTS_PER_DAY
                },
                'violations': self._violations_today,
                'max_violations': self.MAX_VIOLATIONS_PER_DAY + 1,  # Actual Fyers limit
                'daily_reset_in_hours': round(hours_until_midnight, 2),
                'is_safe': (rates['violations'] < self.MAX_VIOLATIONS_PER_DAY and 
                           rates['per_day'] < self.MAX_REQUESTS_PER_DAY)
            }
    
    def print_statistics(self):
        """Print formatted statistics."""
        stats = self.get_statistics()
        
        print("="*80)
        print("Fyers API Rate Limit Statistics")
        print("="*80)
        print(f"\n📊 Request Statistics:")
        print(f"   Total requests made: {stats['total_requests']}")
        print(f"   Total waits triggered: {stats['total_waits']}")
        print(f"   Total wait time: {stats['total_wait_time']:.1f}s")
        
        print(f"\n⚡ Current Rates:")
        rates = stats['current_rates']
        limits = stats['limits']
        print(f"   Per second: {rates['per_second']}/{limits['per_second']} "
              f"({rates['per_second']/limits['per_second']*100:.0f}%)")
        print(f"   Per minute: {rates['per_minute']}/{limits['per_minute']} "
              f"({rates['per_minute']/limits['per_minute']*100:.0f}%)")
        print(f"   Per day: {rates['per_day']}/{limits['per_day']} "
              f"({rates['per_day']/limits['per_day']*100:.1f}%)")
        
        print(f"\n⚠️  Violations:")
        print(f"   Today: {stats['violations']}/{stats['max_violations']}")
        if stats['violations'] > 0:
            print(f"   ⚠️ WARNING: {stats['max_violations'] - stats['violations']} violations until DAILY BLOCK!")
        
        print(f"\n⏰ Daily Reset:")
        print(f"   Resets in: {stats['daily_reset_in_hours']:.2f} hours")
        
        status = "✅ SAFE" if stats['is_safe'] else "⛔ AT RISK"
        print(f"\n🎯 Status: {status}")
        print("="*80)
    
    def reset_for_testing(self):
        """Reset all counters (for testing only)."""
        with self._lock:
            logger.warning("⚠️ Resetting rate limit counters (TESTING ONLY)")
            self._requests_per_second = []
            self._requests_per_minute = []
            self._requests_per_day = []
            self._violations_today = 0
            self._total_requests = 0
            self._total_waits = 0
            self._total_wait_time = 0.0


# Global singleton instance
_rate_limiter: Optional[RateLimitManager] = None
_limiter_lock = threading.Lock()


def get_rate_limiter() -> RateLimitManager:
    """
    Get the global rate limiter instance (thread-safe singleton).
    
    Returns:
        Global RateLimitManager instance
    """
    global _rate_limiter
    
    if _rate_limiter is None:
        with _limiter_lock:
            # Double-check locking pattern
            if _rate_limiter is None:
                _rate_limiter = RateLimitManager()
    
    return _rate_limiter


def demo_rate_limiter():
    """Demo: Show rate limiter in action."""
    print("="*80)
    print("Rate Limit Manager Demo")
    print("="*80)
    
    limiter = get_rate_limiter()
    
    print("\n📊 Simulating 10 rapid API calls...")
    for i in range(10):
        print(f"\nRequest #{i+1}")
        wait_time = limiter.wait_if_needed()
        print(f"   Waited: {wait_time:.3f}s")
        
        # Simulate API call
        time.sleep(0.01)  # Fake API response time
        
        limiter.record_request(success=True)
    
    print("\n" + "="*80)
    limiter.print_statistics()


if __name__ == "__main__":
    demo_rate_limiter()
