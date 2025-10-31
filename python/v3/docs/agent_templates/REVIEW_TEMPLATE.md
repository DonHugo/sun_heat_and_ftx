# Code Review: [Feature Name]

**Date:** [YYYY-MM-DD]  
**Status:** [In Review | Approved | Changes Requested]  
**Agent:** @reviewer  
**Reviewer:** [Name if human, @reviewer if AI]  
**Developer:** @developer  
**Related Docs:** [Links to requirements, architecture, implementation]

---

## 📋 Review Summary

**Feature Complexity:** [Low | Medium | High | Critical]  
**Review Type:** [Standard | Security-Focused | Performance-Focused | Refactoring]  
**Review Duration:** [Time spent]  
**Lines of Code Reviewed:** [Number]

**Overall Assessment:** [Brief summary of code quality]

---

## 🏗️ Architecture Compliance

**Status:** ✅ Fully Compliant | ⚠️ Minor Deviations | ❌ Non-Compliant

### Alignment with Architecture Document
- [ ] Implementation follows architecture design
- [ ] Component responsibilities match design
- [ ] Data flow matches design
- [ ] Interfaces implemented as specified
- [ ] Dependencies are as designed

### Findings

#### Compliance ✅
- [Aspect 1 that follows architecture well]
- [Aspect 2 that follows architecture well]

#### Deviations ⚠️
| Deviation | Severity | Justification | Action |
|-----------|----------|---------------|--------|
| [Deviation 1] | High/Med/Low | [Why it happened] | [Required fix or accept] |
| [Deviation 2] | High/Med/Low | [Why it happened] | [Required fix or accept] |

#### Design Pattern Usage
**Patterns Used:**
- [Pattern 1]: ✅ Correctly applied | ⚠️ Could be improved | ❌ Misapplied
- [Pattern 2]: ✅ Correctly applied | ⚠️ Could be improved | ❌ Misapplied

**Analysis:** [Detailed analysis of pattern usage]

---

## 💎 Code Quality Assessment

**Overall Score:** [X/10]

### Code Structure (Score: X/10)
- **Modularity:** [Assessment]
- **Separation of Concerns:** [Assessment]
- **Code Organization:** [Assessment]
- **File Structure:** [Assessment]

### Readability (Score: X/10)
- **Naming Conventions:** [Assessment]
- **Code Clarity:** [Assessment]
- **Comments:** [Assessment]
- **Complexity:** [Assessment]

### Maintainability (Score: X/10)
- **Code Duplication:** [Assessment]
- **Technical Debt:** [Assessment]
- **Future Extensibility:** [Assessment]
- **Documentation:** [Assessment]

### Strengths ✅
1. [Strength 1 - what was done well]
2. [Strength 2]
3. [Strength 3]

### Areas for Improvement ⚠️
1. **Issue:** [Description]
   - **Location:** [File:line]
   - **Severity:** Critical | High | Medium | Low
   - **Recommendation:** [Specific fix]
   - **Effort:** [Time estimate]

2. **Issue:** [Description]
   - **Location:** [File:line]
   - **Severity:** Critical | High | Medium | Low
   - **Recommendation:** [Specific fix]
   - **Effort:** [Time estimate]

### Code Smells Detected 🔍
- [ ] Long Method (functions > 50 lines)
- [ ] Large Class (class > 300 lines)
- [ ] Too Many Parameters (> 5 params)
- [ ] Duplicate Code
- [ ] Magic Numbers
- [ ] Deep Nesting (> 3 levels)
- [ ] Complex Conditionals
- [ ] God Object

**Details:** [Specifics about any code smells found]

---

## 🔐 Security Analysis

**Status:** ✅ Secure | ⚠️ Minor Issues | ❌ Vulnerabilities Found

### Security Checklist
- [ ] Input validation implemented
- [ ] No SQL injection vulnerabilities
- [ ] No command injection vulnerabilities
- [ ] Sensitive data encrypted
- [ ] Secrets not hardcoded
- [ ] Authentication properly implemented
- [ ] Authorization checked
- [ ] Error messages don't leak info
- [ ] Logging doesn't expose sensitive data

### Security Findings

#### Vulnerabilities ❌
| Vulnerability | Severity | Location | Impact | Fix |
|---------------|----------|----------|--------|-----|
| [Vuln 1] | Critical/High/Med/Low | [File:line] | [Impact] | [Fix] |

#### Security Concerns ⚠️
- [Concern 1]: [Description and recommendation]
- [Concern 2]: [Description and recommendation]

#### Security Strengths ✅
- [Good practice 1]
- [Good practice 2]

