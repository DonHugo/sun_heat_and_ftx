# API Error Handling Integration - Issue #46

## Summary
Successfully integrated standardized error handling into `api_server.py` to fix security vulnerability where internal exception details were exposed to users.

## Changes Made

### 1. New Module: `api_errors.py`
- **APIErrorCode** enum with 18 standardized error codes (E001-E399)
- **Error categories:**
  - System Errors (E001-E099): System status, MQTT, hardware, services
  - Control Errors (E100-E199): Manual control, heater limits, lockouts
  - Validation Errors (E200-E299): Invalid requests/parameters
  - Hardware Errors (E300-E399): Relay, sensor, board errors
- **Helper functions:**
  - `create_error_response()`: Logs detailed errors server-side, returns generic user message
  - `create_success_response()`: Consistent success response structure
  - `create_failure_response()`: Non-exception error responses

### 2. Updated: `api_server.py`
Refactored **11 exception handlers** across the file:

#### Exception Handlers Refactored:
1. Line 145: `get_system_status()` - Now uses E002 (SYSTEM_STATUS_ERROR)
2. Line 177: `_get_mqtt_status()` - Generic MQTT error message
3. Line 235: `_get_last_mqtt_message()` - Log parsing error (no exception details)
4. Line 258: `_get_hardware_status()` - Enhanced logging, generic error
5. Line 282: Subprocess errors - Debug logging for service checks
6. Line 286: Service status errors - Enhanced logging
7. Line 456: `control_system()` - Uses E104 (CONTROL_FAILED) with no exception details
8. Line 496: `set_system_mode()` - Uses E105 (MODE_CHANGE_FAILED)
9. Line 510: `_publish_mqtt()` - Enhanced error logging
10. Line 518: `start_server()` - Server startup failure logging
11. Line 640: `TemperaturesAPI` - Uses E006 (TEMPERATURE_READ_ERROR)

### 3. Security Improvements

#### Before (Vulnerable):
```python
except Exception as e:
    return {"error": f"Failed to get system status: {str(e)}"}
```
**Problem:** Exposes internal exception details (file paths, variable names, stack traces)

#### After (Secure):
```python
except Exception as e:
    error_response, _ = create_error_response(
        APIErrorCode.SYSTEM_STATUS_ERROR,
        exception=e
    )
    return error_response
```
**Benefit:** 
- User sees: `{"error": "Unable to retrieve system status", "error_code": "E002"}`
- Server logs: Full exception with stack trace
- No sensitive information leaked

### 4. Test Coverage
Created `test_api_error_handling.py` with 5 test cases:
- ✅ Verifies exception details are hidden from users
- ✅ Confirms all error codes have messages
- ✅ Validates success/failure response structures
- ✅ Tests error code categorization
- ✅ All tests passing

## Breaking Changes

### Client Code Impact
API error responses have changed structure:

**Old format:**
```json
{
  "error": "Failed to get system status: KeyError 'temperature_sensor'"
}
```

**New format:**
```json
{
  "error": "Unable to retrieve system status",
  "error_code": "E002"
}
```

### Migration Guide for Clients
If your client code parses error messages:
1. **Update error detection:** Check for `error_code` field instead of parsing `error` string
2. **Handle generic messages:** Don't rely on specific error text content
3. **Use error codes for logic:** Base conditional logic on `error_code` values

**Example client update:**
```javascript
// OLD (fragile)
if (response.error.includes("Failed to get")) {
    // handle error
}

// NEW (robust)
if (response.error_code === "E002") {
    // handle system status error
}
```

## Benefits

1. **Security:** No internal exception details exposed to users
2. **Consistency:** All API errors use standardized codes
3. **Debugging:** Enhanced server-side logging with full stack traces
4. **Maintainability:** Centralized error message management
5. **User Experience:** Clear, professional error messages

## Error Code Reference

| Code | Category | Description |
|------|----------|-------------|
| E001 | System | Internal system error |
| E002 | System | System status unavailable |
| E003 | System | MQTT communication error |
| E004 | System | Hardware communication error |
| E005 | System | Service status unavailable |
| E006 | System | Temperature data unavailable |
| E100 | Control | Manual control mode required |
| E101 | Control | Temperature limit exceeded |
| E102 | Control | Anti-cycling lockout active |
| E103 | Control | Invalid control action |
| E104 | Control | Control operation failed |
| E105 | Control | Mode change failed |
| E200 | Validation | Invalid request format |
| E201 | Validation | Required parameter missing |
| E202 | Validation | Invalid parameter value |
| E300 | Hardware | Relay control error |
| E301 | Hardware | Sensor read error |
| E302 | Hardware | Board communication error |

## Testing

```bash
# Run error handling tests
cd python/v3
python3 test_api_error_handling.py

# Verify no exception leakage
grep -n "str(e)" api_server.py  # Should return nothing

# Check syntax
python3 -m py_compile api_server.py api_errors.py
```

## Next Steps

1. ✅ Code review this PR
2. ⏳ Update frontend to handle new error format (if needed)
3. ⏳ Deploy to staging for integration testing
4. ⏳ Monitor logs for any issues after deployment
5. ⏳ Update API documentation with error codes

## Related Issues
- Fixes #46 (Security: Prevent internal error information leakage)
- Related to #43 (Input validation security)
