# Hardware Validation Guide: Issue #43 - API Input Validation

**Issue:** #43 - [SECURITY] API Input Validation Missing  
**Agent:** @validator  
**Date:** 2025-10-31  
**Status:** Ready for Hardware Testing

---

## 🎯 Validation Objectives

1. ✅ Verify pydantic validation works on Raspberry Pi
2. ✅ Confirm valid inputs are accepted
3. ✅ Confirm invalid inputs are rejected (security)
4. ✅ Ensure frontend continues to work
5. ✅ Verify hardware control (pumps, relays) works
6. ✅ Check system stability

---

## 📋 Phase 1: Code Review (Already Complete)

### Architecture Compliance ✅
- [x] Implementation follows architecture document
- [x] Pydantic models correctly structured
- [x] Decorator pattern properly implemented
- [x] Business logic simplified (redundant validation removed)

### Code Quality ✅
- [x] Clean, readable code
- [x] Proper naming conventions
- [x] Good documentation and comments
- [x] No code smells

### Error Handling & Logging ✅
- [x] Validation errors return 400 Bad Request
- [x] Error messages clear and don't leak system info
- [x] Proper error formatting with ValidationErrorResponse

### Best Practices ✅
- [x] Python best practices followed
- [x] Type hints used (pydantic models)
- [x] Security considerations addressed
- [x] Performance acceptable

**Code Review Result:** ✅ Approved for Hardware Testing

---

## 📋 Phase 2: Hardware Validation

### Pre-Deployment Checklist

Before deploying to Raspberry Pi, verify:
- [ ] Code is committed to git repository
- [ ] You have SSH access to Raspberry Pi
- [ ] Raspberry Pi IP address: `192.168.0.18` (confirm this is correct)
- [ ] You have sudo access on Pi
- [ ] Current system is running and stable

---

## 🚀 Step 1: Deploy to Raspberry Pi

### Connect and Verify Current State

```bash
# SSH to Raspberry Pi
ssh pi@192.168.0.18

# Check current system status
sudo systemctl status solar_heating_v3.service

# Check current API is running
curl http://localhost:5001/api/status
```

**Expected:** System is running and API responds

---

### Pull Latest Code

```bash
# Navigate to project directory
cd /home/pi/sun_heat_and_ftx

# Check current branch
git branch

# Pull latest changes
git pull origin main

# Verify new files exist
ls -la python/v3/api_models.py
ls -la python/v3/tests/api/test_api_validation.py
```

**Expected:** 
- git pull succeeds
- api_models.py exists
- test files exist

---

### Install Dependencies

```bash
# Navigate to v3 directory
cd python/v3

# Install/upgrade pydantic and flask
pip3 install --upgrade pydantic>=2.5.0 flask>=3.0.0 flask-restful>=0.3.10

# Verify installation
python3 -c "import pydantic; print(f'Pydantic version: {pydantic.__version__}')"
python3 -c "import flask; print(f'Flask version: {flask.__version__}')"
```

**Expected:**
- Pydantic 2.5.0 or higher installed
- Flask 3.0.0 or higher installed
- No error messages

---

### Test Pydantic Models Directly

```bash
# Test pydantic models work
python3 << 'EOF'
from api_models import ControlRequest, ModeRequest, ControlAction, SystemMode
from pydantic import ValidationError

print("Testing pydantic models...")

# Test valid input
try:
    req = ControlRequest(action='pump_start')
    print("✅ Valid pump_start accepted")
    print(f"   Action value: {req.action.value}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test invalid input
try:
    req = ControlRequest(action='invalid_action')
    print("❌ SECURITY ISSUE: Invalid action was accepted!")
    exit(1)
except ValidationError as e:
    print("✅ Invalid action rejected correctly")

# Test injection attempt
try:
    req = ControlRequest(action="pump_start'; DROP TABLE sensors;--")
    print("❌ SECURITY ISSUE: SQL injection not prevented!")
    exit(1)
except ValidationError as e:
    print("✅ SQL injection attempt blocked")

print("\n🎉 Pydantic models working correctly!")
EOF
```

