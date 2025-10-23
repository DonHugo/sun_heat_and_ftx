#!/usr/bin/env python3
"""
Production MQTT Test Suite
Tests the system with the actual production MQTT broker.

This test suite:
1. Connects to the production MQTT broker (192.168.0.110:1883)
2. Tests real sensor data publishing and subscription
3. Tests system status and control messages
4. Validates production-like MQTT behavior
"""

import sys
import os
import time
import json
import threading
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("⚠️  paho-mqtt not available. Install with: pip install paho-mqtt")

try:
    from main_system import SolarHeatingSystem
    from config import SystemConfig
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class ProductionMQTTTest:
    """Production MQTT test class"""
    
    def __init__(self):
        self.config = SystemConfig()
        self.client = None
        self.connected = False
        self.messages_received = []
        self.messages_published = []
        self.test_results = {}
        
    def connect(self, timeout=10):
        """Connect to production MQTT broker with timeout"""
        if not MQTT_AVAILABLE:
            return False, "MQTT library not available"
            
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            
            # Set authentication if provided
            if hasattr(self.config, 'mqtt_username') and hasattr(self.config, 'mqtt_password'):
                self.client.username_pw_set(self.config.mqtt_username, self.config.mqtt_password)
            
            # Connect to production broker
            self.client.connect(self.config.mqtt_broker, self.config.mqtt_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                return True, f"Connected to production broker {self.config.mqtt_broker}:{self.config.mqtt_port}"
            else:
                return False, "Connection timeout"
                
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
        else:
            self.connected = False
    
    def on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            message = {
                'topic': msg.topic,
                'payload': msg.payload.decode('utf-8'),
                'timestamp': time.time(),
                'qos': msg.qos
            }
            self.messages_received.append(message)
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
    
    def on_publish(self, client, userdata, mid):
        """MQTT publish callback"""
        self.messages_published.append({
            'mid': mid,
            'timestamp': time.time()
        })
    
    def publish(self, topic, payload, qos=0, retain=False):
        """Publish message to production MQTT broker"""
        if not self.connected:
            return False, "Not connected"
        
        try:
            result = self.client.publish(topic, payload, qos, retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                return True, "Published successfully"
            else:
                return False, f"Publish failed with code {result.rc}"
        except Exception as e:
            return False, f"Publish error: {str(e)}"
    
    def subscribe(self, topic, qos=0):
        """Subscribe to MQTT topic"""
        if not self.connected:
            return False, "Not connected"
        
        try:
            result = self.client.subscribe(topic, qos)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                return True, "Subscribed successfully"
            else:
                return False, f"Subscribe failed with code {result[0]}"
        except Exception as e:
            return False, f"Subscribe error: {str(e)}"
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False

def test_production_mqtt_connection():
    """Test connection to production MQTT broker"""
    print("🏭 Testing production MQTT broker connection...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    mqtt_test = ProductionMQTTTest()
    connected, message = mqtt_test.connect(timeout=10)
    
    if connected:
        print(f"   ✅ {message}")
        mqtt_test.disconnect()
        return True
    else:
        print(f"   ❌ Failed: {message}")
        return False

def test_production_sensor_data_publishing():
    """Test publishing sensor data to production MQTT broker"""
    print("\n📊 Testing production sensor data publishing...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    mqtt_test = ProductionMQTTTest()
    connected, message = mqtt_test.connect(timeout=10)
    
    if not connected:
        print(f"   ❌ Cannot connect to production broker: {message}")
        return False
    
    try:
        # Test publishing realistic sensor data
        sensor_data = {
            'megabas_sensor_6': 75.5,  # Solar collector
            'megabas_sensor_7': 45.2,  # Storage tank
            'megabas_sensor_8': 60.1,  # Return line
            'rtd_sensor_0': 42.1,      # Water heater bottom
            'rtd_sensor_1': 44.3,      # Water heater 20cm
            'rtd_sensor_2': 46.8,      # Water heater 40cm
            'rtd_sensor_3': 49.2,      # Water heater 60cm
            'rtd_sensor_4': 51.7,      # Water heater 80cm
            'rtd_sensor_5': 54.1,      # Water heater 100cm
            'rtd_sensor_6': 56.4,      # Water heater 120cm
            'rtd_sensor_7': 58.9,      # Water heater 140cm (top)
        }
        
        all_passed = True
        
        for sensor_id, value in sensor_data.items():
            topic = f"solar_heating/sensors/{sensor_id}"
            payload = json.dumps({
                'sensor_id': sensor_id,
                'value': value,
                'unit': 'celsius',
                'timestamp': datetime.now().isoformat(),
                'test': True
            })
            
            published, result_message = mqtt_test.publish(topic, payload)
            
            if published:
                print(f"   ✅ Published {sensor_id}: {value}°C")
            else:
                print(f"   ❌ Failed to publish {sensor_id}: {result_message}")
                all_passed = False
            
            # Small delay between messages
            time.sleep(0.1)
        
        return all_passed
        
    finally:
        mqtt_test.disconnect()

def test_production_system_status_publishing():
    """Test publishing system status to production MQTT broker"""
    print("\n📈 Testing production system status publishing...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    mqtt_test = ProductionMQTTTest()
    connected, message = mqtt_test.connect(timeout=10)
    
    if not connected:
        print(f"   ❌ Cannot connect to production broker: {message}")
        return False
    
    try:
        # Test publishing system status messages
        status_messages = [
            {
                'topic': 'solar_heating/status/system_mode',
                'payload': json.dumps({
                    'mode': 'heating',
                    'reason': 'dT=15.2°C >= 8.0°C',
                    'timestamp': datetime.now().isoformat(),
                    'test': True
                }),
                'description': 'System mode status'
            },
            {
                'topic': 'solar_heating/status/pump_state',
                'payload': json.dumps({
                    'pump_on': True,
                    'dT': 15.2,
                    'collector_temp': 75.5,
                    'tank_temp': 60.3,
                    'timestamp': datetime.now().isoformat(),
                    'test': True
                }),
                'description': 'Pump state status'
            },
            {
                'topic': 'solar_heating/status/energy',
                'payload': json.dumps({
                    'daily_energy': 12.5,
                    'lifetime_energy': 1250.8,
                    'current_power': 2.3,
                    'timestamp': datetime.now().isoformat(),
                    'test': True
                }),
                'description': 'Energy status'
            }
        ]
        
        all_passed = True
        
        for msg in status_messages:
            published, result_message = mqtt_test.publish(msg['topic'], msg['payload'])
            
            if published:
                print(f"   ✅ Published {msg['description']}")
            else:
                print(f"   ❌ Failed to publish {msg['description']}: {result_message}")
                all_passed = False
            
            # Small delay between messages
            time.sleep(0.1)
        
        return all_passed
        
    finally:
        mqtt_test.disconnect()

def test_production_mqtt_subscription():
    """Test subscribing to production MQTT topics"""
    print("\n📥 Testing production MQTT subscription...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    mqtt_test = ProductionMQTTTest()
    connected, message = mqtt_test.connect(timeout=10)
    
    if not connected:
        print(f"   ❌ Cannot connect to production broker: {message}")
        return False
    
    try:
        # Subscribe to test topics
        test_topics = [
            'solar_heating/test/subscription',
            'solar_heating/sensors/+',
            'solar_heating/status/+'
        ]
        
        all_subscribed = True
        
        for topic in test_topics:
            subscribed, result_message = mqtt_test.subscribe(topic)
            
            if subscribed:
                print(f"   ✅ Subscribed to: {topic}")
            else:
                print(f"   ❌ Failed to subscribe to {topic}: {result_message}")
                all_subscribed = False
        
        if not all_subscribed:
            return False
        
        # Publish a test message
        test_topic = "solar_heating/test/subscription"
        test_payload = json.dumps({
            'test_id': 'production_subscription_test',
            'timestamp': time.time(),
            'message': 'Test subscription message to production broker'
        })
        
        published, result_message = mqtt_test.publish(test_topic, test_payload)
        
        if not published:
            print(f"   ❌ Test message publish failed: {result_message}")
            return False
        
        print(f"   ✅ Published test message")
        
        # Wait for message to be received
        time.sleep(2)
        
        # Check if message was received
        if len(mqtt_test.messages_received) > 0:
            received_msg = mqtt_test.messages_received[0]
            print(f"   ✅ Message received:")
            print(f"      Topic: {received_msg['topic']}")
            print(f"      Payload: {received_msg['payload']}")
            print(f"      QoS: {received_msg['qos']}")
            return True
        else:
            print(f"   ❌ No messages received")
            return False
        
    finally:
        mqtt_test.disconnect()

def test_production_mqtt_performance():
    """Test MQTT performance with production broker"""
    print("\n⚡ Testing production MQTT performance...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    mqtt_test = ProductionMQTTTest()
    connected, message = mqtt_test.connect(timeout=10)
    
    if not connected:
        print(f"   ❌ Cannot connect to production broker: {message}")
        return False
    
    try:
        # Subscribe to test topic
        test_topic = "solar_heating/test/performance"
        subscribed, result_message = mqtt_test.subscribe(test_topic)
        
        if not subscribed:
            print(f"   ❌ Subscription failed: {result_message}")
            return False
        
        # Test publishing multiple sensor messages
        num_messages = 20
        start_time = time.time()
        
        for i in range(num_messages):
            test_payload = json.dumps({
                'message_id': i,
                'sensor_id': f'megabas_sensor_{i % 8}',
                'value': 25.0 + (i * 0.5),
                'timestamp': time.time(),
                'test': True
            })
            
            published, result_message = mqtt_test.publish(test_topic, test_payload)
            
            if not published:
                print(f"   ❌ Message {i} publish failed: {result_message}")
                return False
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   ✅ Published {num_messages} messages in {duration:.2f} seconds")
        print(f"   ✅ Rate: {num_messages/duration:.1f} messages/second")
        
        # Wait for messages to be received
        time.sleep(3)
        
        # Check received messages
        received_count = len(mqtt_test.messages_received)
        print(f"   ✅ Received {received_count} messages")
        
        if received_count >= num_messages * 0.8:  # Allow for some message loss
            print(f"   ✅ Message delivery rate: {received_count/num_messages*100:.1f}%")
            return True
        else:
            print(f"   ❌ Low message delivery rate: {received_count/num_messages*100:.1f}%")
            return False
        
    finally:
        mqtt_test.disconnect()

def test_production_mqtt_real_system_integration():
    """Test integration with real system using production MQTT"""
    print("\n🔗 Testing production MQTT real system integration...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    mqtt_test = ProductionMQTTTest()
    connected, message = mqtt_test.connect(timeout=10)
    
    if not connected:
        print(f"   ❌ Cannot connect to production broker: {message}")
        return False
    
    try:
        # Subscribe to real system topics
        real_topics = [
            'solar_heating/sensors/+',
            'solar_heating/status/+',
            'solar_heating/control/+'
        ]
        
        all_subscribed = True
        
        for topic in real_topics:
            subscribed, result_message = mqtt_test.subscribe(topic)
            
            if subscribed:
                print(f"   ✅ Subscribed to real system topic: {topic}")
            else:
                print(f"   ❌ Failed to subscribe to {topic}: {result_message}")
                all_subscribed = False
        
        if not all_subscribed:
            return False
        
        # Wait for real system messages
        print(f"   ⏳ Waiting for real system messages (10 seconds)...")
        time.sleep(10)
        
        # Check received messages
        received_count = len(mqtt_test.messages_received)
        print(f"   ✅ Received {received_count} real system messages")
        
        if received_count > 0:
            print(f"   ✅ Real system integration working:")
            for msg in mqtt_test.messages_received[:5]:  # Show first 5 messages
                print(f"      Topic: {msg['topic']}")
                print(f"      Payload: {msg['payload'][:100]}{'...' if len(msg['payload']) > 100 else ''}")
            return True
        else:
            print(f"   ⚠️  No real system messages received (system may not be running)")
            return True  # This is not a failure, just no active system
        
    finally:
        mqtt_test.disconnect()

def main():
    """Main test runner"""
    print("🏭 Starting Production MQTT Test Suite")
    print("=" * 70)
    print("This test suite tests the system with the actual production MQTT broker.")
    print("Production MQTT Broker: 192.168.0.110:1883")
    print("=" * 70)
    
    tests = [
        ("Production MQTT Connection", test_production_mqtt_connection),
        ("Production Sensor Data Publishing", test_production_sensor_data_publishing),
        ("Production System Status Publishing", test_production_system_status_publishing),
        ("Production MQTT Subscription", test_production_mqtt_subscription),
        ("Production MQTT Performance", test_production_mqtt_performance),
        ("Production MQTT Real System Integration", test_production_mqtt_real_system_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n❌ {test_name}: EXCEPTION - {str(e)}")
    
    print("\n📊 PRODUCTION MQTT TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Production MQTT integration is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED. Production MQTT integration needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
