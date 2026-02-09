# Requirements: Issue #44 - MQTT Authentication Security

**Issue:** #44 - [SECURITY] MQTT Authentication Not Always Enforced  
**Agent:** @requirements  
**Priority:** CRITICAL 🔥  
**Date:** October 31, 2025  
**Status:** Requirements Complete

---

## 🎯 Problem Statement

**Current State:** MQTT authentication is implemented but has critical security vulnerabilities that allow unauthorized access to the solar heating system.

**Impact:** HIGH - Unauthorized users could:
- Control heating system (pumps, heaters)
- Read sensitive sensor data
- Modify system settings via MQTT
- Disable safety features
- Cause physical damage or safety hazards
- Monitor home occupancy patterns

---

## 🚨 CRITICAL FINDINGS

### Finding 1: HARDCODED CREDENTIALS (CRITICAL)

**Location:** 
- `python/v3/mqtt_handler.py` lines 24-25
- `python/v3/config.py` lines 42-43

**Code:**
```python
self.username = "mqtt_beaches"
self.password = "uQX6NiZ.7R"
```

**Severity:** CRITICAL  
**CVE Category:** CWE-798 (Use of Hard-coded Credentials)

**Risks:**
- ✅ Credentials visible in source code
- ✅ Credentials committed to git history
- ✅ Anyone with code access has MQTT password
- ✅ Same credentials across all instances
- ✅ No way to rotate credentials without code changes
- ✅ Credentials exposed in backups, logs, etc.

**Related Issue:** This also addresses Issue #45 (Hardcoded Secrets)

---

### Finding 2: NO ENVIRONMENT VARIABLE SUPPORT

**Current State:** No `.env` file or environment variable loading mechanism

**Impact:**
- Cannot use different credentials per environment
- Cannot secure credentials in production
- Violates security best practices
- Makes credential rotation difficult

---

### Finding 3: INSUFFICIENT AUTHENTICATION LOGGING

**Current Code:**
```python
logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
```

**Problems:**
- Doesn't distinguish authentication failures from network failures
- No logging of WHO tried to connect
- No logging of connection attempts (success or failure)
- No audit trail for security review
- Can't detect brute force attacks

---

### Finding 4: NO CERTIFICATE/TLS SUPPORT

**Current State:** Using unencrypted MQTT on port 1883

**Risks:**
- Credentials sent in cleartext over network
- Man-in-the-middle attacks possible
- Network sniffing can reveal credentials
- No encryption of sensor data or commands

**Industry Standard:** MQTT should use TLS/SSL on port 8883

---

### Finding 5: NO AUTH VERIFICATION

**Problem:** Code doesn't verify that authentication was REQUIRED by broker

**Current Behavior:**
- Sets username/password
- Connects to broker
- If connection succeeds, assumes auth worked
- BUT: Broker might allow anonymous connections as fallback

**Risk:** If broker is misconfigured to allow anonymous access, the authentication is bypassed entirely

---

## 📋 Functional Requirements

### FR-001: Environment-Based Credential Management
**Priority:** CRITICAL

**Requirements:**
- SHALL load MQTT credentials from environment variables
- SHALL support `.env` file for local development
- SHALL NOT hardcode credentials in source code
- SHALL support different credentials per environment (dev/test/prod)
- SHALL fail securely if credentials are not provided

**Environment Variables:**
- `MQTT_BROKER` - MQTT broker address
- `MQTT_PORT` - MQTT broker port
- `MQTT_USERNAME` - MQTT username
- `MQTT_PASSWORD` - MQTT password
- `MQTT_CLIENT_ID` - MQTT client ID (optional, can be generated)

---

### FR-002: Authentication Enforcement
**Priority:** CRITICAL

**Requirements:**
- SHALL require authentication for ALL MQTT connections
- SHALL fail if authentication fails
- SHALL NOT fall back to anonymous connection
- SHALL validate authentication before subscribing to topics
- SHALL verify broker requires authentication

**MQTT Return Code Handling:**
- `rc=0`: Connection accepted
- `rc=1`: Connection refused - incorrect protocol version
- `rc=2`: Connection refused - invalid client identifier
- `rc=3`: Connection refused - server unavailable
- `rc=4`: Connection refused - bad username or password ← **KEY**
- `rc=5`: Connection refused - not authorized ← **KEY**

