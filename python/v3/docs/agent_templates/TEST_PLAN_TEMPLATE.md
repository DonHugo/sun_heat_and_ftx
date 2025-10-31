# Test Plan: [Feature Name]

**Date:** [YYYY-MM-DD]  
**Status:** [Draft | Ready for Implementation | Tests Written | Tests Passing]  
**Agent:** @tester  
**Requirements Doc:** [Link to requirements]  
**Architecture Doc:** [Link to architecture]  
**Version:** [Version number]

---

## 📋 Test Strategy Overview

### Testing Objectives
- [Objective 1 - What we're trying to validate]
- [Objective 2]
- [Objective 3]

### Scope
**In Scope:**
- [What will be tested]
- [What will be tested]

**Out of Scope:**
- [What will NOT be tested]
- [What will NOT be tested]

### Test Approach
[Description of overall testing approach - TDD, integration-first, etc.]

---

## 🎯 Test Coverage

### Requirements Coverage
| Requirement ID | Test Cases | Status |
|----------------|------------|--------|
| REQ-001 | TC-001, TC-002 | ⏳ Pending |
| REQ-002 | TC-003, TC-004, TC-005 | ⏳ Pending |
| REQ-003 | TC-006 | ⏳ Pending |

### Code Coverage Goals
- **Target:** 80%+ code coverage
- **Critical Paths:** 100% coverage
- **Edge Cases:** All identified edge cases covered

---

## 🧪 Unit Tests

### Component 1: [Component Name]

#### Test Case UT-001: [Test Description]
**Purpose:** [What this test validates]

**Test Type:** Unit Test  
**Priority:** [Critical | High | Medium | Low]

**Given:** [Initial state/setup]
```python
# Test setup code
```

**When:** [Action being tested]
```python
# Action code
```

**Then:** [Expected outcome]
```python
# Assertion code
assert expected == actual
```

**Test Code Location:** `tests/test_[component].py::test_[name]`

**Status:** ⏳ Not Written | ✍️ Written | ✅ Passing | ❌ Failing

---

#### Test Case UT-002: [Test Description]
[Same structure as UT-001]

---

### Component 2: [Component Name]
[Same structure as Component 1]

---

## 🔗 Integration Tests

### Integration 1: [Component A ↔ Component B]

#### Test Case IT-001: [Test Description]
**Purpose:** [What integration behavior is being validated]

**Test Type:** Integration Test  
**Priority:** [Critical | High | Medium | Low]

**Components Involved:**
- Component A
- Component B
- [Any dependencies]

**Given:** [Initial state]
```python
# Setup multiple components
```

**When:** [Interaction occurs]
```python
# Trigger interaction
```

**Then:** [Expected behavior]
```python
# Verify both components behave correctly
```

**Test Code Location:** `tests/integration/test_[integration_name].py`

**Mocks/Stubs Needed:**
- [Mock 1 - what and why]
- [Mock 2 - what and why]

**Status:** ⏳ Not Written | ✍️ Written | ✅ Passing | ❌ Failing

---

#### Test Case IT-002: [Test Description]
[Same structure as IT-001]

---

## 🖥️ Hardware Tests (Raspberry Pi)

⚠️ **IMPORTANT:** All hardware tests MUST be run on the actual Raspberry Pi device.

### Hardware Test 1: [Hardware Component]

#### Test Case HW-001: [Test Description]
**Purpose:** [What hardware behavior is being validated]

**Test Type:** Hardware Integration Test  
**Priority:** [Critical | High | Medium | Low]

**Hardware Required:**
- [Raspberry Pi 4]
- [Relay board]
- [Temperature sensors]
- [Any other hardware]

**Execution Location:** Raspberry Pi at `/opt/solar_heating_v3`

**Given:** [Initial hardware state]
```bash
# Commands to set up hardware state
```

**When:** [Hardware action]
```python
# Code that controls hardware
```

**Then:** [Expected hardware response]
```python
# Verify hardware responded correctly
```

**Execution Command:**
```bash
ssh pi@192.168.0.18 "cd /opt/solar_heating_v3 && python3 -m pytest tests/hardware/test_[name].py::test_[name] -v"
```

**Safety Precautions:**
- [Safety note 1]
- [Safety note 2]

**Expected Output:**
```
[Description of expected test output]
```

**Status:** ⏳ Not Written | ✍️ Written | ⏳ Not Tested | ✅ Passing | ❌ Failing

---

## 🌐 End-to-End Tests

### E2E Test 1: [Complete Workflow]

#### Test Case E2E-001: [Test Description]
**Purpose:** [What end-to-end scenario is being validated]

**Test Type:** End-to-End Test  
**Priority:** [Critical | High | Medium | Low]

**User Story:** As a [user], I want to [goal] so that [benefit]

**Preconditions:**
- [Precondition 1]
- [Precondition 2]

**Test Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Step 4]

