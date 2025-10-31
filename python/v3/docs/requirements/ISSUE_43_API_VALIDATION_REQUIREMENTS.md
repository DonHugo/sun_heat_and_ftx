# Requirement: API Input Validation (Issue #43)

**Issue:** #43 - [SECURITY] API Input Validation Missing  
**Priority:** CRITICAL  
**Type:** Security Vulnerability  
**Agent:** @requirements  
**Date:** 2025-10-31

---

## Problem Statement

The REST API endpoints in `api_server.py` lack proper input validation, creating security vulnerabilities:

- **No schema validation**: Input parameters aren't validated against schemas
- **Type checking missing**: String parameters aren't type-checked
- **No sanitization**: Malicious input could be passed through
- **Error messages unclear**: Invalid input returns generic errors
- **Injection risk**: Unvalidated input could lead to injection attacks
- **System crash risk**: Bad input could crash the API or main system

**Current State:**
- `POST /api/control` - Only checks if action is in a hardcoded list (lines 310-314)
- `POST /api/mode` - Only checks if mode is in a hardcoded list (lines 328-333)
- Uses Flask-RESTful's `reqparse` which is deprecated and lacks validation
- No pydantic models for request/response validation

---

## Desired Outcome

Implement comprehensive input validation using pydantic that:

1. **Validates all input** before processing
2. **Returns clear errors** (400 Bad Request) for invalid input
3. **Prevents injection attacks** through proper sanitization
4. **Type-checks all parameters** (string, int, float, bool)
5. **Enforces constraints** (allowed values, ranges, patterns)
6. **Provides API documentation** through pydantic schemas
7. **Makes API robust** against malicious or accidental bad input

---

## API Endpoints Requiring Validation

### 1. POST /api/control
**Current Implementation:** Lines 389-400  
**Input Parameters:**
- `action` (string, required)

**Valid Values:**
- `pump_start` - Start the solar pump
- `pump_stop` - Stop the solar pump  
- `emergency_stop` - Emergency stop all systems

**Validation Rules:**
- ✅ Must be one of the three valid actions
- ✅ Must be a string
- ✅ Case-sensitive validation
- ✅ No extra parameters allowed
- ❌ Currently: Only validated in business logic (line 310)

---

### 2. POST /api/mode
**Current Implementation:** Lines 403-414  
**Input Parameters:**
- `mode` (string, required)

**Valid Values:**
- `auto` - Automatic mode (system controls pump based on temperature)
- `manual` - Manual mode (user controls pump)
- `eco` - Eco mode (optimized for energy saving)

**Validation Rules:**
- ✅ Must be one of the three valid modes
- ✅ Must be a string
- ✅ Case-sensitive validation
- ✅ No extra parameters allowed
- ❌ Currently: Only validated in business logic (line 328)

---

### 3. GET /api/status
**Current Implementation:** Lines 377-386  
**Input Parameters:** None (GET endpoint)  
**Validation:** ✅ No validation needed (read-only)

---

### 4. GET /api/temperatures
**Current Implementation:** Lines 417-442  
**Input Parameters:** None (GET endpoint)  
**Validation:** ✅ No validation needed (read-only)

---

### 5. GET /api/mqtt
**Current Implementation:** Lines 445-456  
**Input Parameters:** None (GET endpoint)  
**Validation:** ✅ No validation needed (read-only)

---

## Acceptance Criteria

### Core Requirements

- [ ] **Pydantic models created** for all POST endpoints
- [ ] **Request validation** happens before business logic
- [ ] **Clear error messages** returned for invalid input (400 Bad Request)
- [ ] **Type checking** enforced (string types validated)
- [ ] **Enum validation** for action and mode parameters
- [ ] **No deprecated reqparse** - Replace with pydantic
- [ ] **API documentation** generated from pydantic models

### Security Requirements

- [ ] **Injection prevention** - Input sanitized before use
- [ ] **No unvalidated input** reaches business logic
- [ ] **Strict validation** - Only expected parameters accepted
- [ ] **Error handling** doesn't leak system information
- [ ] **Security tests** pass with malicious input

### Usability Requirements

- [ ] **Clear error messages** - User knows what's wrong
- [ ] **Consistent error format** - All validation errors use same structure
- [ ] **HTTP status codes** - 400 for validation errors, 500 for server errors
- [ ] **Validation errors** include field name and reason

---

## Test Scenarios

### Test 1: Valid Control Actions
**Given:** API receives valid control actions  
**When:** POST /api/control with action="pump_start", "pump_stop", "emergency_stop"  
**Then:** Request passes validation and reaches business logic

### Test 2: Invalid Control Action
**Given:** API receives invalid action  
**When:** POST /api/control with action="invalid_action"  
**Then:** 
- Returns 400 Bad Request
- Error message: "action must be one of: pump_start, pump_stop, emergency_stop"
- Business logic is NOT executed

### Test 3: Missing Required Field
**Given:** API receives request without action  
**When:** POST /api/control with no parameters  
**Then:**
- Returns 400 Bad Request
- Error message: "action is required"

### Test 4: Wrong Type
**Given:** API receives wrong type  
**When:** POST /api/control with action=123 (integer instead of string)  
**Then:**
- Returns 400 Bad Request
- Error message: "action must be a string"

