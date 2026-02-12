"""
Pydantic Models for API Request/Response Validation
Issue #43 - API Input Validation Missing
Provides type-safe, validated data models for all API endpoints
Prevents injection attacks and ensures data integrity
"""
from pydantic import BaseModel, Field, validator, ValidationError
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
# ============================================================
# ENUMS - Fixed value sets for parameters
# ============================================================
class ControlAction(str, Enum):
    """
    Valid control actions for manual controls
    
    Values:
        PUMP_START: Start the solar heating pump
        PUMP_STOP: Stop the solar heating pump
        HEATER_START: Energize cartridge heater relay (NC logic)
        HEATER_STOP: De-energize cartridge heater relay
    """
    PUMP_START = "pump_start"
    PUMP_STOP = "pump_stop"
    HEATER_START = "heater_start"
    HEATER_STOP = "heater_stop"
class SystemMode(str, Enum):
    """
    Valid system operating modes
    
    Values:
        AUTO: Automatic mode - system controls pump based on temperature
        MANUAL: Manual mode - user has full control
    """
    AUTO = "auto"
    MANUAL = "manual"
# ============================================================
# REQUEST MODELS - Validate incoming data
# ============================================================
class ControlRequest(BaseModel):
    """
    Request model for POST /api/control
    
    Validates control action requests before execution
    Prevents injection attacks through enum validation
    """
    action: ControlAction = Field(
        ...,  # Required field
        description="Control action to perform",
        example="pump_start"
    )
    
    class Config:
        # Reject any extra fields not in model
        extra = "forbid"
        # Use enum values in JSON schema
        use_enum_values = True
    
    @validator('action')
    def validate_action_string(cls, v):
        """Additional validation for action parameter"""
        # Ensure it's a string and matches enum
        if not isinstance(v, (str, ControlAction)):
            raise ValueError('action must be a string')
        return v
class ModeRequest(BaseModel):
    """
    Request model for POST /api/mode
    
    Validates mode change requests
    Ensures only valid modes can be set
    """
    mode: SystemMode = Field(
        ...,  # Required field
        description="System mode to set",
        example="auto"
    )
    
    class Config:
        extra = "forbid"
        use_enum_values = True
    
    @validator('mode')
    def validate_mode_string(cls, v):
        """Additional validation for mode parameter"""
        if not isinstance(v, (str, SystemMode)):
            raise ValueError('mode must be a string')
        return v
# ============================================================
# RESPONSE MODELS - Validate outgoing data
# ============================================================
class SystemState(BaseModel):
    """System state information"""
    primary_pump: Optional[bool] = None
    cartridge_heater: Optional[bool] = None
    mode: Optional[str] = None
    manual_control: Optional[bool] = None
    
    class Config:
        extra = "allow"  # Allow additional state fields
class APIResponse(BaseModel):
    """
    Standard successful API response
    
    Used for all successful API operations
    Provides consistent response structure
    """
    success: bool = True
    message: Optional[str] = Field(None, description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    system_state: Optional[SystemState] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None  # For error responses
    error_code: Optional[str] = None
    
    class Config:
        # Allow extra fields in response (for flexibility)
        extra = "allow"
class ValidationErrorDetail(BaseModel):
    """Detailed validation error information"""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")
class ValidationErrorResponse(BaseModel):
    """
    Validation error response (400 Bad Request)
    
    Returned when input validation fails
    Provides clear, actionable error messages without leaking system info
    """
    success: bool = False
    error: str = Field(..., description="Error message")
    error_code: str = "VALIDATION_ERROR"
    details: Optional[List[ValidationErrorDetail]] = Field(
        None,
        description="Detailed validation errors"
    )
    timestamp: Optional[str] = None
    
    @classmethod
    def from_pydantic_error(cls, error: ValidationError):
        """
        Convert pydantic ValidationError to API error response
        
        Args:
            error: Pydantic ValidationError
            
        Returns:
            ValidationErrorResponse with formatted errors
        """
        errors = error.errors()
        details = [
            ValidationErrorDetail(
                field='.'.join(str(loc) for loc in err['loc']),
                message=err['msg'],
                type=err['type']
            )
            for err in errors
        ]
        
        # Create user-friendly main error message
        if len(errors) == 1:
            main_error = f"{details[0].field}: {details[0].message}"
        else:
            main_error = f"Validation failed for {len(errors)} field(s)"
        
        return cls(
            error=main_error,
            details=details,
            timestamp=datetime.now().isoformat() + "Z"
        )
class ServerErrorResponse(BaseModel):
    """
    Server error response (500 Internal Server Error)
    
    Returned when server error occurs (NOT validation)
    Does not leak system information
    """
    success: bool = False
    error: str = Field(..., description="Error message")
    error_code: str = "SERVER_ERROR"
    timestamp: Optional[str] = None
# ============================================================
# HELPER FUNCTIONS
# ============================================================
def create_error_response(
    error_message: str,
    error_code: str = "ERROR",
    status_code: int = 500
) -> tuple:
    """
    Create standardized error response
    
    Args:
        error_message: Error message
        error_code: Error code
        status_code: HTTP status code
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    if status_code == 400:
        response = ValidationErrorResponse(
            error=error_message,
            error_code=error_code,
            timestamp=datetime.now().isoformat() + "Z"
        )
    else:
        response = ServerErrorResponse(
            error=error_message,
            error_code=error_code,
            timestamp=datetime.now().isoformat() + "Z"
        )
    
    return response.dict(), status_code
# ============================================================
# VALIDATION DECORATOR
# ============================================================
def validate_request(model_class):
    """
    Decorator to validate request body against pydantic model
    
    Usage:
        @validate_request(ControlRequest)
        def post(self, validated_data):
            # validated_data is a pydantic model instance
            action = validated_data.action
            ...
    
    Args:
        model_class: Pydantic model class to validate against
        
    Returns:
        Decorated function that validates input
    """
    from functools import wraps
    from flask import request
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get request data (JSON body or form data)
                if request.is_json:
                    data = request.get_json()
                else:
                    data = request.form.to_dict()
                
                # Handle None data
                if data is None:
                    data = {}
                
                # Validate with pydantic
                validated_data = model_class(**data)
                
                # Call original function with validated data
                return func(*args, validated_data=validated_data, **kwargs)
                
            except ValidationError as e:
                # Return formatted validation error
                error_response = ValidationErrorResponse.from_pydantic_error(e)
                return error_response.dict(), 400
            
            except Exception as e:
                # Unexpected error during validation
                return {
                    "success": False,
                    "error": "Validation failed",
                    "error_code": "VALIDATION_ERROR",
                    "timestamp": datetime.now().isoformat() + "Z"
                }, 400
        
        return wrapper
    return decorator
# Export main classes and functions
__all__ = [
    'ControlAction',
    'SystemMode',
    'ControlRequest',
    'ModeRequest',
    'SystemState',
    'APIResponse',
    'ValidationErrorDetail',
    'ValidationErrorResponse',
    'ServerErrorResponse',
    'create_error_response',
    'validate_request',
]
