# Project Plan: Issue #44 - MQTT Authentication

**Manager:** @manager  
**Issue:** #44 - [SECURITY] MQTT Authentication Not Always Enforced  
**Priority:** CRITICAL 🔥  
**Category:** Security  
**Date:** October 31, 2025  
**Status:** Planning → Ready to Start

---

## 🎯 Overall Goal

**Ensure MQTT authentication is properly enforced on all connections to prevent unauthorized access to the solar heating system.**

**Security Impact:** HIGH - Unauthorized access could allow attackers to:
- Control heating system (pumps, heaters)
- Read sensitive sensor data
- Disable safety features
- Cause physical damage

---

## 📋 Current Status

### Issue #43 Complete ✅
- API input validation deployed to production
- All security tests passing
- Zero downtime deployment
- New workflow improvements in place

### Ready for Issue #44 ✅
- Pre-deployment checklist available
- Deployment runbook ready
- Environment verification scripts ready
- Team familiar with process

---

## 🔍 Problem Statement

**From Issue #44:**
- MQTT connections don't always require authentication
- No certificate validation
- Weak or missing password enforcement
- Connection attempts not logged
- Potential for unauthorized control of heating system

---

## 🏗️ Agent Workflow

### 1. @requirements - Gather MQTT Security Requirements
**Deliverable:** `python/v3/docs/requirements/ISSUE_44_MQTT_AUTH_REQUIREMENTS.md`

**Tasks:**
- Document current MQTT authentication state
- Identify all MQTT connection points
- Define security requirements
- Specify authentication methods (username/password, certificates)
- Define connection logging requirements
- Create security test scenarios

**Questions to Answer:**
- Where is MQTT authentication currently configured?
- What authentication is currently in place?
- Where can unauthorized connections occur?
- What data/controls are exposed via MQTT?
- What are the consequences of unauthorized access?

**Estimated Time:** 1 hour

---

### 2. @architect - Design MQTT Security Architecture
**Deliverable:** `python/v3/docs/architecture/ISSUE_44_MQTT_AUTH_ARCHITECTURE.md`

**Tasks:**
- Review current MQTT handler implementation
- Design authentication enforcement strategy
- Plan certificate-based auth (if applicable)
- Design connection attempt logging
- Plan configuration management for credentials
- Ensure backward compatibility (if needed)

**Key Decisions:**
- Authentication method (username/password, TLS/SSL, certificates)
- Where to enforce authentication (code, broker config, both)
- Credential storage strategy
- Logging approach
- Fallback behavior for auth failures

**Estimated Time:** 1.5 hours

---

### 3. @tester - Write MQTT Security Tests
**Deliverable:** `python/v3/tests/mqtt/test_mqtt_security.py`

**Test Categories:**
1. **Unauthorized Access Tests**
   - Test connection without credentials
   - Test connection with invalid credentials
   - Test connection with expired credentials (if applicable)

2. **Authentication Enforcement Tests**
   - Verify authentication is required
   - Verify invalid auth is rejected
   - Verify valid auth is accepted

3. **Connection Logging Tests**
   - Verify successful connections are logged
   - Verify failed connection attempts are logged
   - Verify log entries contain useful information

4. **Certificate Tests (if applicable)**
   - Test with valid certificate
   - Test with invalid certificate
   - Test with expired certificate

5. **Integration Tests**
   - Test MQTT functionality with authentication
   - Test Home Assistant integration with auth
   - Test sensor data publishing with auth

**Estimated Time:** 2 hours

---

### 4. @developer - Implement MQTT Authentication
**Deliverable:** Updated MQTT handler with authentication

**Implementation Tasks:**

#### Code Changes:
1. **mqtt_handler.py:**
   - Add authentication parameters to connection
   - Enforce credential validation
   - Add connection attempt logging
   - Implement certificate support (if applicable)
   - Add error handling for auth failures

2. **config.py:**
   - Add MQTT authentication configuration
   - Support environment variables for credentials
   - Add certificate path configuration (if applicable)