---

### FR-003: Comprehensive Connection Logging
**Priority:** HIGH

**Requirements:**
- SHALL log ALL connection attempts (success and failure)
- SHALL log authentication failures with return code
- SHALL log client ID attempting connection
- SHALL log timestamp of connection attempts
- SHALL NOT log passwords or sensitive data
- SHALL provide audit trail for security review

**Log Format:**
```
TIMESTAMP - LEVEL - MQTT Connection - ClientID: <id> - Status: <success/failed> - RC: <code> - Reason: <reason>
```

---

### FR-004: TLS/SSL Support (Future Enhancement)
**Priority:** MEDIUM (Phase 2)

**Requirements:**
- SHOULD support TLS/SSL encryption
- SHOULD use port 8883 for secure MQTT
- SHOULD validate server certificates
- SHOULD support client certificates (optional)
- MAY support MQTT over WebSockets

**Note:** This can be implemented in a future issue to maintain focus

---

### FR-005: Broker Configuration Verification
**Priority:** HIGH

**Requirements:**
- SHALL verify broker requires authentication
- SHALL check broker configuration on startup
- SHALL warn if broker allows anonymous connections
- SHALL provide broker security audit command

---

### FR-006: Connection Security Monitoring
**Priority:** MEDIUM

**Requirements:**
- SHOULD detect repeated failed authentication attempts
- SHOULD alert on suspicious connection patterns
- MAY implement connection rate limiting
- MAY implement IP-based access control (via broker config)

---

## 🔐 Security Requirements

### SEC-001: Credential Storage
- **SHALL NOT** store credentials in source code
- **SHALL** use environment variables or secure vault
- **SHALL** use different credentials per environment
- **SHALL** document credential rotation procedure
- **SHALL** use strong passwords (min 16 characters, mixed case, numbers, symbols)

---

### SEC-002: Authentication Strength
- **SHALL** enforce username AND password authentication
- **SHALL** reject anonymous connections
- **SHALL** use non-default usernames
- **SHALL** use strong, unique passwords
- **SHOULD** support certificate-based auth (future)

---

### SEC-003: Error Handling
- **SHALL NOT** reveal authentication details in error messages
- **SHALL NOT** distinguish between "invalid username" and "invalid password"
- **SHALL** use generic error messages: "Authentication failed"
- **SHALL** log detailed errors securely (not user-facing)

---

### SEC-004: Audit & Monitoring
- **SHALL** log all authentication attempts
- **SHALL** retain logs for security audit
- **SHALL** alert on repeated authentication failures
- **SHOULD** integrate with security monitoring systems

---

### SEC-005: Broker Security
- **SHALL** document secure broker configuration
- **SHALL** verify broker disables anonymous access
- **SHALL** implement broker access control lists (ACLs)
- **SHALL** document broker security hardening steps

---

## 📊 Acceptance Criteria

### AC-001: Credentials Removed from Code
- [ ] No hardcoded username in code
- [ ] No hardcoded password in code
- [ ] Credentials loaded from environment variables
- [ ] `.env.example` file provided with documentation

---

### AC-002: Authentication Works Correctly
- [ ] System connects with valid credentials
- [ ] System rejects invalid credentials
- [ ] System fails securely without credentials
- [ ] No fallback to anonymous connection

---

### AC-003: Logging Implemented
- [ ] Connection attempts logged (success)
- [ ] Authentication failures logged (with RC)
- [ ] Logs contain client ID and timestamp
- [ ] Logs do NOT contain passwords
- [ ] Audit trail available for review

---

### AC-004: Broker Configuration
- [ ] Broker configured to require authentication
- [ ] Broker does NOT allow anonymous connections
- [ ] ACLs configured for user access control
- [ ] Configuration documented

---

### AC-005: Security Testing
- [ ] Test with valid credentials → Success
- [ ] Test with invalid credentials → Rejected
- [ ] Test with no credentials → Rejected
- [ ] Test anonymous connection → Rejected
- [ ] Verify logs show authentication status

