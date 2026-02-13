"""
API Error Codes and Messages
Security: Generic user-facing messages, detailed logging only
Issue #46: Prevent sensitive information leakage
"""

from enum import Enum
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class APIErrorCode(Enum):
    """Standardized error codes for API responses"""
    
    # System Errors (E001-E099)
    SYSTEM_ERROR = "E001"
    SYSTEM_STATUS_ERROR = "E002"
    MQTT_ERROR = "E003"
    HARDWARE_ERROR = "E004"
    SERVICE_ERROR = "E005"
    TEMPERATURE_READ_ERROR = "E006"
    
    # Control Errors (E100-E199)
    MANUAL_CONTROL_REQUIRED = "E100"
    HEATER_TEMP_LIMIT = "E101"
    HEATER_LOCKOUT = "E102"
    INVALID_ACTION = "E103"
    CONTROL_FAILED = "E104"
    MODE_CHANGE_FAILED = "E105"
    
    # Validation Errors (E200-E299)
    INVALID_REQUEST = "E200"
    MISSING_PARAMETER = "E201"
    INVALID_PARAMETER = "E202"
    
    # Hardware Errors (E300-E399)
    RELAY_ERROR = "E300"
    SENSOR_ERROR = "E301"
    BOARD_ERROR = "E302"


# Generic error messages (user-facing, safe)
ERROR_MESSAGES = {
    APIErrorCode.SYSTEM_ERROR: "Internal system error occurred",
    APIErrorCode.SYSTEM_STATUS_ERROR: "Unable to retrieve system status",
    APIErrorCode.MQTT_ERROR: "MQTT communication error",
    APIErrorCode.HARDWARE_ERROR: "Hardware communication error",
    APIErrorCode.SERVICE_ERROR: "Service status unavailable",
    APIErrorCode.TEMPERATURE_READ_ERROR: "Temperature data unavailable",
    
    APIErrorCode.MANUAL_CONTROL_REQUIRED: "Manual control mode required",
    APIErrorCode.HEATER_TEMP_LIMIT: "Temperature limit exceeded",
    APIErrorCode.HEATER_LOCKOUT: "Anti-cycling lockout active",
    APIErrorCode.INVALID_ACTION: "Invalid control action",
    APIErrorCode.CONTROL_FAILED: "Control operation failed",
    APIErrorCode.MODE_CHANGE_FAILED: "Mode change failed",
    
    APIErrorCode.INVALID_REQUEST: "Invalid request format",
    APIErrorCode.MISSING_PARAMETER: "Required parameter missing",
    APIErrorCode.INVALID_PARAMETER: "Invalid parameter value",
    
    APIErrorCode.RELAY_ERROR: "Relay control error",
    APIErrorCode.SENSOR_ERROR: "Sensor read error",
    APIErrorCode.BOARD_ERROR: "Board communication error",
}


def create_error_response(
    error_code: APIErrorCode,
    details: str = None,
    exception: Exception = None,
    http_status: int = 500
) -> tuple[Dict[str, Any], int]:
    """
    Create a sanitized error response
    
    Args:
        error_code: Standardized error code
        details: Additional safe details (optional, must not contain sensitive info)
        exception: Original exception (logged only, never returned)
        http_status: HTTP status code
    
    Returns:
        Tuple of (response_dict, http_status)
    """
    # Log detailed error server-side only (with stack trace)
    if exception:
        logger.error(
            f"API Error [{error_code.value}]: {ERROR_MESSAGES[error_code]}",
            exc_info=exception
        )
    else:
        logger.error(f"API Error [{error_code.value}]: {ERROR_MESSAGES[error_code]}")
    
    # Log additional details if provided
    if details:
        logger.error(f"Error details: {details}")
    
    # Return generic user-facing message
    response = {
        "error": ERROR_MESSAGES[error_code],
        "error_code": error_code.value
    }
    
    # Add safe details if provided (e.g., "Temperature: 85.5°C")
    if details:
        response["details"] = details
    
    return response, http_status


def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a success response with consistent structure"""
    return {
        "success": True,
        **data
    }


def create_failure_response(
    message: str,
    error_code: str,
    details: str = None
) -> Dict[str, bool]:
    """Create a failure response (non-exception errors)"""
    response = {
        "success": False,
        "error": message,
        "error_code": error_code
    }
    
    if details:
        response["details"] = details
    
    return response
