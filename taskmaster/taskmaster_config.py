"""
TaskMaster AI Configuration for Solar Heating System
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class TaskMasterConfig:
    """Configuration for TaskMaster AI integration"""
    
    # TaskMaster AI settings
    taskmaster_api_key: str = os.getenv("TASKMASTER_API_KEY", "")
    taskmaster_base_url: str = os.getenv("TASKMASTER_BASE_URL", "https://api.taskmaster.ai")
    
    # System integration settings
    mqtt_broker: str = os.getenv("MQTT_BROKER", "localhost")
    mqtt_port: int = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_username: str = os.getenv("MQTT_USERNAME", "")
    mqtt_password: str = os.getenv("MQTT_PASSWORD", "")
    
    # Temperature monitoring settings
    temperature_threshold_high: float = float(os.getenv("TEMP_THRESHOLD_HIGH", "80.0"))
    temperature_threshold_low: float = float(os.getenv("TEMP_THRESHOLD_LOW", "20.0"))
    
    # Task definitions for solar heating system
    system_tasks: Dict[str, Any] = {
        "temperature_monitoring": {
            "description": "Monitor temperature sensors and trigger alerts",
            "frequency": "continuous",
            "priority": "high"
        },
        "pump_control": {
            "description": "Control water circulation pumps based on temperature",
            "frequency": "on_demand",
            "priority": "medium"
        },
        "valve_control": {
            "description": "Control valves for optimal heat distribution",
            "frequency": "on_demand", 
            "priority": "medium"
        },
        "data_logging": {
            "description": "Log system data for analysis and optimization",
            "frequency": "periodic",
            "priority": "low"
        },
        "system_optimization": {
            "description": "AI-powered system optimization recommendations",
            "frequency": "daily",
            "priority": "medium"
        }
    }
    
    # TaskMaster AI workflow settings
    enable_ai_optimization: bool = os.getenv("ENABLE_AI_OPTIMIZATION", "true").lower() == "true"
    ai_analysis_interval: int = int(os.getenv("AI_ANALYSIS_INTERVAL", "3600"))  # seconds
    max_concurrent_tasks: int = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        if not self.taskmaster_api_key:
            print("Warning: TASKMASTER_API_KEY not set")
            return False
        return True

# Global configuration instance
config = TaskMasterConfig()
