import logging
from typing import Dict, Any
from hardware_interface import SequentHardware
from sensor_manager import SensorManager
from config import SystemConfig

class SunCollectorController:
    def __init__(self, config: SystemConfig, hardware: SequentHardware, sensor_manager: SensorManager):
        self.config = config
        self.hardware = hardware
        self.sensor_manager = sensor_manager
        self.state = {
            'mode': 'startup',
            'state': 1,
            'sub_state': 0,
            'overheated': False
        }
    
    def update_control_logic(self, test_mode: bool = False) -> Dict[str, Any]:
        """Main control logic for sun collector"""
        try:
            if test_mode:
                return self._test_mode_logic()
            else:
                return self._production_mode_logic()
        except Exception as e:
            logging.error(f"Error in control logic: {e}")
            return {}
    
    def _production_mode_logic(self) -> Dict[str, Any]:
        """Production mode control logic"""
        # Get sensor readings
        T1 = self.sensor_manager.get_averaged_temperature(2, 5)  # Collector
        T2 = self.sensor_manager.get_averaged_temperature(2, 6)  # Tank
        dT = round(T1 - T2, 1)
        
        current_pump_status = self.hardware.get_pump_status()
        
        # Control logic (simplified version of your original logic)
        self._execute_control_logic(T1, T2, dT, current_pump_status)
        
        return {
            'T1': T1,
            'T2': T2,
            'dT': dT,
            'pump_status': self.hardware.get_pump_status(),
            'mode': self.state['mode'],
            'state': self.state['state'],
            'sub_state': self.state['sub_state']
        }
    
    def _test_mode_logic(self) -> Dict[str, Any]:
        """Test mode control logic using MQTT data"""
        T1 = self.sensor_manager.mqtt_sun[0]
        T2 = self.sensor_manager.mqtt_sun[1]
        dT = round(T1 - T2, 1)
        
        # Similar logic but using test variables instead of actual hardware
        return {
            'T1': T1,
            'T2': T2,
            'dT': dT,
            'mode': self.state['mode']
        }
    
    def _execute_control_logic(self, T1: float, T2: float, dT: float, current_pump_status: bool):
        """Execute the actual control decisions"""
        set_temp_grans = self.config.set_temp_tank_1 - self.config.set_temp_tank_1_hysteres
        
        # Manual control
        if hasattr(self, 'manual_control') and self.manual_control:
            return
        
        # Overheating protection
        if T1 >= self.config.temp_kok or self.state['overheated']:
            if T1 >= self.config.temp_kok:
                self.state['overheated'] = True
                self.hardware.set_pump(False)
                self.state['mode'] = "20"
            elif self.state['overheated'] and T1 < (self.config.temp_kok - self.config.temp_kok_hysteres):
                self.state['overheated'] = False
                self.hardware.set_pump(True)
                self.state['mode'] = "21"
        
        # Pump off or startup
        elif not current_pump_status or self.state['mode'] == "startup":
            if dT >= self.config.dTStart_tank_1 and T2 <= set_temp_grans:
                self.hardware.set_pump(True)
                self.state['mode'] = "30"
            elif T1 >= self.config.kylning_kollektor:
                self.hardware.set_pump(True)
                self.state['mode'] = "31"
        
        # Pump on
        elif current_pump_status:
            if dT <= self.config.dTStop_tank_1:
                self.hardware.set_pump(False)
                self.state['mode'] = "40"
            elif T2 >= self.config.set_temp_tank_1 and T1 <= (self.config.kylning_kollektor - self.config.kylning_kollektor_hysteres):
                self.hardware.set_pump(False)
                self.state['mode'] = "41"

class CartridgeHeaterController:
    def __init__(self, hardware: SequentHardware):
        self.hardware = hardware
        self.enabled = False
    
    def update(self) -> Dict[str, Any]:
        """Update heater control"""
        self.hardware.set_heater(self.enabled)
        status = "on" if self.hardware.get_heater_status() else "off"
        
        return {
            'name': 'elpatron',
            'elpatron_input': self.enabled,
            'elpatron_status': status
        }

class TestSwitchController:
    def __init__(self, hardware: SequentHardware):
        self.hardware = hardware
        self.enabled = False
    
    def update(self) -> Dict[str, Any]:
        """Update test switch control"""
        self.hardware.set_test_switch(self.enabled)
        status = "on" if self.hardware.get_test_switch_status() else "off"
        
        return {
            'name': 'test_switch',
            'value': status,
            'switch_input': self.enabled,
            'switch_status': status
        }
