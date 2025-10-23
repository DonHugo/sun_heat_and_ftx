#!/usr/bin/env python3
"""
MQTT Connectivity Test Suite
Tests MQTT connectivity to various brokers including production.

This test suite:
1. Tests connection to production MQTT broker (192.168.0.110:1883)
2. Tests connection to public MQTT brokers
3. Tests connection to local MQTT broker
4. Provides connectivity status for all brokers
"""

import sys
import os
import time
import socket

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("⚠️  paho-mqtt not available. Install with: pip install paho-mqtt")

try:
    from config import SystemConfig
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class MQTTConnectivityTest:
    """MQTT connectivity test class"""
    
    def __init__(self, broker_host, broker_port):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = None
        self.connected = False
        self.connection_time = 0
        
    def test_network_connectivity(self):
        """Test basic network connectivity to broker"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.broker_host, self.broker_port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def test_mqtt_connection(self, timeout=10):
        """Test MQTT connection to broker"""
        if not MQTT_AVAILABLE:
            return False, "MQTT library not available"
            
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            
            # Set authentication if this is the production broker
            if self.broker_host == "192.168.0.110":
                config = SystemConfig()
                if hasattr(config, 'mqtt_username') and hasattr(config, 'mqtt_password'):
                    self.client.username_pw_set(config.mqtt_username, config.mqtt_password)
            
            start_time = time.time()
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                self.connection_time = time.time() - start_time
                return True, f"Connected in {self.connection_time:.2f}s"
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
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False

def test_production_mqtt_connectivity():
    """Test connectivity to production MQTT broker"""
    print("🏭 Testing production MQTT broker connectivity...")
    
    config = SystemConfig()
    broker_host = config.mqtt_broker
    broker_port = config.mqtt_port
    
    print(f"   Production Broker: {broker_host}:{broker_port}")
    
    # Test network connectivity
    mqtt_test = MQTTConnectivityTest(broker_host, broker_port)
    network_ok = mqtt_test.test_network_connectivity()
    
    if network_ok:
        print(f"   ✅ Network connectivity: OK")
        
        # Test MQTT connection
        connected, message = mqtt_test.test_mqtt_connection(timeout=5)
        
        if connected:
            print(f"   ✅ MQTT connection: {message}")
            mqtt_test.disconnect()
            return True
        else:
            print(f"   ❌ MQTT connection: {message}")
            return False
    else:
        print(f"   ❌ Network connectivity: FAILED")
        print(f"   ℹ️  Production broker not accessible from development environment")
        return False

def test_public_mqtt_brokers():
    """Test connectivity to public MQTT brokers"""
    print("\n🌐 Testing public MQTT broker connectivity...")
    
    public_brokers = [
        {"host": "test.mosquitto.org", "port": 1883, "name": "Mosquitto Test Broker"},
        {"host": "broker.hivemq.com", "port": 1883, "name": "HiveMQ Public Broker"},
        {"host": "mqtt.eclipse.org", "port": 1883, "name": "Eclipse MQTT Broker"},
    ]
    
    all_passed = True
    
    for i, broker in enumerate(public_brokers, 1):
        print(f"\n   Test {i}: {broker['name']} ({broker['host']}:{broker['port']})")
        
        mqtt_test = MQTTConnectivityTest(broker['host'], broker['port'])
        
        # Test network connectivity
        network_ok = mqtt_test.test_network_connectivity()
        
        if network_ok:
            print(f"      ✅ Network connectivity: OK")
            
            # Test MQTT connection
            connected, message = mqtt_test.test_mqtt_connection(timeout=5)
            
            if connected:
                print(f"      ✅ MQTT connection: {message}")
                mqtt_test.disconnect()
            else:
                print(f"      ❌ MQTT connection: {message}")
                all_passed = False
        else:
            print(f"      ❌ Network connectivity: FAILED")
            all_passed = False
    
    return all_passed

def test_local_mqtt_broker():
    """Test connectivity to local MQTT broker"""
    print("\n🏠 Testing local MQTT broker connectivity...")
    
    local_brokers = [
        {"host": "localhost", "port": 1883, "name": "Local MQTT Broker"},
        {"host": "127.0.0.1", "port": 1883, "name": "Local MQTT Broker (127.0.0.1)"},
    ]
    
    all_passed = True
    
    for i, broker in enumerate(local_brokers, 1):
        print(f"\n   Test {i}: {broker['name']} ({broker['host']}:{broker['port']})")
        
        mqtt_test = MQTTConnectivityTest(broker['host'], broker['port'])
        
        # Test network connectivity
        network_ok = mqtt_test.test_network_connectivity()
        
        if network_ok:
            print(f"      ✅ Network connectivity: OK")
            
            # Test MQTT connection
            connected, message = mqtt_test.test_mqtt_connection(timeout=5)
            
            if connected:
                print(f"      ✅ MQTT connection: {message}")
                mqtt_test.disconnect()
            else:
                print(f"      ❌ MQTT connection: {message}")
                all_passed = False
        else:
            print(f"      ❌ Network connectivity: FAILED")
            print(f"      ℹ️  Local MQTT broker not running")
            all_passed = False
    
    return all_passed

def test_mqtt_library_availability():
    """Test MQTT library availability"""
    print("\n📚 Testing MQTT library availability...")
    
    if MQTT_AVAILABLE:
        print("   ✅ MQTT library (paho-mqtt) is available")
        
        # Test library version
        try:
            import paho.mqtt.client as mqtt
            print(f"   ✅ MQTT library version: {mqtt.__version__}")
            return True
        except Exception as e:
            print(f"   ❌ MQTT library error: {e}")
            return False
    else:
        print("   ❌ MQTT library (paho-mqtt) is not available")
        print("   ℹ️  Install with: pip install paho-mqtt")
        return False

def main():
    """Main test runner"""
    print("🔌 Starting MQTT Connectivity Test Suite")
    print("=" * 70)
    print("This test suite tests MQTT connectivity to various brokers.")
    print("=" * 70)
    
    tests = [
        ("MQTT Library Availability", test_mqtt_library_availability),
        ("Production MQTT Broker", test_production_mqtt_connectivity),
        ("Public MQTT Brokers", test_public_mqtt_brokers),
        ("Local MQTT Broker", test_local_mqtt_broker),
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
    
    print("\n📊 MQTT CONNECTIVITY TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    
    print(f"\n🔍 CONNECTIVITY ANALYSIS:")
    print(f"{'='*70}")
    
    if MQTT_AVAILABLE:
        print("✅ MQTT Library: Available")
    else:
        print("❌ MQTT Library: Not available")
    
    # Test production broker
    config = SystemConfig()
    production_test = MQTTConnectivityTest(config.mqtt_broker, config.mqtt_port)
    production_network = production_test.test_network_connectivity()
    
    if production_network:
        print(f"✅ Production Broker ({config.mqtt_broker}:{config.mqtt_port}): Network accessible")
    else:
        print(f"❌ Production Broker ({config.mqtt_broker}:{config.mqtt_port}): Network not accessible")
        print("   ℹ️  This is expected in development environment")
    
    # Test public brokers
    public_test = MQTTConnectivityTest("test.mosquitto.org", 1883)
    public_network = public_test.test_network_connectivity()
    
    if public_network:
        print("✅ Public Brokers: Network accessible")
    else:
        print("❌ Public Brokers: Network not accessible")
    
    # Test local broker
    local_test = MQTTConnectivityTest("localhost", 1883)
    local_network = local_test.test_network_connectivity()
    
    if local_network:
        print("✅ Local Broker: Network accessible")
    else:
        print("❌ Local Broker: Network not accessible")
        print("   ℹ️  Install and start local MQTT broker for full testing")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"{'='*70}")
    
    if not MQTT_AVAILABLE:
        print("1. Install MQTT library: pip install paho-mqtt")
    
    if not local_network:
        print("2. Set up local MQTT broker for development testing")
        print("   - Install: brew install mosquitto (macOS) or apt-get install mosquitto (Ubuntu)")
        print("   - Start: mosquitto -c /usr/local/etc/mosquitto/mosquitto.conf")
    
    if not production_network:
        print("3. Production broker not accessible from development environment")
        print("   - This is expected and normal")
        print("   - Production tests should be run on the production network")
    
    if public_network:
        print("4. Public MQTT brokers are accessible for testing")
        print("   - Use public brokers for MQTT functionality testing")
        print("   - Avoid publishing sensitive data to public brokers")
    
    if passed >= total * 0.75:
        print(f"\n🎉 MQTT connectivity test completed successfully!")
        print("The system has good MQTT connectivity for testing purposes.")
        return True
    else:
        print(f"\n⚠️  MQTT connectivity issues detected.")
        print("Please address the connectivity issues for full MQTT testing.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
