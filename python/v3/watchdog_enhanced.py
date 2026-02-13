#!/usr/bin/env python3
"""
Enhanced Watchdog System for Solar Heating System v3
Monitors network connectivity, MQTT communication, and system health
with automatic recovery and connection validation
"""

import asyncio
import json
import logging
import time
import subprocess
import signal
import sys
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from paho.mqtt import client as mqtt_client
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/solar_heating_watchdog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedWatchdogConfig:
    """Enhanced watchdog configuration with auto-recovery"""
    # Network monitoring
    ping_hosts: List[str] = None
    ping_interval: int = 30  # seconds
    ping_timeout: int = 10   # seconds
    
    # MQTT monitoring with enhanced settings
    mqtt_broker: str = "192.168.0.110"
    mqtt_port: int = 1883
    mqtt_username: str = "mqtt_beaches"
    mqtt_password: str = "uQX6NiZ.7R"
    mqtt_heartbeat_topic: str = "solar_heating_v3/heartbeat"
    mqtt_check_interval: int = 30  # Check every 30 seconds
    mqtt_timeout: int = 60  # 60 seconds timeout for heartbeat
    mqtt_keepalive: int = 60  # MQTT keepalive interval
    mqtt_clean_session: bool = True  # Clean session for reliable connections
    
    # Auto-recovery settings
    max_mqtt_failures: int = 3  # Max consecutive MQTT failures before restart
    connection_retry_delay: int = 10  # Seconds between connection retries
    watchdog_restart_interval: int = 86400  # Restart watchdog daily (24 hours)
    
    # System monitoring
    system_check_interval: int = 60  # seconds
    service_name: str = "solar_heating_v3"
    
    # Alerting
    max_failures: int = 3
    alert_interval: int = 300  # 5 minutes
    
    def __post_init__(self):
        if self.ping_hosts is None:
            self.ping_hosts = ["8.8.8.8", "1.1.1.1", "192.168.0.110"]

@dataclass
class EnhancedSystemStatus:
    """Enhanced system status with connection tracking"""
    network_healthy: bool = True
    mqtt_healthy: bool = True
    system_healthy: bool = True
    last_heartbeat: Optional[float] = None
    last_network_check: Optional[float] = None
    last_system_check: Optional[float] = None
    consecutive_failures: int = 0
    consecutive_mqtt_failures: int = 0
    uptime: float = 0.0
    mqtt_connection_count: int = 0
    last_watchdog_restart: float = 0.0

