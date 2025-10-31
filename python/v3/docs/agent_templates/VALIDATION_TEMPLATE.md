# User Validation: [Feature Name]

**Date:** [YYYY-MM-DD]  
**Status:** [Phase 1 - Code Review | Phase 2 - Hardware Testing | Complete]  
**Agent:** @validator  
**Issue:** #[number]  
**Implementation Doc:** [Link]

---

## 📋 Validation Overview

### Validation Approach
This validation follows a two-phase approach:
1. **Phase 1:** Code Review (before hardware testing)
2. **Phase 2:** Hardware Validation (after code review passes)
3. **Phase 3:** Production Deployment Verification

### Original Requirements
[Link to requirements document or brief summary]

### Success Criteria
- [ ] All requirements met
- [ ] Code quality standards met
- [ ] Hardware tests pass on Raspberry Pi
- [ ] User acceptance criteria satisfied
- [ ] Production deployment successful

---

## ✅ PHASE 1: CODE REVIEW

**Purpose:** Verify code quality and readiness before hardware testing

### Architecture Compliance

**Architecture Document:** [Link]

#### Design Alignment
- [ ] Implementation follows architecture document
- [ ] All components implemented as designed
- [ ] Data flow matches design
- [ ] Design patterns correctly applied
- [ ] Component interactions as specified
- [ ] No unauthorized deviations from design