3. **MQTT Broker Configuration:**
   - Configure mosquitto (or broker) for authentication
   - Set up password file or certificate auth
   - Disable anonymous access
   - Configure ACLs (Access Control Lists)

#### Configuration Files:
- Update `.env.example` with MQTT auth variables
- Document credential setup in README
- Create mosquitto.conf template (if using mosquitto)

**Pre-Deployment Checklist:**
- [ ] Syntax check all modified files
- [ ] Import check with production Python
- [ ] All tests passing (120+ tests)
- [ ] Dependencies documented
- [ ] Rollback plan ready
- [ ] Git diff reviewed

**Estimated Time:** 2-3 hours

---

### 5. @validator - Validate MQTT Security

**Phase 1: Code Review**

**Review Areas:**
- [ ] Authentication properly enforced in all connection paths
- [ ] No bypasses or fallbacks that skip authentication
- [ ] Credentials properly managed (not hardcoded)
- [ ] Error handling is secure (no info leakage)
- [ ] Logging is comprehensive
- [ ] Certificate validation correct (if applicable)

**Phase 2: Hardware Validation on Raspberry Pi**

**Test Scenarios:**

1. **Test Unauthorized Access:**
   ```bash
   # Try to connect without credentials
   mosquitto_pub -h localhost -t "test/unauthorized" -m "test"
   # Expected: Connection refused
   ```

2. **Test Invalid Credentials:**
   ```bash
   # Try to connect with wrong password
   mosquitto_pub -h localhost -t "test" -m "test" -u wrong_user -P wrong_pass
   # Expected: Authentication failed
   ```

3. **Test Valid Credentials:**
   ```bash
   # Connect with correct credentials
   mosquitto_pub -h localhost -t "test" -m "test" -u correct_user -P correct_pass
   # Expected: Success
   ```

4. **Verify System Still Works:**
   - Check service status
   - Verify sensor data publishing
   - Test Home Assistant integration
   - Check all MQTT functionality

5. **Check Logs:**
   - Verify connection attempts logged
   - Check authentication failures logged
   - Ensure no sensitive data in logs

**Phase 3: Production Deployment**

- Follow `docs/development/DEPLOYMENT_RUNBOOK.md`
- Use `scripts/test_production_env.sh` before deployment
- Monitor service for 10 minutes post-deployment
- Verify no disruption to MQTT communications

**Estimated Time:** 2 hours

---

## 📊 Implementation Steps Summary

| Step | Agent | Time | Status |
|------|-------|------|--------|
| 1 | @requirements | 1h | ⏳ Not Started |
| 2 | @architect | 1.5h | ⏳ Not Started |
| 3 | @tester | 2h | ⏳ Not Started |
| 4 | @developer | 2-3h | ⏳ Not Started |
| 5 | @validator | 2h | ⏳ Not Started |

**Total Estimated Time:** 8.5-9.5 hours  
**Target Completion:** Same day (if started now)

---

## 📁 Files to Create/Modify

### New Files:
- `python/v3/docs/requirements/ISSUE_44_MQTT_AUTH_REQUIREMENTS.md`
- `python/v3/docs/architecture/ISSUE_44_MQTT_AUTH_ARCHITECTURE.md`
- `python/v3/tests/mqtt/test_mqtt_security.py`
- `mosquitto.conf` (MQTT broker config)
- `.env.example` (updated with MQTT auth variables)

### Modified Files:
- `python/v3/mqtt_handler.py` - Add authentication enforcement
- `python/v3/config.py` - Add auth configuration
- `python/v3/requirements.txt` - (if new dependencies)
- `docs/MQTT_SECURITY.md` - Document authentication setup

---

## 🔐 Security Considerations

### Critical Requirements:
1. **No Anonymous Access** - All connections must authenticate
2. **Strong Credentials** - Enforce password strength
3. **Secure Storage** - Credentials in environment variables or secure vault
4. **Connection Logging** - Log all connection attempts (success/failure)
5. **No Info Leakage** - Error messages don't reveal system details
6. **Certificate Validation** - If using TLS, validate certificates

