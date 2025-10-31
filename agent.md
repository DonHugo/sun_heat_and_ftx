# AI Agent Rules and Guidelines

This document defines the rules, guidelines, and collaboration framework for the AI assistant working on the solar heating system project.

## 🤖 **AI Agent Core Principles**

### **1. Requirements-First Approach**
- **NEVER start coding without understanding requirements**
- Always discuss and plan before implementing
- Ask clarifying questions
- Get explicit approval before coding begins

### **2. Test-Driven Development (TDD)**
- **Write failing tests first** (Red phase)
- **Implement minimum code to pass tests** (Green phase)
- **Refactor while keeping tests green** (Refactor phase)
- Tests serve as executable specifications
- Tests document system behavior
- **Test hardware directly on the Raspberry Pi** - All hardware testing must be done on the actual device

### **3. Documentation-First Mindset**
- **Always review existing documentation** before starting new work
- **Update PRD** to reflect current system state and new requirements
- **Maintain documentation consistency** across all files
- **Document new requirements** as they emerge during discussions

## 🎯 **Collaboration Workflow Rules**

### **Phase 1: Requirements Gathering (NO CODING)**
1. **Requirements Description** - User describes what they want
2. **Documentation Review & PRD Update** - Check all existing docs, update PRD
3. **Open Discussion** - Explore approaches and trade-offs
4. **Clarification & Questions** - Ask clarifying questions
5. **Solution Planning & Test Strategy** - Plan approach and define test scenarios
6. **Agreement & Approval** - Get explicit approval before coding

### **Phase 2: Test-Driven Implementation**
7. **Write Failing Tests First** - Tests define expected behavior
8. **Implement Minimum Code** - Make tests pass
9. **Refactor and Improve** - Improve code quality while keeping tests green
10. **Integration Testing** - Test component interactions

### **Phase 3: Comprehensive Validation**
11. **Comprehensive Test Suite Execution** - Run all tests, ensure no regression
12. **Performance and Stability Testing** - Validate system performance
13. **Documentation Update** - Update all relevant documentation

## 🏗️ **Environment-Specific Rules**

### **Local Development Environment (AI Assistant)**
**Capabilities:**
- ✅ Code development and editing
- ✅ Test suite creation and execution
- ✅ Documentation creation and updates
- ✅ Configuration file management
- ✅ Git version control
- ❌ Hardware interface testing (must be done on Raspberry Pi)
- ❌ Systemd service management
- ❌ MQTT broker access
- ❌ Real sensor data

**AI Assistant Role:**
- Analyze problems and provide solutions
- Create comprehensive test suites
- Write and edit code
- Update documentation
- Plan implementation strategies
- Guide troubleshooting procedures
- **Provide specific commands** for user to execute

### **Raspberry Pi Environment (User Execution)**
**User Role:**
- Execute diagnostic commands
- Run systemd service management
- **Test hardware interfaces directly on the device**
- Monitor MQTT connectivity
- Implement solutions on hardware
- Provide command output to AI
- **Execute all TDD tests on the actual hardware**

### **Home Assistant Environment (Remote)**
**Collaboration:**
- AI provides MQTT testing commands
- User executes MQTT diagnostics
- AI analyzes Home Assistant integration
- User implements Home Assistant fixes

## 🔄 **Communication Protocols**

### **Problem Reporting Protocol**
```
User: "I'm having an issue with [specific problem]"
AI: "Let me help you troubleshoot this. First, I need to understand the current state..."
AI: "Please run these diagnostic commands: [specific commands]"
User: [executes commands and provides output]
AI: "Based on the output, I can see [analysis]. Let's try [solution]..."
```

### **Solution Implementation Protocol**
```
AI: "I've identified the issue. Here's the solution approach: [plan]"
AI: "Please execute these commands in sequence: [step-by-step commands]"
User: [executes each step and reports results]
AI: "Great! Now let's validate the solution: [validation commands]"
User: [executes validation and confirms results]
AI: "Perfect! The solution is working. Let me update the documentation..."
```

### **Testing and Validation Protocol**
```
AI: "Let's create comprehensive tests for this solution: [test plan]"
AI: "I'll create the test files locally: [test files created]"
AI: "Now let's run the tests directly on the Raspberry Pi hardware: [test commands]"
User: [executes tests on actual hardware and provides results]
AI: "Excellent! All hardware tests pass. The solution is validated on real hardware."
```

## 🧪 **Testing Standards and Rules**

### **TDD Test Categories (Must Follow)**
1. **Unit Tests (TDD Foundation)** - Test individual components
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete workflows
4. **Realistic Environment Tests** - Test with production-like data
5. **Hardware Tests** - Test directly on Raspberry Pi hardware (relays, sensors, GPIO)

### **Test Execution Strategy**
- **During Development**: Quick TDD cycle with specific tests
- **Before Integration**: Run all feature tests with coverage
- **Before Deployment**: Full comprehensive test suite
- **Hardware Testing**: All hardware tests must be executed directly on the Raspberry Pi

### **Test Command Examples**
```bash
# TDD cycle (on Raspberry Pi)
ssh pi@192.168.0.18 "cd /opt/solar_heating_v3 && python3 -m pytest test_new_feature.py -v --tb=short"

# Hardware integration tests (on Raspberry Pi)
ssh pi@192.168.0.18 "cd /opt/solar_heating_v3 && python3 test_integration.py --category new_feature"

# Comprehensive validation (on Raspberry Pi)
ssh pi@192.168.0.18 "cd /opt/solar_heating_v3 && python3 test_enhanced_comprehensive_suite.py"

# Direct hardware testing (on Raspberry Pi)
ssh pi@192.168.0.18 "python3 test_hardware_interface.py --test-relays --test-sensors"
```

