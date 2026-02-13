#!/usr/bin/env python3
"""
Robust Sensor Reader with Retry Logic and Exponential Backoff
Issue #50 Fix: Adds retry logic to sensor reads to handle transient errors

This module wraps the HardwareInterface sensor read methods with:
- Exponential backoff retry logic
- Configurable max retry attempts
- Detailed error logging
- Return of partial success indicators
"""

import time
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class RobustSensorReader:
    """Wrapper for sensor reads with retry logic and exponential backoff"""
    
    def __init__(self, hardware_interface, max_retries: int = 3, initial_backoff_ms: int = 50):
        """
        Initialize robust sensor reader
        
        Args:
            hardware_interface: HardwareInterface instance
            max_retries: Maximum retry attempts (default: 3)
            initial_backoff_ms: Initial backoff time in milliseconds (default: 50ms)
        """
        self.hardware = hardware_interface
        self.max_retries = max_retries
        self.initial_backoff_ms = initial_backoff_ms
        
        logger.info(f"RobustSensorReader initialized (max_retries={max_retries}, initial_backoff={initial_backoff_ms}ms)")
    
    def read_rtd_temperature_with_retry(self, sensor_id: int, stack: int = None) -> Tuple[Optional[float], int]:
        """
        Read RTD temperature with exponential backoff retry
        
        Args:
            sensor_id: Sensor ID (0-7)
            stack: Stack number (optional)
            
        Returns:
            Tuple of (temperature, attempts):
            - temperature: Temperature in Celsius or None if all retries failed
            - attempts: Number of attempts made (1 = success on first try)
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                temp = self.hardware.read_rtd_temperature(sensor_id, stack)
                
                if temp is not None:
                    # Success!
                    if attempt > 1:
                        logger.info(f"RTD sensor {sensor_id} read succeeded on attempt {attempt}")
                    return temp, attempt
                
                # None returned (validation failed or sensor error)
                last_error = "Validation failed or sensor returned None"
                
            except Exception as e:
                last_error = str(e)
                logger.debug(f"RTD sensor {sensor_id} attempt {attempt}/{self.max_retries} failed: {e}")
            
            # Apply exponential backoff if not last attempt
            if attempt < self.max_retries:
                backoff_ms = self.initial_backoff_ms * (2 ** (attempt - 1))
                logger.debug(f"RTD sensor {sensor_id} backing off for {backoff_ms}ms before retry")
                time.sleep(backoff_ms / 1000.0)
        
        # All retries exhausted
        logger.warning(
            f"RTD sensor {sensor_id} failed after {self.max_retries} attempts. "
            f"Last error: {last_error}"
        )
        return None, self.max_retries
    
    def read_megabas_temperature_with_retry(self, sensor_id: int, stack: int = None) -> Tuple[Optional[float], int]:
        """
        Read MegaBAS temperature with exponential backoff retry
        
        Args:
            sensor_id: Sensor ID (1-8)
            stack: Stack number (optional)
            
        Returns:
            Tuple of (temperature, attempts):
            - temperature: Temperature in Celsius or None if all retries failed
            - attempts: Number of attempts made (1 = success on first try)
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                temp = self.hardware.read_megabas_temperature(sensor_id, stack)
                
                if temp is not None:
                    # Success!
                    if attempt > 1:
                        logger.info(f"MegaBAS sensor {sensor_id} read succeeded on attempt {attempt}")
                    return temp, attempt
                
                # None returned (error value 60 or sensor error)
                last_error = "Sensor returned error value or None"
                
            except Exception as e:
                last_error = str(e)
                logger.debug(f"MegaBAS sensor {sensor_id} attempt {attempt}/{self.max_retries} failed: {e}")
            
            # Apply exponential backoff if not last attempt
            if attempt < self.max_retries:
                backoff_ms = self.initial_backoff_ms * (2 ** (attempt - 1))
                logger.debug(f"MegaBAS sensor {sensor_id} backing off for {backoff_ms}ms before retry")
                time.sleep(backoff_ms / 1000.0)
        
        # All retries exhausted
        logger.warning(
            f"MegaBAS sensor {sensor_id} failed after {self.max_retries} attempts. "
            f"Last error: {last_error}"
        )
        return None, self.max_retries
    
    def read_all_rtd_sensors(self) -> Tuple[Dict[str, Optional[float]], Dict[str, int]]:
        """
        Read all RTD sensors (0-7) with retry logic
        
        Returns:
            Tuple of (temperatures, attempts):
            - temperatures: Dict mapping sensor names to temperatures
            - attempts: Dict mapping sensor names to attempt counts
        """
        temperatures = {}
        attempts = {}
        
        for sensor_id in range(8):
            sensor_name = f'rtd_sensor_{sensor_id}'
            temp, attempt_count = self.read_rtd_temperature_with_retry(sensor_id)
            temperatures[sensor_name] = temp
            attempts[sensor_name] = attempt_count
        
        return temperatures, attempts
    
    def read_all_megabas_sensors(self) -> Tuple[Dict[str, Optional[float]], Dict[str, int]]:
        """
        Read all MegaBAS sensors (1-8) with retry logic
        
        Returns:
            Tuple of (temperatures, attempts):
            - temperatures: Dict mapping sensor names to temperatures
            - attempts: Dict mapping sensor names to attempt counts
        """
        temperatures = {}
        attempts = {}
        
        for sensor_id in range(1, 9):
            sensor_name = f'megabas_sensor_{sensor_id}'
            temp, attempt_count = self.read_megabas_temperature_with_retry(sensor_id)
            temperatures[sensor_name] = temp
            attempts[sensor_name] = attempt_count
        
        return temperatures, attempts
