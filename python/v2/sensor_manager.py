import numpy as np
import logging
import time
from typing import Optional, Dict, List
from hardware_interface import SequentHardware
from config import SENSOR_CONFIG

class SensorManager:
    def __init__(self, hardware: SequentHardware):
        self.hardware = hardware
        self.input_array = np.zeros((4, 8, 10))
        self.mqtt_rtd = np.zeros(9)
        self.mqtt_sun = np.zeros(3)
    
    def collect_sensor_data(self, iterations: int = 10):
        """Collect data from all configured sensors"""
        try:
            # Collect MegaBas data
            for i in range(1, 9):  # Inputs 1-8
                self._collect_megabas_data(i, iterations)
            
            # Collect RTD data
            for i in range(1, 9):  # Inputs 1-8
                self._collect_rtd_data(i, iterations)
                
        except Exception as e:
            logging.error(f"Error collecting sensor data: {e}")
    
    def _collect_megabas_data(self, input_pin: int, iterations: int):
        """Collect data from a specific MegaBas input"""
        for i in range(iterations):
            temp = self.hardware.read_megabas_temperature(input_pin)
            if temp is not None:
                self.input_array[self.hardware.megabas_stack-1, input_pin-1, i] = temp
            time.sleep(0.02)
    
    def _collect_rtd_data(self, input_pin: int, iterations: int):
        """Collect data from a specific RTD input"""
        for i in range(iterations):
            temp = self.hardware.read_rtd_temperature(input_pin)
            if temp is not None:
                self.input_array[self.hardware.rtd_stack, input_pin-1, i] = temp
            time.sleep(0.02)
    
    def get_averaged_temperature(self, stack: int, input_pin: int) -> float:
        """Get averaged temperature reading"""
        return round(self.input_array.mean(2)[stack, input_pin], 1)
    
    def update_mqtt_data(self, topic: str, data: Dict):
        """Update sensor data from MQTT messages"""
        if topic == "rtd/acctank":
            self.mqtt_rtd[0:8] = [data[f"RTD_{i}"] for i in range(1, 9)]
            self.mqtt_rtd[8] = data["T3"]
            self.mqtt_sun[0:3] = [data["T1"], data["T2"], data["T3"]]
