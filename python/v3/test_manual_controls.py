#!/usr/bin/env python3
"""
Test script for manual control switches in Solar Heating System v3
Verifies that all manual control switches work properly in Home Assistant
"""

import asyncio
import json
import time
import paho.mqtt.client as mqtt_client
from config import config

class ManualControlTester:
    def __init__(self):
        self.client = None
        self.connected = False
        self.test_results = {}
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker")
            self.connected = True
        else:
            print(f"❌ Failed to connect to MQTT broker: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        print("🔌 Disconnected from MQTT broker")
        self.connected = False
    
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        
        print(f"📨 Received: {topic} = {payload}")
        
        # Parse Home Assistant state messages
        if topic.endswith('/state'):
            try:
                data = json.loads(payload)
                entity_id = topic.split('/')[-2]  # Extract entity ID from topic
                
                if entity_id in self.test_results:
                    self.test_results[entity_id]['current_state'] = data.get('state', payload)
                    print(f"   📊 {entity_id}: {data.get('state', payload)}")
            except json.JSONDecodeError:
                # Handle non-JSON payloads (like simple strings)
                entity_id = topic.split('/')[-2]
                if entity_id in self.test_results:
                    self.test_results[entity_id]['current_state'] = payload
                    print(f"   📊 {entity_id}: {payload}")
    
    def connect_mqtt(self):
        """Connect to MQTT broker"""
        self.client = mqtt_client.Client()
        self.client.username_pw_set(config.mqtt_username, config.mqtt_password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        try:
            self.client.connect(config.mqtt_broker, config.mqtt_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            if not self.connected:
                raise Exception("Failed to connect to MQTT broker")
                
        except Exception as e:
            print(f"❌ MQTT connection error: {e}")
            return False
        
        return True
    
    def subscribe_to_controls(self):
        """Subscribe to all control topics"""
        topics = [
            f"homeassistant/switch/{config.mqtt_client_id}_primary_pump/state",
            f"homeassistant/switch/{config.mqtt_client_id}_primary_pump_manual/state", 
            f"homeassistant/switch/{config.mqtt_client_id}_cartridge_heater/state",
            f"homeassistant/number/{config.mqtt_client_id}_set_temp_tank_1/state",
            f"homeassistant/number/{config.mqtt_client_id}_dTStart_tank_1/state",
            f"homeassistant/number/{config.mqtt_client_id}_dTStop_tank_1/state",
            f"homeassistant/number/{config.mqtt_client_id}_kylning_kollektor/state",
            f"homeassistant/number/{config.mqtt_client_id}_temp_kok/state",
            f"homeassistant/number/{config.mqtt_client_id}_temp_kok_hysteres/state",
        ]
        
        for topic in topics:
            self.client.subscribe(topic)
            print(f"📡 Subscribed to: {topic}")
            
            # Extract entity ID for tracking
            entity_id = topic.split('/')[-2]
            self.test_results[entity_id] = {
                'topic': topic,
                'current_state': None,
                'tested': False
            }
    
    def test_switch_control(self, entity_id, test_value):
        """Test a switch control"""
        topic = f"homeassistant/switch/{config.mqtt_client_id}_{entity_id}/set"
        payload = "ON" if test_value else "OFF"
        
        print(f"🔧 Testing {entity_id}: Sending {payload}")
        self.client.publish(topic, payload)
        
        # Wait for response
        time.sleep(2)
        
        if entity_id in self.test_results:
            self.test_results[entity_id]['tested'] = True
            current_state = self.test_results[entity_id]['current_state']
            expected_state = "ON" if test_value else "OFF"
            
            if current_state == expected_state:
                print(f"   ✅ {entity_id}: {current_state} (Expected: {expected_state})")
                return True
            else:
                print(f"   ❌ {entity_id}: {current_state} (Expected: {expected_state})")
                return False
        
        return False
    
    def test_number_control(self, entity_id, test_value):
        """Test a number control"""
        topic = f"homeassistant/number/{config.mqtt_client_id}_{entity_id}/set"
        payload = str(test_value)
        
        print(f"🔧 Testing {entity_id}: Sending {payload}")
        self.client.publish(topic, payload)
        
        # Wait for response
        time.sleep(2)
        
        if entity_id in self.test_results:
            self.test_results[entity_id]['tested'] = True
            current_state = self.test_results[entity_id]['current_state']
            
            try:
                current_value = float(current_state)
                if abs(current_value - test_value) < 0.1:
                    print(f"   ✅ {entity_id}: {current_value} (Expected: {test_value})")
                    return True
                else:
                    print(f"   ❌ {entity_id}: {current_value} (Expected: {test_value})")
                    return False
            except (ValueError, TypeError):
                print(f"   ❌ {entity_id}: Invalid value '{current_state}' (Expected: {test_value})")
                return False
        
        return False
    
    def run_tests(self):
        """Run all manual control tests"""
        print("🧪 Solar Heating System v3 - Manual Control Tests")
        print("=" * 60)
        
        if not self.connect_mqtt():
            return False
        
        # Subscribe to all control topics
        self.subscribe_to_controls()
        time.sleep(3)  # Wait for initial state messages
        
        print("\n🔧 Testing Switch Controls:")
        print("-" * 30)
        
        # Test switch controls
        switch_tests = [
            ('primary_pump', True),
            ('primary_pump', False),
            ('primary_pump_manual', True),
            ('primary_pump_manual', False),
            ('cartridge_heater', True),
            ('cartridge_heater', False),
        ]
        
        switch_results = []
        for entity_id, value in switch_tests:
            result = self.test_switch_control(entity_id, value)
            switch_results.append(result)
            time.sleep(1)
        
        print("\n🔢 Testing Number Controls:")
        print("-" * 30)
        
        # Test number controls
        number_tests = [
            ('set_temp_tank_1', 75.0),
            ('dTStart_tank_1', 8.0),
            ('dTStop_tank_1', 4.0),
            ('kylning_kollektor', 90.0),
            ('temp_kok', 150.0),
            ('temp_kok_hysteres', 10.0),
        ]
        
        number_results = []
        for entity_id, value in number_tests:
            result = self.test_number_control(entity_id, value)
            number_results.append(result)
            time.sleep(1)
        
        # Summary
        print("\n📊 Test Results Summary:")
        print("=" * 60)
        
        switch_passed = sum(switch_results)
        switch_total = len(switch_results)
        number_passed = sum(number_results)
        number_total = len(number_results)
        
        print(f"Switch Controls: {switch_passed}/{switch_total} passed")
        print(f"Number Controls: {number_passed}/{number_total} passed")
        print(f"Overall: {switch_passed + number_passed}/{switch_total + number_total} passed")
        
        if switch_passed + number_passed == switch_total + number_total:
            print("🎉 All manual controls are working correctly!")
            return True
        else:
            print("⚠️  Some manual controls have issues")
            return False
    
    def cleanup(self):
        """Cleanup MQTT connection"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

def main():
    tester = ManualControlTester()
    try:
        success = tester.run_tests()
        return 0 if success else 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    exit(main())
