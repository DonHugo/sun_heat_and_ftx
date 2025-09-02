#!/usr/bin/env python3
"""
Simple MQTT Heartbeat Test - Minimal Dependencies
Tests only MQTT connection and heartbeat publishing
"""

import json
import time
import random
from paho.mqtt import client as mqtt_client

# MQTT Configuration
MQTT_BROKER = "192.168.0.110"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt_beaches"
MQTT_PASSWORD = "uQX6NiZ.7R"
MQTT_CLIENT_ID = f"solar_heating_v3_test_{random.randint(0, 1000)}"
HEARTBEAT_TOPIC = "solar_heating_v3/heartbeat"

def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        print("✓ Connected to MQTT broker successfully")
    else:
        print(f"✗ Failed to connect to MQTT broker, return code: {rc}")

def on_disconnect(client, userdata, rc):
    """MQTT disconnection callback"""
    print(f"Disconnected from MQTT broker with result code: {rc}")

def test_heartbeat():
    """Test MQTT heartbeat functionality"""
    print("=== Simple MQTT Heartbeat Test ===\n")
    
    # Create MQTT client
    client = mqtt_client.Client(client_id=MQTT_CLIENT_ID)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    try:
        # Connect to MQTT broker
        print(f"Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        if not client.is_connected():
            print("✗ Failed to connect to MQTT broker")
            return False
        
        print(f"Heartbeat topic: {HEARTBEAT_TOPIC}")
        
        # Test heartbeat messages
        for i in range(5):
            print(f"\nSending heartbeat {i+1}/5...")
            
            # Create heartbeat message
            heartbeat_data = {
                "status": "alive",
                "timestamp": time.time(),
                "version": "v3",
                "uptime": 0.0,
                "system_state": "test",
                "primary_pump": i % 2 == 0,  # Alternate pump state
                "cartridge_heater": False,
                "temperature_count": 16,
                "last_update": time.time()
            }
            
            # Publish heartbeat
            payload = json.dumps(heartbeat_data)
            result = client.publish(HEARTBEAT_TOPIC, payload, retain=False)
            
            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                print(f"✓ Heartbeat {i+1} sent successfully")
                print(f"  Payload: {payload[:100]}...")
            else:
                print(f"✗ Failed to send heartbeat {i+1}: {result.rc}")
            
            # Wait 2 seconds between heartbeats
            time.sleep(2)
        
        # Disconnect
        client.loop_stop()
        client.disconnect()
        print("\n✓ Test completed successfully!")
        print("Check your MQTT client for heartbeat messages on topic:", HEARTBEAT_TOPIC)
        return True
        
    except Exception as e:
        print(f"✗ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_heartbeat()
    if not success:
        print("\nTest failed. Please check:")
        print("1. MQTT broker is running and accessible")
        print("2. Network connectivity to", MQTT_BROKER)
        print("3. MQTT credentials are correct")
        print("4. MQTT broker allows connections from this client")
