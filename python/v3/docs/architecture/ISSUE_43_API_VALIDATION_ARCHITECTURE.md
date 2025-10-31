# Architecture Design: API Input Validation (Issue #43)

**Issue:** #43 - [SECURITY] API Input Validation Missing  
**Agent:** @architect  
**Date:** 2025-10-31  
**Based on:** ISSUE_43_API_VALIDATION_REQUIREMENTS.md

---

## Overview

Design pydantic-based input validation system for REST API endpoints to prevent security vulnerabilities and ensure data integrity.

### Architecture Goals
- ✅ **Security First** - Validate all input before processing
- ✅ **Clean Separation** - Validation layer separate from business logic
- ✅ **Type Safety** - Leverage pydantic's type checking
- ✅ **Easy Maintenance** - Clear model definitions in separate file
- ✅ **Performance** - Minimal overhead (< 5ms per request)
- ✅ **Backward Compatible** - Existing frontend continues to work

---

## Component Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (JavaScript)                     │
│                                                               │
│  POST /api/control    POST /api/mode    GET /api/status     │
└───────────────────┬──────────────────────┬──────────────────┘
                    │                      │
                    ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask API Layer                           │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  NEW: Pydantic Validation Decorator                  │   │
│  │  @validate_request(ControlRequest)                   │   │
│  │  @validate_response(APIResponse)                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                    │
│                          ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Pydantic Models (api_models.py)                     │   │
│  │  - ControlRequest                                     │   │
│  │  - ModeRequest                                        │   │
│  │  - APIResponse                                        │   │
│  │  - ValidationErrorResponse                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                    │
│                          ▼ (validated data)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Business Logic (api_server.py)                      │   │
│  │  - control_system()                                   │   │
│  │  - set_system_mode()                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Main System / Hardware                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Pydantic Models (`api_models.py`)

**Location:** `python/v3/api_models.py` (NEW FILE)

**Purpose:** Define all request/response schemas using pydantic

**Design Principles:**
- Use Enums for fixed value sets (action, mode)
- Strict validation with `extra="forbid"` (no unexpected fields)
- Clear error messages
- Type-safe models

**Structure:**

```python
"""
Pydantic models for API request/response validation
Provides type-safe, validated data models for all API endpoints
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
    Valid control actions for pump control
    
    Values:
        PUMP_START: Start the solar heating pump
        PUMP_STOP: Stop the solar heating pump
        EMERGENCY_STOP: Emergency stop all systems
    """
    PUMP_START = "pump_start"
    PUMP_STOP = "pump_stop"
    EMERGENCY_STOP = "emergency_stop"


class SystemMode(str, Enum):
    """
    Valid system operating modes
    
    Values:
        AUTO: Automatic mode - system controls pump based on temperature
        MANUAL: Manual mode - user has full control
        ECO: Eco mode - optimized for energy efficiency
    """
    AUTO = "auto"
    MANUAL = "manual"
    ECO = "eco"


# ============================================================
# REQUEST MODELS - Validate incoming data
# ============================================================

class ControlRequest(BaseModel):
    """
    Request model for POST /api/control
    
    Validates control action requests before execution
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


class APIResponse(BaseModel):
    """
    Standard successful API response
    
    Used for all successful API operations
    """
    success: bool = True
    message: Optional[str] = Field(None, description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    system_state: Optional[SystemState] = None
    timestamp: Optional[str] = None
    
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
```

---

### 2. Validation Decorator (Integration Layer)

**Purpose:** Clean decorator to validate requests before business logic

**Design:**

```python
# In api_server.py - add this decorator function

from functools import wraps
from flask import request, jsonify
from pydantic import ValidationError
from api_models import ValidationErrorResponse

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
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get request data (JSON body or form data)
                if request.is_json:
                    data = request.get_json()
                else:
                    data = request.form.to_dict()
                
                # Validate with pydantic
                validated_data = model_class(**data)
                
                # Call original function with validated data
                return func(*args, validated_data=validated_data, **kwargs)
                
            except ValidationError as e:
                # Return formatted validation error
                error_response = ValidationErrorResponse.from_pydantic_error(e)
                return jsonify(error_response.dict()), 400
            
            except Exception as e:
                # Unexpected error during validation
                return jsonify({
                    "success": False,
                    "error": "Validation failed",
                    "error_code": "VALIDATION_ERROR",
                    "timestamp": datetime.now().isoformat() + "Z"
                }), 400
        
        return wrapper
    return decorator
```

---

### 3. Modified API Endpoints

**Integration Approach:** Minimal changes to existing code

**Before (Current - Lines 389-400):**
```python
class ControlAPI(Resource):
    def post(self):
        """POST /api/control"""
        api_server = getattr(ControlAPI, '_api_server', None)
        if not api_server:
            return {"error": "API server not initialized"}, 500
        
        parser = reqparse.RequestParser()
        parser.add_argument('action', required=True, help='Action is required')
        args = parser.parse_args()
        
        return api_server.control_system(args['action'])
```