**Expected:**
```
Testing pydantic models...
✅ Valid pump_start accepted
   Action value: pump_start
✅ Invalid action rejected correctly
✅ SQL injection attempt blocked

🎉 Pydantic models working correctly!
```

---

### Restart Service

```bash
# Restart the solar heating service
sudo systemctl restart solar_heating_v3.service

# Wait a moment for startup
sleep 5

# Check service status
sudo systemctl status solar_heating_v3.service

# Check for errors in logs
sudo journalctl -u solar_heating_v3.service -n 50 --no-pager
```

**Expected:**
- Service restarts successfully
- Status shows "active (running)"
- No error messages in logs about pydantic or api_models

---

## 🧪 Step 2: Functional Testing

### Test 1: Valid Control Actions

```bash
echo "Test 1: Valid pump_start action"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_start"}' \
  | python3 -m json.tool

echo -e "\n\nTest 2: Valid pump_stop action"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_stop"}' \
  | python3 -m json.tool

echo -e "\n\nTest 3: Valid emergency_stop action"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "emergency_stop"}' \
  | python3 -m json.tool
```

**Expected Results:**
- HTTP 200 OK for all three requests
- Response shows `"success": true`
- No validation errors
- Actions execute (check hardware if pump connected)

**Success Criteria:**
- [ ] pump_start returns 200 OK
- [ ] pump_stop returns 200 OK
- [ ] emergency_stop returns 200 OK
- [ ] All responses have success: true

---

### Test 2: Valid Mode Changes

```bash
echo "Test 4: Valid auto mode"
curl -X POST http://localhost:5001/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "auto"}' \
  | python3 -m json.tool

echo -e "\n\nTest 5: Valid manual mode"
curl -X POST http://localhost:5001/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "manual"}' \
  | python3 -m json.tool

echo -e "\n\nTest 6: Valid eco mode"
curl -X POST http://localhost:5001/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "eco"}' \
  | python3 -m json.tool
```

**Expected Results:**
- HTTP 200 OK for all requests
- Mode changes successfully
- Response shows success: true

**Success Criteria:**
- [ ] auto mode returns 200 OK
- [ ] manual mode returns 200 OK
- [ ] eco mode returns 200 OK

---

### Test 3: Invalid Input Rejection

```bash
echo "Test 7: Invalid control action (should be rejected)"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "invalid_action"}' \
  | python3 -m json.tool

echo -e "\n\nTest 8: Invalid mode (should be rejected)"
curl -X POST http://localhost:5001/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "invalid_mode"}' \
  | python3 -m json.tool
```

**Expected Results:**
- HTTP 400 Bad Request
- Response shows `"success": false`
- Error message explains validation failure
- Error code: "VALIDATION_ERROR"

**Success Criteria:**
- [ ] Invalid action returns 400
- [ ] Invalid mode returns 400
- [ ] Error messages are clear
- [ ] No system info leaked in errors

---

### Test 4: Missing Required Fields

```bash
echo "Test 9: Missing action parameter"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{}' \
  | python3 -m json.tool

echo -e "\n\nTest 10: Missing mode parameter"
curl -X POST http://localhost:5001/api/mode \
  -H "Content-Type: application/json" \
  -d '{}' \
  | python3 -m json.tool
```

**Expected Results:**
- HTTP 400 Bad Request
- Error indicates field is required

**Success Criteria:**
- [ ] Missing fields return 400
- [ ] Error mentions "required"

---

## 🔒 Step 3: Security Testing

### Test 5: SQL Injection Prevention

```bash
echo "Test 11: SQL injection attempt in action"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_start'\'' OR '\''1'\''='\''1"}' \
  | python3 -m json.tool

echo -e "\n\nTest 12: SQL injection with DROP TABLE"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_start'\''; DROP TABLE sensors;--"}' \
  | python3 -m json.tool
```

