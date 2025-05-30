import logging
import lib4relind
import librtd
import megabas as m
from typing import Optional
from config import HARDWARE_CONFIG

class TemperatureLookup:
    def __init__(self):
        self.limits = [882.2, 921.6, 960.9, 1000, 1039, 1077.9, 1116.7, 1155.4, 1194, 
                      1232.4, 1270.8, 1309, 1347.1, 1385.1, 1422.9, 1460.7, 1498.3, 
                      1535.8, 1573.3, 1610.5, 1647.7, 1684.8]
        self.deltas = [4, 3.9, 3.9, 3.9, 3.89, 3.88, 3.87, 3.86, 3.84, 3.84, 3.82, 
                      3.81, 3.8, 3.78, 3.78, 3.76, 3.75, 3.75, 3.72, 3.72, 3.71]
        self.base_temps = [-30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 
                          100, 110, 120, 130, 140, 150, 160, 170]
    
    def resistance_to_temperature(self, resistance: float) -> Optional[float]:
        """Convert resistance reading to temperature"""
        if resistance == 60:  # Error condition
            return None
            
        mod_resistance = resistance * 1000
        
        for i, limit in enumerate(self.limits[:-1]):
            if limit <= mod_resistance < self.limits[i + 1]:
                offset = mod_resistance - limit
                return round((offset / self.deltas[i]) + self.base_temps[i], 1)
        
        return None

class SequentHardware:
    def __init__(self):
        self.relay_stack = HARDWARE_CONFIG['relay_stack']
        self.megabas_stack = HARDWARE_CONFIG['megabas_stack']
        self.rtd_stack = HARDWARE_CONFIG['rtd_stack']
        self.temp_lookup = TemperatureLookup()
    
    def safe_relay_operation(self, operation, *args):
        """Safely execute relay operations with basic error handling"""
        try:
            return operation(*args)
        except Exception as e:
            logging.error(f"Relay operation failed: {e}")
            return False

    def safe_sensor_read(self, sensor_func, *args):
        """Safely read sensors with basic error handling"""
        try:
            return sensor_func(*args)
        except Exception as e:
            logging.error(f"Sensor read failed: {e}")
            return None
    
    # Relay Controls
    def get_pump_status(self) -> bool:
        """Get pump status (handles NC relay inversion)"""
        return self.safe_relay_operation(lib4relind.get_relay, self.relay_stack, 1) == 0
    
    def set_pump(self, on: bool) -> bool:
        """Control pump (handles NC relay inversion)"""
        return self.safe_relay_operation(lib4relind.set_relay, self.relay_stack, 1, 0 if on else 1)
    
    def get_heater_status(self) -> bool:
        """Get heater status (handles NC relay inversion)"""
        return self.safe_relay_operation(lib4relind.get_relay, self.relay_stack, 2) == 0
    
    def set_heater(self, on: bool) -> bool:
        """Control heater (handles NC relay inversion)"""
        return self.safe_relay_operation(lib4relind.set_relay, self.relay_stack, 2, 0 if on else 1)
    
    def get_test_switch_status(self) -> bool:
        """Get test switch status (handles NC relay inversion)"""
        return self.safe_relay_operation(lib4relind.get_relay, self.relay_stack, 3) == 0
    
    def set_test_switch(self, on: bool) -> bool:
        """Control test switch (handles NC relay inversion)"""
        return self.safe_relay_operation(lib4relind.set_relay, self.relay_stack, 3, 0 if on else 1)
    
    # Sensor Readings
    def read_rtd_temperature(self, input_pin: int) -> Optional[float]:
        """Read RTD sensor temperature"""
        temp = self.safe_sensor_read(librtd.get, self.rtd_stack, input_pin)
        return temp if temp and -50 <= temp <= 200 else None
    
    def read_megabas_temperature(self, input_pin: int) -> Optional[float]:
        """Read MegaBas resistance sensor temperature"""
        resistance = self.safe_sensor_read(m.getRIn1K, self.megabas_stack, input_pin)
        if resistance is None:
            return None
        return self.temp_lookup.resistance_to_temperature(resistance)
