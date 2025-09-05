#!/usr/bin/env python3
"""
Test script to verify Home Assistant switch control via MQTT
"""

import json
import time
import paho.mqtt.client as mqtt_client
from config import config

def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        print("✅ Connected to MQTT broker")
        # Subscribe to switch state topics to see responses
        client.subscribe("homeassistant/switch/solar_heating_+/state")
    else:
        print(f"❌ Failed to connect to MQTT broker: {rc}")

def on_message(client, userdata, msg):
    """MQTT message callback"""
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"📨 Received: {topic} = {payload}")

def test_switch_control():
    """Test Home Assistant switch control"""
    print("🧪 Testing Home Assistant Switch Control via MQTT")
    print("=" * 60)
    
    # Create MQTT client
    client = mqtt_client.Client()
    client.username_pw_set(config.mqtt_username, config.mqtt_password)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Connect to MQTT broker
        print(f"🔌 Connecting to MQTT broker: {config.mqtt_broker}:{config.mqtt_port}")
        client.connect(config.mqtt_broker, config.mqtt_port, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        # Test switch commands
        switch_tests = [
            ("homeassistant/switch/solar_heating_primary_pump/set", "ON"),
            ("homeassistant/switch/solar_heating_primary_pump/set", "OFF"),
            ("homeassistant/switch/solar_heating_cartridge_heater/set", "ON"),
            ("homeassistant/switch/solar_heating_cartridge_heater/set", "OFF"),
            ("homeassistant/switch/solar_heating_primary_pump_manual/set", "ON"),
            ("homeassistant/switch/solar_heating_primary_pump_manual/set", "OFF"),
        ]
        
        print("\n🎛️ Testing switch commands:")
        for topic, command in switch_tests:
            print(f"  📤 Sending: {topic} = {command}")
            client.publish(topic, command)
            time.sleep(1)  # Wait for processing
        
        # Test number commands
        number_tests = [
            ("homeassistant/number/solar_heating_set_temp_tank_1/set", "75.0"),
            ("homeassistant/number/solar_heating_dTStart_tank_1/set", "8.5"),
            ("homeassistant/number/solar_heating_temp_kok_hysteres/set", "12.0"),
        ]
        
        print("\n🔢 Testing number commands:")
        for topic, value in number_tests:
            print(f"  📤 Sending: {topic} = {value}")
            client.publish(topic, value)
            time.sleep(1)  # Wait for processing
        
        # Wait for responses
        print("\n⏳ Waiting for responses...")
        time.sleep(5)
        
        print("\n✅ Switch control test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    test_switch_control()
