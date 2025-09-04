#!/usr/bin/env python3
"""
Test Mode Change Detection

This script tests if the mode change detection is working properly.
"""

import time
import json
import paho.mqtt.client as mqtt_client
import sys
from datetime import datetime

# MQTT Configuration
MQTT_BROKER = "192.168.0.110"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt_beaches"
MQTT_PASSWORD = "uQX6NiZ.7R"

class ModeChangeTester:
    def __init__(self):
        self.client = mqtt_client.Client()
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.mode_changes = []
        self.start_time = time.time()
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker")
            # Subscribe to system mode
            client.subscribe("homeassistant/sensor/solar_heating_system_mode/state")
            print("📡 Subscribed to system mode changes")
        else:
            print(f"❌ Failed to connect to MQTT broker: {rc}")
            
    def on_message(self, client, userdata, msg):
        try:
            if msg.topic == "homeassistant/sensor/solar_heating_system_mode/state":
                mode = msg.payload.decode()
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Record mode change
                self.mode_changes.append({
                    'time': current_time,
                    'mode': mode,
                    'timestamp': time.time()
                })
                
                print(f"🔄 {current_time} - Mode: {mode}")
                
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            
    def test_mode_changes(self, duration_minutes=5):
        """Test mode changes for specified duration"""
        print(f"🔍 Testing mode changes for {duration_minutes} minutes...")
        print("=" * 60)
        
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            
            # Wait for specified duration
            end_time = time.time() + (duration_minutes * 60)
            
            while time.time() < end_time:
                remaining = int((end_time - time.time()) / 60)
                print(f"\r⏱️  Time remaining: {remaining} minutes", end="", flush=True)
                time.sleep(1)
            
            print(f"\n\n📊 Test Results:")
            print("=" * 60)
            
            if len(self.mode_changes) > 1:
                print(f"✅ Mode changes detected: {len(self.mode_changes)}")
                print("\n🔄 Mode Change History:")
                for i, change in enumerate(self.mode_changes):
                    if i > 0:
                        prev_mode = self.mode_changes[i-1]['mode']
                        print(f"   {change['time']}: {prev_mode} → {change['mode']}")
                    else:
                        print(f"   {change['time']}: {change['mode']} (initial)")
                        
                # Calculate change frequency
                if len(self.mode_changes) > 1:
                    time_span = self.mode_changes[-1]['timestamp'] - self.mode_changes[0]['timestamp']
                    changes_per_hour = (len(self.mode_changes) - 1) / (time_span / 3600)
                    print(f"\n📈 Change Frequency: {changes_per_hour:.1f} changes per hour")
            else:
                print("❌ No mode changes detected")
                print("   This could mean:")
                print("   - System is stable (good)")
                print("   - Mode change detection not working (bad)")
                print("   - System stuck in one mode")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

def main():
    """Main function"""
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Usage: python3 test_mode_changes.py [duration_minutes]")
            print("Default duration: 5 minutes")
            return
    else:
        duration = 5
        
    tester = ModeChangeTester()
    tester.test_mode_changes(duration)

if __name__ == "__main__":
    main()
