#!/usr/bin/env python3
"""
Script to remove the secondary pump entity from Home Assistant
Run this if the secondary pump is still showing in Home Assistant
"""

import json
import time
from mqtt_handler import MQTTHandler
import config

def remove_secondary_pump():
    """Remove secondary pump entity from Home Assistant"""
    print("🔧 Removing secondary pump entity from Home Assistant...")
    
    # Initialize MQTT handler
    mqtt = MQTTHandler()
    
    if not mqtt.connect():
        print("❌ Failed to connect to MQTT broker")
        return False
    
    print("✅ Connected to MQTT broker")
    
    try:
        # Publish empty config to remove the entity
        topic = "homeassistant/switch/solar_heating_secondary_pump/config"
        mqtt.publish(topic, "", retain=True)
        print(f"📤 Published removal message to {topic}")
        
        # Clear the state topic
        state_topic = "homeassistant/switch/solar_heating_secondary_pump/state"
        mqtt.publish_raw(state_topic, "")
        print(f"📤 Cleared state topic {state_topic}")
        
        # Wait a moment for MQTT to process
        time.sleep(2)
        
        print("✅ Secondary pump removal completed")
        print("🔄 Restart Home Assistant or wait a few minutes for the entity to disappear")
        
        return True
        
    except Exception as e:
        print(f"❌ Error removing secondary pump: {e}")
        return False
    finally:
        mqtt.disconnect()
        print("🔌 Disconnected from MQTT")

if __name__ == "__main__":
    remove_secondary_pump()
