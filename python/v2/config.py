from dataclasses import dataclass
import os
import argparse

@dataclass
class MQTTConfig:
    broker: str = '192.168.0.110'
    port: int = 1883
    username: str = os.getenv('MQTT_USERNAME', os.getenv('SOLAR_MQTT_USERNAME', ''))
    password: str = os.getenv('MQTT_PASSWORD', os.getenv('SOLAR_MQTT_PASSWORD', ''))
    client_id_prefix: str = 'python-mqtt-tcp-pub-sub'
    sub_topics: list = None

    def __post_init__(self):
        if self.sub_topics is None:
            self.sub_topics = ["rtd/#", "hass/#"]

@dataclass
class SystemConfig:
    set_temp_tank_1: float = 70
    set_temp_tank_1_hysteres: float = 2
    dTStart_tank_1: float = 8
    dTStop_tank_1: float = 4
    kylning_kollektor: float = 90
    kylning_kollektor_hysteres: float = 4
    temp_kok: float = 150
    temp_kok_hysteres: float = 10
    loops: int = 10

# Hardware configuration
HARDWARE_CONFIG = {
    'relay_stack': 2,
    'megabas_stack': 3,
    'rtd_stack': 0,
    'sensor_mapping': {
        'T1': {'stack': 2, 'input': 6},  # Collector temp
        'T2': {'stack': 2, 'input': 7},  # Tank temp
        'T3': {'stack': 2, 'input': 8},  # Additional temp
    },
    'relays': {
        'pump': 1,
        'heater': 2,
        'test_switch': 3
    }
}

SENSOR_CONFIG = {
    'collector_temp': {'type': 'megabas', 'stack': 3, 'input': 6},
    'tank_temp': {'type': 'megabas', 'stack': 3, 'input': 7},
    'tank_sensors': [
        {'type': 'rtd', 'stack': 0, 'input': 1},
        {'type': 'rtd', 'stack': 0, 'input': 2},
        {'type': 'rtd', 'stack': 0, 'input': 3},
        {'type': 'rtd', 'stack': 0, 'input': 4},
        {'type': 'rtd', 'stack': 0, 'input': 5},
        {'type': 'rtd', 'stack': 0, 'input': 6},
        {'type': 'rtd', 'stack': 0, 'input': 7},
        {'type': 'rtd', 'stack': 0, 'input': 8},
    ]
}