---

### AC-006: Production Deployment
- [ ] Credentials configured via environment variables
- [ ] Service starts with correct authentication
- [ ] Home Assistant integration works
- [ ] MQTT communications functioning
- [ ] No security regressions

---

## 🧪 Test Scenarios

### Test Scenario 1: Valid Authentication
**Given:** Valid MQTT credentials in environment variables  
**When:** System starts and connects to MQTT broker  
**Then:** 
- Connection succeeds
- Log shows "Connected to MQTT broker successfully"
- System can publish and subscribe to topics

---

### Test Scenario 2: Invalid Username
**Given:** Invalid username in environment variables  
**When:** System attempts to connect to MQTT broker  
**Then:**
- Connection fails with RC=4 or RC=5
- Log shows "MQTT authentication failed"
- System does NOT connect
- Retry logic activates

---

### Test Scenario 3: Invalid Password
**Given:** Valid username but invalid password  
**When:** System attempts to connect to MQTT broker  
**Then:**
- Connection fails with RC=4
- Log shows "MQTT authentication failed" (no details about password)
- System does NOT connect
- Error message is generic

---

### Test Scenario 4: No Credentials
**Given:** Missing MQTT credentials (environment variables not set)  
**When:** System starts  
**Then:**
- System fails to start OR fails securely
- Clear error message: "MQTT credentials not configured"
- Does NOT attempt connection with empty credentials
- Does NOT attempt anonymous connection

---

### Test Scenario 5: Anonymous Connection Attempt
**Given:** Broker configured to require auth  
**When:** Attempt to connect without credentials (direct MQTT client test)  
**Then:**
- Connection refused by broker
- Broker logs show rejected connection
- System logs show no anonymous attempts from our client

---

