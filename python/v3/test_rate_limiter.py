"""
Simple test for rate limiter (Issue #47)
"""

import time
from rate_limiter import SimpleRateLimiter

def test_rate_limiter():
    """Test rate limiter basic functionality"""
    print("Testing Rate Limiter (Issue #47)")
    print("=" * 50)
    
    # Create rate limiter with low limits for testing
    limiter = SimpleRateLimiter(
        default_limit=5,       # 5 requests per window
        window_seconds=10,     # 10 second window
        burst_limit=3,         # 3 requests per second
        burst_window=1         # 1 second burst window
    )
    
    test_ip = "192.168.1.100"
    test_endpoint = "/api/test"
    
    print(f"\nTest 1: Normal requests (should allow 5 in 10s)")
    for i in range(6):
        allowed, info = limiter.is_allowed(test_ip, test_endpoint)
        print(f"  Request {i+1}: {'ALLOWED' if allowed else 'BLOCKED'} - Remaining: {info['remaining']}/{info['limit']}")
        if i < 4:
            time.sleep(0.2)  # Small delay between requests
    
    print(f"\nTest 2: Burst protection (should block after 3 in 1s)")
    limiter2 = SimpleRateLimiter(burst_limit=3, burst_window=1)
    test_ip2 = "192.168.1.101"
    
    for i in range(5):
        allowed, info = limiter2.is_allowed(test_ip2, test_endpoint)
        status = 'ALLOWED' if allowed else f'BLOCKED ({info.get("limit_type", "unknown")})'
        print(f"  Burst request {i+1}: {status}")
    
    print(f"\nTest 3: Statistics")
    stats = limiter.get_stats()
    print(f"  Total tracked IPs: {stats['total_tracked_ips']}")
    print(f"  Total violations: {stats['total_violations']}")
    
    ip_stats = limiter.get_stats(test_ip)
    print(f"  IP {test_ip}: {ip_stats['active_requests']} active, {ip_stats['violations']} violations")
    
    print(f"\nTest 4: Custom endpoint limits")
    limiter3 = SimpleRateLimiter(default_limit=10)
    limiter3.set_endpoint_limit('/api/status', limit=20, window=60)
    
    allowed, info = limiter3.is_allowed("192.168.1.102", "/api/status")
    print(f"  /api/status limit: {info['limit']} req/{info['window']}s")
    
    allowed, info = limiter3.is_allowed("192.168.1.102", "/api/control")
    print(f"  /api/control limit: {info['limit']} req/{info['window']}s (default)")
    
    print("\n" + "=" * 50)
    print("Rate limiter tests completed!")

if __name__ == '__main__':
    test_rate_limiter()