class EnhancedMQTTMonitor:
    """Enhanced MQTT monitor with auto-recovery"""
    
    def __init__(self, config: EnhancedWatchdogConfig, status: EnhancedSystemStatus):
        self.config = config
        self.status = status
        self.client = None
        self.connected = False
        self.last_heartbeat_time = None
        self.heartbeat_received = False
        self.connection_attempts = 0
        self.last_connection_time = 0
        
    async def check_mqtt(self) -> bool:
        """Enhanced MQTT connectivity check with auto-recovery"""
        try:
            # Check if we need to restart watchdog due to time
            if self._should_restart_watchdog():
                logger.info("Scheduled watchdog restart triggered")
                await self._restart_watchdog()
                return True
            
            # Check if we've received a heartbeat recently
            if self.last_heartbeat_time:
                time_since_heartbeat = time.time() - self.last_heartbeat_time
                if time_since_heartbeat < self.config.mqtt_timeout:
                    self.status.mqtt_healthy = True
                    self.status.last_heartbeat = self.last_heartbeat_time
                    self.status.consecutive_mqtt_failures = 0
                    logger.debug(f"MQTT healthy: Last heartbeat {time_since_heartbeat:.1f}s ago")
                    return True
                else:
                    logger.warning(f"MQTT unhealthy: No heartbeat for {time_since_heartbeat:.1f}s")
                    self.status.mqtt_healthy = False
                    self.status.consecutive_mqtt_failures += 1
                    
                    # Check if we need to restart due to consecutive failures
                    if self.status.consecutive_mqtt_failures >= self.config.max_mqtt_failures:
                        logger.warning(f"Too many consecutive MQTT failures ({self.status.consecutive_mqtt_failures}), attempting reconnection")
                        await self._force_reconnect()
                        return False
                    return False
            
            # If no heartbeat received yet, try to connect and listen
            if not self.connected:
                await self._connect_mqtt()
            
            # Wait a bit for potential heartbeat
            await asyncio.sleep(5)
            
            if self.heartbeat_received:
                self.status.mqtt_healthy = True
                self.status.last_heartbeat = self.last_heartbeat_time
                self.status.consecutive_mqtt_failures = 0
                return True
            else:
                self.status.mqtt_healthy = False
                self.status.consecutive_mqtt_failures += 1
                return False
                
        except Exception as e:
            logger.error(f"MQTT check error: {e}")
            self.status.mqtt_healthy = False
            self.status.consecutive_mqtt_failures += 1
            return False
    
    def _should_restart_watchdog(self) -> bool:
        """Check if watchdog should be restarted based on uptime"""
        if self.status.last_watchdog_restart == 0:
            self.status.last_watchdog_restart = time.time()
            return False
        
        uptime_since_restart = time.time() - self.status.last_watchdog_restart
        return uptime_since_restart >= self.config.watchdog_restart_interval
    
    async def _restart_watchdog(self):
        """Restart the watchdog service"""
        try:
            logger.info("Restarting watchdog service to prevent stale connections")
            result = subprocess.run(
                ["sudo", "systemctl", "restart", "solar_heating_watchdog"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info("Watchdog service restarted successfully")
                self.status.last_watchdog_restart = time.time()
            else:
                logger.error(f"Failed to restart watchdog: {result.stderr}")
        except Exception as e:
            logger.error(f"Error restarting watchdog: {e}")
    
    async def _force_reconnect(self):
        """Force MQTT reconnection"""
        try:
            logger.info("Forcing MQTT reconnection")
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
            
            self.connected = False
            self.heartbeat_received = False
            self.last_heartbeat_time = None
            
            # Wait before reconnecting
            await asyncio.sleep(self.config.connection_retry_delay)
            await self._connect_mqtt()
            
        except Exception as e:
            logger.error(f"Error during forced reconnection: {e}")
    
    async def _connect_mqtt(self):
        """Enhanced MQTT connection with better error handling"""
        try:
            # Prevent too frequent connection attempts
            if time.time() - self.last_connection_time < self.config.connection_retry_delay:
                return
            
            self.last_connection_time = time.time()
            self.connection_attempts += 1
            
            logger.info(f"Attempting MQTT connection (attempt {self.connection_attempts})")
            
            self.client = mqtt_client.Client(clean_session=self.config.mqtt_clean_session)
            self.client.username_pw_set(self.config.mqtt_username, self.config.mqtt_password)
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect
            
            # Set keepalive
            self.client.connect(self.config.mqtt_broker, self.config.mqtt_port, keepalive=self.config.mqtt_keepalive)
            self.client.loop_start()
            
            # Wait for connection with timeout
            timeout = 15
            while not self.connected and timeout > 0:
                await asyncio.sleep(0.1)
                timeout -= 0.1
            
            if self.connected:
                # Subscribe to heartbeat topic
                self.client.subscribe(self.config.mqtt_heartbeat_topic, 0)
                logger.info(f"MQTT connected and listening to {self.config.mqtt_heartbeat_topic}")
                self.status.mqtt_connection_count += 1
            else:
                logger.error("Failed to connect to MQTT broker")
                
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Enhanced MQTT connection callback"""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Enhanced MQTT disconnection callback"""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Enhanced MQTT message callback with validation"""
        if msg.topic == self.config.mqtt_heartbeat_topic:
            try:
                data = json.loads(msg.payload.decode())
                if data.get('status') == 'alive':
                    self.last_heartbeat_time = time.time()
                    self.heartbeat_received = True
                    logger.debug(f"Heartbeat received: {data.get('system_state', 'unknown')}")
            except Exception as e:
                logger.error(f"Error parsing heartbeat message: {e}")

# Rest of the classes would be similar to the original watchdog.py
# but with enhanced monitoring and auto-recovery features

class EnhancedWatchdogSystem:
    """Enhanced watchdog system with auto-recovery"""
    
    def __init__(self, config: EnhancedWatchdogConfig):
        self.config = config
        self.status = EnhancedSystemStatus()
        self.running = False
        
        # Initialize enhanced monitors
        self.mqtt_monitor = EnhancedMQTTMonitor(config, self.status)
        
        # Status tracking
        self.start_time = time.time()
        self.last_alert_time = 0
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    async def run(self):
        """Run the enhanced watchdog system"""
        logger.info("Starting Enhanced Solar Heating System Watchdog...")
        self.running = True
        
        try:
            while self.running:
                await self._health_check()
                await asyncio.sleep(self.config.mqtt_check_interval)
                
        except Exception as e:
            logger.error(f"Watchdog error: {e}")
        finally:
            await self._cleanup()
    
    async def _health_check(self):
        """Enhanced health check with auto-recovery"""
        try:
            # Update uptime
            self.status.uptime = time.time() - self.start_time
            
            # Run MQTT check with auto-recovery
            mqtt_ok = await self.mqtt_monitor.check_mqtt()
            
            # Update overall status
            if mqtt_ok:
                if self.status.consecutive_failures > 0:
                    logger.info("System recovered - MQTT communication restored")
                self.status.consecutive_failures = 0
            else:
                self.status.consecutive_failures += 1
                logger.warning(f"Health check failed (consecutive: {self.status.consecutive_failures})")
                
                if not mqtt_ok:
                    logger.error("MQTT communication issue detected")
                
                # Send alert if needed
                if (self.status.consecutive_failures >= self.config.max_failures and 
                    time.time() - self.last_alert_time > self.config.alert_interval):
                    await self._send_alert()
                    self.last_alert_time = time.time()
            
            # Log status periodically
            if int(time.time()) % 300 == 0:  # Every 5 minutes
                logger.info(f"Enhanced Watchdog Status - MQTT: {mqtt_ok}, Connections: {self.status.mqtt_connection_count}, Uptime: {self.status.uptime/3600:.1f}h")
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
    
    async def _send_alert(self):
        """Send enhanced alert about system issues"""
        try:
            alert_message = {
                "type": "enhanced_watchdog_alert",
                "timestamp": time.time(),
                "status": {
                    "mqtt": self.status.mqtt_healthy,
                    "consecutive_failures": self.status.consecutive_failures,
                    "mqtt_connection_count": self.status.mqtt_connection_count
                },
                "uptime": self.status.uptime,
                "auto_recovery": "enabled"
            }
            
            # Publish alert to MQTT if available
            if self.mqtt_monitor.connected:
                topic = f"{self.config.mqtt_heartbeat_topic}/alert"
                self.mqtt_monitor.client.publish(topic, json.dumps(alert_message))
                logger.warning(f"Enhanced alert sent to MQTT topic: {topic}")
            
            # Log alert
            logger.warning(f"ENHANCED WATCHDOG ALERT: {alert_message}")
            
        except Exception as e:
            logger.error(f"Failed to send enhanced alert: {e}")
    
    async def _cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up enhanced watchdog resources...")
        
        if self.mqtt_monitor.client:
            self.mqtt_monitor.client.loop_stop()
            self.mqtt_monitor.client.disconnect()
        
        logger.info("Enhanced watchdog shutdown complete")
    
    def _signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown"""
        logger.info(f"Received signal {signum}, shutting down enhanced watchdog...")
        self.running = False

async def main():
    """Main entry point for enhanced watchdog"""
    # Load enhanced configuration
    config = EnhancedWatchdogConfig()
    
    # Create and start enhanced watchdog
    watchdog = EnhancedWatchdogSystem(config)
    await watchdog.run()

if __name__ == "__main__":
    asyncio.run(main())












