#!/usr/bin/env python3
"""
Watchdog System for Solar Heating System v3
Monitors network connectivity, MQTT communication, and system health

Security: Issue #45 - Credentials loaded from environment variables
"""

import asyncio
import json
import logging
import os
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
class WatchdogConfig:
    """Watchdog configuration
    
    Security (Issue #45): Credentials must be set via environment variables:
    - MQTT_USERNAME or SOLAR_MQTT_USERNAME
    - MQTT_PASSWORD or SOLAR_MQTT_PASSWORD
    """
    # Network monitoring
    ping_hosts: List[str] = None
    ping_interval: int = 30  # seconds
    ping_timeout: int = 10   # seconds
    
    # MQTT monitoring
    mqtt_broker: str = "192.168.0.110"
    mqtt_port: int = 1883
    # Security: No default credentials - must be set from environment
    mqtt_username: str = None
    mqtt_password: str = None
    mqtt_heartbeat_topic: str = "solar_heating_v3/heartbeat"
    mqtt_check_interval: int = 60  # seconds
    mqtt_timeout: int = 30  # seconds
    
    # System monitoring
    system_check_interval: int = 60  # seconds
    service_name: str = "solar_heating_v3"
    
    # Alerting
    max_failures: int = 3
    alert_interval: int = 300  # 5 minutes
    
    def __post_init__(self):
        if self.ping_hosts is None:
            self.ping_hosts = ["8.8.8.8", "1.1.1.1", "192.168.0.1"]
        
        # Security (Issue #45): Load credentials from environment
        if self.mqtt_username is None:
            self.mqtt_username = os.getenv('MQTT_USERNAME') or os.getenv('SOLAR_MQTT_USERNAME')
        if self.mqtt_password is None:
            self.mqtt_password = os.getenv('MQTT_PASSWORD') or os.getenv('SOLAR_MQTT_PASSWORD')
        
        # Validate credentials are provided
        if not self.mqtt_username or not self.mqtt_password:
            raise ValueError(
                "MQTT credentials required. Set MQTT_USERNAME and MQTT_PASSWORD "
                "environment variables. See .env.example for template."
            )

@dataclass
class SystemStatus:
    """Current system status"""
    network_healthy: bool = True
    mqtt_healthy: bool = True
    system_healthy: bool = True
    last_heartbeat: Optional[float] = None
    last_network_check: Optional[float] = None
    last_system_check: Optional[float] = None
    consecutive_failures: int = 0
    uptime: float = 0.0

