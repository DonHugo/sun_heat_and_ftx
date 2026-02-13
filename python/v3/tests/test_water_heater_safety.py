"""
Test Suite for Water Heater Safety Sensors
Tests for overheating prevention and safety monitoring

TDD Red Phase: These tests will FAIL until implementation in Phase 4
Related Issue: https://github.com/DonHugo/sun_heat_and_ftx/issues/58
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestWaterHeaterSafetyMetrics:
    """Test suite for water heater safety sensor calculations"""
    
    @pytest.fixture
    def mock_solar_system(self):
        """Create a mock solar heating system with temperature data"""
        from main_system import SolarHeatingSystem
        
        # Mock the hardware and MQTT dependencies
        with patch('main_system.HardwareInterface') as mock_hw, \
             patch('main_system.MQTTHandler') as mock_mqtt, \
             patch('main_system.taskmaster_service') as mock_taskmaster:
            
            mock_hw.return_value = Mock()
            mock_mqtt.return_value = Mock()
            mock_taskmaster.analyze_temperatures = Mock(return_value="Normal operation")
            
            system = SolarHeatingSystem()
            system.temperatures = {}
            return system
    
    def test_peak_temperature_normal_operation(self, mock_solar_system):
        """Test peak temperature calculation with normal temperatures"""
        # Arrange: Set normal water heater temperatures (all below 60°C)
        mock_solar_system.temperatures = {
            'water_heater_bottom': 35.0,   # 0cm
            'water_heater_20cm': 38.0,
            'water_heater_40cm': 42.0,
            'water_heater_60cm': 45.0,
            'water_heater_80cm': 48.0,
            'water_heater_100cm': 52.0,
            'water_heater_120cm': 55.0,
            'water_heater_140cm': 58.0,    # Top (hottest)
        }
        
        # Act: Calculate safety metrics
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: Peak should be 58.0°C (highest layer)
        assert 'water_heater_peak_temp' in mock_solar_system.temperatures
        assert mock_solar_system.temperatures['water_heater_peak_temp'] == 58.0
        assert mock_solar_system.temperatures['water_heater_overheating_risk'] == False
    
    def test_peak_temperature_overheating(self, mock_solar_system):
        """Test peak temperature detection when overheating occurs"""
        # Arrange: Set overheating scenario (top layer at 72°C)
        mock_solar_system.temperatures = {
            'water_heater_bottom': 45.0,
            'water_heater_20cm': 48.0,
            'water_heater_40cm': 52.0,
            'water_heater_60cm': 56.0,
            'water_heater_80cm': 62.0,
            'water_heater_100cm': 66.0,
            'water_heater_120cm': 69.0,
            'water_heater_140cm': 72.0,    # CRITICAL TEMPERATURE
        }
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: Peak should be 72.0°C and risk should be TRUE
        assert mock_solar_system.temperatures['water_heater_peak_temp'] == 72.0
        assert mock_solar_system.temperatures['water_heater_overheating_risk'] == True
    
    def test_thermal_mass_top4_calculation(self, mock_solar_system):
        """Test thermal mass calculation for top 4 layers"""
        # Arrange: Set temperatures with clear top 4 average
        mock_solar_system.temperatures = {
            'water_heater_bottom': 30.0,
            'water_heater_20cm': 32.0,
            'water_heater_40cm': 35.0,
            'water_heater_60cm': 38.0,
            'water_heater_80cm': 60.0,     # Top 4 starts here
            'water_heater_100cm': 62.0,
            'water_heater_120cm': 64.0,
            'water_heater_140cm': 66.0,    # Top 4 ends here
        }
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: Top 4 average should be (60+62+64+66)/4 = 63.0°C
        assert 'water_heater_thermal_mass_top4' in mock_solar_system.temperatures
        assert mock_solar_system.temperatures['water_heater_thermal_mass_top4'] == 63.0
    
    def test_thermal_mass_all8_calculation(self, mock_solar_system):
        """Test thermal mass calculation for all 8 layers"""
        # Arrange: Set temperatures with known average
        mock_solar_system.temperatures = {
            'water_heater_bottom': 40.0,
            'water_heater_20cm': 42.0,
            'water_heater_40cm': 44.0,
            'water_heater_60cm': 46.0,
            'water_heater_80cm': 48.0,
            'water_heater_100cm': 50.0,
            'water_heater_120cm': 52.0,
            'water_heater_140cm': 54.0,
        }
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: Average should be (40+42+44+46+48+50+52+54)/8 = 47.0°C
        assert 'water_heater_thermal_mass_all8' in mock_solar_system.temperatures
        assert mock_solar_system.temperatures['water_heater_thermal_mass_all8'] == 47.0
    
    def test_layers_above_70c_none(self, mock_solar_system):
        """Test layer counting when no layers exceed threshold"""
        # Arrange: All temperatures below 70°C
        mock_solar_system.temperatures = {
            'water_heater_bottom': 50.0,
            'water_heater_20cm': 52.0,
            'water_heater_40cm': 54.0,
            'water_heater_60cm': 56.0,
            'water_heater_80cm': 58.0,
            'water_heater_100cm': 60.0,
            'water_heater_120cm': 62.0,
            'water_heater_140cm': 65.0,
        }
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: No layers should be above 70°C
        assert mock_solar_system.temperatures['water_heater_layers_above_70c'] == 0
        assert mock_solar_system.temperatures['water_heater_overheating_risk'] == False
    
    def test_layers_above_70c_multiple(self, mock_solar_system):
        """Test layer counting when multiple layers exceed threshold"""
        # Arrange: 3 layers at or above 70°C
        mock_solar_system.temperatures = {
            'water_heater_bottom': 50.0,
            'water_heater_20cm': 55.0,
            'water_heater_40cm': 60.0,
            'water_heater_60cm': 65.0,
            'water_heater_80cm': 69.0,
            'water_heater_100cm': 70.0,    # At threshold
            'water_heater_120cm': 71.0,    # Above threshold
            'water_heater_140cm': 72.0,    # Above threshold
        }
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: 3 layers should be at or above 70°C
        assert mock_solar_system.temperatures['water_heater_layers_above_70c'] == 3
    
    def test_overheating_risk_peak_threshold(self, mock_solar_system):
        """Test overheating risk detection via peak temperature threshold"""
        # Arrange: Peak temperature at 70°C (critical threshold)
        mock_solar_system.temperatures = {
            'water_heater_bottom': 40.0,
            'water_heater_20cm': 45.0,
            'water_heater_40cm': 50.0,
            'water_heater_60cm': 55.0,
            'water_heater_80cm': 60.0,
            'water_heater_100cm': 65.0,
            'water_heater_120cm': 68.0,
            'water_heater_140cm': 70.0,    # Exactly at critical threshold
        }
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: Risk should be detected (peak ≥ 70°C)
        assert mock_solar_system.temperatures['water_heater_overheating_risk'] == True
    
    def test_overheating_risk_combined_condition(self, mock_solar_system):
        """Test overheating risk detection via combined conditions"""
        # Arrange: Top 4 avg = 68°C AND 2+ layers ≥70°C
        mock_solar_system.temperatures = {
            'water_heater_bottom': 50.0,
            'water_heater_20cm': 52.0,
            'water_heater_40cm': 54.0,
            'water_heater_60cm': 56.0,
            'water_heater_80cm': 67.0,     # Top 4 start
            'water_heater_100cm': 68.0,
            'water_heater_120cm': 70.0,    # At threshold (layer 1)
            'water_heater_140cm': 71.0,    # Above threshold (layer 2)
        }
        # Top 4 average: (67+68+70+71)/4 = 69.0°C ≥ 68°C ✓
        # Layers ≥70°C: 2 layers ✓
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: Risk should be detected (combined condition met)
        assert mock_solar_system.temperatures['water_heater_thermal_mass_top4'] >= 68.0
        assert mock_solar_system.temperatures['water_heater_layers_above_70c'] >= 2
        assert mock_solar_system.temperatures['water_heater_overheating_risk'] == True
    
    def test_invalid_sensor_data_handling(self, mock_solar_system):
        """Test graceful handling of invalid sensor data (zeros/None)"""
        # Arrange: Some sensors returning 0 (invalid)
        mock_solar_system.temperatures = {
            'water_heater_bottom': 45.0,
            'water_heater_20cm': 0,        # Invalid sensor
            'water_heater_40cm': 50.0,
            'water_heater_60cm': 0,        # Invalid sensor
            'water_heater_80cm': 55.0,
            'water_heater_100cm': 60.0,
            'water_heater_120cm': 62.0,
            'water_heater_140cm': 65.0,
        }
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: Should calculate with valid sensors only (6 valid)
        assert 'water_heater_peak_temp' in mock_solar_system.temperatures
        assert mock_solar_system.temperatures['water_heater_peak_temp'] == 65.0
        # Should use only valid temperatures for calculations
        assert mock_solar_system.temperatures['water_heater_thermal_mass_all8'] > 0
    
    def test_insufficient_sensors_fallback(self, mock_solar_system):
        """Test fallback behavior when too few sensors are valid"""
        # Arrange: Only 3 valid sensors (< 4 minimum)
        mock_solar_system.temperatures = {
            'water_heater_bottom': 45.0,
            'water_heater_20cm': 0,        # Invalid
            'water_heater_40cm': 0,        # Invalid
            'water_heater_60cm': 0,        # Invalid
            'water_heater_80cm': 0,        # Invalid
            'water_heater_100cm': 50.0,
            'water_heater_120cm': 0,       # Invalid
            'water_heater_140cm': 55.0,
        }
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: Should set safe default values
        assert mock_solar_system.temperatures['water_heater_peak_temp'] == 0
        assert mock_solar_system.temperatures['water_heater_thermal_mass_top4'] == 0
        assert mock_solar_system.temperatures['water_heater_thermal_mass_all8'] == 0
        assert mock_solar_system.temperatures['water_heater_layers_above_70c'] == 0
        assert mock_solar_system.temperatures['water_heater_overheating_risk'] == False
    
    def test_edge_case_all_at_threshold(self, mock_solar_system):
        """Test edge case where all layers are exactly at 70°C threshold"""
        # Arrange: All layers at exactly 70°C
        mock_solar_system.temperatures = {
            'water_heater_bottom': 70.0,
            'water_heater_20cm': 70.0,
            'water_heater_40cm': 70.0,
            'water_heater_60cm': 70.0,
            'water_heater_80cm': 70.0,
            'water_heater_100cm': 70.0,
            'water_heater_120cm': 70.0,
            'water_heater_140cm': 70.0,
        }
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: All metrics should reflect critical state
        assert mock_solar_system.temperatures['water_heater_peak_temp'] == 70.0
        assert mock_solar_system.temperatures['water_heater_thermal_mass_top4'] == 70.0
        assert mock_solar_system.temperatures['water_heater_thermal_mass_all8'] == 70.0
        assert mock_solar_system.temperatures['water_heater_layers_above_70c'] == 8
        assert mock_solar_system.temperatures['water_heater_overheating_risk'] == True
    
    def test_rounding_precision(self, mock_solar_system):
        """Test that temperature values are properly rounded to 1 decimal"""
        # Arrange: Temperatures with multiple decimals
        mock_solar_system.temperatures = {
            'water_heater_bottom': 45.123,
            'water_heater_20cm': 47.456,
            'water_heater_40cm': 49.789,
            'water_heater_60cm': 52.012,
            'water_heater_80cm': 54.345,
            'water_heater_100cm': 56.678,
            'water_heater_120cm': 58.901,
            'water_heater_140cm': 60.234,
        }
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: Values should be rounded to 1 decimal place
        peak = mock_solar_system.temperatures['water_heater_peak_temp']
        assert isinstance(peak, float)
        assert round(peak, 1) == peak  # Should already be rounded
    
    @patch('main_system.logger')
    def test_exception_handling_fail_safe(self, mock_logger, mock_solar_system):
        """Test fail-safe behavior when calculation raises exception"""
        # Arrange: Intentionally cause an error by setting invalid data
        mock_solar_system.temperatures = {
            'water_heater_bottom': 'invalid',  # String instead of float
            'water_heater_20cm': 45.0,
        }
        
        # Act: Should not crash, should log error
        try:
            mock_solar_system._calculate_water_heater_safety_metrics()
        except Exception:
            pytest.fail("Method should handle exceptions gracefully")
        
        # Assert: Fail-safe should assume HIGH RISK
        assert mock_solar_system.temperatures.get('water_heater_overheating_risk') == True
        # Should log error
        assert mock_logger.error.called
    
    def test_no_risk_safe_temperatures(self, mock_solar_system):
        """Test that no risk is detected under safe operating conditions"""
        # Arrange: Safe operating temperatures (45-60°C range)
        mock_solar_system.temperatures = {
            'water_heater_bottom': 45.0,
            'water_heater_20cm': 48.0,
            'water_heater_40cm': 51.0,
            'water_heater_60cm': 54.0,
            'water_heater_80cm': 56.0,
            'water_heater_100cm': 58.0,
            'water_heater_120cm': 59.0,
            'water_heater_140cm': 60.0,
        }
        
        # Act
        mock_solar_system._calculate_water_heater_safety_metrics()
        
        # Assert: All risk indicators should be safe
        assert mock_solar_system.temperatures['water_heater_peak_temp'] < 70.0
        assert mock_solar_system.temperatures['water_heater_thermal_mass_top4'] < 68.0
        assert mock_solar_system.temperatures['water_heater_layers_above_70c'] == 0
        assert mock_solar_system.temperatures['water_heater_overheating_risk'] == False


class TestWaterHeaterSafetyIntegration:
    """Integration tests for safety sensors with MQTT and Home Assistant"""
    
    @pytest.fixture
    def mock_solar_system_with_mqtt(self):
        """Create mock system with MQTT handler"""
        from main_system import SolarHeatingSystem
        
        with patch('main_system.HardwareInterface') as mock_hw, \
             patch('main_system.MQTTHandler') as mock_mqtt, \
             patch('main_system.taskmaster_service') as mock_taskmaster:
            
            mock_hw.return_value = Mock()
            mock_mqtt_instance = Mock()
            mock_mqtt_instance.is_connected = Mock(return_value=True)
            mock_mqtt_instance.publish = Mock(return_value=True)
            mock_mqtt_instance.publish_raw = Mock()
            mock_mqtt.return_value = mock_mqtt_instance
            mock_taskmaster.analyze_temperatures = Mock(return_value="Normal")
            
            system = SolarHeatingSystem()
            system.mqtt = mock_mqtt_instance
            system.temperatures = {
                'water_heater_bottom': 45.0,
                'water_heater_20cm': 48.0,
                'water_heater_40cm': 51.0,
                'water_heater_60cm': 54.0,
                'water_heater_80cm': 57.0,
                'water_heater_100cm': 60.0,
                'water_heater_120cm': 63.0,
                'water_heater_140cm': 66.0,
            }
            return system
    
    def test_mqtt_discovery_includes_safety_sensors(self, mock_solar_system_with_mqtt):
        """Test that MQTT discovery includes all 5 safety sensors"""
        # This test will verify the discovery configuration in Phase 4
        # For now, we're just checking the structure exists
        
        # Act: Would call _publish_hass_discovery()
        # Assert: Discovery should include our new sensors
        # This will be implemented in Phase 4
        pass
    
    def test_binary_sensor_publishes_correctly(self, mock_solar_system_with_mqtt):
        """Test that overheating risk publishes as binary sensor (ON/OFF)"""
        # Arrange: Set overheating condition
        mock_solar_system_with_mqtt.temperatures.update({
            'water_heater_140cm': 71.0,  # Trigger overheating
        })
        
        # Act: Calculate and publish
        mock_solar_system_with_mqtt._calculate_water_heater_safety_metrics()
        
        # The binary sensor should be set to True
        assert mock_solar_system_with_mqtt.temperatures['water_heater_overheating_risk'] == True
        
        # Note: MQTT publishing will be tested when _publish_status() is called in Phase 4


# Test configuration
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
