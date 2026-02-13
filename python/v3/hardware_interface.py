"""
Hardware Interface Module for Solar Heating System v3
Abstracts Sequent Microsystems hardware interactions
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

# Import Sequent Microsystems libraries
try:
    import megabas as m
    import librtd
    import lib4relind
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    logging.warning("Sequent Microsystems libraries not available. Running in simulation mode.")

from config import config, sensor_mapping, pump_config

logger = logging.getLogger(__name__)

class HardwareInterface:
    """Hardware interface for Sequent Microsystems boards"""
    
    def __init__(self, simulation_mode: bool = False):
        self.simulation_mode = simulation_mode or not HARDWARE_AVAILABLE
        self.rtd_board = config.rtd_board_address
        self.megabas_board = config.megabas_board_address
        self.relay_board = config.relay_board_address
        
        # Simulation data for testing
        self.simulation_temperatures = {
            'solar_collector': 75.2,
            'storage_tank': 62.8,
            'return_line': 58.9,
            'heat_exchanger_in': 45.3,
            'heat_exchanger_out': 52.1,
            'storage_tank_top': 68.5,
            'storage_tank_bottom': 55.2,
            'ambient_air': 22.4,
            'uteluft': 18.7,
            'avluft': 24.3,
            'tilluft': 26.8,
            'franluft': 25.1,
        }
        
        # Simulation relay states
        self.simulation_relays = {
            1: False,  # Primary pump
            3: False,  # Cartridge heater
            4: False,  # Test switch
        }
        
        logger.info(f"Hardware interface initialized in {'simulation' if self.simulation_mode else 'hardware'} mode")
    
    def read_rtd_temperature(self, sensor_id: int, stack: int = None) -> Optional[float]:
        """
        Read temperature from RTD sensor
        
        Args:
            sensor_id: Sensor ID (0-7)
            stack: Stack number (defaults to configured RTD board)
            
        Returns:
            Temperature in Celsius or None if error
        """
        if self.simulation_mode:
            # Return simulated temperature based on sensor mapping
            sensor_names = list(self.simulation_temperatures.keys())
            if sensor_id < len(sensor_names):
                temp = self.simulation_temperatures[sensor_names[sensor_id]]
                # Add some realistic variation
                temp += np.random.normal(0, 0.5)
                return round(temp, 1)
            return 25.0
        
        try:
            stack = stack or self.rtd_board
            temp = librtd.get(stack, sensor_id + 1)  # librtd uses 1-based indexing
            
            # Validate temperature reading
            if temp > 200 or temp < -50:
                # Only log warning once per sensor to reduce spam
                if not hasattr(self, '_rtd_warnings'):
                    self._rtd_warnings = set()
                
                if sensor_id not in self._rtd_warnings:
                    logger.warning(f"Invalid RTD temperature reading: {temp}°C for sensor {sensor_id}")
                    self._rtd_warnings.add(sensor_id)
                return None
            
            # Clear warning if sensor is working again
            if hasattr(self, '_rtd_warnings') and sensor_id in self._rtd_warnings:
                logger.info(f"RTD sensor {sensor_id} is working again")
                self._rtd_warnings.remove(sensor_id)
                
            return round(temp, 1)
            
        except Exception as e:
            # Only log error once per sensor to reduce spam
            if not hasattr(self, '_rtd_errors'):
                self._rtd_errors = set()
            
            if sensor_id not in self._rtd_errors:
                logger.error(f"Error reading RTD sensor {sensor_id}: {e}")
                self._rtd_errors.add(sensor_id)
            return None
    
    def read_megabas_temperature(self, sensor_id: int, stack: int = None) -> Optional[float]:
        """
        Read temperature from MegaBAS 1K sensor
        
        Args:
            sensor_id: Sensor ID (1-8)
            stack: Stack number (defaults to configured MegaBAS board)
            
        Returns:
            Temperature in Celsius or None if error
        """
        if self.simulation_mode:
            # Return simulated temperature
            temp = 25.0 + np.random.normal(0, 2.0)
            return round(temp, 1)
        
        try:
            stack = stack or self.megabas_board
            sensor = m.getRIn1K(stack, sensor_id)
            
            if sensor == 60:  # Error value
                # Only log warning once per sensor to reduce spam
                if not hasattr(self, '_sensor_warnings'):
                    self._sensor_warnings = set()
                
                if sensor_id not in self._sensor_warnings:
                    logger.warning(f"Error reading MegaBAS sensor {sensor_id} - sensor may be disconnected or faulty")
                    self._sensor_warnings.add(sensor_id)
                return None
            
            # Clear warning if sensor is working again
            if hasattr(self, '_sensor_warnings') and sensor_id in self._sensor_warnings:
                logger.info(f"MegaBAS sensor {sensor_id} is working again")
                self._sensor_warnings.remove(sensor_id)
            
            # Convert to temperature using existing calibration
            temp = self._convert_megabas_to_temperature(sensor)
            return temp
            
        except Exception as e:
            # Only log error once per sensor to reduce spam
            if not hasattr(self, '_sensor_errors'):
                self._sensor_errors = set()
            
            if sensor_id not in self._sensor_errors:
                logger.error(f"Error reading MegaBAS sensor {sensor_id}: {e}")
                self._sensor_errors.add(sensor_id)
            return None
    
    def _convert_megabas_to_temperature(self, sensor_value: float) -> float:
        """
        Convert MegaBAS sensor value to temperature
        Based on existing calibration from v2 system
        """
        # Calibration data from existing system
        limit = [882.2, 921.6, 960.9, 1000, 1039, 1077.9, 1116.7, 1155.4, 1194, 1232.4, 
                1270.8, 1309, 1347.1, 1385.1, 1422.9, 1460.7, 1498.3, 1535.8, 1573.3, 
                1610.5, 1647.7, 1684.8]
        delta = [4, 3.9, 3.9, 3.9, 3.89, 3.88, 3.87, 3.86, 3.84, 3.84, 3.82, 3.81, 
                3.8, 3.78, 3.78, 3.76, 3.75, 3.75, 3.72, 3.72, 3.71]
        
        mod_sensor = sensor_value * 1000
        
        try:
            if mod_sensor >= limit[0] and mod_sensor < limit[1]:
                return self._calc_megabas_temp(mod_sensor - limit[0], delta[0], -30)
            elif mod_sensor >= limit[1] and mod_sensor < limit[2]:
                return self._calc_megabas_temp(mod_sensor - limit[1], delta[1], -20)
            elif mod_sensor >= limit[2] and mod_sensor < limit[3]:
                return self._calc_megabas_temp(mod_sensor - limit[2], delta[2], -10)
            elif mod_sensor >= limit[3] and mod_sensor < limit[4]:
                return self._calc_megabas_temp(mod_sensor - limit[3], delta[3], 0)
            elif mod_sensor >= limit[4] and mod_sensor < limit[5]:
                return self._calc_megabas_temp(mod_sensor - limit[4], delta[4], 10)
            elif mod_sensor >= limit[5] and mod_sensor < limit[6]:
                return self._calc_megabas_temp(mod_sensor - limit[5], delta[5], 20)
            elif mod_sensor >= limit[6] and mod_sensor < limit[7]:
                return self._calc_megabas_temp(mod_sensor - limit[6], delta[6], 30)
            elif mod_sensor >= limit[7] and mod_sensor < limit[8]:
                return self._calc_megabas_temp(mod_sensor - limit[7], delta[7], 40)
            elif mod_sensor >= limit[8] and mod_sensor < limit[9]:
                return self._calc_megabas_temp(mod_sensor - limit[8], delta[8], 50)
            elif mod_sensor >= limit[9] and mod_sensor < limit[10]:
                return self._calc_megabas_temp(mod_sensor - limit[9], delta[9], 60)
            elif mod_sensor >= limit[10] and mod_sensor < limit[11]:
                return self._calc_megabas_temp(mod_sensor - limit[10], delta[10], 70)
            elif mod_sensor >= limit[11] and mod_sensor < limit[12]:
                return self._calc_megabas_temp(mod_sensor - limit[11], delta[11], 80)
            elif mod_sensor >= limit[12] and mod_sensor < limit[13]:
                return self._calc_megabas_temp(mod_sensor - limit[12], delta[12], 90)
            elif mod_sensor >= limit[13] and mod_sensor < limit[14]:
                return self._calc_megabas_temp(mod_sensor - limit[13], delta[13], 100)
            elif mod_sensor >= limit[14] and mod_sensor < limit[15]:
                return self._calc_megabas_temp(mod_sensor - limit[14], delta[14], 110)
            elif mod_sensor >= limit[15] and mod_sensor < limit[16]:
                return self._calc_megabas_temp(mod_sensor - limit[15], delta[15], 120)
            elif mod_sensor >= limit[16] and mod_sensor < limit[17]:
                return self._calc_megabas_temp(mod_sensor - limit[16], delta[16], 130)
            elif mod_sensor >= limit[17] and mod_sensor < limit[18]:
                return self._calc_megabas_temp(mod_sensor - limit[17], delta[17], 140)
            elif mod_sensor >= limit[18] and mod_sensor < limit[19]:
                return self._calc_megabas_temp(mod_sensor - limit[18], delta[18], 150)
            elif mod_sensor >= limit[19] and mod_sensor < limit[20]:
                return self._calc_megabas_temp(mod_sensor - limit[19], delta[19], 160)
            elif mod_sensor >= limit[20] and mod_sensor < limit[21]:
                return self._calc_megabas_temp(mod_sensor - limit[20], delta[20], 170)
            else:
                return 25.0  # Default temperature
                
        except Exception as e:
            logger.error(f"Error converting MegaBAS value {sensor_value}: {e}")
            return 25.0
    
    def _calc_megabas_temp(self, calc: float, delta: float, deci: float) -> float:
        """Calculate temperature from MegaBAS calibration"""
        try:
            calculated_temp = (calc / delta) + deci
            return round(calculated_temp, 1)
        except Exception as e:
            logger.error(f"Error in temperature calculation: {e}")
            return 25.0
    
    def set_relay_state(self, relay_id: int, state: bool, stack: int = None) -> bool:
        """
        Set relay state
        
        Args:
            relay_id: Relay ID (1-4)
            state: True for ON, False for OFF
            stack: Stack number (defaults to configured relay board)
            
        Returns:
            True if successful, False otherwise
        """
        if self.simulation_mode:
            self.simulation_relays[relay_id] = state
            logger.info(f"Simulation: Relay {relay_id} set to {'ON' if state else 'OFF'}")
            return True
        
        try:
            stack = stack or self.relay_board
            
            # Apply NC inversion based on relay type
            if relay_id == 1:  # Primary pump - use pump config logic
                relay_value = pump_config.set_pump_status(state)
            elif relay_id == 2:  # Cartridge heater - direct NC inversion like V1
                relay_value = 0 if state else 1  # NC inversion: 0=ON, 1=OFF
            else:  # Other relays - use pump config logic
                relay_value = pump_config.set_pump_status(state)
            
            lib4relind.set_relay(stack, relay_id, relay_value)
            logger.info(f"Relay {relay_id} set to {'ON' if state else 'OFF'}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting relay {relay_id}: {e}")
            return False
    
    def get_relay_state(self, relay_id: int, stack: int = None) -> Optional[bool]:
        """
        Get relay state
        
        Args:
            relay_id: Relay ID (1-4)
            stack: Stack number (defaults to configured relay board)
            
        Returns:
            True if ON, False if OFF, None if error
        """
        if self.simulation_mode:
            return self.simulation_relays.get(relay_id, False)
        
        try:
            stack = stack or self.relay_board
            relay_value = lib4relind.get_relay(stack, relay_id)
            
            # Apply NC inversion for cartridge heater (relay 2)
            if relay_id == 2:  # Cartridge heater - direct NC inversion
                return relay_value == 0  # NC relay: 0=ON, 1=OFF
            else:  # Other relays - use pump config logic
                return pump_config.get_pump_status(relay_value)
            
        except Exception as e:
            logger.error(f"Error reading relay {relay_id}: {e}")
            return None
    
    def read_all_temperatures(self) -> Dict[str, float]:
        """
        Read all temperature sensors
        
        Returns:
            Dictionary of sensor names and temperatures
        """
        temperatures = {}
        
        # Read RTD sensors
        for sensor_name, sensor_id in sensor_mapping.__dict__.items():
            if isinstance(sensor_id, int):
                temp = self.read_rtd_temperature(sensor_id)
                if temp is not None:
                    temperatures[sensor_name] = temp
        
        # Read MegaBAS sensors (FTX sensors)
        ftx_sensors = ['uteluft', 'avluft', 'tilluft', 'franluft']
        for i, sensor_name in enumerate(ftx_sensors):
            temp = self.read_megabas_temperature(i + 1)
            if temp is not None:
                temperatures[sensor_name] = temp
        
        return temperatures
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get complete system hardware status
        
        Returns:
            Dictionary with hardware status information
        """
        status = {
            'hardware_available': HARDWARE_AVAILABLE,
            'simulation_mode': self.simulation_mode,
            'temperatures': self.read_all_temperatures(),
            'relays': {},
            'boards': {
                'rtd_board': self.rtd_board,
                'megabas_board': self.megabas_board,
                'relay_board': self.relay_board,
            }
        }
        
        # Get relay states
        for relay_id in range(1, 5):
            state = self.get_relay_state(relay_id)
            if state is not None:
                status['relays'][f'relay_{relay_id}'] = 'ON' if state else 'OFF'
        
        return status
    
    def test_hardware_connection(self) -> Dict[str, bool]:
        """
        Test hardware connections
        
        Returns:
            Dictionary with test results
        """
        results = {
            'rtd_board': False,
            'megabas_board': False,
            'relay_board': False,
            'overall': False
        }
        
        if self.simulation_mode:
            results = {k: True for k in results.keys()}
            return results
        
        try:
            # Test RTD board
            temp = self.read_rtd_temperature(0)
            results['rtd_board'] = temp is not None
            
            # Test MegaBAS board
            temp = self.read_megabas_temperature(1)
            results['megabas_board'] = temp is not None
            
            # Test relay board
            current_state = self.get_relay_state(1)
            if current_state is not None:
                # Toggle relay and check if it changed
                new_state = not current_state
                self.set_relay_state(1, new_state)
                time.sleep(0.1)
                actual_state = self.get_relay_state(1)
                self.set_relay_state(1, current_state)  # Restore original state
                results['relay_board'] = actual_state == new_state
            
            results['overall'] = all([results['rtd_board'], results['megabas_board'], results['relay_board']])
            
        except Exception as e:
            logger.error(f"Hardware connection test failed: {e}")
        
        return results
