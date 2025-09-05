#!/usr/bin/env python3
"""
Environment Detection for Solar Heating System v3
Automatically detects whether running in simulation or hardware environment
"""

import os
import sys
import platform
import subprocess
from typing import Dict, Any, Optional

def detect_raspberry_pi() -> bool:
    """Detect if running on Raspberry Pi"""
    try:
        # Check for Raspberry Pi specific files
        if os.path.exists('/proc/device-tree/model'):
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().lower()
                if 'raspberry pi' in model:
                    return True
        
        # Check for Raspberry Pi in uname
        uname = platform.uname()
        if 'arm' in uname.machine.lower() and 'linux' in uname.system.lower():
            # Additional check for Raspberry Pi
            try:
                result = subprocess.run(['cat', '/proc/cpuinfo'], 
                                      capture_output=True, text=True, timeout=5)
                if 'BCM' in result.stdout or 'Raspberry Pi' in result.stdout:
                    return True
            except:
                pass
        
        return False
    except:
        return False

def detect_hardware_libraries() -> bool:
    """Detect if Sequent Microsystems hardware libraries are available"""
    try:
        import megabas
        import librtd
        import lib4relind
        return True
    except ImportError:
        return False

def detect_mqtt_broker() -> bool:
    """Detect if MQTT broker is accessible"""
    try:
        from config import config
        import socket
        
        # Try to connect to MQTT broker
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((config.mqtt_broker, config.mqtt_port))
        sock.close()
        
        return result == 0
    except:
        return False

def detect_system_service() -> bool:
    """Detect if system service is running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'solar_heating_v3.service'],
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip() == 'active'
    except:
        return False

def detect_environment() -> Dict[str, Any]:
    """Detect the current environment and capabilities"""
    environment = {
        'platform': {
            'system': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'is_raspberry_pi': detect_raspberry_pi()
        },
        'hardware': {
            'libraries_available': detect_hardware_libraries(),
            'simulation_mode': not detect_hardware_libraries()
        },
        'network': {
            'mqtt_broker_accessible': detect_mqtt_broker()
        },
        'system': {
            'service_running': detect_system_service(),
            'is_root': os.geteuid() == 0
        },
        'recommendations': []
    }
    
    # Generate recommendations
    if not environment['platform']['is_raspberry_pi']:
        environment['recommendations'].append("Not running on Raspberry Pi - use simulation tests")
    
    if not environment['hardware']['libraries_available']:
        environment['recommendations'].append("Hardware libraries not available - use simulation tests")
    
    if not environment['network']['mqtt_broker_accessible']:
        environment['recommendations'].append("MQTT broker not accessible - some tests may fail")
    
    if not environment['system']['service_running']:
        environment['recommendations'].append("System service not running - service tests will fail")
    
    # Determine recommended test suite
    if (environment['platform']['is_raspberry_pi'] and 
        environment['hardware']['libraries_available']):
        environment['recommended_test_suite'] = 'hardware'
    else:
        environment['recommended_test_suite'] = 'simulation'
    
    return environment

def print_environment_info(environment: Dict[str, Any]):
    """Print environment information"""
    print("🔍 Environment Detection Results")
    print("=" * 50)
    
    print(f"Platform: {environment['platform']['system']} {environment['platform']['machine']}")
    print(f"Python: {environment['platform']['python_version']}")
    print(f"Raspberry Pi: {'Yes' if environment['platform']['is_raspberry_pi'] else 'No'}")
    
    print(f"\nHardware Libraries: {'Available' if environment['hardware']['libraries_available'] else 'Not Available'}")
    print(f"Simulation Mode: {'Yes' if environment['hardware']['simulation_mode'] else 'No'}")
    
    print(f"\nMQTT Broker: {'Accessible' if environment['network']['mqtt_broker_accessible'] else 'Not Accessible'}")
    print(f"System Service: {'Running' if environment['system']['service_running'] else 'Not Running'}")
    print(f"Root Access: {'Yes' if environment['system']['is_root'] else 'No'}")
    
    print(f"\nRecommended Test Suite: {environment['recommended_test_suite'].upper()}")
    
    if environment['recommendations']:
        print("\nRecommendations:")
        for rec in environment['recommendations']:
            print(f"  - {rec}")

def main():
    """Main function"""
    environment = detect_environment()
    print_environment_info(environment)
    
    # Return exit code based on recommendations
    if environment['recommended_test_suite'] == 'hardware':
        return 0  # Hardware environment ready
    else:
        return 1  # Simulation environment recommended

if __name__ == "__main__":
    exit(main())
