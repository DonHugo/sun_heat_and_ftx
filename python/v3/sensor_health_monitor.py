#!/usr/bin/env python3
"""
Sensor Health Monitor for Solar Heating System v3
Tracks sensor health, last known good values, and error statistics

Issue #50 Fix: Provides robust sensor error handling with:
- Last known good value tracking
- Sensor health status monitoring
- Error statistics and alerting
- Graceful degradation support
"""

import time
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SensorHealthMonitor:
    """Monitor sensor health and track last known good values"""
    
    # Sensor health states
    STATUS_HEALTHY = "healthy"
    STATUS_DEGRADED = "degraded"  # Using last known good value
    STATUS_FAILED = "failed"      # No data available
    STATUS_UNKNOWN = "unknown"    # Not yet initialized
    
    def __init__(self, stale_threshold_seconds: int = 300):
        """
        Initialize sensor health monitor
        
        Args:
            stale_threshold_seconds: Seconds before last known value considered stale (default: 5 minutes)
        """
        self.stale_threshold = stale_threshold_seconds
        
        # Tracking dictionaries
        self._last_known_good = {}  # sensor_id -> (value, timestamp)
        self._error_counts = {}     # sensor_id -> consecutive_error_count
        self._total_errors = {}     # sensor_id -> total_error_count
        self._first_seen = {}       # sensor_id -> first_seen_timestamp
        self._last_success = {}     # sensor_id -> last_success_timestamp
        self._status = {}           # sensor_id -> current_status
        
        logger.info(f"SensorHealthMonitor initialized (stale threshold: {stale_threshold_seconds}s)")
    
    def record_reading(self, sensor_id: str, value: Optional[float]) -> Tuple[Optional[float], str]:
        """
        Record a sensor reading and return the value to use
        
        Args:
            sensor_id: Unique sensor identifier (e.g., 'rtd_sensor_0', 'megabas_sensor_1')
            value: Sensor reading (None if read failed)
            
        Returns:
            Tuple of (value_to_use, status):
            - value_to_use: The reading if valid, last known good if available, None otherwise
            - status: Current sensor health status
        """
        now = time.time()
        
        # Initialize tracking for new sensors
        if sensor_id not in self._first_seen:
            self._first_seen[sensor_id] = now
            self._error_counts[sensor_id] = 0
            self._total_errors[sensor_id] = 0
            self._status[sensor_id] = self.STATUS_UNKNOWN
        
        # Handle successful reading
        if value is not None:
            self._last_known_good[sensor_id] = (value, now)
            self._last_success[sensor_id] = now
            
            # Clear error count on success
            if self._error_counts[sensor_id] > 0:
                logger.info(f"Sensor {sensor_id} recovered after {self._error_counts[sensor_id]} errors")
            self._error_counts[sensor_id] = 0
            
            # Update status
            old_status = self._status[sensor_id]
            self._status[sensor_id] = self.STATUS_HEALTHY
            
            if old_status != self.STATUS_HEALTHY and old_status != self.STATUS_UNKNOWN:
                logger.info(f"Sensor {sensor_id} status changed: {old_status} -> {self.STATUS_HEALTHY}")
            
            return value, self.STATUS_HEALTHY
        
        # Handle failed reading
        self._error_counts[sensor_id] += 1
        self._total_errors[sensor_id] += 1
        
        # Check if we have a last known good value
        if sensor_id in self._last_known_good:
            last_value, last_timestamp = self._last_known_good[sensor_id]
            age_seconds = now - last_timestamp
            
            # Determine if value is still usable
            if age_seconds < self.stale_threshold:
                # Use last known good value
                old_status = self._status[sensor_id]
                self._status[sensor_id] = self.STATUS_DEGRADED
                
                if old_status != self.STATUS_DEGRADED:
                    logger.warning(
                        f"Sensor {sensor_id} degraded (error #{self._error_counts[sensor_id]}): "
                        f"Using last known good value {last_value}°C from {age_seconds:.0f}s ago"
                    )
                
                return last_value, self.STATUS_DEGRADED
            else:
                # Value too old, mark as failed
                old_status = self._status[sensor_id]
                self._status[sensor_id] = self.STATUS_FAILED
                
                if old_status != self.STATUS_FAILED:
                    logger.error(
                        f"Sensor {sensor_id} FAILED (error #{self._error_counts[sensor_id]}): "
                        f"Last good value {last_value}°C is {age_seconds:.0f}s old (threshold: {self.stale_threshold}s)"
                    )
                
                return None, self.STATUS_FAILED
        else:
            # No last known good value available
            self._status[sensor_id] = self.STATUS_FAILED
            logger.error(f"Sensor {sensor_id} FAILED: No last known good value available (error #{self._error_counts[sensor_id]})")
            return None, self.STATUS_FAILED
    
    def get_sensor_status(self, sensor_id: str) -> str:
        """Get current health status for a sensor"""
        return self._status.get(sensor_id, self.STATUS_UNKNOWN)
    
    def get_sensor_health_summary(self) -> Dict[str, Dict]:
        """
        Get comprehensive health summary for all sensors
        
        Returns:
            Dictionary with sensor health data for monitoring/alerting
        """
        now = time.time()
        summary = {
            'timestamp': datetime.now().isoformat(),
            'sensors': {},
            'statistics': {
                'total_sensors': len(self._status),
                'healthy': 0,
                'degraded': 0,
                'failed': 0,
                'unknown': 0
            }
        }
        
        for sensor_id in self._status:
            status = self._status[sensor_id]
            
            # Update statistics
            summary['statistics'][status] += 1
            
            # Sensor details
            sensor_info = {
                'status': status,
                'consecutive_errors': self._error_counts.get(sensor_id, 0),
                'total_errors': self._total_errors.get(sensor_id, 0),
                'first_seen': datetime.fromtimestamp(self._first_seen[sensor_id]).isoformat() if sensor_id in self._first_seen else None,
            }
            
            # Add last known good value info
            if sensor_id in self._last_known_good:
                value, timestamp = self._last_known_good[sensor_id]
                age_seconds = now - timestamp
                sensor_info['last_known_good'] = {
                    'value': value,
                    'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                    'age_seconds': round(age_seconds, 1),
                    'is_stale': age_seconds >= self.stale_threshold
                }
            
            # Add last success time
            if sensor_id in self._last_success:
                sensor_info['last_success'] = datetime.fromtimestamp(self._last_success[sensor_id]).isoformat()
                sensor_info['seconds_since_success'] = round(now - self._last_success[sensor_id], 1)
            
            summary['sensors'][sensor_id] = sensor_info
        
        return summary
    
    def get_failed_sensors(self) -> list:
        """Get list of sensor IDs that are currently failed"""
        return [sid for sid, status in self._status.items() if status == self.STATUS_FAILED]
    
    def get_degraded_sensors(self) -> list:
        """Get list of sensor IDs that are currently degraded"""
        return [sid for sid, status in self._status.items() if status == self.STATUS_DEGRADED]
    
    def reset_sensor_errors(self, sensor_id: str):
        """Reset error counters for a specific sensor (for testing/maintenance)"""
        if sensor_id in self._error_counts:
            self._error_counts[sensor_id] = 0
            logger.info(f"Reset error counter for sensor {sensor_id}")
    
    def should_alert(self, sensor_id: str, alert_threshold: int = 5) -> bool:
        """
        Check if sensor errors have reached alert threshold
        
        Args:
            sensor_id: Sensor to check
            alert_threshold: Number of consecutive errors before alerting
            
        Returns:
            True if alert should be sent
        """
        error_count = self._error_counts.get(sensor_id, 0)
        
        # Alert on threshold and every 10 errors after
        if error_count == alert_threshold:
            return True
        elif error_count > alert_threshold and error_count % 10 == 0:
            return True
        
        return False