**After (With Pydantic):**
```python
class ControlAPI(Resource):
    @validate_request(ControlRequest)
    def post(self, validated_data):
        """POST /api/control"""
        api_server = getattr(ControlAPI, '_api_server', None)
        if not api_server:
            return {"error": "API server not initialized"}, 500
        
        # validated_data is already validated ControlRequest model
        return api_server.control_system(validated_data.action.value)
```

**Changes:**
- ❌ Remove: `reqparse.RequestParser()` (deprecated)
- ✅ Add: `@validate_request(ControlRequest)` decorator
- ✅ Add: `validated_data` parameter
- ✅ Use: `validated_data.action.value` (enum value)

---

### 4. Updated Business Logic

**Minimal Changes:** Business logic stays mostly the same

**Before:**
```python
def control_system(self, action: str) -> Dict[str, Any]:
    """Control system actions"""
    with self.lock:
        try:
            if action == "pump_start":
                # ... business logic ...
            elif action == "pump_stop":
                # ... business logic ...
            elif action == "emergency_stop":
                # ... business logic ...
            else:
                return {
                    "success": False,
                    "error": "Invalid action",
                    "error_code": "INVALID_ACTION"
                }
```

**After:**
```python
def control_system(self, action: str) -> Dict[str, Any]:
    """Control system actions - action is already validated"""
    with self.lock:
        try:
            # No need for validation - already done by pydantic!
            if action == "pump_start":
                # ... business logic ...
            elif action == "pump_stop":
                # ... business logic ...
            elif action == "emergency_stop":
                # ... business logic ...
            # No else clause needed - pydantic ensures valid action
```

**Changes:**
- ❌ Remove: Validation logic (line 310-315) - now redundant
- ✅ Add: Comment explaining validation already done
- ✅ Simplify: No need for else clause with error

---

## Data Flow

### Validation Flow Diagram

```
1. Frontend Request
   POST /api/control
   Body: {"action": "pump_start"}
        │
        ▼
2. Flask Route
   ControlAPI.post() method
        │
        ▼
3. @validate_request Decorator
   ┌─────────────────────────────┐
   │ Parse JSON body             │
   │ Create ControlRequest model │
   │ Pydantic validates:         │
   │  - action is present        │
   │  - action is string         │
   │  - action in valid enum     │
   │  - no extra fields          │
   └─────────────────────────────┘
        │
        ├─── Invalid? ───┐
        │                 │
        │                 ▼
        │         Return 400 Bad Request
        │         ValidationErrorResponse
        │         {
        │           "success": false,
        │           "error": "action must be one of...",
        │           "error_code": "VALIDATION_ERROR"
        │         }
        │
        ├─── Valid? ──────┐
        │                 │
        ▼                 ▼
4. Business Logic       Frontend
   control_system()     Receives error
   (validated data)     Shows error to user
        │
        ▼
5. Hardware Control
   Set relay state
        │
        ▼
6. Response
   Return 200 OK
   APIResponse
```

---

## Technology Choices

### Pydantic v2.0+

**Why Pydantic:**
- ✅ **Industry Standard** - Most popular Python validation library
- ✅ **Type Safety** - Leverages Python type hints
- ✅ **Performance** - Fast validation (Rust-based core in v2)
- ✅ **Error Messages** - Clear, detailed validation errors
- ✅ **Documentation** - Auto-generates API schemas
- ✅ **Integration** - Works seamlessly with Flask

**Alternatives Considered:**
- ❌ **marshmallow** - Older, less performant, more verbose
- ❌ **cerberus** - Less type-safe, less popular
- ❌ **Flask-RESTful reqparse** - DEPRECATED, minimal validation

**Trade-offs:**
- **Pro:** Best-in-class validation, excellent error messages
- **Con:** Adds dependency (~2MB), but worth it for security
- **Pro:** Widely used, well-documented, active development
- **Con:** Breaking changes between v1 and v2, but we start with v2

---

## Security Considerations

### Injection Attack Prevention

**SQL Injection:**
- ✅ Enum validation prevents arbitrary strings
- ✅ Only predefined values ("pump_start", "pump_stop", "emergency_stop") allowed
- ✅ Cannot inject SQL through validated parameters

**XSS (Cross-Site Scripting):**
- ✅ Enum validation prevents script tags
- ✅ Input sanitization through type checking
- ✅ Response encoding handled by Flask/jsonify

**Command Injection:**
- ✅ No shell commands use user input
- ✅ Validated enums prevent command injection
- ✅ Subprocess calls use hardcoded values only

**Path Traversal:**
- ✅ No file paths from user input
- ✅ Not applicable to current endpoints

### DoS Prevention

**Request Size:**
- ✅ Flask has built-in max content length
- ✅ Pydantic validates quickly (< 5ms overhead)
- ✅ Enum validation prevents extremely long strings

**Validation Complexity:**
- ✅ Simple validation (enum matching)
- ✅ No regex or complex operations
- ✅ Fast failure on invalid input

---

## Performance Impact

### Validation Overhead

**Expected Performance:**
- Pydantic validation: **~0.5-2ms** per request
- JSON parsing: **~0.1-0.5ms**
- Total overhead: **~1-5ms** per request