### Test 5: Extra Parameters
**Given:** API receives extra unexpected parameters  
**When:** POST /api/control with action="pump_start" AND extra_param="value"  
**Then:**
- Returns 400 Bad Request  
- Error message: "unexpected field: extra_param"

### Test 6: Valid Mode Changes
**Given:** API receives valid mode changes  
**When:** POST /api/mode with mode="auto", "manual", "eco"  
**Then:** Request passes validation

### Test 7: Invalid Mode
**Given:** API receives invalid mode  
**When:** POST /api/mode with mode="invalid"  
**Then:**
- Returns 400 Bad Request
- Error message: "mode must be one of: auto, manual, eco"

### Test 8: SQL Injection Attempt
**Given:** Malicious input attempting SQL injection  
**When:** POST /api/control with action="pump_start'; DROP TABLE sensors;--"  
**Then:**
- Returns 400 Bad Request
- Does NOT execute any database commands
- Error message: "action must be one of: pump_start, pump_stop, emergency_stop"

### Test 9: XSS Attempt
**Given:** Malicious input attempting XSS  
**When:** POST /api/mode with mode="<script>alert('xss')</script>"  
**Then:**
- Returns 400 Bad Request
- Script is NOT executed or stored
- Error message: "mode must be one of: auto, manual, eco"

### Test 10: Very Long Input
**Given:** Extremely long string input  
**When:** POST /api/control with action="a" * 10000 (10,000 characters)  
**Then:**
- Returns 400 Bad Request
- Error message: "action must be one of the allowed values"
- Does NOT cause memory issues or crashes

---

## Constraints

### Technical Constraints
- Must use pydantic for validation (not deprecated reqparse)
- Must maintain backward compatibility with existing frontend
- Must not break existing API contract
- Performance: Validation overhead should be < 5ms per request

### Security Constraints
- All input must be validated before use
- No user input should reach business logic unvalidated
- Error messages must not leak system information
- Must prevent all common injection attacks

### Compatibility Constraints
- Existing frontend (`frontend/static/js/dashboard.js`) must continue to work
- Response format must remain unchanged
- HTTP status codes must be appropriate (400 for validation, 500 for server)

---

## Questions/Clarifications

### Q1: Should we validate response data as well?
**Answer:** YES - pydantic can validate both requests and responses to ensure API contract

### Q2: What about request size limits?
**Answer:** YES - implement max request size (e.g., 1MB) to prevent DoS

### Q3: Should we log validation failures?
**Answer:** YES - log validation failures for security monitoring (but not in user-facing errors)

### Q4: Rate limiting?
**Answer:** Separate issue (#47) - focus on input validation for this issue

### Q5: Authentication/Authorization?
**Answer:** Separate issues (#44) - focus on input validation for this issue

---

## Implementation Notes

### Files to Create
1. `python/v3/api_models.py` - NEW file with pydantic models
2. `python/v3/tests/api/test_api_validation.py` - NEW comprehensive validation tests

### Files to Modify
1. `python/v3/api_server.py` - Replace reqparse with pydantic validation
2. `python/v3/requirements.txt` - Add pydantic dependency

### Pydantic Models Needed

```python
# api_models.py structure

from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Optional, Dict, Any

class ControlAction(str, Enum):
    """Valid control actions"""
    PUMP_START = "pump_start"
    PUMP_STOP = "pump_stop"
    EMERGENCY_STOP = "emergency_stop"

class SystemMode(str, Enum):
    """Valid system modes"""
    AUTO = "auto"
    MANUAL = "manual"
    ECO = "eco"

class ControlRequest(BaseModel):
    """Request model for /api/control"""
    action: ControlAction
    
    class Config:
        # Don't allow extra fields
        extra = "forbid"

class ModeRequest(BaseModel):
    """Request model for /api/mode"""
    mode: SystemMode
    
    class Config:
        extra = "forbid"

class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    success: bool = False
    error: str
    field: Optional[str] = None
    error_code: str = "VALIDATION_ERROR"
```

---

## Dependencies

### New Dependencies
- `pydantic>=2.0.0` - For request/response validation
- `pydantic[email]>=2.0.0` - If we add email validation later

### Updated Dependencies
- Remove dependency on Flask-RESTful's reqparse (deprecated)

---

## Success Metrics

**Validation Coverage:**
- ✅ 100% of POST endpoints have pydantic validation
- ✅ 100% of parameters validated before business logic
- ✅ 0 unvalidated inputs reach business logic

**Security Metrics:**
- ✅ All injection attack tests pass (SQL, XSS, Command)
- ✅ All malicious input tests return 400 errors
- ✅ No validation errors cause system crashes

**Quality Metrics:**
- ✅ All validation tests pass (at least 10 test scenarios)
- ✅ Test coverage for validation code: 100%
- ✅ No regressions in existing functionality

---

## Next Steps

1. **@architect** - Design pydantic model structure and integration approach
2. **@tester** - Write comprehensive validation tests (TDD approach)
3. **@developer** - Implement pydantic models and integrate with API
4. **@validator** - Security audit and hardware verification

---

**Status:** ✅ Requirements Complete  
**Ready for:** @architect (Design Phase)  
**Estimated Implementation Time:** 4-6 hours

**GitHub Issue:** #43  
**Priority:** CRITICAL  
**Blocking:** Production deployment (security requirement)

