#!/usr/bin/env python3
"""
Solar Heating System Mode Change Monitor

This script helps you monitor and understand why the system changes
between heating and standby modes by showing detailed reasoning.
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

class ModeMonitor:
    def __init__(self):
        self.client = mqtt_client.Client()
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.last_mode = None
        self.last_reasoning = None
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker")
            # Subscribe to system mode and mode reasoning
            client.subscribe("homeassistant/sensor/solar_heating_system_mode/state")
            client.subscribe("solar_heating/mode_reasoning")
            print("📡 Subscribed to mode monitoring topics")
        else:
            print(f"❌ Failed to connect to MQTT broker: {rc}")
            
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            
            if topic == "homeassistant/sensor/solar_heating_system_mode/state":
                self.handle_mode_change(payload)
            elif topic == "solar_heating/mode_reasoning":
                self.handle_mode_reasoning(payload)
                
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            
    def handle_mode_change(self, mode):
        """Handle system mode changes"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if mode != self.last_mode:
            if self.last_mode is not None:
                print(f"\n🔄 {current_time} - Mode Changed: {self.last_mode} → {mode}")
                print("=" * 60)
            else:
                print(f"\n🔄 {current_time} - Current Mode: {mode}")
                print("=" * 60)
                
            self.last_mode = mode
            
            # Request detailed reasoning
            self.request_mode_reasoning()
            
    def handle_mode_reasoning(self, reasoning_json):
        """Handle detailed mode reasoning"""
        try:
            reasoning = json.loads(reasoning_json)
            self.last_reasoning = reasoning
            
            print(f"📊 Mode Reasoning:")
            print(f"   Current Mode: {reasoning['current_mode']}")
            print(f"   Pump State: {reasoning['pump_state']}")
            print(f"   Explanation: {reasoning['explanation']}")
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
            
        except Exception as e:
            print(f"❌ Error parsing mode reasoning: {e}")
            
    def request_mode_reasoning(self):
        """Request detailed mode reasoning from the system"""
        try:
            command = {
                "command_type": "get_mode_reasoning",
                "data": {}
            }
            self.client.publish("solar_heating/command", json.dumps(command))
        except Exception as e:
            print(f"❌ Error requesting mode reasoning: {e}")
            
    def start_monitoring(self):
        """Start monitoring mode changes"""
        print("🔍 Solar Heating System Mode Monitor")
        print("=" * 60)
        print("Monitoring system mode changes and reasoning...")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.client.disconnect()

def main():
    """Main function"""
    monitor = ModeMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