**Expected Results:**
- HTTP 400 Bad Request
- Validation error
- **CRITICAL:** No SQL commands executed!

**Success Criteria:**
- [ ] SQL injection returns 400
- [ ] No database changes occurred
- [ ] System remains stable

---

### Test 6: XSS Attack Prevention

```bash
echo "Test 13: XSS attempt with script tag"
curl -X POST http://localhost:5001/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "<script>alert(1)</script>"}' \
  | python3 -m json.tool

echo -e "\n\nTest 14: XSS with img tag"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "<img src=x onerror=alert(1)>"}' \
  | python3 -m json.tool
```

**Expected Results:**
- HTTP 400 Bad Request
- Script tags rejected
- No script execution

**Success Criteria:**
- [ ] XSS attempts return 400
- [ ] Scripts not reflected in response
- [ ] No XSS vulnerability

---

### Test 7: Command Injection Prevention

```bash
echo "Test 15: Command injection attempt"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_start; rm -rf /"}' \
  | python3 -m json.tool

echo -e "\n\nTest 16: Shell command attempt"
curl -X POST http://localhost:5001/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "auto && shutdown -h now"}' \
  | python3 -m json.tool
```

**Expected Results:**
- HTTP 400 Bad Request
- **CRITICAL:** No shell commands executed!
- System remains running

**Success Criteria:**
- [ ] Command injection returns 400
- [ ] No commands executed
- [ ] System still running (obviously!)

---

### Test 8: Extra Fields Rejection

```bash
echo "Test 17: Extra fields in request"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_start", "extra_field": "malicious", "admin": true}' \
  | python3 -m json.tool
```

**Expected Results:**
- HTTP 400 Bad Request
- Error mentions "extra" or "forbidden" field

**Success Criteria:**
- [ ] Extra fields return 400
- [ ] Only expected fields accepted

---

### Test 9: Type Confusion

```bash
echo "Test 18: Integer instead of string"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": 123}' \
  | python3 -m json.tool

echo -e "\n\nTest 19: Array instead of string"
curl -X POST http://localhost:5001/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": ["auto"]}' \
  | python3 -m json.tool
```

**Expected Results:**
- HTTP 400 Bad Request
- Type error in response

**Success Criteria:**
- [ ] Wrong types return 400
- [ ] Type checking enforced

---

## 🌐 Step 4: Frontend Integration Testing

### Test 10: Web Dashboard Access

```bash
# From your local machine (not SSH):
# Open browser to: http://192.168.0.18/

# Or test from Pi:
curl http://localhost/ | head -20
```

**Success Criteria:**
- [ ] Dashboard loads successfully
- [ ] No JavaScript errors in console
- [ ] Controls are functional

---

### Test 11: Dashboard Control Actions

**Manual Testing Required:**

1. Open dashboard: `http://192.168.0.18/`
2. Navigate to "Control" tab
3. Try to start pump
4. Try to stop pump
5. Try to change mode (auto/manual/eco)

**Expected Results:**
- All controls work
- Actions execute successfully
- No errors displayed
- System responds correctly

**Success Criteria:**
- [ ] Dashboard loads
- [ ] Pump controls work
- [ ] Mode changes work
- [ ] No JavaScript errors

---

## 🔌 Step 5: Hardware Integration Testing

### Test 12: Actual Hardware Control

```bash
echo "Test 20: Start pump (hardware test)"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_start"}'

# Wait and observe
sleep 2

echo -e "\n\nTest 21: Stop pump (hardware test)"
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_stop"}'
```

**Manual Verification Required:**
- [ ] Pump actually starts (if connected)
- [ ] Pump actually stops
- [ ] Relay clicks heard
- [ ] MQTT messages published

---

## 📊 Step 6: System Stability Testing