**Expected Results:**
- [Result 1]
- [Result 2]

**Test Code Location:** `tests/e2e/test_[workflow].py`

**Dependencies:**
- [System dependency 1]
- [System dependency 2]

**Status:** ⏳ Not Written | ✍️ Written | ✅ Passing | ❌ Failing

---

## 🎭 Edge Cases & Error Scenarios

### Edge Case 1: [Description]

#### Test Case EC-001: [Test Description]
**Purpose:** [What edge case is being tested]

**Test Type:** Edge Case Test  
**Priority:** [Critical | High | Medium | Low]

**Scenario:** [Description of edge case]

**Given:** [Boundary condition setup]
**When:** [Edge case trigger]
**Then:** [Expected handling]

**Examples:**
- [Example 1: Input at boundary]
- [Example 2: Unusual but valid condition]

**Test Code Location:** `tests/test_[component].py::test_[edge_case]`

**Status:** ⏳ Not Written | ✍️ Written | ✅ Passing | ❌ Failing

---

### Error Scenario 1: [Description]

#### Test Case ERR-001: [Test Description]
**Purpose:** [What error handling is being tested]

**Test Type:** Error Handling Test  
**Priority:** [Critical | High | Medium | Low]

**Error Condition:** [What goes wrong]

**Given:** [Setup for error condition]
**When:** [Error occurs]
**Then:** [Expected error handling]

**Expected Behavior:**
- [System should detect error]
- [System should log error]
- [System should recover gracefully]
- [User should be notified (if applicable)]

**Test Code Location:** `tests/test_[component].py::test_error_[scenario]`

**Status:** ⏳ Not Written | ✍️ Written | ✅ Passing | ❌ Failing

---

## ⚡ Performance Tests

### Performance Test 1: [Performance Aspect]

#### Test Case PERF-001: [Test Description]
**Purpose:** [What performance characteristic is being tested]

**Test Type:** Performance Test  
**Priority:** [Critical | High | Medium | Low]

**Performance Requirement:**
- **Metric:** [Response time | Throughput | Resource usage]
- **Target:** [Specific target value]
- **Threshold:** [Acceptable range]

**Test Setup:**
```python
# Performance test setup
```

**Test Execution:**
```python
# Code that measures performance
```

