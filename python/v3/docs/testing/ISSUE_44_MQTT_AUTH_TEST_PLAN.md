# Test Plan: Issue #44 - MQTT Authentication Security

**Issue:** #44 - [SECURITY] MQTT Authentication Not Always Enforced  
**Agent:** @tester  
**Priority:** CRITICAL 🔥  
**Date:** October 31, 2025  
**Status:** Test Specifications Complete - Ready for @developer

---

## 🎯 Testing Overview

**Test Strategy:** Test-Driven Development (TDD)  
**Test First Principle:** All tests written BEFORE implementation  
**Expected State:** All tests should FAIL until implementation is complete

**Total Test Files:** 2  
**Total Test Cases:** 60+  
**Coverage Target:** 95%+

---

## 📋 Test Files Created

### 1. test_mqtt_authenticator.py
**Purpose:** Unit tests for MQTTAuthenticator class  
**Location:** `python/v3/tests/mqtt/test_mqtt_authenticator.py`  
**Test Count:** 25+ unit tests

**Test Coverage:**
- Authenticator initialization
- Credential validation
- Return code interpretation  
- Connection logging
- Broker security verification
- Edge cases

---

### 2. test_mqtt_security.py
**Purpose:** Integration tests for MQTT security  
**Location:** `python/v3/tests/mqtt/test_mqtt_security.py`  
**Test Count:** 35+ integration tests

**Test Coverage:**
- Configuration validation
- Successful authentication
- Authentication failures
- Connection logging
- Anonymous connection prevention
- Reconnection security
- Error message security
- Broker security verification
- Integration with existing system
- Credential rotation
- Hardware integration (manual)

---

## 🧪 Test Categories

### Category 1: Configuration Validation (6 tests)
**Purpose:** Ensure credentials are validated at startup

**Tests:**
1. `test_config_accepts_valid_credentials` - Valid creds accepted
2. `test_config_rejects_missing_username` - Reject None username
3. `test_config_rejects_missing_password` - Reject None password
4. `test_config_rejects_empty_username` - Reject empty string username
5. `test_config_rejects_empty_password` - Reject empty string password
6. `test_handler_requires_credentials` - No anonymous connections

**Expected Behavior:** System fails fast with clear error message

---

### Category 2: Credential Validation (8 tests)
**Purpose:** Test credential validation logic

**Tests:**
1. `test_validate_credentials_with_valid_credentials` - Return True for valid
2. `test_validate_credentials_with_empty_username` - Return False for empty
3. `test_validate_credentials_with_empty_password` - Return False for empty
4. `test_validate_credentials_with_none_username` - Return False for None
5. `test_validate_credentials_with_none_password` - Return False for None
6. `test_validate_credentials_with_whitespace_only` - Return False for whitespace
7. `test_authenticator_with_special_characters_in_password` - Handle special chars
8. `test_authenticator_with_unicode_in_credentials` - Handle unicode

**Expected Behavior:** Robust validation of all credential types

---

### Category 3: Return Code Interpretation (6 tests)
**Purpose:** Test MQTT return code interpretation

**Tests:**
1. `test_interpret_return_code_0_success` - RC=0 → Success
2. `test_interpret_return_code_1_protocol_error` - RC=1 → Protocol error
3. `test_interpret_return_code_4_auth_failed` - RC=4 → Auth failed (**CRITICAL**)
4. `test_interpret_return_code_5_not_authorized` - RC=5 → Not authorized
5. `test_interpret_return_code_unknown` - Unknown RC → Error
6. MQTT RC codes properly mapped

**Expected Behavior:** Clear interpretation of all MQTT return codes

---

### Category 4: Successful Authentication (3 tests)
**Purpose:** Test successful authentication flow

**Tests:**
1. `test_successful_connection_with_valid_credentials` - Connection succeeds
2. `test_successful_connection_logs_correctly` - Proper success logging
3. `test_handler_always_sets_credentials` - username_pw_set called before connect

**Expected Behavior:** Successful authentication and proper logging

---

### Category 5: Authentication Failures (4 tests)
**Purpose:** Test authentication failure scenarios

**Tests:**
1. `test_connection_fails_with_bad_username_or_password` - RC=4 failure
2. `test_connection_fails_with_not_authorized` - RC=5 failure
3. `test_auth_failure_does_not_expose_password` - Password NEVER logged
4. Authentication failures logged with context

**Expected Behavior:** Proper failure handling, no password exposure

---

### Category 6: Connection Logging (9 tests)
**Purpose:** Test comprehensive connection logging

**Tests:**
1. `test_log_connection_attempt_success` - Success logged at INFO level
2. `test_log_connection_attempt_failure` - Failure logged at ERROR level
3. `test_log_connection_attempt_no_password_in_log` - **CRITICAL:** No password in logs
4. `test_log_connection_includes_username` - Username included for audit
5. `test_logs_include_timestamp` - Timestamp present (via framework)
6. `test_logs_include_client_id` - Client ID included
7. `test_logs_include_return_code` - Return code included
8. `test_logs_include_username_for_audit` - Username for audit trail
9. `test_successful_connection_logs_correctly` - Complete log format

