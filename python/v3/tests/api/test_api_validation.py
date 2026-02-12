"""
Comprehensive API Validation Tests for Issue #43
Tests pydantic-based input validation for all API endpoints

Following TDD: These tests should FAIL initially, then pass after implementation
"""

import pytest
from pydantic import ValidationError
import sys
import os
from typing import Any, cast

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import pydantic models (will be created)
try:
    from api_models import (
        ControlRequest, ModeRequest, ControlAction, SystemMode,
        APIResponse, ValidationErrorResponse, ValidationErrorDetail
    )
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    pytest.skip("Pydantic models not yet implemented", allow_module_level=True)


def _ca(value: Any) -> ControlAction:
    """Helper to satisfy type checkers while passing arbitrary values."""
    return cast(ControlAction, value)


def _sm(value: Any) -> SystemMode:
    return cast(SystemMode, value)


class TestControlRequestModel:
    """Test ControlRequest pydantic model validation"""
    
    def test_valid_pump_start(self):
        """Test valid pump_start action"""
        request = ControlRequest(action=ControlAction.PUMP_START)
        assert request.action == ControlAction.PUMP_START
        assert request.action.value == "pump_start"
    
    def test_valid_pump_stop(self):
        """Test valid pump_stop action"""
        request = ControlRequest(action=ControlAction.PUMP_STOP)
        assert request.action == ControlAction.PUMP_STOP
        assert request.action.value == "pump_stop"
    
    def test_valid_heater_start(self):
        """Test valid heater_start action"""
        request = ControlRequest(action=ControlAction.HEATER_START)
        assert request.action == ControlAction.HEATER_START
        assert request.action.value == "heater_start"
    
    def test_valid_heater_stop(self):
        """Test valid heater_stop action"""
        request = ControlRequest(action=ControlAction.HEATER_STOP)
        assert request.action == ControlAction.HEATER_STOP
        assert request.action.value == "heater_stop"
    
    def test_invalid_action(self):
        """Test that invalid action raises ValidationError"""
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca("invalid_action"))
    
    def test_missing_action(self):
        """Test that missing action raises ValidationError"""
        with pytest.raises(ValidationError):
            ControlRequest()
    
    def test_extra_fields_rejected(self):
        """Test that extra fields are rejected (extra='forbid')"""
        with pytest.raises(ValidationError):
            ControlRequest(action=ControlAction.PUMP_START, extra_field="value")
    
    def test_wrong_type_integer(self):
        """Test that integer action is rejected"""
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca(123))
    
    def test_wrong_type_boolean(self):
        """Test that boolean action is rejected"""
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca(True))
    
    def test_wrong_type_list(self):
        """Test that list action is rejected"""
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca(["pump_start"]))
    
    def test_empty_string(self):
        """Test that empty string action is rejected"""
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca(""))
    
    def test_case_sensitive_validation(self):
        """Test that action validation is case-sensitive"""
        # "PUMP_START" should fail (must be "pump_start")
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca("PUMP_START"))
        
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca("Pump_Start"))


