import asyncio
import logging
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from hardware_interface import SequentHardware
from sensor_manager import SensorManager
from mqtt_handler import MQTTHandler
from controller import SunCollectorController, CartridgeHeaterController, TestSwitchController
from config import MQTTConfig, SystemConfig

class TemperatureMonitoringSystem:
    def __init__(self):
        self.config = SystemConfig()
        self.mqtt_config = MQTTConfig()
        self.hardware = SequentHardware()
        self.sensor_manager = SensorManager(self.hardware)
        self.sun_controller = SunCollectorController(self.config, self.hardware, self.sensor_manager)
        self.heater_controller = CartridgeHeaterController(self.hardware)
        self.switch_controller = TestSwitchController(self.hardware)
        self.mqtt_handler = None
        self.running = False
        self.test_mode = False
        self.log_level = "info"
        
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--debug", dest="debug_mode", default="false", help="true|false")
        parser.add_argument("-t", "--test", dest="test_mode", default="false", help="true|false")
        self.args = parser.parse_args()
    
    def setup_logging(self):
        """Configure logging"""
        level = logging.DEBUG if self.args.debug_mode == "true" or self.log_level == "debug" else logging.INFO
        logging.basicConfig(
            filename="temperature_monitoring.log",
            filemode='a',
            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            datefmt='%H:%M:%S',
            level=level
        )
    
    def handle_mqtt_message(self, topic: str, payload: dict):
        """Handle incoming MQTT messages"""
        try:
            if topic == "rtd/acctank":
                self.sensor_manager.update_mqtt_data(topic, payload)
            elif topic == "hass/test_mode":
                self.test_mode = payload["state"] == 1
            elif topic == "hass/log_level":
                self.log_level = "debug" if payload["state"] == 1 else "info"
            elif topic == "hass/elpatron":
                self.heater_controller.enabled = payload["state"] == 1
            elif topic == "hass/test_switch":
                self.switch_controller.enabled = payload["state"] == 1
            # Add other MQTT handlers as needed
        except Exception as e:
            logging.error(f"Error handling MQTT message from {topic}: {e}")
    
    async def start(self):
        """Start the monitoring system"""
        try:
            self.setup_logging()
            logging.info("Starting Temperature Monitoring System")
            
            # Connect MQTT
            self.mqtt_handler = MQTTHandler(self.mqtt_config, self.handle_mqtt_message)
            client = self.mqtt_handler.connect()
            client.loop_start()
            
            # Start main loops
            self.running = True
            with ThreadPoolExecutor(max_workers=3) as executor:
                executor.submit(self._sensor_collection_loop)
                executor.submit(self._control_loop)
                executor.submit(self._publishing_loop)
                
                # Keep running
                while self.running:
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            logging.info("Shutdown requested")
        except Exception as e:
            logging.error(f"System error: {e}")
        finally:
            self.running = False
            if self.mqtt_handler and self.mqtt_handler.client:
                self.mqtt_handler.client.loop_stop()
    
    def _sensor_collection_loop(self):
        """Continuously collect sensor data"""
        while self.running:
            try:
                self.sensor_manager.collect_sensor_data()
                time.sleep(5)
            except Exception as e:
                logging.error(f"Sensor collection error: {e}")
    
    def _control_loop(self):
        """Main control loop"""
        while self.running:
            try:
                # Update sun collector
                sun_data = self.sun_controller.update_control_logic(self.test_mode)
                
                # Update heater
                heater_data = self.heater_controller.update()
                
                # Update test switch
                switch_data = self.switch_controller.update()
                
                time.sleep(1)
            except Exception as e:
                logging.error(f"Control loop error: {e}")
    
    def _publishing_loop(self):
        """Publish data to MQTT"""
        while self.running:
            try:
                if self.mqtt_handler:
                    # Publish sensor calculations
                    self._publish_sensor_data()
                    
                    # Publish stored energy
                    self._publish_stored_energy()
                    
                time.sleep(5)
            except Exception as e:
                logging.error(f"Publishing error: {e}")
    
    def _publish_sensor_data(self):
        """Publish individual sensor readings"""
        for x in range(4):
            for y in range(8):
                temp = self.sensor_manager.get_averaged_temperature(x, y)
                if temp != 0:  # Only publish valid readings
                    msg = {
                        "name": f"sequentmicrosystems_{x+1}_{y+1}",
                        "temperature": temp
                    }
                    topic = f"sequentmicrosystems/sequentmicrosystems_{x+1}_{y+1}"
                    self.mqtt_handler.publish(topic, msg)
    
    def _publish_stored_energy(self):
        """Calculate and publish stored energy data"""
        # Your existing stored energy calculation logic
        pass

if __name__ == "__main__":
    system = TemperatureMonitoringSystem()
    asyncio.run(system.start())