**Optimization:**
- Model instances are reused
- Enum validation is O(1) lookup
- No complex regex or database queries

**Benchmark Plan:**
```python
# Test validation performance
import time

# Without validation: ~10ms per request
# With pydantic: ~12ms per request
# Overhead: ~2ms (20% increase, acceptable for security)
```

---

## Testing Strategy

### Unit Tests (Model Validation)

```python
# Test pydantic models directly
def test_control_request_valid():
    request = ControlRequest(action="pump_start")
    assert request.action == ControlAction.PUMP_START

def test_control_request_invalid():
    with pytest.raises(ValidationError):
        ControlRequest(action="invalid_action")

def test_control_request_extra_fields():
    with pytest.raises(ValidationError):
        ControlRequest(action="pump_start", extra="field")
```

### Integration Tests (API Endpoints)

```python
# Test API with validation
def test_api_control_valid(client):
    response = client.post('/api/control', json={"action": "pump_start"})
    assert response.status_code == 200

def test_api_control_invalid(client):
    response = client.post('/api/control', json={"action": "invalid"})
    assert response.status_code == 400
    assert "validation" in response.json['error'].lower()
```

### Security Tests (Injection Attacks)

```python
# Test injection prevention
def test_sql_injection_prevented(client):
    response = client.post('/api/control', 
        json={"action": "pump_start'; DROP TABLE sensors;--"})
    assert response.status_code == 400

def test_xss_prevented(client):
    response = client.post('/api/mode',
        json={"mode": "<script>alert('xss')</script>"})
    assert response.status_code == 400
```

---

## Backward Compatibility

### Frontend Compatibility

**No Changes Required to Frontend:**
- ✅ Same URL endpoints (`/api/control`, `/api/mode`)
- ✅ Same request format (JSON body)
- ✅ Same response format (success, message, data)
- ✅ Same HTTP status codes (200, 400, 500)

**Error Response Changes:**
- **Before:** Generic error messages
- **After:** More detailed validation errors (BETTER for frontend)

**Example:**

Before:
```json
{
  "success": false,
  "error": "Invalid action",
  "error_code": "INVALID_ACTION"
}
```

After (more helpful):
```json
{
  "success": false,
  "error": "action: value is not a valid enumeration member",
  "error_code": "VALIDATION_ERROR",
  "details": [
    {
      "field": "action",
      "message": "value is not a valid enumeration member; permitted: 'pump_start', 'pump_stop', 'emergency_stop'",
      "type": "enum"
    }
  ]
}
```

---

## Migration Strategy

### Phase 1: Add Pydantic (No Breaking Changes)
1. Add `api_models.py` with all pydantic models
2. Add `validate_request` decorator
3. Keep existing code working

### Phase 2: Migrate Endpoints (One at a Time)
1. **First:** `/api/control` - Add decorator, test thoroughly
2. **Second:** `/api/mode` - Add decorator, test thoroughly
3. **Verify:** Frontend still works with both endpoints

### Phase 3: Remove Old Code
1. Remove reqparse imports and usage
2. Remove validation logic from business methods
3. Clean up redundant error handling

### Phase 4: Verify & Document
1. Run all tests
2. Test on hardware
3. Update API documentation
4. Update frontend if desired (to use detailed errors)

---

## File Structure

```
python/v3/
├── api_server.py                    # MODIFIED - Add decorator, update endpoints
├── api_models.py                    # NEW - Pydantic models
├── requirements.txt                 # MODIFIED - Add pydantic
├── docs/
│   ├── requirements/
│   │   └── ISSUE_43_API_VALIDATION_REQUIREMENTS.md  # EXISTS
│   └── architecture/
│       └── ISSUE_43_API_VALIDATION_ARCHITECTURE.md  # THIS FILE
└── tests/
    └── api/
        ├── test_api_validation.py   # NEW - Validation tests
        ├── test_api_endpoints.py    # MODIFIED - Update with new validation
        └── test_api_security.py     # NEW - Injection attack tests
```

---

## Success Criteria

**Architecture Complete When:**
- ✅ Pydantic model structure designed
- ✅ Validation decorator designed
- ✅ Integration approach defined
- ✅ Backward compatibility ensured
- ✅ Security considerations addressed
- ✅ Performance impact assessed
- ✅ Testing strategy defined
- ✅ Migration strategy planned

---

## Next Steps

**Ready for @tester:**
- Write comprehensive validation tests
- Write injection attack tests
- Write performance benchmarks

**After @tester:**
- @developer implements pydantic models
- @developer integrates validation
- @validator verifies on hardware

---

**Status:** ✅ Architecture Design Complete  
**Ready for:** @tester (Test Specification Phase)  
**Estimated Implementation:** 4-6 hours (as estimated in requirements)

**Key Design Decisions:**
1. **Pydantic v2.0** for validation
2. **Decorator pattern** for clean integration
3. **Enum types** for fixed value sets
4. **Minimal business logic changes**
5. **100% backward compatible**

