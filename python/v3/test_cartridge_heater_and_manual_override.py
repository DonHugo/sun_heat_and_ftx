#!/usr/bin/env python3
"""
Test script to verify cartridge heater and manual override functionality
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
        client.subscribe("homeassistant/switch/+/state")
    else:
        print(f"❌ Failed to connect to MQTT broker: {rc}")

def on_message(client, userdata, msg):
    """MQTT message callback"""
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"📨 Received: {topic} = {payload}")

def test_cartridge_heater():
    """Test cartridge heater control"""
    print("🔥 Testing Cartridge Heater Control")
    print("=" * 50)
    
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
        
        # Test cartridge heater commands
        print("\n🔥 Testing cartridge heater commands:")
        
        # Turn ON cartridge heater
        print("  📤 Turning ON cartridge heater...")
        client.publish("homeassistant/switch/solar_heating_cartridge_heater/set", "ON")
        time.sleep(3)
        
        # Turn OFF cartridge heater
        print("  📤 Turning OFF cartridge heater...")
        client.publish("homeassistant/switch/solar_heating_cartridge_heater/set", "OFF")
        time.sleep(3)
        
        print("✅ Cartridge heater test completed!")
        
    except Exception as e:
        print(f"❌ Error during cartridge heater test: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

def test_manual_override():
    """Test manual override functionality"""
    print("\n🎛️ Testing Manual Override Functionality")
    print("=" * 50)
    
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
        
        print("\n🎛️ Testing manual override commands:")
        
        # Test 1: Enable manual override and force pump ON
        print("  📤 Test 1: Enable manual override and force pump ON...")
        client.publish("homeassistant/switch/solar_heating_primary_pump_manual/set", "ON")
        time.sleep(3)
        
        # Test 2: Disable manual override (should return to automatic control)
        print("  📤 Test 2: Disable manual override (return to automatic)...")
        client.publish("homeassistant/switch/solar_heating_primary_pump_manual/set", "OFF")
        time.sleep(3)
        
        # Test 3: Enable manual override and force pump OFF
        print("  📤 Test 3: Enable manual override and force pump OFF...")
        client.publish("homeassistant/switch/solar_heating_primary_pump_manual/set", "ON")
        time.sleep(1)
        client.publish("homeassistant/switch/solar_heating_primary_pump_manual/set", "OFF")
        time.sleep(3)
        
        print("✅ Manual override test completed!")
        
    except Exception as e:
        print(f"❌ Error during manual override test: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

def main():
    """Main test function"""
    print("🧪 Testing Cartridge Heater and Manual Override")
    print("=" * 60)
    
    # Test cartridge heater
    test_cartridge_heater()
    
    # Wait between tests
    time.sleep(2)
    
    # Test manual override
    test_manual_override()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Expected Results:")
    print("  🔥 Cartridge Heater: Should turn ON/OFF when controlled from Home Assistant")
    print("  🎛️ Manual Override: Should force pump ON/OFF and override automatic control")
    print("  📨 MQTT Responses: Should see state updates published back to Home Assistant")

if __name__ == "__main__":
    main()
