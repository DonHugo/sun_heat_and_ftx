"""
Test Configuration for Solar Heating System v3
Configuration settings for automated testing
"""

import os
from typing import Dict, Any, List

class TestConfig:
    """Test configuration settings"""
    
    # Test Categories
    TEST_CATEGORIES = {
        'hardware': {
            'name': 'Hardware Interface Tests',
            'description': 'Tests for hardware interface functionality',
            'tests': [
                'hardware_initialization',
                'temperature_reading',
                'relay_control',
                'error_handling'
            ]
        },
        'control': {
            'name': 'Control Logic Tests',
            'description': 'Tests for control logic and algorithms',
            'tests': [
                'control_initialization',
                'emergency_stop',
                'collector_cooling',
                'pump_control',
                'hysteresis_logic'
            ]
        },
        'mqtt': {
            'name': 'MQTT Integration Tests',
            'description': 'Tests for MQTT communication',
            'tests': [
                'mqtt_connection',
                'mqtt_publishing',
                'mqtt_subscription',
                'home_assistant_integration'
            ]
        },
        'state': {
            'name': 'State Management Tests',
            'description': 'Tests for state persistence and management',
            'tests': [
                'state_persistence',
                'midnight_reset',
                'energy_tracking',
                'data_validation'
            ]
        },
        'modes': {
            'name': 'Mode System Tests',
            'description': 'Tests for system mode management',
            'tests': [
                'mode_initialization',
                'mode_transitions',
                'manual_control',
                'mode_reasoning'
            ]
        },
        'taskmaster': {
            'name': 'TaskMaster AI Tests',
            'description': 'Tests for TaskMaster AI integration',
            'tests': [
                'taskmaster_initialization',
                'task_creation',
                'task_processing',
                'ai_integration'
            ]
        },
        'integration': {
            'name': 'Integration Tests',
            'description': 'Tests for full system integration',
            'tests': [
                'full_system_integration',
                'component_interaction',
                'end_to_end_workflow'
            ]
        }
    }
    
    # Test Environment Settings
    TEST_ENVIRONMENT = {
        'simulation_mode': True,
        'mqtt_timeout': 10,
        'test_duration_limit': 300,  # 5 minutes
        'retry_attempts': 3,
        'log_level': 'INFO'
    }
    
    # Test Data
    TEST_DATA = {
        'temperatures': {
            'normal_operation': {
                'solar_collector': 65.0,
                'storage_tank': 50.0,
                'storage_tank_top': 60.0,
                'storage_tank_bottom': 45.0
            },
            'heating_condition': {
                'solar_collector': 75.0,
                'storage_tank': 50.0,
                'storage_tank_top': 65.0,
                'storage_tank_bottom': 45.0
            },
            'emergency_condition': {
                'solar_collector': 160.0,
                'storage_tank': 50.0,
                'storage_tank_top': 60.0,
                'storage_tank_bottom': 45.0
            },
            'collector_cooling': {
                'solar_collector': 95.0,
                'storage_tank': 50.0,
                'storage_tank_top': 60.0,
                'storage_tank_bottom': 45.0
            }
        },
        'control_parameters': {
            'dTStart_tank_1': 8.0,
            'dTStop_tank_1': 4.0,
            'temp_kok': 150.0,
            'temp_kok_hysteres': 10.0,
            'kylning_kollektor': 90.0,
            'kylning_kollektor_hysteres': 4.0,
            'set_temp_tank_1': 75.0
        },
        'system_states': {
            'normal': {
                'primary_pump': False,
                'overheated': False,
                'collector_cooling_active': False,
                'manual_control': False
            },
            'heating': {
                'primary_pump': True,
                'overheated': False,
                'collector_cooling_active': False,
                'manual_control': False
            },
            'emergency': {
                'primary_pump': False,
                'overheated': True,
                'collector_cooling_active': False,
                'manual_control': False
            },
            'manual': {
                'primary_pump': True,
                'overheated': False,
                'collector_cooling_active': False,
                'manual_control': True
            }
        }
    }
    
    # Expected Results
    EXPECTED_RESULTS = {
        'temperature_ranges': {
            'solar_collector': (0, 200),
            'storage_tank': (0, 100),
            'ambient_air': (-20, 50)
        },
        'control_thresholds': {
            'dTStart_tank_1': (3, 40),
            'dTStop_tank_1': (2, 20),
            'temp_kok': (100, 200),
            'temp_kok_hysteres': (1, 50)
        },
        'system_limits': {
            'max_heating_cycles': 1000,
            'max_energy_per_day': 50.0,
            'max_pump_runtime': 24.0
        }
    }
    
    # Test Output Settings
    OUTPUT_SETTINGS = {
        'generate_report': True,
        'save_logs': True,
        'log_directory': '/tmp/solar_heating_tests',
        'report_format': 'json',  # json, html, text
        'include_details': True,
        'include_performance_metrics': True
    }
    
    @classmethod
    def get_test_category(cls, category: str) -> Dict[str, Any]:
        """Get test category configuration"""
        return cls.TEST_CATEGORIES.get(category, {})
    
    @classmethod
    def get_test_data(cls, data_type: str, scenario: str = None) -> Dict[str, Any]:
        """Get test data for specific scenario"""
        if data_type in cls.TEST_DATA:
            if scenario and scenario in cls.TEST_DATA[data_type]:
                return cls.TEST_DATA[data_type][scenario]
            return cls.TEST_DATA[data_type]
        return {}
    
    @classmethod
    def get_expected_result(cls, result_type: str, key: str = None) -> Any:
        """Get expected result for validation"""
        if result_type in cls.EXPECTED_RESULTS:
            if key and key in cls.EXPECTED_RESULTS[result_type]:
                return cls.EXPECTED_RESULTS[result_type][key]
            return cls.EXPECTED_RESULTS[result_type]
        return None
    
    @classmethod
    def validate_temperature(cls, sensor: str, value: float) -> bool:
        """Validate temperature reading"""
        ranges = cls.get_expected_result('temperature_ranges')
        if sensor in ranges:
            min_temp, max_temp = ranges[sensor]
            return min_temp <= value <= max_temp
        return True
    
    @classmethod
    def validate_control_parameter(cls, parameter: str, value: float) -> bool:
        """Validate control parameter"""
        thresholds = cls.get_expected_result('control_thresholds')
        if parameter in thresholds:
            min_val, max_val = thresholds[parameter]
            return min_val <= value <= max_val
        return True
