"""
Rate Limiting Implementation for API Server (Issue #47)

Simple in-memory rate limiter with sliding window algorithm.
For production use with multiple instances, consider Redis-based limiter.
"""

import logging
import time
from collections import defaultdict
from typing import Dict, Any, Tuple, Optional
from flask import request, jsonify

from api_errors import APIErrorCode, create_error_response

logger = logging.getLogger(__name__)


class SimpleRateLimiter:
    """
    Simple in-memory rate limiter for API endpoints (Issue #47)
    
    Implements sliding window rate limiting per IP address.
    """
    
    def __init__(self, 
                 default_limit: int = 60,
                 window_seconds: int = 60,
                 burst_limit: int = 10,
                 burst_window: int = 1):
        """
        Initialize rate limiter
        
        Args:
            default_limit: Maximum requests per window (default: 60/min)
            window_seconds: Time window in seconds (default: 60)
            burst_limit: Maximum requests in burst window (default: 10/sec)
            burst_window: Burst time window in seconds (default: 1)
        """
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self.burst_limit = burst_limit
        self.burst_window = burst_window
        
        # Track requests: {ip: [(timestamp, endpoint), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        
        # Track violations for logging
        self.violations = defaultdict(int)
        
        # Custom limits per endpoint: {endpoint: (limit, window)}
        self.endpoint_limits: Dict[str, Tuple[int, int]] = {}
        
        logger.info(f"Rate limiter initialized: {default_limit} req/{window_seconds}s, burst: {burst_limit} req/{burst_window}s")
    
    def set_endpoint_limit(self, endpoint: str, limit: int, window: int = 60):
        """Set custom rate limit for specific endpoint"""
        self.endpoint_limits[endpoint] = (limit, window)
        logger.info(f"Custom limit set for {endpoint}: {limit} req/{window}s")
    
    def _cleanup_old_requests(self, ip: str, current_time: float):
        """Remove requests outside the time window"""
        if ip not in self.requests:
            return
        
        # Keep only requests within the longest window
        max_window = max(self.window_seconds, self.burst_window)
        cutoff = current_time - max_window
        
        self.requests[ip] = [
            (ts, endpoint) for ts, endpoint in self.requests[ip]
            if ts > cutoff
        ]
        
        # Clean up empty entries
        if not self.requests[ip]:
            del self.requests[ip]
    
    def is_allowed(self, ip: str, endpoint: str = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed
        
        Returns:
            (allowed, info_dict) where info_dict contains:
            - limit: applicable rate limit
            - remaining: requests remaining
            - reset: timestamp when limit resets
            - retry_after: seconds to wait (if blocked)
        """
        current_time = time.time()
        
        # Cleanup old requests
        self._cleanup_old_requests(ip, current_time)
        
        # Get applicable limits
        if endpoint and endpoint in self.endpoint_limits:
            limit, window = self.endpoint_limits[endpoint]
        else:
            limit, window = self.default_limit, self.window_seconds
        
        # Count requests in window
        window_cutoff = current_time - window
        window_requests = [
            ts for ts, _ in self.requests.get(ip, [])
            if ts > window_cutoff
        ]
        window_count = len(window_requests)
        
        # Count requests in burst window
        burst_cutoff = current_time - self.burst_window
        burst_requests = [
            ts for ts, _ in self.requests.get(ip, [])
            if ts > burst_cutoff
        ]
        burst_count = len(burst_requests)
        
        # Calculate reset time
        if window_requests:
            reset_time = min(window_requests) + window
        else:
            reset_time = current_time + window
        
        # Check limits
        info = {
            'limit': limit,
            'remaining': max(0, limit - window_count - 1),
            'reset': int(reset_time),
            'window': window
        }
        
        # Check burst limit first
        if burst_count >= self.burst_limit:
            self.violations[ip] += 1
            info['retry_after'] = int(self.burst_window)
            info['limit_type'] = 'burst'
            logger.warning(f"Rate limit exceeded (burst) for {ip}: {burst_count}/{self.burst_limit} in {self.burst_window}s (violation #{self.violations[ip]})")
            return False, info
        
        # Check window limit
        if window_count >= limit:
            self.violations[ip] += 1
            info['retry_after'] = int(reset_time - current_time)
            info['limit_type'] = 'window'
            logger.warning(f"Rate limit exceeded (window) for {ip}: {window_count}/{limit} in {window}s (violation #{self.violations[ip]})")
            return False, info
        
        # Allowed - record request
        self.requests[ip].append((current_time, endpoint))
        return True, info
    
    def get_stats(self, ip: str = None) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        if ip:
            return {
                'ip': ip,
                'active_requests': len(self.requests.get(ip, [])),
                'violations': self.violations.get(ip, 0)
            }
        else:
            return {
                'total_tracked_ips': len(self.requests),
                'total_violations': sum(self.violations.values()),
                'top_violators': sorted(
                    self.violations.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }
    
    def reset_violations(self, ip: str = None):
        """Reset violation counter"""
        if ip:
            self.violations[ip] = 0
        else:
            self.violations.clear()


# Global rate limiter instance
api_rate_limiter: Optional[SimpleRateLimiter] = None


def check_rate_limit():
    """
    Check rate limit for current request
    Returns None if allowed, Flask response if blocked
    """
    if api_rate_limiter is None:
        return None  # Rate limiting not initialized
    
    # Get client IP (handles proxy headers)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    
    endpoint = request.endpoint
    
    # Check rate limit
    allowed, info = api_rate_limiter.is_allowed(ip, endpoint)
    
    # Store info for adding headers later
    request.rate_limit_info = info
    
    if not allowed:
        # Rate limit exceeded - return error response
        error_response = create_error_response(
            code=APIErrorCode.RATE_LIMIT_EXCEEDED,
            message=f"Rate limit exceeded. Try again in {info.get('retry_after', 60)} seconds.",
            details={
                'limit': info['limit'],
                'window': info['window'],
                'retry_after': info.get('retry_after', 60),
                'limit_type': info.get('limit_type', 'unknown')
            },
            status_code=429
        )
        # Add rate limit headers
        error_response.headers['X-RateLimit-Limit'] = str(info['limit'])
        error_response.headers['X-RateLimit-Remaining'] = '0'
        error_response.headers['X-RateLimit-Reset'] = str(info['reset'])
        error_response.headers['Retry-After'] = str(info.get('retry_after', 60))
        return error_response
    
    return None  # Allowed


def add_rate_limit_headers(response):
    """Add rate limit headers to response"""
    if hasattr(request, 'rate_limit_info'):
        info = request.rate_limit_info
        response.headers['X-RateLimit-Limit'] = str(info['limit'])
        response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
        response.headers['X-RateLimit-Reset'] = str(info['reset'])
    return response