---

## ⚡ Performance Review

**Status:** ✅ Optimal | ⚠️ Could Improve | ❌ Issues Found

### Performance Analysis

#### Algorithm Complexity
| Function | Time Complexity | Space Complexity | Assessment |
|----------|----------------|------------------|------------|
| [function1] | O(?) | O(?) | ✅/⚠️/❌ |
| [function2] | O(?) | O(?) | ✅/⚠️/❌ |

#### Resource Usage
- **CPU Usage:** [Expected usage and assessment]
- **Memory Usage:** [Expected usage and assessment]
- **I/O Operations:** [Assessment]
- **Network Calls:** [Assessment]

#### Performance Issues ⚠️
1. **Issue:** [Description]
   - **Location:** [File:line]
   - **Impact:** [Performance impact]
   - **Optimization:** [Suggested fix]
   - **Expected Improvement:** [Estimated improvement]

#### Performance Strengths ✅
- [Good practice 1]
- [Good practice 2]

### Scalability Assessment
**Current Load:** [Expected load]  
**Maximum Load:** [Assessment of maximum capacity]  
**Bottlenecks:** [Identified bottlenecks]

---

## 🧪 Test Coverage Analysis

**Coverage:** [X]%  
**Status:** ✅ Excellent (>80%) | ⚠️ Adequate (60-80%) | ❌ Insufficient (<60%)

### Coverage Breakdown
| Component | Line Coverage | Branch Coverage | Assessment |
|-----------|--------------|-----------------|------------|
| [Component1] | X% | Y% | ✅/⚠️/❌ |
| [Component2] | X% | Y% | ✅/⚠️/❌ |

### Test Quality Assessment
- [ ] Unit tests are comprehensive
- [ ] Integration tests cover interactions
- [ ] Edge cases are tested
- [ ] Error scenarios are tested
- [ ] Tests are readable
- [ ] Tests are maintainable
- [ ] Tests run quickly
- [ ] No flaky tests

