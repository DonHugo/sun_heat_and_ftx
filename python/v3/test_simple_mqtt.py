#!/usr/bin/env python3
"""
Simple MQTT Test for Solar Heating System v3
"""

import time
from mqtt_handler import MQTTHandler
from hardware_interface import HardwareInterface

def test_simple_mqtt():
    print("🧪 Simple MQTT Test")
    print("=" * 30)
    
    # Initialize components
    mqtt = MQTTHandler()
    hw = HardwareInterface(simulation_mode=True)
    
    print("✅ Components initialized")
    
    # Connect to MQTT
    print("📡 Connecting to MQTT broker...")
    connected = mqtt.connect()
    print(f"Connected: {connected}")
    
    if connected:
        # Read temperatures
        temps = hw.read_all_temperatures()
        print(f"🌡️  Temperatures: {temps}")
        
        # Publish a test message
        print("📤 Publishing test message...")
        success = mqtt.publish("solar_heating_v3/test", {
            "test": True,
            "timestamp": time.time(),
            "message": "Simple MQTT test"
        })
        print(f"Published: {success}")
        
        # Publish temperature
        solar_temp = temps.get('solar_collector', 0)
        success = mqtt.publish_temperature('solar_collector', solar_temp)
        print(f"Published temperature: {success}")
        
        # Wait a moment
        print("⏱️  Waiting 3 seconds...")
        time.sleep(3)
        
        # Disconnect
        print("🔌 Disconnecting...")
        mqtt.disconnect()
        print("✅ Disconnected")
        
        print("🎉 Test completed successfully!")
        return True
    else:
        print("❌ Failed to connect")
        return False

if __name__ == "__main__":
    test_simple_mqtt()