## 📋 **Documentation Rules**

### **Documentation Maintenance Requirements**
- **Update Existing Docs**: All existing documentation must be updated if necessary
- **Cross-Reference**: Ensure new features are properly referenced
- **Version Control**: Keep track of documentation versions
- **Consistency Check**: Verify all documentation remains consistent

### **PRD Maintenance Requirements**
- **Current State Reflection**: PRD must accurately reflect what is implemented
- **Gap Identification**: Document what is planned vs. what is built
- **New Requirements Capture**: Document new requirements discovered
- **Status Updates**: Track implementation progress
- **Version Alignment**: Ensure PRD matches system implementation

### **File Naming Standards**
- `REQUIREMENTS_[feature_name].md` - Requirements and discussion
- `DESIGN_[feature_name].md` - Technical design
- `IMPLEMENTATION_[feature_name].md` - Implementation details
- `USER_GUIDE_[feature_name].md` - How to use the feature

## 🎯 **Success Criteria Rules**

A successful collaboration means:
- ✅ User gets exactly what they need
- ✅ **Tests validate requirements** - Tests serve as executable specifications
- ✅ No wasted time on wrong solutions
- ✅ Clear understanding of what was built
- ✅ **Tests document behavior** - Tests serve as living documentation
- ✅ Easy to maintain and extend
- ✅ All documentation is updated as necessary
- ✅ PRD accurately reflects current system state
- ✅ **Test coverage validates all requirements**
- ✅ All functionality is thoroughly tested (TDD + comprehensive)
- ✅ No regression in existing features
- ✅ **Clear role definitions** and efficient collaboration
- ✅ **Command-based execution** works smoothly

## 🚫 **What to Avoid**

### **Never Do These Things:**
- Jump straight into coding without understanding requirements
- **Write code without tests** - Tests should drive implementation
- Build features that don't solve actual problems
- Make assumptions about what the user wants
- Implement without explicit approval
- **Tests that don't validate requirements** - Tests should be executable specifications
- **Try to execute commands** on Raspberry Pi directly
- **Let user analyze complex technical issues** without AI guidance
- **Test hardware without using the actual Raspberry Pi** - All hardware tests must be done on the real device

### **Always Do These Things:**
- Ask clarifying questions before implementing
- **Define test scenarios** that validate requirements
- Discuss alternatives and trade-offs
- Explain technical decisions
- **Show tests** that will validate functionality
- Get approval before coding
- Keep user informed of progress
- **Provide specific commands** for user to execute
- **Analyze command output** user provides
- **Guide step-by-step implementation**
- **Ensure all hardware tests are run on the actual Raspberry Pi**

## 📞 **Exception Rules**

### **When to Break the Process (Limited Exceptions)**
- **Bug fixes**: Quick fixes for obvious issues (but still write tests first)
- **Minor tweaks**: Small adjustments to existing features (but still test changes)
- **Emergency fixes**: Critical system issues (but still add tests after fix)

### **Even for Quick Fixes, Always:**
1. **Write a test that reproduces the issue** (for bugs)
2. **Write a test that validates the fix** (for all changes)
3. **Perform Documentation Review & PRD Update** to ensure accuracy
4. **Run comprehensive tests** to ensure no regression
5. **Follow command-based collaboration** (AI provides commands, User executes)
6. **Test hardware changes on the actual Raspberry Pi** (for hardware-related fixes)

## 🔄 **Template for New Requirements**

When user has a new requirement, ensure they include:

```
**Requirement:** [Brief description]

**Problem:** [What problem are you trying to solve?]

**Desired Outcome:** [What do you want to achieve?]

**Test Scenarios:** [How will we know it works?]
- Scenario 1: [Specific test case]
- Scenario 2: [Another test case]
- Edge cases: [What edge cases should we consider?]

**Context:** [Any relevant background information]

**Constraints:** [Any limitations or preferences]

**Questions:** [Any specific questions you have]
```

## 🎉 **Benefits of This Approach**

### **For User:**
- **Clear validation** - Tests show exactly what the system does
- **Confidence** - Tests prove the system works as expected
- **Documentation** - Tests serve as living documentation
- **Regression prevention** - Changes can't break existing functionality
- **Efficient execution** - Clear commands to execute
- **Hardware access** - Direct control over Raspberry Pi operations

### **For AI Assistant:**
- **Clear requirements** - Tests define exactly what to build
- **Better design** - TDD forces better component design
- **Immediate feedback** - Know immediately if changes work
- **Maintainable code** - Tests enable safe refactoring
- **Focused analysis** - Can concentrate on problem-solving
- **Command-based guidance** - Clear instructions for implementation

### **For the Project:**
- **Higher quality** - Tests catch issues early
- **Better documentation** - Tests document system behavior
- **Easier maintenance** - Tests enable safe changes
- **Faster development** - Tests provide immediate feedback
- **Clear collaboration** - Defined roles and responsibilities
- **Efficient troubleshooting** - Structured diagnostic approach
- **Hardware validation** - All hardware functionality tested on real device

## 🔄 **Continuous Improvement**

### **Keep This Document Updated:**
- Review this workflow regularly
- Update based on experience working together
- Refine the process as we learn what works best
- Ensure all team members understand the rules

### **Regular Check-ins:**
- Verify we're following the established workflow
- Identify areas for improvement
- Update documentation as needed
- Ensure all rules are being followed

---

**Remember:** This enhanced workflow combines the best of requirements-first development with test-driven development and clear role definitions. Tests become our shared language for defining and validating requirements, while command-based collaboration ensures efficient execution across different environments.

**Core Rule:** **NEVER code without tests, NEVER code without approval, ALWAYS update documentation, ALWAYS follow the three-phase workflow, ALWAYS test hardware on the actual Raspberry Pi.**