### Test Scenario 6: Broker Misconfiguration Detection
**Given:** Broker accidentally allows anonymous connections  
**When:** System connects  
**Then:**
- System detects anonymous access is allowed
- Warning logged: "Broker allows anonymous connections - security risk"
- System still uses authentication (doesn't downgrade)

---

### Test Scenario 7: Authentication Failure Logging
**Given:** Multiple failed connection attempts with bad credentials  
**When:** Reviewing logs after failures  
**Then:**
- Each attempt logged with timestamp
- Return codes logged (RC=4 or RC=5)
- Client ID logged
- No passwords in logs
- Clear audit trail

---

### Test Scenario 8: Credential Rotation
**Given:** Need to change MQTT password  
**When:** Update environment variable and restart service  
**Then:**
- Service restarts with new credentials
- Connection succeeds with new password
- No code changes required
- Old password no longer works

---

## 🏗️ Technical Constraints

### TC-001: Backward Compatibility
- **MUST** maintain compatibility with existing Home Assistant integration
- **MUST** maintain compatibility with existing MQTT topics
- **MUST NOT** break existing sensor publishing

---

### TC-002: Performance
- **MUST** not significantly impact connection time (<2 seconds overhead)
- **MUST** handle authentication failures gracefully (retry logic)
- **MUST NOT** create memory leaks with failed connections

---

### TC-003: Platform Compatibility
- **MUST** work on Raspberry Pi ARM architecture
- **MUST** work with Python 3.11+
- **MUST** work with paho-mqtt library
- **MUST** work with common MQTT brokers (Mosquitto, etc.)

---

### TC-004: Configuration Management
- **MUST** support environment variables
- **SHOULD** support `.env` files for development
- **MAY** support other secret management systems (future)

---

## 📁 Files Requiring Changes

### Code Files:
1. **`python/v3/mqtt_handler.py`** - MODIFY
   - Remove hardcoded credentials
   - Load credentials from config
   - Enhance connection logging
   - Add authentication verification

2. **`python/v3/config.py`** - MODIFY
   - Remove default credential values
   - Add environment variable loading
   - Make credentials required (no defaults)

3. **`python/v3/tests/mqtt/test_mqtt_security.py`** - CREATE
   - Test valid authentication
   - Test invalid authentication
   - Test no credentials
   - Test logging
   - Test anonymous rejection

---

### Configuration Files:
4. **`.env.example`** - CREATE
   - Template for environment variables
   - Documentation of required variables
   - Example values (NOT production)

5. **`docs/MQTT_SECURITY_SETUP.md`** - CREATE
   - How to configure MQTT credentials
   - Broker configuration guide
   - Security best practices
   - Troubleshooting

6. **`mosquitto.conf`** (or broker config) - DOCUMENT
   - Sample secure broker configuration
   - Anonymous access disabled
   - Password file configuration
   - ACL configuration

---

## 🔗 Related Issues

### Issue #45: Hardcoded Secrets in Configuration
**Status:** Open  
**Relationship:** This issue PARTIALLY addresses #45 for MQTT credentials specifically

**Note:** Full resolution of #45 requires addressing ALL hardcoded secrets, not just MQTT

---

### Issue #46: Error Messages Leak System Info
**Status:** Open  
**Relationship:** Auth error messages must not leak info (addressed in SEC-003)

---

### Issue #43: API Input Validation
**Status:** ✅ Complete  
**Relationship:** Similar security hardening, lessons learned applied

---

## 💡 Implementation Notes

### Note 1: Two-Phase Approach Recommended

**Phase 1 (This Issue):**
- Remove hardcoded credentials
- Implement environment variable loading
- Add authentication verification
- Enhance logging
- Basic security testing

**Phase 2 (Future Issue - Optional):**
- TLS/SSL support
- Certificate-based authentication
- Advanced security monitoring
- Rate limiting

---

### Note 2: Mosquitto Broker Configuration

**Required Broker Settings:**
```conf
# Disable anonymous access
allow_anonymous false

# Password file
password_file /etc/mosquitto/passwd

# ACL file (optional but recommended)
acl_file /etc/mosquitto/acls

# Listeners
listener 1883 0.0.0.0

# For TLS (Phase 2):
# listener 8883
# cafile /etc/mosquitto/ca_certificates/ca.crt
# certfile /etc/mosquitto/certs/server.crt
# keyfile /etc/mosquitto/certs/server.key
```

---

### Note 3: Creating MQTT Users

```bash
# Create password file
sudo mosquitto_passwd -c /etc/mosquitto/passwd mqtt_beaches

# Add additional users
sudo mosquitto_passwd /etc/mosquitto/passwd another_user

# Restart mosquitto
sudo systemctl restart mosquitto
```

---

### Note 4: Home Assistant Configuration

**Home Assistant must be updated with new credentials:**

```yaml
# configuration.yaml
mqtt:
  broker: 192.168.0.110
  port: 1883
  username: !secret mqtt_username
  password: !secret mqtt_password
```

**User should be notified about this requirement**

---

## 🎯 Success Criteria Summary

**Issue is complete when:**

1. ✅ No hardcoded credentials in code
2. ✅ Credentials loaded from environment variables
3. ✅ Authentication failures properly handled and logged
4. ✅ Broker configured to require authentication
5. ✅ All security tests pass
6. ✅ Documentation complete
7. ✅ Deployed to production successfully
8. ✅ Home Assistant integration still works
9. ✅ Audit trail available for connection attempts
10. ✅ User can rotate credentials without code changes

---

## 🚀 Next Steps

**Handoff to @architect:**

These requirements are ready for architectural design. Key decisions needed:

1. Environment variable loading strategy (python-dotenv or manual?)
2. Configuration validation approach
3. Error handling strategy for missing credentials
4. Logging format and destination
5. Broker configuration approach

**Estimated Implementation Time:** 8.5-9.5 hours (as per project plan)

---

## ✅ Requirements Sign-Off

**Requirements gathered by:** @requirements  
**Date:** October 31, 2025  
**Status:** Complete - Ready for @architect  
**Approval:** Pending user review

---

**Questions or Clarifications Needed?**
- Is TLS/SSL required immediately or can it be Phase 2?
- Are there any other MQTT brokers in use besides 192.168.0.110?
- Is there a preferred secret management system?
- Should we implement certificate auth now or later?

---

*Next Agent: @architect*  
*Handoff Notes: Comprehensive requirements documented. Critical security issues identified (hardcoded credentials). Clear acceptance criteria defined. Ready for architecture design.*

