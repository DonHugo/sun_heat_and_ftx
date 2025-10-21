#!/usr/bin/env python3
"""
MQTT Integration Test Suite
Tests real MQTT broker connections and message handling.

This test suite:
1. Tests connection to real MQTT brokers
2. Tests message publishing and subscription
3. Tests MQTT message handling
4. Tests MQTT failure scenarios
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
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class MQTTIntegrationTest:
    """MQTT integration test class"""
    
    def __init__(self, broker_host="192.168.0.110", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = None
        self.connected = False
        self.messages_received = []
        self.messages_published = []
        self.test_results = {}
        
    def connect(self, timeout=10):
        """Connect to MQTT broker with timeout"""
        if not MQTT_AVAILABLE:
            return False, "MQTT library not available"
            
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            
            # Set authentication if this is the production broker
            if self.broker_host == "192.168.0.110":
                from config import SystemConfig
                config = SystemConfig()
                if hasattr(config, 'mqtt_username') and hasattr(config, 'mqtt_password'):
                    self.client.username_pw_set(config.mqtt_username, config.mqtt_password)
            
            # Set connection timeout
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                return True, "Connected successfully"
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
        """Publish message to MQTT broker"""
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

def test_mqtt_broker_connection():
    """Test connection to various MQTT brokers"""
    print("📡 Testing MQTT broker connections...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    # Test different MQTT brokers
    brokers = [
        {"host": "192.168.0.110", "port": 1883, "name": "Production MQTT broker"},
        {"host": "test.mosquitto.org", "port": 1883, "name": "Mosquitto test broker"},
        {"host": "broker.hivemq.com", "port": 1883, "name": "HiveMQ public broker"},
    ]
    
    all_passed = True
    
    for i, broker in enumerate(brokers, 1):
        print(f"\n   Test {i}: {broker['name']} ({broker['host']}:{broker['port']})")
        
        mqtt_test = MQTTIntegrationTest(broker['host'], broker['port'])
        connected, message = mqtt_test.connect(timeout=5)
        
        if connected:
            print(f"      ✅ Connected: {message}")
            mqtt_test.disconnect()
        else:
            print(f"      ❌ Failed: {message}")
            all_passed = False
    
    return all_passed

def test_mqtt_message_publishing():
    """Test MQTT message publishing"""
    print("\n📤 Testing MQTT message publishing...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    # Use a public test broker
    mqtt_test = MQTTIntegrationTest("test.mosquitto.org", 1883)
    connected, message = mqtt_test.connect(timeout=10)
    
    if not connected:
        print(f"   ❌ Cannot connect to test broker: {message}")
        return False
    
    try:
        # Test publishing different types of messages
        test_messages = [
            {
                'topic': 'solar_heating/test/simple',
                'payload': 'Hello MQTT!',
                'description': 'Simple text message'
            },
            {
                'topic': 'solar_heating/test/json',
                'payload': json.dumps({
                    'timestamp': time.time(),
                    'temperature': 25.5,
                    'humidity': 60.0,
                    'test': True
                }),
                'description': 'JSON message'
            },
            {
                'topic': 'solar_heating/test/sensor_data',
                'payload': json.dumps({
                    'sensor_id': 'megabas_sensor_6',
                    'value': 75.5,
                    'unit': 'celsius',
                    'timestamp': datetime.now().isoformat()
                }),
                'description': 'Sensor data message'
            }
        ]
        
        all_passed = True
        
        for i, msg in enumerate(test_messages, 1):
            print(f"\n      Test {i}: {msg['description']}")
            
            published, result_message = mqtt_test.publish(msg['topic'], msg['payload'])
            
            if published:
                print(f"         ✅ Published: {result_message}")
                print(f"         Topic: {msg['topic']}")
                print(f"         Payload: {msg['payload'][:50]}{'...' if len(msg['payload']) > 50 else ''}")
            else:
                print(f"         ❌ Failed: {result_message}")
                all_passed = False
            
            # Small delay between messages
            time.sleep(0.5)
        
        return all_passed
        
    finally:
        mqtt_test.disconnect()

def test_mqtt_message_subscription():
    """Test MQTT message subscription"""
    print("\n📥 Testing MQTT message subscription...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    # Use a public test broker
    mqtt_test = MQTTIntegrationTest("test.mosquitto.org", 1883)
    connected, message = mqtt_test.connect(timeout=10)
    
    if not connected:
        print(f"   ❌ Cannot connect to test broker: {message}")
        return False
    
    try:
        # Subscribe to test topic
        test_topic = "solar_heating/test/subscription"
        subscribed, result_message = mqtt_test.subscribe(test_topic)
        
        if not subscribed:
            print(f"   ❌ Subscription failed: {result_message}")
            return False
        
        print(f"   ✅ Subscribed to: {test_topic}")
        
        # Publish a test message
        test_payload = json.dumps({
            'test_id': 'subscription_test',
            'timestamp': time.time(),
            'message': 'Test subscription message'
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

def test_mqtt_qos_levels():
    """Test MQTT QoS levels"""
    print("\n🔒 Testing MQTT QoS levels...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    # Use a public test broker
    mqtt_test = MQTTIntegrationTest("test.mosquitto.org", 1883)
    connected, message = mqtt_test.connect(timeout=10)
    
    if not connected:
        print(f"   ❌ Cannot connect to test broker: {message}")
        return False
    
    try:
        # Test different QoS levels
        qos_levels = [0, 1, 2]
        all_passed = True
        
        for qos in qos_levels:
            print(f"\n      Testing QoS {qos}:")
            
            # Subscribe with specific QoS
            test_topic = f"solar_heating/test/qos{qos}"
            subscribed, result_message = mqtt_test.subscribe(test_topic, qos)
            
            if not subscribed:
                print(f"         ❌ Subscription failed: {result_message}")
                all_passed = False
                continue
            
            print(f"         ✅ Subscribed with QoS {qos}")
            
            # Publish with specific QoS
            test_payload = json.dumps({
                'qos_level': qos,
                'timestamp': time.time(),
                'test': True
            })
            
            published, result_message = mqtt_test.publish(test_topic, test_payload, qos)
            
            if not published:
                print(f"         ❌ Publish failed: {result_message}")
                all_passed = False
                continue
            
            print(f"         ✅ Published with QoS {qos}")
            
            # Wait for message
            time.sleep(1)
            
            # Check if message was received
            received_messages = [msg for msg in mqtt_test.messages_received if msg['topic'] == test_topic]
            if received_messages:
                print(f"         ✅ Message received with QoS {received_messages[0]['qos']}")
            else:
                print(f"         ❌ No message received")
                all_passed = False
        
        return all_passed
        
    finally:
        mqtt_test.disconnect()

def test_mqtt_failure_scenarios():
    """Test MQTT failure scenarios"""
    print("\n⚠️ Testing MQTT failure scenarios...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    all_passed = True
    
    # Test 1: Invalid broker
    print("\n      Test 1: Invalid broker connection")
    mqtt_test = MQTTIntegrationTest("invalid.broker.com", 1883)
    connected, message = mqtt_test.connect(timeout=5)
    
    if not connected:
        print(f"         ✅ Correctly failed to connect: {message}")
    else:
        print(f"         ❌ Unexpectedly connected to invalid broker")
        all_passed = False
        mqtt_test.disconnect()
    
    # Test 2: Invalid port
    print("\n      Test 2: Invalid port")
    mqtt_test = MQTTIntegrationTest("test.mosquitto.org", 9999)
    connected, message = mqtt_test.connect(timeout=5)
    
    if not connected:
        print(f"         ✅ Correctly failed to connect: {message}")
    else:
        print(f"         ❌ Unexpectedly connected to invalid port")
        all_passed = False
        mqtt_test.disconnect()
    
    # Test 3: Publish without connection
    print("\n      Test 3: Publish without connection")
    mqtt_test = MQTTIntegrationTest("test.mosquitto.org", 1883)
    # Don't connect
    published, result_message = mqtt_test.publish("test/topic", "test message")
    
    if not published:
        print(f"         ✅ Correctly failed to publish: {result_message}")
    else:
        print(f"         ❌ Unexpectedly published without connection")
        all_passed = False
    
    return all_passed

def test_mqtt_performance():
    """Test MQTT performance"""
    print("\n⚡ Testing MQTT performance...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    # Use a public test broker
    mqtt_test = MQTTIntegrationTest("test.mosquitto.org", 1883)
    connected, message = mqtt_test.connect(timeout=10)
    
    if not connected:
        print(f"   ❌ Cannot connect to test broker: {message}")
        return False
    
    try:
        # Subscribe to test topic
        test_topic = "solar_heating/test/performance"
        subscribed, result_message = mqtt_test.subscribe(test_topic)
        
        if not subscribed:
            print(f"   ❌ Subscription failed: {result_message}")
            return False
        
        # Test publishing multiple messages
        num_messages = 10
        start_time = time.time()
        
        for i in range(num_messages):
            test_payload = json.dumps({
                'message_id': i,
                'timestamp': time.time(),
                'data': f'Performance test message {i}'
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
        time.sleep(2)
        
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

def main():
    """Main test runner"""
    print("🚀 Starting MQTT Integration Test Suite")
    print("=" * 70)
    print("This test suite tests real MQTT broker connections and message handling.")
    print("=" * 70)
    
    tests = [
        ("MQTT Broker Connection", test_mqtt_broker_connection),
        ("MQTT Message Publishing", test_mqtt_message_publishing),
        ("MQTT Message Subscription", test_mqtt_message_subscription),
        ("MQTT QoS Levels", test_mqtt_qos_levels),
        ("MQTT Failure Scenarios", test_mqtt_failure_scenarios),
        ("MQTT Performance", test_mqtt_performance),
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
    
    print("\n📊 MQTT INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! MQTT integration is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED. MQTT integration needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