**Expected Behavior:** Comprehensive, secure logging with audit trail

**CRITICAL SECURITY TEST:** Password MUST NEVER appear in logs under any circumstance

---

### Category 7: Error Message Security (2 tests)
**Purpose:** Ensure error messages don't leak sensitive information

**Tests:**
1. `test_error_messages_dont_reveal_password` - Generic error messages
2. `test_error_messages_dont_distinguish_username_vs_password` - Don't reveal which is wrong

**Expected Behavior:** Generic error messages that don't aid attackers

**Security Principle:** "Authentication failed" not "Invalid password"

---

### Category 8: Anonymous Connection Prevention (2 tests)
**Purpose:** Ensure anonymous connections are impossible

**Tests:**
1. `test_handler_requires_credentials` - Cannot initialize without creds
2. `test_handler_always_sets_credentials` - Always use authentication

**Expected Behavior:** No path to anonymous connection

---

### Category 9: Reconnection Security (2 tests)
**Purpose:** Test security during reconnection

**Tests:**
1. `test_reconnection_validates_credentials` - Re-validate on reconnect
2. `test_reconnection_uses_same_credentials` - Consistent credentials

**Expected Behavior:** Reconnection doesn't bypass security

---

### Category 10: Integration Tests (4 tests)
**Purpose:** Test integration with existing system

**Tests:**
1. `test_handler_still_supports_topic_subscription` - Topics work after auth
2. `test_handler_still_supports_message_handling` - Messages work after auth
3. `test_handler_uses_config_credentials` - Use config for credentials
4. `test_new_handler_uses_updated_credentials` - Support credential rotation

**Expected Behavior:** No regression in existing functionality

---

### Category 11: Hardware Tests (3 tests - MANUAL)
**Purpose:** Test on actual Raspberry Pi with real MQTT broker

**Tests:**
1. `test_real_broker_requires_authentication` - Real broker rejects anonymous
2. `test_real_broker_accepts_valid_credentials` - Real broker accepts valid creds
3. `test_home_assistant_integration_still_works` - HA integration maintained

**Expected Behavior:** Works on real hardware with real broker

**Note:** These tests must be run manually on Raspberry Pi by @validator

---

## 🔐 Security Test Matrix

| Test Scenario | Expected Result | Security Level |
|---------------|-----------------|----------------|
| Valid credentials | Connection succeeds | Normal |
| Invalid username | Connection fails (RC=4) | CRITICAL |
| Invalid password | Connection fails (RC=4) | CRITICAL |
| No credentials | System fails at startup | CRITICAL |
| Empty credentials | System fails at startup | CRITICAL |
| Anonymous attempt | Impossible (blocked at init) | CRITICAL |
| Password in logs | NEVER appears | CRITICAL |
| Generic errors | No info leakage | HIGH |
| Reconnect bypass | Credentials re-validated | HIGH |
| Broker misconfigured | Warning logged | MEDIUM |

---

## 🎯 Test Execution Strategy

### Phase 1: Unit Tests (Before Implementation)
```bash
# Run unit tests - should FAIL
cd python/v3
pytest tests/mqtt/test_mqtt_authenticator.py -v

# Expected: All tests FAIL (code not implemented yet)
```

---

### Phase 2: Integration Tests (After Unit Tests Pass)
```bash
# Run integration tests
pytest tests/mqtt/test_mqtt_security.py -v

# Expected: Tests pass as implementation progresses
```

---

### Phase 3: All Tests Together
```bash
# Run all MQTT tests
pytest tests/mqtt/ -v --tb=short

# Expected: All tests PASS before deployment
```

---

### Phase 4: Hardware Tests (On Raspberry Pi)
```bash
# SSH to Raspberry Pi
ssh pi@192.168.0.18

# Run hardware tests
cd ~/solar_heating/python/v3
/opt/solar_heating_v3/bin/python3 -m pytest tests/mqtt/ -v -m hardware

# Expected: Real broker integration works
```

---

## 📊 Test Coverage Requirements

### Coverage Targets

**Overall:** 95%+ coverage required  
**Critical Paths:** 100% coverage required

**Critical Paths:**
- Credential validation
- Authentication flow
- Return code handling (RC=4, RC=5)
- Password logging prevention
- Error message generation

### Coverage Report
```bash
# Generate coverage report
pytest tests/mqtt/ --cov=mqtt_handler --cov=mqtt_authenticator --cov-report=html --cov-report=term

# Review HTML report
open htmlcov/index.html
```

---

## 🚨 Critical Security Tests

**These tests MUST pass before deployment:**

### 1. Password Never Logged ✅
```python
test_log_connection_attempt_no_password_in_log
test_auth_failure_does_not_expose_password
test_error_messages_dont_reveal_password
```

**Verification:** Search all logs for password string - MUST be empty

---

### 2. No Anonymous Connections ✅
```python
test_handler_requires_credentials
test_config_rejects_missing_username
test_config_rejects_missing_password
```

**Verification:** Cannot initialize handler without credentials

---

### 3. Authentication Failures Handled ✅
```python
test_connection_fails_with_bad_username_or_password
test_connection_fails_with_not_authorized
```