**Findings:**
- ✅ [What's good]
- ⚠️ [Minor issues if any]
- ❌ [Critical issues if any]

**Status:** [ ] ✅ Compliant / [ ] ⚠️ Minor Issues / [ ] ❌ Non-Compliant

---

### Code Quality Assessment

#### Readability & Maintainability
- [ ] Code is clean and readable
- [ ] Proper naming conventions used
- [ ] Functions are focused (single responsibility)
- [ ] Appropriate abstraction levels
- [ ] No code duplication
- [ ] Consistent coding style

**Score:** __/10

#### Documentation
- [ ] All public functions documented
- [ ] All classes documented
- [ ] Complex logic explained
- [ ] Type hints present
- [ ] Comments are clear and helpful

**Score:** __/10

#### Code Structure
- [ ] Appropriate file organization
- [ ] Logical code flow
- [ ] No circular dependencies
- [ ] Proper separation of concerns
- [ ] Module boundaries clear

**Score:** __/10

**Overall Code Quality Score:** __/10

**Findings:**
```
✅ Strengths:
- [Strength 1]
- [Strength 2]

⚠️ Areas for Improvement:
- [Issue 1] - Severity: [High/Med/Low]
- [Issue 2] - Severity: [High/Med/Low]
```

**Status:** [ ] ✅ Excellent / [ ] ⚠️ Acceptable / [ ] ❌ Needs Work

---

### Error Handling & Logging

#### Error Handling
- [ ] All error cases handled
- [ ] No bare `except:` clauses
- [ ] Error messages are clear
- [ ] Resources properly cleaned up
- [ ] Graceful degradation implemented
- [ ] Recovery logic appropriate

**Findings:**
- ✅ [What's good]
- ⚠️ [Issues if any]

#### Logging
- [ ] Appropriate log levels used
- [ ] Critical operations logged
- [ ] Errors logged with context
- [ ] No sensitive data in logs
- [ ] Log messages are actionable
- [ ] Logging is consistent

**Findings:**
- ✅ [What's good]
- ⚠️ [Issues if any]

**Status:** [ ] ✅ Excellent / [ ] ⚠️ Acceptable / [ ] ❌ Needs Work

---

### Best Practices & Standards

#### Python Best Practices
- [ ] PEP 8 compliance
- [ ] Pythonic code patterns
- [ ] Type hints used properly
- [ ] Context managers for resources
- [ ] F-strings for formatting
- [ ] Pathlib for file operations

#### Project Standards
- [ ] Follows project conventions
- [ ] Consistent with existing code
- [ ] No anti-patterns
- [ ] Efficient algorithms used
- [ ] Appropriate data structures

**Findings:**
- ✅ [What's good]
- ⚠️ [Issues if any]

**Status:** [ ] ✅ Excellent / [ ] ⚠️ Acceptable / [ ] ❌ Needs Work

---

### Security Review

#### Input Validation
- [ ] All inputs validated
- [ ] SQL injection prevented
- [ ] Command injection prevented
- [ ] XSS prevention (if applicable)
- [ ] Path traversal prevented

#### Secrets Management
- [ ] No hardcoded secrets
- [ ] Credentials properly managed
- [ ] Environment variables used
- [ ] Error messages don't leak info

#### Authentication & Authorization
- [ ] Auth checks implemented (if applicable)
- [ ] Permission checks correct
- [ ] Session management secure

**Findings:**
- ✅ [Security measures in place]
- ⚠️ [Concerns if any]
- ❌ [Vulnerabilities if any]

**Status:** [ ] ✅ Secure / [ ] ⚠️ Minor Issues / [ ] ❌ Vulnerabilities Found

---

### Performance Review

#### Efficiency
- [ ] No obvious bottlenecks
- [ ] Efficient algorithms used
- [ ] Appropriate caching
- [ ] Resource usage acceptable
- [ ] Async patterns used appropriately

#### Scalability
- [ ] Can handle expected load
- [ ] No hardcoded limits
- [ ] Memory usage reasonable
- [ ] CPU usage reasonable

**Findings:**
- ✅ [Performance strengths]
- ⚠️ [Concerns if any]

**Status:** [ ] ✅ Optimal / [ ] ⚠️ Acceptable / [ ] ❌ Issues Found

---

### Test Coverage Analysis

#### Test Completeness
- [ ] Unit tests comprehensive
- [ ] Integration tests present
- [ ] Edge cases covered
- [ ] Error scenarios tested
- [ ] Tests are clear and maintainable

**Test Results:**
```
Unit Tests: X/X passed
Integration Tests: Y/Y passed
Coverage: Z%
```

**Test Quality:**
- [ ] Tests are independent
- [ ] Tests are repeatable
- [ ] No flaky tests
- [ ] Test names are descriptive
- [ ] Assertions are clear

**Status:** [ ] ✅ Adequate / [ ] ⚠️ Needs More / [ ] ❌ Insufficient

---

### Phase 1 Summary

#### Critical Issues (Must Fix Before Hardware Testing)
1. [ ] [Critical Issue 1 - if any]
2. [ ] [Critical Issue 2 - if any]

#### Important Issues (Should Fix)
1. [ ] [Important Issue 1 - if any]
2. [ ] [Important Issue 2 - if any]

#### Suggestions (Nice to Have)
1. [ ] [Suggestion 1]
2. [ ] [Suggestion 2]

---

### **PHASE 1 DECISION:**

- [ ] ✅ **APPROVED FOR HARDWARE TESTING** - Code review passed, ready for Phase 2
- [ ] ⚠️ **APPROVED WITH NOTES** - Minor issues noted, can proceed to hardware testing
- [ ] ❌ **CHANGES REQUIRED** - Must fix critical issues before hardware testing

**Reviewer:** @validator  
**Date:** [Date]  
**Notes:** [Any additional context]

---

## 🖥️ PHASE 2: HARDWARE VALIDATION

**Purpose:** Verify functionality on actual Raspberry Pi hardware

⚠️ **Prerequisites:**
- [ ] Phase 1 code review passed
- [ ] All critical issues from Phase 1 resolved
- [ ] Code deployed to Raspberry Pi

---

### Pre-Hardware Test Environment Check

#### Verify Production Environment
```bash
# Run environment verification
./scripts/test_production_env.sh
```

**Expected:**
- ✅ Production venv exists
- ✅ Python version correct (3.11+)
- ✅ All dependencies installed

**Results:**
```
[Paste output here]
```

**Status:** [ ] ✅ Environment Ready / [ ] ❌ Issues Found

#### Verify Dependencies in Production
```bash
# Check dependencies
./scripts/verify_deps.sh
```

**Expected:**
- ✅ All requirements.txt packages installed
- ✅ No missing dependencies

**Results:**
```
[Paste output here]
```

**Status:** [ ] ✅ Dependencies OK / [ ] ❌ Missing Packages

---

### Hardware Test Scenarios

### Test 1: [Primary Functionality]

**Goal:** [What we're validating]

**Prerequisites:**
- [Setup requirement 1]
- [Setup requirement 2]

**Steps to Execute on Raspberry Pi:**

```bash
# Step 1: [Description]
ssh pi@192.168.0.18 "cd ~/solar_heating/python/v3 && [command]"

# Step 2: [Description]
ssh pi@192.168.0.18 "[command]"

# Step 3: [Description]
[command]
```

**Expected Results:**
- ✅ [Expected result 1]
- ✅ [Expected result 2]
- ✅ [Expected result 3]

**Actual Results:**
```
[Paste actual output/results here]
```

**Success Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Status:** [ ] ✅ PASS / [ ] ❌ FAIL

**Notes:** [Any observations]

---

### Test 2: [Edge Case Handling]

**Goal:** [What we're testing]

**Steps:**
```bash
# Test commands
```

**Expected:**
- [Expected behavior]

**Actual:**
```
[Results]
```

**Status:** [ ] ✅ PASS / [ ] ❌ FAIL

---

### Test 3: [Error Scenarios]

**Goal:** Test error handling

**Steps:**
```bash
# Trigger error condition
```

**Expected:**
- ✅ Graceful error handling
- ✅ Clear error message
- ✅ System remains stable

**Actual:**
```
[Results]
```

**Status:** [ ] ✅ PASS / [ ] ❌ FAIL

---

### Test 4: [Integration with Real Hardware]

**Goal:** Verify integration with sensors/relays/MQTT

**Steps:**
```bash
# Integration test commands
```

**Expected:**
- ✅ Hardware responds correctly
- ✅ Data is accurate
- ✅ No errors in logs

**Actual:**
```
[Results]
```

**Status:** [ ] ✅ PASS / [ ] ❌ FAIL

---

### Performance on Hardware

#### Resource Usage
```bash
# Check resource usage while running
ssh pi@192.168.0.18 "top -b -n 1 | head -20"
```

**Results:**
- CPU Usage: __%
- Memory Usage: __MB
- Status: [ ] ✅ Acceptable / [ ] ⚠️ High / [ ] ❌ Excessive

#### Response Times
- Test 1: __ms
- Test 2: __ms
- Test 3: __ms
- Status: [ ] ✅ Fast / [ ] ⚠️ Acceptable / [ ] ❌ Slow

---

### Service Integration

#### Service Status
```bash
ssh pi@192.168.0.18 "sudo systemctl status solar_heating_v3.service"
```

**Expected:**
- ✅ Service is active (running)
- ✅ No errors in status
- ✅ Process running correctly

**Actual:**
```
[Service status output]
```

**Status:** [ ] ✅ Running / [ ] ❌ Failed

#### Log Check
```bash
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service -n 50 --no-pager"
```

**Findings:**
- ✅ [Good observations]
- ⚠️ [Warnings if any]
- ❌ [Errors if any]

**Status:** [ ] ✅ Clean / [ ] ⚠️ Minor Issues / [ ] ❌ Errors Found

---

### Phase 2 Summary

#### Hardware Tests Results
- Total Tests: __
- Passed: __
- Failed: __
- Skipped: __

#### Issues Found on Hardware
1. [ ] [Issue 1 - if any]
2. [ ] [Issue 2 - if any]

#### User Experience
**Feedback:** [User's subjective assessment of functionality]

---

### **PHASE 2 DECISION:**

- [ ] ✅ **APPROVED FOR PRODUCTION** - All hardware tests passed
- [ ] ⚠️ **APPROVED WITH MONITORING** - Minor issues, monitor in production
- [ ] ❌ **NOT APPROVED** - Must fix issues before production

**Validator:** @validator  
**Date:** [Date]  
**Notes:** [Any additional context]

---

## 🚀 PHASE 3: PRODUCTION DEPLOYMENT VERIFICATION

**Purpose:** Verify deployment steps and production readiness

### Pre-Deployment Final Checks

#### Pre-Deployment Checklist Completed
- [ ] @developer completed pre-deployment checklist
- [ ] All dependencies documented
- [ ] Rollback plan documented
- [ ] Production environment verified

#### Deployment Plan Review
```bash
# Deployment steps documented?
```

- [ ] Deployment steps clear
- [ ] Service restart plan ready
- [ ] Rollback commands ready
- [ ] Monitoring plan in place

**Status:** [ ] ✅ Ready / [ ] ❌ Not Ready

---

### Deployment Execution

#### Step 1: Backup Current State
```bash
# Verify backup/rollback capability
ssh pi@192.168.0.18 "cd ~/solar_heating && git log --oneline -1"
```

**Last Known Good Commit:** `___________`

**Status:** [ ] ✅ Documented

---

#### Step 2: Deploy Changes
```bash
# Pull latest code
ssh pi@192.168.0.18 "cd ~/solar_heating && git pull"
```

**Output:**
```
[Deployment output]
```

**Status:** [ ] ✅ Success / [ ] ❌ Failed

---

#### Step 3: Install Dependencies (if needed)
```bash
# Install any new dependencies
ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/pip3 install [packages]"
```

**Output:**
```
[Installation output]
```

**Status:** [ ] ✅ Success / [ ] N/A / [ ] ❌ Failed

---

#### Step 4: Restart Service
```bash
# Restart production service
ssh pi@192.168.0.18 "sudo systemctl restart solar_heating_v3.service && sleep 5 && sudo systemctl status solar_heating_v3.service --no-pager"
```

**Output:**
```
[Service status]
```

**Service Status:**
- [ ] ✅ Active (running)
- [ ] ❌ Failed to start

**Status:** [ ] ✅ Success / [ ] ❌ Failed

---

#### Step 5: Production Smoke Tests

##### Test 1: Service Responds
```bash
# Verify service is responding
ssh pi@192.168.0.18 "curl -s http://localhost:5001/api/status | head -20"
```

**Expected:** Valid JSON response with system data

**Actual:**
```
[Response]
```

**Status:** [ ] ✅ PASS / [ ] ❌ FAIL

---

##### Test 2: Core Functionality
```bash
# Test core functionality
[Command to test main feature]
```

**Expected:** [Expected behavior]

**Actual:**
```
[Results]
```

**Status:** [ ] ✅ PASS / [ ] ❌ FAIL

---

##### Test 3: No Errors in Logs
```bash
# Check for errors
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service --since '5 minutes ago' --no-pager | grep -i error"
```

**Expected:** No errors (or only expected errors)

**Actual:**
```
[Log output]
```

**Status:** [ ] ✅ Clean / [ ] ⚠️ Minor Issues / [ ] ❌ Errors

---

#### Step 6: Monitor for Stability (5 minutes)
```bash
# Watch service for 5 minutes
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service -f"
```

**Observations:**
- [Any issues or anomalies]

**Status:** [ ] ✅ Stable / [ ] ⚠️ Minor Issues / [ ] ❌ Unstable

---

### Production Verification Summary

#### Deployment Results
- [ ] Code deployed successfully
- [ ] Dependencies installed
- [ ] Service started successfully
- [ ] Smoke tests passed
- [ ] System is stable
- [ ] No errors in logs

#### Production Metrics (after 5-10 minutes)
- **Uptime:** __ minutes
- **CPU Usage:** __%
- **Memory Usage:** __MB
- **Response Time:** __ms
- **Error Count:** __

---

### **PHASE 3 DECISION:**

- [ ] ✅ **PRODUCTION DEPLOYMENT SUCCESSFUL** - Issue is complete
- [ ] ⚠️ **MONITORING REQUIRED** - Deployed but needs watching
- [ ] ❌ **ROLLBACK REQUIRED** - Issues found, must revert

**Validator:** @validator  
**Date:** [Date]  
**Notes:** [Any additional context]

---

## 📊 Overall Validation Summary

### Validation Phases Completion
- [x] Phase 1: Code Review - **[STATUS]**
- [x] Phase 2: Hardware Validation - **[STATUS]**  
- [x] Phase 3: Production Deployment - **[STATUS]**

### Requirements Met
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

### Quality Metrics
- **Code Quality:** __/10
- **Test Coverage:** __%
- **Performance:** [Fast/Acceptable/Slow]
- **Security:** [Secure/Issues/Vulnerable]

### Issues Summary
- **Critical:** __ found, __ resolved
- **Important:** __ found, __ resolved
- **Minor:** __ found, __ resolved

---

## ✅ Final Approval

### Approval Checklist
- [ ] All requirements met
- [ ] Code review passed
- [ ] Hardware tests passed
- [ ] Production deployment successful
- [ ] No critical issues remaining
- [ ] User is satisfied
- [ ] Documentation complete

### **FINAL STATUS:**

- [ ] ✅ **APPROVED - ISSUE COMPLETE** - Ready to close issue
- [ ] ⚠️ **APPROVED WITH FOLLOW-UP** - Complete with noted follow-up items
- [ ] ❌ **NOT APPROVED** - More work needed

**Issue Status:** [Complete | Needs Follow-up | Not Complete]

---

## 📝 Follow-Up Items

### Future Improvements
1. [Improvement idea 1]
2. [Improvement idea 2]

### Known Limitations
1. [Limitation 1]
2. [Limitation 2]

### Monitoring Recommendations
- [What to monitor in production]
- [Metrics to track]
- [Alerts to set up]

---

## 📚 Documentation

### Documents Updated
- [ ] Requirements document
- [ ] Architecture document
- [ ] User guide
- [ ] API documentation
- [ ] Deployment guide

### GitHub Issue
- [ ] Issue updated with validation results
- [ ] Comments added
- [ ] Issue closed (if complete)

---

## 🎓 Lessons Learned

### What Went Well
- [Positive observation 1]
- [Positive observation 2]

### What Could Be Improved
- [Improvement 1]
- [Improvement 2]

### Recommendations for Future
- [Recommendation 1]
- [Recommendation 2]

---

**Validated by:** @validator  
**Date:** [YYYY-MM-DD]  
**Time Spent:** [X hours]  
**Next Agent:** @manager (for issue closure)

---

**Hand-off to @manager:**
[Summary of validation results, production status, and any follow-up needed]

