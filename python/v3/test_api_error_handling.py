#!/usr/bin/env python3
"""
Test API Error Handling Integration (Issue #46)
Verify that error responses use standardized codes and don't leak sensitive info
"""

import sys
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0, '.')

from api_errors import (
    APIErrorCode,
    create_error_response,
    create_success_response,
    create_failure_response
)


class TestAPIErrorHandling(unittest.TestCase):
    """Test standardized error handling"""
    
    def test_error_response_hides_exception_details(self):
        """Verify exception details are not exposed to users"""
        # Simulate an internal error with sensitive information
        sensitive_error = Exception("Database password: secret123, user: admin")
        
        response, status = create_error_response(
            APIErrorCode.SYSTEM_ERROR,
            exception=sensitive_error,
            http_status=500
        )
        
        # Verify response structure
        self.assertIn("error", response)
        self.assertIn("error_code", response)
        self.assertEqual(response["error_code"], "E001")
        
        # Verify sensitive data is NOT in response
        response_str = str(response)
        self.assertNotIn("secret123", response_str)
        self.assertNotIn("admin", response_str)
        self.assertNotIn("Database password", response_str)
        
        # Verify only generic message is returned
        self.assertEqual(response["error"], "Internal system error occurred")
    
    def test_all_error_codes_have_messages(self):
        """Verify all error codes have corresponding messages"""
        from api_errors import ERROR_MESSAGES
        
        for error_code in APIErrorCode:
            self.assertIn(error_code, ERROR_MESSAGES,
                         f"Error code {error_code} missing message")
    
    def test_success_response_structure(self):
        """Verify success responses have consistent structure"""
        response = create_success_response({"temperature": 72.5})
        
        self.assertTrue(response["success"])
        self.assertEqual(response["temperature"], 72.5)
    
    def test_failure_response_structure(self):
        """Verify failure responses have consistent structure"""
        response = create_failure_response(
            "Operation failed",
            "E100",
            details="Temperature too high: 85°C"
        )
        
        self.assertFalse(response["success"])
        self.assertEqual(response["error"], "Operation failed")
        self.assertEqual(response["error_code"], "E100")
        self.assertIn("85°C", response["details"])
    
    def test_error_codes_by_category(self):
        """Verify error codes are properly categorized"""
        # System errors (E001-E099)
        system_codes = [code for code in APIErrorCode if code.value.startswith("E0")]
        self.assertGreaterEqual(len(system_codes), 6)
        
        # Control errors (E100-E199)
        control_codes = [code for code in APIErrorCode if code.value.startswith("E1")]
        self.assertGreaterEqual(len(control_codes), 6)
        
        # Validation errors (E200-E299)
        validation_codes = [code for code in APIErrorCode if code.value.startswith("E2")]
        self.assertGreaterEqual(len(validation_codes), 3)
        
        # Hardware errors (E300-E399)
        hardware_codes = [code for code in APIErrorCode if code.value.startswith("E3")]
        self.assertGreaterEqual(len(hardware_codes), 3)


if __name__ == '__main__':
    print("Testing API Error Handling Integration (Issue #46)...")
    print("=" * 60)
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAPIErrorHandling)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ All error handling tests passed!")
        print(f"   - {result.testsRun} tests executed")
        print("   - No sensitive information leakage detected")
        print("   - All error codes properly structured")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
