#!/usr/bin/env python3
"""
Test script for the real-time energy sensor
This script tests the new real-time energy rate sensor functionality
"""

import asyncio
import json
import time
from mqtt_handler import MQTTHandler
from config import config

async def test_realtime_energy_sensor():
    """Test the real-time energy sensor functionality"""
    print("Testing Real-time Energy Sensor...")
    
    # Initialize MQTT handler
    mqtt = MQTTHandler()
    
    # Connect to MQTT broker
    if not mqtt.connect():
        print("Failed to connect to MQTT broker")
        return
    
    print("Connected to MQTT broker")
    
    # Test data - simulate real sensor data
    test_data = {
        'realtime_energy_rate_kw': 2.345,
        'realtime_temp_rate_per_hour': 3.2,
        'energy_efficiency_index': 75.5,
        'system_performance_score': 82.3,
        'energy_trend': 'increasing',
        'temperature_trend': 'increasing',
        'energy_temp_ratio': 0.045,
        'energy_total_ratio': 0.023,
        'temp_change_ratio': 0.032,
        'energy_efficiency_factor': 0.031
    }
    
    # Publish test data
    print("Publishing test data...")
    success = mqtt.publish_realtime_energy_sensor(test_data)
    
    if success:
        print("✅ Test data published successfully")
        print(f"Topic: solar_heating_v3/status/realtime_energy_sensor")
        print(f"Data: {json.dumps(test_data, indent=2)}")
    else:
        print("❌ Failed to publish test data")
    
    # Wait a moment for the message to be sent
    await asyncio.sleep(2)
    
    # Test with water usage (negative energy rate)
    print("\nTesting with water usage (negative energy rate)...")
    test_data_2 = {
        'realtime_energy_rate_kw': -1.2,  # Water being used
        'realtime_temp_rate_per_hour': -2.5,  # Temperature decreasing
        'energy_efficiency_index': 25.0,
        'system_performance_score': 35.7,
        'energy_trend': 'water_usage',
        'temperature_trend': 'cooling',
        'energy_temp_ratio': 0.0,
        'energy_total_ratio': 0.0,
        'temp_change_ratio': -0.025,
        'energy_efficiency_factor': 0.0,
        'water_usage_rate_kw': 1.2,
        'water_usage_intensity': 'moderate'
    }
    
    success = mqtt.publish_realtime_energy_sensor(test_data_2)
    
    if success:
        print("✅ Second test data published successfully")
        print(f"Data: {json.dumps(test_data_2, indent=2)}")
    else:
        print("❌ Failed to publish second test data")
    
    # Wait a moment for the message to be sent
    await asyncio.sleep(2)
    
    # Test with heavy water usage
    print("\nTesting with heavy water usage...")
    test_data_3 = {
        'realtime_energy_rate_kw': -2.8,  # Heavy water usage
        'realtime_temp_rate_per_hour': -4.2,  # Rapid temperature decrease
        'energy_efficiency_index': 15.0,
        'system_performance_score': 45.0,
        'energy_trend': 'water_usage',
        'temperature_trend': 'cooling',
        'energy_temp_ratio': 0.0,
        'energy_total_ratio': 0.0,
        'temp_change_ratio': -0.042,
        'energy_efficiency_factor': 0.0,
        'water_usage_rate_kw': 2.8,
        'water_usage_intensity': 'heavy'
    }
    
    success = mqtt.publish_realtime_energy_sensor(test_data_3)
    
    if success:
        print("✅ Third test data published successfully")
        print(f"Data: {json.dumps(test_data_3, indent=2)}")
    else:
        print("❌ Failed to publish third test data")
    
    # Wait a moment for the message to be sent
    await asyncio.sleep(2)
    
    # Test with stable values (no usage, no heating)
    print("\nTesting with stable values (no usage, no heating)...")
    test_data_4 = {
        'realtime_energy_rate_kw': 0.001,
        'realtime_temp_rate_per_hour': 0.05,
        'energy_efficiency_index': 50.0,
        'system_performance_score': 60.0,
        'energy_trend': 'stable',
        'temperature_trend': 'stable',
        'energy_temp_ratio': 0.001,
        'energy_total_ratio': 0.0005,
        'temp_change_ratio': 0.005,
        'energy_efficiency_factor': 0.001,
        'water_usage_rate_kw': 0.0,
        'water_usage_intensity': 'none'
    }
    
    success = mqtt.publish_realtime_energy_sensor(test_data_4)
    
    if success:
        print("✅ Fourth test data published successfully")
        print(f"Data: {json.dumps(test_data_4, indent=2)}")
    else:
        print("❌ Failed to publish fourth test data")
    
    # Disconnect
    mqtt.disconnect()
    print("\n✅ Real-time energy sensor test completed")
    print("\nTo verify in Home Assistant:")
    print("1. Check the MQTT topic: solar_heating_v3/status/realtime_energy_sensor")
    print("2. Add the MQTT sensors to your configuration.yaml")
    print("3. Create dashboard cards using the provided examples")
    print("4. Monitor the sensor values in real-time")

def test_mqtt_message_format():
    """Test the MQTT message format"""
    print("\nTesting MQTT message format...")
    
    # Sample data
    sensor_data = {
        'realtime_energy_rate_kw': 1.5,
        'realtime_temp_rate_per_hour': 2.0,
        'energy_efficiency_index': 70.0,
        'system_performance_score': 80.0,
        'energy_trend': 'heating',
        'temperature_trend': 'heating',
        'energy_temp_ratio': 0.03,
        'energy_total_ratio': 0.015,
        'temp_change_ratio': 0.02,
        'energy_efficiency_factor': 0.021,
        'water_usage_rate_kw': 0.0,
        'water_usage_intensity': 'none'
    }
    
    # Create the message format
    message = {
        "sensor": "realtime_energy_sensor",
        "energy_rate_kw": sensor_data.get('realtime_energy_rate_kw', 0.0),
        "temp_rate_per_hour": sensor_data.get('realtime_temp_rate_per_hour', 0.0),
        "efficiency_index": sensor_data.get('energy_efficiency_index', 0.0),
        "performance_score": sensor_data.get('system_performance_score', 0.0),
        "energy_trend": sensor_data.get('energy_trend', 'unknown'),
        "temperature_trend": sensor_data.get('temperature_trend', 'unknown'),
        "energy_temp_ratio": sensor_data.get('energy_temp_ratio', 0.0),
        "energy_total_ratio": sensor_data.get('energy_total_ratio', 0.0),
        "temp_change_ratio": sensor_data.get('temp_change_ratio', 0.0),
        "efficiency_factor": sensor_data.get('energy_efficiency_factor', 0.0),
        "water_usage_rate_kw": sensor_data.get('water_usage_rate_kw', 0.0),
        "water_usage_intensity": sensor_data.get('water_usage_intensity', 'none'),
        "unit": "kW",
        "timestamp": time.time()
    }
    
    print("✅ MQTT message format:")
    print(json.dumps(message, indent=2))
    
    # Test JSON serialization
    try:
        json_str = json.dumps(message)
        print(f"✅ JSON serialization successful ({len(json_str)} characters)")
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")

if __name__ == "__main__":
    print("Real-time Energy Sensor Test")
    print("=" * 40)
    
    # Test MQTT message format
    test_mqtt_message_format()
    
    # Test MQTT publishing
    try:
        asyncio.run(test_realtime_energy_sensor())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")
    
    print("\nTest completed!")
