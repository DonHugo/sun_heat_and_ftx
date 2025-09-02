#!/usr/bin/env python3
"""
Test script for Solar Heating System v3 Watchdog
Tests individual components of the watchdog system
"""

import asyncio
import time
from watchdog import NetworkMonitor, MQTTMonitor, SystemMonitor, WatchdogConfig

async def test_network_monitor():
    """Test network monitoring functionality"""
    print("=== Testing Network Monitor ===")
    
    config = WatchdogConfig()
    monitor = NetworkMonitor(config)
    
    print("Testing network connectivity...")
    result = await monitor.check_network()
    
    if result:
        print("✓ Network monitor: Connectivity OK")
    else:
        print("✗ Network monitor: Connectivity issues detected")
    
    return result

async def test_mqtt_monitor():
    """Test MQTT monitoring functionality"""
    print("\n=== Testing MQTT Monitor ===")
    
    config = WatchdogConfig()
    monitor = MQTTMonitor(config)
    
    print("Testing MQTT connectivity and heartbeat...")
    result = await monitor.check_mqtt()
    
    if result:
        print("✓ MQTT monitor: Communication OK")
    else:
        print("✗ MQTT monitor: Communication issues detected")
    
    return result

async def test_system_monitor():
    """Test system monitoring functionality"""
    print("\n=== Testing System Monitor ===")
    
    config = WatchdogConfig()
    monitor = SystemMonitor(config)
    
    print("Testing system service status...")
    result = await monitor.check_system()
    
    if result:
        print("✓ System monitor: Service OK")
    else:
        print("✗ System monitor: Service issues detected")
    
    return result

async def test_watchdog_integration():
    """Test full watchdog integration"""
    print("\n=== Testing Watchdog Integration ===")
    
    config = WatchdogConfig()
    
    # Test all monitors
    network_ok = await test_network_monitor()
    mqtt_ok = await test_mqtt_monitor()
    system_ok = await test_system_monitor()
    
    # Overall status
    overall_healthy = network_ok and mqtt_ok and system_ok
    
    print(f"\n=== Overall Status ===")
    print(f"Network: {'✓' if network_ok else '✗'}")
    print(f"MQTT:    {'✓' if mqtt_ok else '✗'}")
    print(f"System:  {'✓' if system_ok else '✗'}")
    print(f"Overall: {'✓ HEALTHY' if overall_healthy else '✗ ISSUES DETECTED'}")
    
    return overall_healthy

async def main():
    """Main test function"""
    print("Solar Heating System v3 Watchdog Test")
    print("=" * 50)
    
    try:
        # Run integration test
        success = await test_watchdog_integration()
        
        if success:
            print("\n🎉 All watchdog tests passed!")
        else:
            print("\n⚠️  Some watchdog tests failed. Check the output above.")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main())
