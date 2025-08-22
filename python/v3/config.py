"""
Configuration module for Solar Heating System v3
Based on PRD requirements and existing system parameters
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SystemConfig(BaseSettings):
    """System configuration based on PRD requirements"""
    
    # Hardware Configuration
    hardware_platform: str = Field(default="raspberry_pi_zero_2_w", description="Hardware platform")
    rtd_board_address: int = Field(default=0, description="RTD board address")
    megabas_board_address: int = Field(default=3, description="MegaBAS board address")
    relay_board_address: int = Field(default=2, description="Relay board address")
    
    # Temperature Monitoring Configuration
    temperature_update_interval: int = Field(default=30, description="Temperature reading interval in seconds")
    temperature_threshold_high: float = Field(default=80.0, description="High temperature threshold in Celsius")
    temperature_threshold_low: float = Field(default=20.0, description="Low temperature threshold in Celsius")
    
    # Solar Collector Configuration
    set_temp_tank_1: float = Field(default=70.0, description="Target tank temperature")
    set_temp_tank_1_hysteres: float = Field(default=2.0, description="Tank temperature hysteresis")
    dTStart_tank_1: float = Field(default=8.0, description="Temperature difference to start pump")
    dTStop_tank_1: float = Field(default=4.0, description="Temperature difference to stop pump")
    kylning_kollektor: float = Field(default=90.0, description="Collector cooling temperature")
    kylning_kollektor_hysteres: float = Field(default=4.0, description="Collector cooling hysteresis")
    temp_kok: float = Field(default=150.0, description="Boiling temperature threshold")
    temp_kok_hysteres: float = Field(default=10.0, description="Boiling temperature hysteresis")
    
    # MQTT Configuration
    mqtt_broker: str = Field(default="192.168.0.110", description="MQTT broker address")
    mqtt_port: int = Field(default=1883, description="MQTT broker port")
    mqtt_username: str = Field(default="mqtt_beaches", description="MQTT username")
    mqtt_password: str = Field(default="uQX6NiZ.7R", description="MQTT password")
    mqtt_client_id: str = Field(default="solar_heating_v3", description="MQTT client ID")
    
    # Home Assistant Integration
    hass_enabled: bool = Field(default=True, description="Enable Home Assistant integration")
    hass_discovery_prefix: str = Field(default="homeassistant", description="HA discovery prefix")
    
    # TaskMaster AI Configuration
    taskmaster_enabled: bool = Field(default=True, description="Enable TaskMaster AI integration")
    taskmaster_api_key: str = Field(default="", description="TaskMaster AI API key")
    taskmaster_base_url: str = Field(default="https://api.taskmaster.ai", description="TaskMaster AI base URL")
    
    # Database Configuration
    influxdb_enabled: bool = Field(default=True, description="Enable InfluxDB logging")
    influxdb_url: str = Field(default="http://localhost:8086", description="InfluxDB URL")
    influxdb_token: str = Field(default="", description="InfluxDB token")
    influxdb_org: str = Field(default="", description="InfluxDB organization")
    influxdb_bucket: str = Field(default="solar_heating", description="InfluxDB bucket")
    
    # System Operation
    test_mode: bool = Field(default=False, description="Enable test mode")
    debug_mode: bool = Field(default=False, description="Enable debug logging")
    log_level: str = Field(default="info", description="Logging level")
    
    # Performance Configuration
    max_concurrent_tasks: int = Field(default=5, description="Maximum concurrent tasks")
    ai_analysis_interval: int = Field(default=3600, description="AI analysis interval in seconds")
    
    class Config:
        env_file = ".env"
        env_prefix = "SOLAR_"

# Global configuration instance
config = SystemConfig()

@dataclass
class SensorMapping:
    """Sensor mapping configuration"""
    
    # RTD sensors (from existing system)
    solar_collector: int = 5  # T1 - sensor marked I
    storage_tank: int = 6     # T2 - sensor marked II
    return_line: int = 7      # T3 - sensor marked III
    
    # Additional temperature sensors
    heat_exchanger_in: int = 0
    heat_exchanger_out: int = 1
    storage_tank_top: int = 2
    storage_tank_bottom: int = 3
    ambient_air: int = 4
    
    # FTX sensors (from existing system)
    uteluft: int = 0          # sensor marked 4
    avluft: int = 1           # sensor marked 5
    tilluft: int = 2          # sensor marked 6
    franluft: int = 3         # sensor marked 7

@dataclass
class PumpConfiguration:
    """Pump control configuration"""
    
    primary_pump_relay: int = 1
    secondary_pump_relay: int = 2
    cartridge_heater_relay: int = 2
    test_switch_relay: int = 3
    
    # Pump control logic
    normally_closed: bool = True  # Relays are NC, so values are inverted in code
    
    def get_pump_status(self, relay_value: int) -> bool:
        """Get pump status from relay value considering NC configuration"""
        if self.normally_closed:
            return relay_value == 0
        return relay_value == 1
    
    def set_pump_status(self, status: bool) -> int:
        """Get relay value for desired pump status considering NC configuration"""
        if self.normally_closed:
            return 0 if status else 1
        return 1 if status else 0

@dataclass
class MQTTTopics:
    """MQTT topic configuration"""
    
    # System topics
    base_topic: str = "solar_heating_v3"
    
    # Temperature topics
    temperature_base: str = "temperature"
    temperature_solar_collector: str = "temperature/solar_collector"
    temperature_storage_tank: str = "temperature/storage_tank"
    temperature_return_line: str = "temperature/return_line"
    temperature_heat_exchanger: str = "temperature/heat_exchanger"
    
    # Control topics
    control_base: str = "control"
    control_pump: str = "control/pump"
    control_heater: str = "control/heater"
    
    # Status topics
    status_base: str = "status"
    status_system: str = "status/system"
    status_pump: str = "status/pump"
    status_energy: str = "status/energy"
    
    # Home Assistant topics
    hass_base: str = "hass"
    hass_config: str = "hass/config"
    hass_state: str = "hass/state"
    
    # TaskMaster AI topics
    taskmaster_base: str = "taskmaster"
    taskmaster_tasks: str = "taskmaster/tasks"
    taskmaster_recommendations: str = "taskmaster/recommendations"

# Global instances
sensor_mapping = SensorMapping()
pump_config = PumpConfiguration()
mqtt_topics = MQTTTopics()

# Calculated values (from existing system logic)
def get_calculated_values() -> Dict[str, float]:
    """Get calculated threshold values"""
    return {
        "set_temp_tank_1_gräns": config.set_temp_tank_1 - config.set_temp_tank_1_hysteres,
        "kylning_kollektor_hysteres_gräns": config.kylning_kollektor - config.kylning_kollektor_hysteres,
        "temp_kok_hysteres_gräns": config.temp_kok - config.temp_kok_hysteres,
    }

# System state constants
class SystemState:
    """System state constants"""
    STARTUP = "startup"
    NORMAL = "normal"
    MANUAL = "manual"
    OVERHEATED = "overheated"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class PumpState:
    """Pump state constants"""
    OFF = "off"
    ON = "on"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"

class ControlMode:
    """Control mode constants"""
    AUTO = "auto"
    MANUAL = "manual"
    TEST = "test"
    EMERGENCY = "emergency"