**Measurement:**
- [What is being measured]
- [How it's being measured]

**Success Criteria:**
- [Criterion 1]
- [Criterion 2]

**Test Code Location:** `tests/performance/test_[aspect].py`

**Status:** ⏳ Not Written | ✍️ Written | ✅ Passing | ❌ Failing

---

## 🗂️ Test Data & Fixtures

### Test Data Set 1: [Description]
**Purpose:** [What this test data is used for]

**Location:** `tests/fixtures/[filename]`

**Format:**
```json
{
  "example": "test data"
}
```

**Usage:**
```python
@pytest.fixture
def test_data():
    return load_fixture('filename')
```

---

### Mock 1: [Component/System to Mock]
**Purpose:** [Why this needs to be mocked]

**Mock Type:** [Pytest mock | unittest.mock | Custom mock]

**Mock Behavior:**
```python
@pytest.fixture
def mock_component():
    mock = MagicMock()
    mock.method.return_value = expected_value
    return mock
```

---

## 🔧 Test Environment Setup

### Local Development Environment
**Requirements:**
- Python 3.x
- pytest
- [Other testing libraries]

**Setup Commands:**
```bash
pip install -r requirements-test.txt
```

**Environment Variables:**
```bash
export TEST_ENV=development
export TEST_DATA_PATH=/path/to/test/data
```

---

### Raspberry Pi Test Environment
**Requirements:**
- Physical access to Raspberry Pi
- SSH access: `ssh pi@192.168.0.18`
- Installed dependencies

**Setup Commands:**
```bash
ssh pi@192.168.0.18 "cd /opt/solar_heating_v3 && pip3 install -r requirements-test.txt"
```

**Safety Checks:**
```bash
# Verify hardware is in safe state before testing
```

---

## 🚀 Test Execution

### Quick Unit Tests (TDD Cycle)
```bash
# Run specific test during development
pytest tests/test_[component].py::test_[name] -v

# Run all unit tests for a component
pytest tests/test_[component].py -v
```

### All Unit Tests
```bash
pytest tests/ -v --tb=short --cov=[component] --cov-report=html
```

### Integration Tests
```bash
pytest tests/integration/ -v --tb=short
```

### Hardware Tests (on Raspberry Pi)
```bash
ssh pi@192.168.0.18 "cd /opt/solar_heating_v3 && python3 -m pytest tests/hardware/ -v"
```

### End-to-End Tests
```bash
pytest tests/e2e/ -v --tb=long
```

### Full Test Suite
```bash
# Local tests
pytest tests/ -v --tb=short --cov=[component] --cov-report=html

# Hardware tests (on Raspberry Pi)
ssh pi@192.168.0.18 "cd /opt/solar_heating_v3 && python3 -m pytest tests/hardware/ -v"
```

---

## 📊 Test Metrics & Reporting

### Coverage Goals
- **Overall Coverage:** 80%+
- **Critical Components:** 100%
- **Integration Points:** 100%

### Test Execution Metrics
- **Total Tests:** [Number]
- **Passing:** [Number]
- **Failing:** [Number]
- **Skipped:** [Number]

### Test Duration
- **Unit Tests:** [Expected duration]
- **Integration Tests:** [Expected duration]
- **Hardware Tests:** [Expected duration]
- **E2E Tests:** [Expected duration]

---

## ✅ Test Checklist

### Before Starting Implementation
- [ ] All test cases defined
- [ ] Test data prepared
- [ ] Mocks/fixtures created
- [ ] Test environment set up
- [ ] Tests reviewed by team

### During Implementation (TDD)
- [ ] Write failing test first
- [ ] Run test to verify it fails
- [ ] Implement minimum code to pass
- [ ] Run test to verify it passes
- [ ] Refactor while keeping tests green

### After Implementation
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All hardware tests passing on Raspberry Pi
- [ ] Edge cases covered
- [ ] Error scenarios covered
- [ ] Performance tests passing
- [ ] Code coverage meets goals
- [ ] Tests reviewed and approved

---

## 🐛 Known Issues & Limitations

### Test Limitation 1
**Issue:** [Description of limitation]  
**Impact:** [What this affects]  
**Workaround:** [How to work around it]

---

## 📚 References

### Testing Tools
- pytest: [Documentation link]
- pytest-cov: [Documentation link]
- [Other tools]

### Testing Best Practices
- [Reference 1]
- [Reference 2]

---

## 📝 Notes & Observations

**[Date] - [Author]:**  
[Notes about test design decisions, challenges, or insights]

---

## 🔄 Next Steps

1. [ ] Test plan review and approval
2. [ ] Create test files and fixtures
3. [ ] Write failing tests (TDD Red phase)
4. [ ] Hand off to @developer for implementation
5. [ ] Execute tests as code is written
6. [ ] Achieve all tests passing (TDD Green phase)

---

## ✅ Approval

**Reviewed by:** _______________  
**Approved by:** _______________  
**Date:** _______________

---

**Next Agent:** @developer  
**Hand-off Notes:** [Summary for developer - what tests are ready, what needs to be implemented, critical areas to focus on]

---

## 📋 Test Execution Log

### [Date] - Test Run 1
**Environment:** [Local | Raspberry Pi]  
**Results:** [Summary]  
**Issues Found:** [List]

### [Date] - Test Run 2
**Environment:** [Local | Raspberry Pi]  
**Results:** [Summary]  
**Issues Found:** [List]