class NetworkMonitor:
    """Monitor network connectivity"""
    
    def __init__(self, config: WatchdogConfig):
        self.config = config
        self.status = SystemStatus()
    
    async def check_network(self) -> bool:
        """Check network connectivity by pinging hosts"""
        try:
            for host in self.config.ping_hosts:
                if await self._ping_host(host):
                    logger.debug(f"Network check passed: {host} is reachable")
                    self.status.network_healthy = True
                    self.status.last_network_check = time.time()
                    return True
            
            logger.warning("Network check failed: No hosts reachable")
            self.status.network_healthy = False
            self.status.last_network_check = time.time()
            return False
            
        except Exception as e:
            logger.error(f"Network check error: {e}")
            self.status.network_healthy = False
            self.status.last_network_check = time.time()
            return False
    
    async def _ping_host(self, host: str) -> bool:
        """Ping a specific host"""
        try:
            # Use subprocess to ping host
            result = subprocess.run(
                ["ping", "-c", "1", "-W", str(self.config.ping_timeout), host],
                capture_output=True,
                timeout=self.config.ping_timeout + 5
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.debug(f"Ping timeout for {host}")
            return False
        except Exception as e:
            logger.debug(f"Ping error for {host}: {e}")
            return False

class MQTTMonitor:
    """Monitor MQTT communication"""
    
    def __init__(self, config: WatchdogConfig):
        self.config = config
        self.status = SystemStatus()
        self.client = None
        self.connected = False
        self.last_heartbeat_time = None
        self.heartbeat_received = False
    
    async def check_mqtt(self) -> bool:
        """Check MQTT connectivity and heartbeat"""
        try:
            # Check if we've received a heartbeat recently
            if self.last_heartbeat_time:
                time_since_heartbeat = time.time() - self.last_heartbeat_time
                if time_since_heartbeat < self.config.mqtt_timeout:
                    self.status.mqtt_healthy = True
                    self.status.last_heartbeat = self.last_heartbeat_time
                    logger.debug(f"MQTT healthy: Last heartbeat {time_since_heartbeat:.1f}s ago")
                    return True
                else:
                    logger.warning(f"MQTT unhealthy: No heartbeat for {time_since_heartbeat:.1f}s")
                    self.status.mqtt_healthy = False
                    return False
            
            # If no heartbeat received yet, try to connect and listen
            if not self.connected:
                await self._connect_mqtt()
            
            # Wait a bit for potential heartbeat
            await asyncio.sleep(5)
            
            if self.heartbeat_received:
                self.status.mqtt_healthy = True
                self.status.last_heartbeat = self.last_heartbeat_time
                return True
            else:
                self.status.mqtt_healthy = False
                return False
                
        except Exception as e:
            logger.error(f"MQTT check error: {e}")
            self.status.mqtt_healthy = False
            return False
    
    async def _connect_mqtt(self):
        """Connect to MQTT broker and listen for heartbeats"""
        try:
            self.client = mqtt_client.Client()
            self.client.username_pw_set(self.config.mqtt_username, self.config.mqtt_password)
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect
            
            self.client.connect(self.config.mqtt_broker, self.config.mqtt_port, keepalive=60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                await asyncio.sleep(0.1)
                timeout -= 0.1
            
            if self.connected:
                # Subscribe to heartbeat topic
                self.client.subscribe(self.config.mqtt_heartbeat_topic, 0)
                logger.info(f"MQTT connected and listening to {self.config.mqtt_heartbeat_topic}")
            else:
                logger.error("Failed to connect to MQTT broker")
                
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
        else:
            self.connected = False
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        logger.info(f"Disconnected from MQTT broker: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        if msg.topic == self.config.mqtt_heartbeat_topic:
            try:
                data = json.loads(msg.payload.decode())
                if data.get('status') == 'alive':
                    self.last_heartbeat_time = time.time()
                    self.heartbeat_received = True
                    logger.debug("Heartbeat received")
            except Exception as e:
                logger.error(f"Error parsing heartbeat message: {e}")

class SystemMonitor:
    """Monitor system service health"""
    
    def __init__(self, config: WatchdogConfig):
        self.config = config
        self.status = SystemStatus()
    
    async def check_system(self) -> bool:
        """Check if the solar heating service is running"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", self.config.service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            is_active = result.stdout.strip() == "active"
            self.status.system_healthy = is_active
            self.status.last_system_check = time.time()
            
            if is_active:
                logger.debug(f"System service {self.config.service_name} is active")
            else:
                logger.warning(f"System service {self.config.service_name} is not active")
            
            return is_active
            
        except Exception as e:
            logger.error(f"System check error: {e}")
            self.status.system_healthy = False
            self.status.last_system_check = time.time()
            return False

class WatchdogSystem:
    """Main watchdog system"""
    
    def __init__(self, config: WatchdogConfig):
        self.config = config
        self.status = SystemStatus()
        self.running = False
        
        # Initialize monitors
        self.network_monitor = NetworkMonitor(config)
        self.mqtt_monitor = MQTTMonitor(config)
        self.system_monitor = SystemMonitor(config)
        
        # Status tracking
        self.start_time = time.time()
        self.last_alert_time = 0
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down watchdog...")
        self.running = False
    
    async def start(self):
        """Start the watchdog system"""
        logger.info("Starting Solar Heating System Watchdog...")
        self.running = True
        self.start_time = time.time()
        
        try:
            while self.running:
                await self._run_health_checks()
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except Exception as e:
            logger.error(f"Watchdog error: {e}")
        finally:
            await self._cleanup()
    
    async def _run_health_checks(self):
        """Run all health checks"""
        try:
            # Update uptime
            self.status.uptime = time.time() - self.start_time
            
            # Run checks
            network_ok = await self.network_monitor.check_network()
            mqtt_ok = await self.mqtt_monitor.check_mqtt()
            system_ok = await self.system_monitor.check_system()
            
            # Update overall status
            overall_healthy = network_ok and mqtt_ok and system_ok
            
            if overall_healthy:
                if self.status.consecutive_failures > 0:
                    logger.info("System recovered - all checks passed")
                self.status.consecutive_failures = 0
            else:
                self.status.consecutive_failures += 1
                logger.warning(f"Health check failed (consecutive: {self.status.consecutive_failures})")
                
                # Log specific issues
                if not network_ok:
                    logger.error("Network connectivity issue detected")
                if not mqtt_ok:
                    logger.error("MQTT communication issue detected")
                if not system_ok:
                    logger.error("System service issue detected")
                
                # Send alert if needed
                if (self.status.consecutive_failures >= self.config.max_failures and 
                    time.time() - self.last_alert_time > self.config.alert_interval):
                    await self._send_alert()
                    self.last_alert_time = time.time()
            
            # Log status periodically
            if int(time.time()) % 300 == 0:  # Every 5 minutes
                logger.info(f"Watchdog Status - Network: {network_ok}, MQTT: {mqtt_ok}, System: {system_ok}")
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
    
    async def _send_alert(self):
        """Send alert about system issues"""
        try:
            alert_message = {
                "type": "watchdog_alert",
                "timestamp": time.time(),
                "status": {
                    "network": self.network_monitor.status.network_healthy,
                    "mqtt": self.mqtt_monitor.status.mqtt_healthy,
                    "system": self.system_monitor.status.system_healthy
                },
                "consecutive_failures": self.status.consecutive_failures,
                "uptime": self.status.uptime
            }
            
            # Publish alert to MQTT if available
            if self.mqtt_monitor.connected:
                topic = f"{self.config.mqtt_heartbeat_topic}/alert"
                self.mqtt_monitor.client.publish(topic, json.dumps(alert_message))
                logger.warning(f"Alert sent to MQTT topic: {topic}")
            
            # Log alert
            logger.warning(f"WATCHDOG ALERT: {alert_message}")
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def _cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up watchdog resources...")
        
        if self.mqtt_monitor.client:
            self.mqtt_monitor.client.loop_stop()
            self.mqtt_monitor.client.disconnect()
        
        logger.info("Watchdog shutdown complete")

async def main():
    """Main entry point"""
    # Load configuration
    config = WatchdogConfig()
    
    # Create and start watchdog
    watchdog = WatchdogSystem(config)
    
    try:
        await watchdog.start()
    except KeyboardInterrupt:
        logger.info("Watchdog interrupted by user")
    except Exception as e:
        logger.error(f"Watchdog error: {e}")
    finally:
        await watchdog._cleanup()

if __name__ == "__main__":
    asyncio.run(main())