### Attack Vectors to Close:
- ❌ Anonymous MQTT connections
- ❌ Weak/default passwords
- ❌ Unencrypted credentials in code
- ❌ No logging of unauthorized attempts
- ❌ No certificate validation

---

## 🎯 Success Criteria

### Functional:
- [ ] All MQTT connections require authentication
- [ ] Invalid credentials are rejected
- [ ] Valid credentials work correctly
- [ ] Connection attempts are logged
- [ ] System functionality unchanged

### Security:
- [ ] Unauthorized connections blocked
- [ ] No bypasses or fallbacks
- [ ] Credentials not hardcoded
- [ ] TLS/SSL encryption enabled (if applicable)
- [ ] Security tests pass

### Production:
- [ ] Deployed to Raspberry Pi
- [ ] Service running and stable
- [ ] Home Assistant integration works
- [ ] No disruption to MQTT communications
- [ ] Monitoring confirms security

---

## 🚨 Risk Assessment

### Potential Issues:
1. **Breaking Home Assistant Integration**
   - Risk: Medium
   - Mitigation: Test HA integration thoroughly, provide clear credential setup

2. **MQTT Broker Configuration**
   - Risk: Medium
   - Mitigation: Document broker setup, provide example configs

3. **Service Disruption**
   - Risk: Low (with our new deployment process)
   - Mitigation: Follow deployment runbook, have rollback ready

4. **Credential Management**
   - Risk: Low
   - Mitigation: Use environment variables, document secure practices

---

## 🔄 Rollback Plan

**If deployment fails or causes issues:**

1. **Revert Code:**
   ```bash
   ssh pi@192.168.0.18 "cd ~/solar_heating && git checkout <last-good-commit> python/v3/mqtt_handler.py python/v3/config.py"
   ```

2. **Revert MQTT Broker Config:**
   ```bash
   # Restore previous mosquitto.conf (if modified)
   ssh pi@192.168.0.18 "sudo cp /etc/mosquitto/mosquitto.conf.backup /etc/mosquitto/mosquitto.conf"
   ssh pi@192.168.0.18 "sudo systemctl restart mosquitto"
   ```

3. **Restart Service:**
   ```bash
   ssh pi@192.168.0.18 "sudo systemctl restart solar_heating_v3.service"
   ```

**Last Known Good Commit:** (will be documented during deployment)

---

## 📝 Deployment Checklist

### Pre-Deployment:
- [ ] Pre-deployment checklist completed
- [ ] All tests passing
- [ ] Syntax verified
- [ ] Environment verified
- [ ] Dependencies checked
- [ ] Rollback plan ready

### Deployment:
- [ ] MQTT broker configured
- [ ] Credentials set up
- [ ] Code deployed
- [ ] Service restarted
- [ ] MQTT broker restarted (if applicable)

### Post-Deployment:
- [ ] Service running
- [ ] MQTT connections working
- [ ] Unauthorized access blocked
- [ ] Home Assistant integration working
- [ ] Logs show authentication in action
- [ ] Monitoring stable (10+ minutes)

---

## 📚 Related Issues

- **Issue #43:** API Input Validation ✅ Complete
- **Issue #45:** Hardcoded Secrets (related - credentials management)
- **Issue #46:** Error Message Leakage (related - secure logging)

---

## 🎓 Lessons from Issue #43

**Apply these improvements:**
1. ✅ Use pre-deployment checklist
2. ✅ Test with production Python environment
3. ✅ Run environment verification scripts
4. ✅ Follow deployment runbook
5. ✅ Monitor for 10+ minutes post-deployment
6. ✅ Document everything
7. ✅ Issue not done until in production

---

## 🚀 Ready to Start?

**Current Status:** Planning Complete ✅

**Next Step:** Invoke @requirements agent to begin requirements gathering

**Command:** `@requirements` or "Let's start with requirements for Issue #44"

---

**Questions Before Starting?**
- Ask @manager for clarification
- Review HIGH_PRIORITY_ACTION_PLAN.md for context
- Review MULTI_AGENT_GUIDE.md for process

---

*Created by: @manager*  
*Date: October 31, 2025*  
*Status: Ready to Start*