**Verification:** RC=4 and RC=5 properly handled and logged

---

### 4. Audit Trail Complete ✅
```python
test_logs_include_username_for_audit
test_logs_include_client_id
test_logs_include_return_code
```

**Verification:** All connection attempts logged with context

---

## 🔍 Test Data

### Valid Test Credentials
```python
username: "test_user"
password: "test_password"
broker: "192.168.0.110"
port: 1883
```

### Invalid Test Credentials
```python
username: "invalid_user"
password: "wrong_password"
```

### Edge Case Test Data
```python
special_chars_password: "p@$$w0rd!#%&*()"
unicode_username: "用户"
long_password: "a" * 1000
empty_string: ""
none_value: None
whitespace: "   "
```

---

## 🐛 Expected Failures (Before Implementation)

**All tests should FAIL initially because:**

1. `mqtt_authenticator.py` doesn't exist yet
2. `mqtt_handler.py` hasn't been updated
3. `config.py` still has hardcoded credentials
4. No environment variable loading

**This is EXPECTED and CORRECT for TDD!**

---

## ✅ Test Success Criteria

**Tests are successful when:**

1. ✅ All unit tests pass (25+)
2. ✅ All integration tests pass (35+)
3. ✅ Code coverage ≥ 95%
4. ✅ Critical security tests pass (100%)
5. ✅ No password appears in logs (verified)
6. ✅ No regressions in existing functionality
7. ✅ Hardware tests pass on Raspberry Pi
8. ✅ Home Assistant integration still works

---

## 📝 Test Maintenance

### Adding New Tests

**When to add tests:**
- New authentication methods added
- New error conditions discovered
- Security vulnerabilities found
- Edge cases identified

**How to add tests:**
1. Follow existing test structure
2. Use descriptive test names
3. Include docstrings explaining purpose
4. Add to appropriate test class
5. Update this test plan

---

### Test Naming Convention

**Pattern:** `test_<component>_<scenario>_<expected_result>`

**Examples:**
- `test_config_rejects_missing_username`
- `test_auth_failure_does_not_expose_password`
- `test_successful_connection_with_valid_credentials`

---

## 🔄 Test Execution Workflow

### Development Phase
```
1. @tester writes tests (DONE)
   ↓
2. @developer runs tests (should FAIL)
   ↓
3. @developer implements code
   ↓
4. @developer runs tests (should PASS)
   ↓
5. @developer runs all tests (no regressions)
   ↓
6. @validator reviews test results
```

---

### Deployment Phase
```
1. All tests pass locally
   ↓
2. Deploy to Raspberry Pi
   ↓
3. Run hardware tests
   ↓
4. Verify Home Assistant integration
   ↓
5. Monitor logs for 10+ minutes
   ↓
6. Confirm no errors
   ↓
7. Production deployment complete
```

---

## 📚 Testing Best Practices Applied

### 1. Test Independence
- Each test can run independently
- No shared state between tests
- Use fixtures for setup

### 2. Clear Assertions
- One concept per test
- Descriptive assertion messages
- Test both positive and negative cases

### 3. Mock External Dependencies
- Mock MQTT broker
- Mock logger
- Mock client connections

### 4. Comprehensive Coverage
- Happy path
- Error path
- Edge cases
- Security scenarios

### 5. Readable Test Names
- Self-documenting
- Describes what is tested
- Indicates expected behavior

---

## 🎓 Lessons from Issue #43

**Applied to this test suite:**

1. ✅ Write tests BEFORE implementation (TDD)
2. ✅ Test with production environment (hardware tests)
3. ✅ Test integration points (Home Assistant)
4. ✅ Test security specifically (password logging)
5. ✅ Test error scenarios (authentication failures)
6. ✅ Test edge cases (unicode, special chars)
7. ✅ Comprehensive logging tests

---

## 🚀 Handoff to @developer

**Test suite is complete and ready for implementation.**

**@developer should:**

1. Run tests first - verify they FAIL ✅
2. Implement `mqtt_authenticator.py` ✅
3. Update `mqtt_handler.py` ✅
4. Update `config.py` ✅
5. Run tests - verify they PASS ✅
6. Run all tests - verify no regressions ✅
7. Check coverage - verify ≥ 95% ✅

**Critical Requirements:**
- Follow architecture design exactly
- Make tests pass one at a time
- No shortcuts on security
- Password NEVER in logs
- Complete pre-deployment checklist

**Estimated Implementation Time:** 2-3 hours

---

## ✅ Test Plan Sign-Off

**Test plan created by:** @tester  
**Date:** October 31, 2025  
**Status:** Complete - Ready for @developer  
**Total Tests:** 60+  
**Critical Security Tests:** 12  
**Coverage Target:** 95%+

---

**Next Agent:** @developer  
**Handoff Notes:** Comprehensive test suite ready. All tests should FAIL initially (TDD). Implement code to make tests pass. Critical security tests MUST pass before deployment. Follow pre-deployment checklist.

---

*"If it's not tested, it's broken. If it's not tested for security, it's a vulnerability."*

