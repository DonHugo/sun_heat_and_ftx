"""
Solar Heating System v3 Package
Intelligent solar heating system with TaskMaster AI integration
"""

__version__ = "3.0.0"
__author__ = "Solar Heating System Team"
__description__ = "Solar Heating System with TaskMaster AI Integration"

from .config import config, sensor_mapping, pump_config, mqtt_topics
from .hardware_interface import HardwareInterface
from .mqtt_handler import MQTTHandler

__all__ = [
    'config',
    'sensor_mapping', 
    'pump_config',
    'mqtt_topics',
    'HardwareInterface',
    'MQTTHandler',
]