### Test 13: System Still Stable

```bash
# Check service status
sudo systemctl status solar_heating_v3.service

# Check recent logs for errors
sudo journalctl -u solar_heating_v3.service -n 100 --no-pager | grep -i error

# Check memory usage
free -h

# Check CPU usage
top -bn1 | head -10

# Check API still responding
curl http://localhost:5001/api/status | python3 -m json.tool
```

**Success Criteria:**
- [ ] Service still running
- [ ] No error messages
- [ ] Memory usage normal
- [ ] CPU usage normal
- [ ] API still responds

---

### Test 14: Concurrent Requests

```bash
# Test system handles multiple requests
for i in {1..10}; do
  curl -s -X POST http://localhost:5001/api/status &
done
wait

echo "All concurrent requests completed"
```

**Success Criteria:**
- [ ] All requests succeed
- [ ] No crashes
- [ ] Response times acceptable

---

## ✅ Final Validation Checklist

### Functional Testing
- [ ] ✅ Valid pump_start works
- [ ] ✅ Valid pump_stop works
- [ ] ✅ Valid emergency_stop works
- [ ] ✅ Valid mode changes work (auto, manual, eco)
- [ ] ✅ Invalid inputs rejected (400 Bad Request)
- [ ] ✅ Missing fields rejected

### Security Testing
- [ ] ✅ SQL injection prevented
- [ ] ✅ XSS attacks prevented
- [ ] ✅ Command injection prevented
- [ ] ✅ Extra fields rejected
- [ ] ✅ Type confusion prevented
- [ ] ✅ Error messages don't leak system info

### Integration Testing
- [ ] ✅ Frontend dashboard works
- [ ] ✅ Dashboard controls work
- [ ] ✅ Hardware control works (pumps, relays)
- [ ] ✅ MQTT integration works
- [ ] ✅ System remains stable

### Performance Testing
- [ ] ✅ Response times acceptable (< 100ms)
- [ ] ✅ No memory leaks
- [ ] ✅ Handles concurrent requests
- [ ] ✅ System stable after testing

---

## 📝 Validation Report

**Date:** _____________  
**Tested By:** _____________  
**Raspberry Pi IP:** 192.168.0.18

### Test Results Summary

**Functional Tests:** ___/10 passed  
**Security Tests:** ___/9 passed  
**Integration Tests:** ___/2 passed  
**System Stability:** ___/2 passed

**Total:** ___/23 passed (Need 23/23 for approval)

### Issues Found

_List any issues discovered during testing:_

1. ________________________________________________
2. ________________________________________________
3. ________________________________________________

### Performance Observations

**API Response Time:** ______ ms average  
**Memory Usage:** ______ MB  
**CPU Usage:** ______ %

### Final Decision

- [ ] ✅ **APPROVED** - All tests passed, ready for production
- [ ] ⚠️ **APPROVED WITH NOTES** - Minor issues, can deploy
- [ ] ❌ **REJECTED** - Critical issues found, needs fixes

### Approver Signature

**Validator:** @validator  
**Date:** _____________  
**Status:** _____________

---

## 🚀 Post-Validation Actions

### If APPROVED:

```bash
# Mark issue as complete on GitHub
gh issue close 43 --comment "✅ Hardware validation complete. All security tests passed. API input validation working correctly on Raspberry Pi."

# Update changelog
echo "- Issue #43: Added pydantic input validation to API endpoints (SECURITY)" >> CHANGELOG.md
```

### If Issues Found:

```bash
# Update issue with findings
gh issue comment 43 --body "⚠️ Hardware validation found issues: [list issues]. Needs fixes before deployment."

# Create follow-up issues if needed
```

---

**Estimated Validation Time:** 1-2 hours  
**Required:** SSH access to Raspberry Pi, sudo privileges  
**Prerequisites:** Code deployed, dependencies installed

**Good luck with testing! This is a critical security improvement.** 🔒