### Testing Gaps ⚠️
1. **Gap:** [What's not tested]
   - **Risk:** [Risk of not testing this]
   - **Recommendation:** [What tests to add]

2. **Gap:** [What's not tested]
   - **Risk:** [Risk of not testing this]
   - **Recommendation:** [What tests to add]

---

## 🛡️ Error Handling Review

**Status:** ✅ Comprehensive | ⚠️ Could Improve | ❌ Insufficient

### Error Handling Checklist
- [ ] All error cases handled
- [ ] Errors are caught at appropriate level
- [ ] Error messages are clear and useful
- [ ] No bare except clauses
- [ ] Resources cleaned up properly (try/finally)
- [ ] Errors logged appropriately
- [ ] User-facing errors are user-friendly
- [ ] System maintains consistency after errors

### Error Handling Issues ⚠️
| Issue | Location | Severity | Fix |
|-------|----------|----------|-----|
| [Issue 1] | [File:line] | High/Med/Low | [Required fix] |
| [Issue 2] | [File:line] | High/Med/Low | [Required fix] |

---

## 📝 Logging & Monitoring Review

**Status:** ✅ Appropriate | ⚠️ Could Improve | ❌ Insufficient

### Logging Assessment
- [ ] Critical operations logged
- [ ] Errors logged with context
- [ ] Log levels used appropriately
- [ ] No sensitive data in logs
- [ ] Logs are structured
- [ ] Logs include timestamps
- [ ] Logs include correlation IDs

### Logging Issues ⚠️
- [Issue 1]: [Description and fix]
- [Issue 2]: [Description and fix]

### Monitoring Recommendations
- [Metric 1 to monitor]
- [Metric 2 to monitor]

---

## 📚 Documentation Review

**Status:** ✅ Well Documented | ⚠️ Could Improve | ❌ Insufficient

### Documentation Checklist
- [ ] All public functions have docstrings
- [ ] All classes have docstrings
- [ ] Complex logic is commented
- [ ] Type hints are used
- [ ] README updated (if needed)
- [ ] API documentation updated
- [ ] Examples provided

### Documentation Issues ⚠️
- [Missing documentation 1]
- [Missing documentation 2]

---

## 🎯 Best Practices Compliance

### Python Best Practices
- [ ] PEP 8 style guide followed
- [ ] Type hints used consistently
- [ ] List comprehensions used appropriately
- [ ] Context managers used for resources
- [ ] Generators used where appropriate
- [ ] F-strings used for formatting
- [ ] Pathlib used for file paths

### Project-Specific Best Practices
- [ ] Project coding standards followed
- [ ] Naming conventions followed
- [ ] Error handling patterns followed
- [ ] Logging patterns followed

### Violations Found ⚠️
| Violation | Location | Fix |
|-----------|----------|-----|
| [Violation 1] | [File:line] | [Fix] |
| [Violation 2] | [File:line] | [Fix] |

---

## 🔍 Detailed Findings

### Critical Issues ❌ (MUST FIX before approval)

#### Issue 1: [Title]
**Severity:** Critical  
**Location:** `[file.py:line]`  
**Category:** [Architecture | Security | Performance | Quality]

**Problem:**
[Detailed description of the problem]

**Impact:**
[What happens if this isn't fixed]

**Recommendation:**
[Specific fix with code example if applicable]

**Estimated Effort:** [Time to fix]

---

#### Issue 2: [Title]
[Same structure as Issue 1]

---

### Important Issues ⚠️ (SHOULD FIX)

#### Issue 1: [Title]
**Severity:** High  
**Location:** `[file.py:line]`  
**Category:** [Architecture | Security | Performance | Quality]

**Problem:**
[Description]

**Impact:**
[Impact if not fixed]

**Recommendation:**
[Suggested fix]

**Estimated Effort:** [Time to fix]

---

### Suggestions 💡 (NICE TO HAVE)

#### Suggestion 1: [Title]
**Location:** `[file.py:line]`  
**Category:** [Code Quality | Performance | Maintainability]

**Suggestion:**
[What could be improved]

**Benefit:**
[Why this would help]

**Example:**
```python
# Current code
[current code]

# Suggested improvement
[improved code]
```

---

## 📊 Code Metrics

### Complexity Metrics
| File | Lines | Functions | Classes | Avg Complexity | Max Complexity |
|------|-------|-----------|---------|----------------|----------------|
| [file1.py] | [X] | [Y] | [Z] | [N] | [M] |

### Quality Indicators
- **Maintainability Index:** [Score 0-100]
- **Technical Debt Ratio:** [Percentage]
- **Code Duplication:** [Percentage]

---

## 🎓 Learning Opportunities

### Good Practices Demonstrated
1. [Practice 1] - Great example at [location]
2. [Practice 2] - Well implemented at [location]

### Learning Points for Developer
1. [Learning 1]: [Explanation]
2. [Learning 2]: [Explanation]

### Recommended Reading
- [Resource 1]: [Why relevant]
- [Resource 2]: [Why relevant]

---

## 🔄 Comparison with Similar Code

**Similar Implementation:** [Reference to similar code in codebase]

**Consistency:** ✅ Consistent | ⚠️ Some differences | ❌ Inconsistent

**Analysis:** [How this compares to similar implementations]

---

## ✅ Review Decision

**Decision:** 
- [ ] ✅ **APPROVED** - Ready for @validator
- [ ] ⚠️ **APPROVED WITH MINOR CHANGES** - Can proceed with noted improvements
- [ ] ❌ **CHANGES REQUIRED** - Must fix critical issues before proceeding

### Approval Conditions
**If Approved:**
- All critical issues resolved: ✅ Yes / ❌ No
- Security concerns addressed: ✅ Yes / ❌ No
- Performance acceptable: ✅ Yes / ❌ No
- Tests adequate: ✅ Yes / ❌ No

### Required Actions Before Approval
1. [ ] Fix critical issue 1
2. [ ] Fix critical issue 2
3. [ ] Add missing tests
4. [ ] Update documentation

---

## 📋 Next Steps

### For Developer (@developer)
**If changes required:**
1. [Action 1]
2. [Action 2]
3. Re-submit for review

**If approved:**
- Proceed to @validator

### For Validator (@validator)
**Focus Areas:**
- [Area 1 to pay special attention to]
- [Area 2 to verify during hardware testing]

**Known Limitations:**
- [Limitation 1 to be aware of]
- [Limitation 2 to be aware of]

---

## 📝 Review Notes

**Positive Highlights:**
- [Highlight 1]
- [Highlight 2]

**Overall Assessment:**
[Comprehensive summary of code quality, readiness, and any concerns]

**Confidence Level:** [High | Medium | Low]

---

## 📊 Review Statistics

**Review Metrics:**
- Time Spent: [Hours]
- Issues Found: [Number]
- Critical: [Number]
- High: [Number]
- Medium: [Number]
- Low: [Number]

---

## ✅ Sign-Off

**Reviewed By:** @reviewer  
**Date:** [Date]  
**Status:** [Approved | Approved with Changes | Changes Required]

**Next Agent:** @validator  
**Handoff Notes:** [Critical information for validator]

---

**Review Complete:** [Date & Time]


