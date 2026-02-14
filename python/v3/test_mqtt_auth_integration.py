#!/usr/bin/env python3
"""
Test script for MQTT authentication integration
Part of Issue #44 local test deployment
"""

import os
import time
import paho.mqtt.client as mqtt
from config import SystemConfig
from mqtt_authenticator import MQTTAuthenticator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("PHASE 4: Testing Python MQTT Authenticator")
print("=" * 60)

# Test 1: Load configuration
print("\nTest 1: Creating SystemConfig with MQTT credentials")
print("-" * 60)
try:
    config = SystemConfig()
    print(f"✅ SystemConfig created successfully")
    print(f"   MQTT_BROKER: {config.mqtt_broker}")
    print(f"   MQTT_PORT: {config.mqtt_port}")
    print(f"   MQTT_USERNAME: {config.mqtt_username}")
    print(f"   MQTT_PASSWORD: {'*' * len(config.mqtt_password)} ({len(config.mqtt_password)} chars)")
except Exception as e:
    print(f"❌ Failed to create SystemConfig: {e}")
    exit(1)

# Test 2: Create authenticator
print("\nTest 2: Creating MQTTAuthenticator from SystemConfig")
print("-" * 60)
try:
    auth = MQTTAuthenticator(config)
    print(f"✅ MQTTAuthenticator created successfully")
    print(f"   Broker: {auth.broker}:{auth.port}")
    print(f"   Username: {auth.username}")
    print(f"   Password: {'*' * len(auth.password)}")
    print(f"   Client ID: {auth.client_id}")
    
    # Validate credentials
    if auth.validate_credentials():
        print(f"✅ Credentials validated successfully")
    else:
        print(f"❌ Credential validation failed")
        exit(1)
except Exception as e:
    print(f"❌ Failed to create MQTTAuthenticator: {e}")
    exit(1)

# Test 3: Test connection with authentication
print("\nTest 3: Testing MQTT connection with authentication")
print("-" * 60)

connected = False
connection_rc = None

def on_connect(client, userdata, flags, rc):
    global connected, connection_rc
    connection_rc = rc
    connected = (rc == 0)
    
    # Use authenticator to log connection attempt
    auth.log_connection_attempt(rc, auth.client_id, connected)

# Create MQTT client with simpler API
client = mqtt.Client(client_id=auth.client_id)
client.on_connect = on_connect

# Set authentication credentials
print(f"Setting authentication for user: {auth.username}")
client.username_pw_set(auth.username, auth.password)

try:
    print(f"Connecting to {auth.broker}:{auth.port}...")
    client.connect(auth.broker, auth.port, 60)
    client.loop_start()
    time.sleep(2)
    client.loop_stop()
    client.disconnect()
    
    if connected:
        print("\n✅ MQTT authentication integration test PASSED")
        print(f"   Return code: {connection_rc}")
        status, reason, severity = auth.interpret_return_code(connection_rc)
        print(f"   Status: {status}")
        print(f"   Reason: {reason}")
    else:
        print(f"\n❌ Connection failed with return code: {connection_rc}")
        if connection_rc is not None:
            status, reason, severity = auth.interpret_return_code(connection_rc)
            print(f"   Status: {status}")
            print(f"   Reason: {reason}")
except Exception as e:
    print(f"❌ Connection error: {e}")
    exit(1)

print("\n" + "=" * 60)
print("Python Integration Testing Complete")
print("=" * 60)

# Return exit code
exit(0 if connected else 1)