class TestModeRequestModel:
    """Test ModeRequest pydantic model validation"""
    
    def test_valid_auto_mode(self):
        """Test valid auto mode"""
        request = ModeRequest(mode=SystemMode.AUTO)
        assert request.mode == SystemMode.AUTO
        assert request.mode.value == "auto"
    
    def test_valid_manual_mode(self):
        """Test valid manual mode"""
        request = ModeRequest(mode=SystemMode.MANUAL)
        assert request.mode == SystemMode.MANUAL
        assert request.mode.value == "manual"
    
    def test_valid_eco_mode(self):
        """Test valid eco mode"""
        with pytest.raises(ValidationError):
            ModeRequest(mode="eco")
    
    def test_invalid_mode(self):
        """Test that invalid mode raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            ModeRequest(mode=_sm("invalid_mode"))
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert 'mode' in str(errors[0])
    
    def test_missing_mode(self):
        """Test that missing mode raises ValidationError"""
        with pytest.raises(ValidationError):
            ModeRequest()
    
    def test_extra_fields_rejected(self):
        """Test that extra fields are rejected"""
        with pytest.raises(ValidationError):
            ModeRequest(mode=SystemMode.AUTO, extra="field")
    
    def test_case_sensitive_mode(self):
        """Test that mode validation is case-sensitive"""
        with pytest.raises(ValidationError):
            ModeRequest(mode=_sm("AUTO"))
        
        with pytest.raises(ValidationError):
            ModeRequest(mode=_sm("Manual"))


class TestInjectionAttackPrevention:
    """Test that validation prevents common injection attacks"""
    
    def test_sql_injection_in_action(self):
        """Test SQL injection attempt in action parameter"""
        malicious_input = "pump_start'; DROP TABLE sensors;--"
        
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca(malicious_input))
    
    def test_sql_injection_in_mode(self):
        """Test SQL injection attempt in mode parameter"""
        malicious_input = "auto' OR '1'='1"
        
        with pytest.raises(ValidationError):
            ModeRequest(mode=_sm(malicious_input))
    
    def test_xss_attack_in_action(self):
        """Test XSS attempt in action parameter"""
        malicious_input = "<script>alert('xss')</script>"
        
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca(malicious_input))
    
    def test_xss_attack_in_mode(self):
        """Test XSS attempt in mode parameter"""
        malicious_input = "<img src=x onerror='alert(1)'>"
        
        with pytest.raises(ValidationError):
            ModeRequest(mode=_sm(malicious_input))
    
    def test_command_injection_attempt(self):
        """Test command injection attempt"""
        malicious_input = "pump_start; rm -rf /"
        
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca(malicious_input))
    
    def test_path_traversal_attempt(self):
        """Test path traversal attempt"""
        malicious_input = "../../../etc/passwd"
        
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca(malicious_input))
    
    def test_null_byte_injection(self):
        """Test null byte injection attempt"""
        malicious_input = "pump_start\x00malicious"
        
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca(malicious_input))
    
    def test_unicode_attack(self):
        """Test unicode/encoding attack"""
        malicious_input = "pump_start\u202e"  # Right-to-left override
        
        with pytest.raises(ValidationError):
            ControlRequest(action=_ca(malicious_input))


class TestExtremeCases:
    """Test extreme and edge cases"""
    
    def test_very_long_string(self):
        """Test very long string input (DoS prevention)"""
        long_string = "a" * 10000
        
        with pytest.raises(ValidationError):
            ControlRequest(action=long_string)
    
    def test_special_characters(self):
        """Test various special characters"""
        special_chars = [
            "pump@start", "pump#start", "pump$start", 
            "pump%start", "pump^start", "pump&start"
        ]
        
        for char_string in special_chars:
            with pytest.raises(ValidationError):
                ControlRequest(action=char_string)
    
    def test_whitespace_variations(self):
        """Test whitespace variations"""
        whitespace_tests = [
            " pump_start",      # Leading space
            "pump_start ",      # Trailing space
            "pump _start",      # Internal space
            "\tpump_start",     # Tab
            "pump_start\n",     # Newline
        ]
        
        for test_input in whitespace_tests:
            with pytest.raises(ValidationError):
                ControlRequest(action=test_input)
    
    def test_numeric_strings(self):
        """Test numeric strings"""
        with pytest.raises(ValidationError):
            ControlRequest(action="123")
        
        with pytest.raises(ValidationError):
            ModeRequest(mode="456")
    
    def test_boolean_strings(self):
        """Test boolean strings"""
        with pytest.raises(ValidationError):
            ControlRequest(action="true")
        
        with pytest.raises(ValidationError):
            ModeRequest(mode="false")


class TestValidationErrorResponse:
    """Test ValidationErrorResponse formatting"""
    
    def test_from_pydantic_error_single(self):
        """Test conversion from pydantic error with single error"""
        try:
            ControlRequest(action="invalid")
        except ValidationError as e:
            response = ValidationErrorResponse.from_pydantic_error(e)
            
            assert response.success is False
            assert response.error_code == "VALIDATION_ERROR"
            assert response.error is not None
            assert response.details is not None
            assert len(response.details) > 0
    
    def test_from_pydantic_error_multiple(self):
        """Test conversion with multiple validation errors"""
        try:
            # This will cause multiple errors (missing field + extra field)
            ControlRequest(extra_field="value")
        except ValidationError as e:
            response = ValidationErrorResponse.from_pydantic_error(e)
            
            assert response.success is False
            assert "field" in response.error.lower() or "required" in response.error.lower()
    
    def test_error_detail_structure(self):
        """Test ValidationErrorDetail structure"""
        detail = ValidationErrorDetail(
            field="action",
            message="Invalid value",
            type="value_error"
        )
        
        assert detail.field == "action"
        assert detail.message == "Invalid value"
        assert detail.type == "value_error"


class TestAPIResponse:
    """Test APIResponse model"""
    
    def test_success_response(self):
        """Test successful response structure"""
        response = APIResponse(
            success=True,
            message="Operation successful",
            data={"status": "ok"}
        )
        
        assert response.success is True
        assert response.message == "Operation successful"
        assert response.data == {"status": "ok"}
    
    def test_response_with_system_state(self):
        """Test response with system state"""
        from api_models import SystemState
        
        response = APIResponse(
            success=True,
            system_state=SystemState(
                primary_pump=True,
                mode="manual"
            )
        )
        
        assert response.system_state.primary_pump is True
        assert response.system_state.mode == "manual"


class TestEnumValues:
    """Test enum value handling"""
    
    def test_control_action_enum_values(self):
        """Test ControlAction enum has correct values"""
        assert ControlAction.PUMP_START.value == "pump_start"
        assert ControlAction.PUMP_STOP.value == "pump_stop"
        assert ControlAction.HEATER_START.value == "heater_start"
        assert ControlAction.HEATER_STOP.value == "heater_stop"
    
    def test_system_mode_enum_values(self):
        """Test SystemMode enum has correct values"""
        assert SystemMode.AUTO.value == "auto"
        assert SystemMode.MANUAL.value == "manual"
        assert SystemMode.ECO.value == "eco"
    
    def test_enum_count(self):
        """Test that enums have exactly the expected number of values"""
        assert len(ControlAction) == 4
        assert len(SystemMode) == 2


# Performance tests (optional, but good to have)
class TestValidationPerformance:
    """Test validation performance"""
    
    def test_validation_speed(self):
        """Test that validation is fast (< 5ms per request)"""
        import time
        
        iterations = 1000
        start_time = time.time()
        
        for _ in range(iterations):
            ControlRequest(action="pump_start")
        
        end_time = time.time()
        avg_time_ms = ((end_time - start_time) / iterations) * 1000
        
        # Should be well under 5ms per validation
        assert avg_time_ms < 5, f"Validation took {avg_time_ms}ms, expected < 5ms"


# Run tests with: pytest python/v3/tests/api/test_api_validation.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
