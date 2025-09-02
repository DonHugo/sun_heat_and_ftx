#!/usr/bin/env python3
"""
Test script for MQTT heartbeat functionality
Run this to verify heartbeat messages are being sent correctly
"""

import asyncio
import json
import time
from mqtt_handler import MQTTHandler
from config import mqtt_topics

async def test_heartbeat():
    """Test heartbeat functionality"""
    print("Testing MQTT heartbeat functionality...")
    
    # Initialize MQTT handler
    mqtt = MQTTHandler()
    
    # Connect to MQTT broker
    print("Connecting to MQTT broker...")
    if not mqtt.connect():
        print("Failed to connect to MQTT broker")
        return
    
    print("Connected to MQTT broker successfully")
    print(f"Heartbeat topic: {mqtt_topics.heartbeat}")
    
    # Test heartbeat messages
    for i in range(5):
        print(f"\nSending heartbeat {i+1}/5...")
        
        # Simulate system info
        system_info = {
            "system_state": "test",
            "primary_pump": i % 2 == 0,  # Alternate pump state
            "cartridge_heater": False,
            "temperature_count": 16,
            "last_update": time.time()
        }
        
        # Publish heartbeat
        success = mqtt.publish_heartbeat(system_info)
        
        if success:
            print(f"✓ Heartbeat {i+1} sent successfully")
        else:
            print(f"✗ Failed to send heartbeat {i+1}")
        
        # Wait 2 seconds between heartbeats
        await asyncio.sleep(2)
    
    # Disconnect
    mqtt.disconnect()
    print("\nTest completed. Check your MQTT client for heartbeat messages.")

def test_mqtt_connection():
    """Test basic MQTT connection"""
    print("Testing MQTT connection...")
    
    mqtt = MQTTHandler()
    
    if mqtt.connect():
        print("✓ MQTT connection successful")
        mqtt.disconnect()
        return True
    else:
        print("✗ MQTT connection failed")
        return False

if __name__ == "__main__":
    print("=== Solar Heating System v3 Heartbeat Test ===\n")
    
    # Test connection first
    if test_mqtt_connection():
        print("\nProceeding with heartbeat test...")
        asyncio.run(test_heartbeat())
    else:
        print("\nCannot proceed without MQTT connection.")
        print("Please check your MQTT broker configuration.")
