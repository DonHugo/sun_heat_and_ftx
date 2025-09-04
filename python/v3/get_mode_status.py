#!/usr/bin/env python3
"""
Quick Mode Status Checker

Get current system mode and reasoning with a simple command.
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

class ModeStatusChecker:
    def __init__(self):
        self.client = mqtt_client.Client()
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.reasoning_received = False
        self.reasoning_data = None
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker")
            # Subscribe to mode reasoning response
            client.subscribe("solar_heating/mode_reasoning")
            # Request mode reasoning
            self.request_mode_reasoning()
        else:
            print(f"❌ Failed to connect to MQTT broker: {rc}")
            sys.exit(1)
            
    def on_message(self, client, userdata, msg):
        try:
            if msg.topic == "solar_heating/mode_reasoning":
                self.reasoning_data = json.loads(msg.payload.decode())
                self.reasoning_received = True
                self.client.disconnect()
                
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            
    def request_mode_reasoning(self):
        """Request detailed mode reasoning from the system"""
        try:
            command = {
                "command_type": "get_mode_reasoning",
                "data": {}
            }
            self.client.publish("solar_heating/command", json.dumps(command))
            print("📡 Requesting mode reasoning...")
        except Exception as e:
            print(f"❌ Error requesting mode reasoning: {e}")
            
    def get_status(self):
        """Get current mode status"""
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            
            # Wait for response (max 5 seconds)
            timeout = 5
            start_time = time.time()
            
            while not self.reasoning_received and (time.time() - start_time) < timeout:
                time.sleep(0.1)
                
            if self.reasoning_received and self.reasoning_data:
                self.display_status()
            else:
                print("❌ Timeout waiting for mode reasoning response")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            
    def display_status(self):
        """Display current mode status"""
        reasoning = self.reasoning_data
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n🔍 Solar Heating System Status - {current_time}")
        print("=" * 60)
        print(f"📊 Current Mode: {reasoning['current_mode'].upper()}")
        print(f"🔧 Pump State: {reasoning['pump_state']}")
        print(f"💡 Explanation: {reasoning['explanation']}")
        print()
        print(f"🌡️  Temperature Status:")
        temps = reasoning['temperatures']
        print(f"   ☀️  Solar Collector: {temps['solar_collector']}°C")
        print(f"   🏠 Storage Tank: {temps['storage_tank']}°C")
        print(f"   📈 Temperature Difference: {temps['temperature_difference']}°C")
        print()
        print(f"⚙️  Control Thresholds:")
        thresholds = reasoning['control_thresholds']
        print(f"   🚀 Start Threshold: {thresholds['start_threshold']}°C")
        print(f"   🛑 Stop Threshold: {thresholds['stop_threshold']}°C")
        print(f"   ⚠️  Emergency Threshold: {thresholds['emergency_threshold']}°C")
        print()
        print(f"🔧 System Status:")
        status = reasoning['status']
        print(f"   🧪 Test Mode: {'ON' if status['test_mode'] else 'OFF'}")
        print(f"   👤 Manual Control: {'ON' if status['manual_control'] else 'OFF'}")
        print(f"   ⚠️  Overheated: {'YES' if status['overheated'] else 'NO'}")
        print("=" * 60)
        
        # Add mode-specific advice
        mode = reasoning['current_mode']
        if mode == 'heating':
            print("🔥 System is actively heating - pump is running")
        elif mode == 'standby':
            print("😴 System is in standby - waiting for heating conditions")
        elif mode == 'overheated':
            print("⚠️  System is overheated - emergency stop active")
        elif mode == 'manual':
            print("👤 Manual control is active - automatic control disabled")
        elif mode == 'test':
            print("🧪 System is in test mode - hardware simulation active")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Solar Heating System Mode Status Checker")
        print("Usage: python3 get_mode_status.py")
        print()
        print("This script shows the current system mode and detailed reasoning")
        print("for why the system is in that mode.")
        return
        
    checker = ModeStatusChecker()
    checker.get_status()

if __name__ == "__main__":
    main()
