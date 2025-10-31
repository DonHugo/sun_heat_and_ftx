# Project Plan: [Feature/Task Name]

**Date:** [YYYY-MM-DD]  
**Status:** [Planning | In Progress | Completed]  
**Agent:** @manager  
**Project Owner:** [Your name]  
**Priority:** [Critical | High | Medium | Low]

---

## 📋 Overall Goal

### User Request
[Original user request - what they want to achieve]

### Project Objective
[Clear, specific objective this project will achieve]

### Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## 🗺️ Project Plan

### Phases

#### Phase 1: Requirements Gathering
**Agent:** @requirements  
**Duration:** [Estimated time]  
**Status:** ⏳ Pending | 🔄 In Progress | ✅ Complete

**Tasks:**
- [ ] Gather and document requirements
- [ ] Clarify user needs
- [ ] Define acceptance criteria
- [ ] Create test scenarios
- [ ] Get user approval

**Deliverables:**
- Requirements document
- Test scenarios
- Updated PRD

**Notes:** [Any specific considerations for requirements phase]

---

#### Phase 2: Architecture Design
**Agent:** @architect  
**Duration:** [Estimated time]  
**Status:** ⏳ Pending | 🔄 In Progress | ✅ Complete

**Tasks:**
- [ ] Review requirements
- [ ] Design system architecture
- [ ] Define component interactions
- [ ] Choose technologies
- [ ] Plan data flow
- [ ] Document design decisions
- [ ] Get approval

**Deliverables:**
- Architecture document
- Component diagrams
- Technology choices
- Integration plan

**Dependencies:**
- Requires: Phase 1 (Requirements) complete

**Notes:** [Any specific considerations for architecture phase]

---

#### Phase 3: Test Specification
**Agent:** @tester  
**Duration:** [Estimated time]  
**Status:** ⏳ Pending | 🔄 In Progress | ✅ Complete

**Tasks:**
- [ ] Review requirements and architecture
- [ ] Design test strategy
- [ ] Write unit test specifications
- [ ] Write integration test specifications
- [ ] Define hardware test procedures
- [ ] Create test fixtures and mocks
- [ ] Write failing tests (TDD Red phase)

**Deliverables:**
- Test plan document
- Failing test suite
- Test fixtures
- Hardware test procedures

**Dependencies:**
- Requires: Phase 2 (Architecture) complete

**Notes:** [Any specific considerations for testing phase]

---

#### Phase 4: Implementation
**Agent:** @developer  
**Duration:** [Estimated time]  
**Status:** ⏳ Pending | 🔄 In Progress | ✅ Complete

**Tasks:**
- [ ] Review requirements, architecture, and tests
- [ ] Implement code to pass tests (TDD Green phase)
- [ ] Refactor for quality
- [ ] Add error handling
- [ ] Add logging
- [ ] Document code
- [ ] Run all tests
- [ ] Verify no regressions

**Deliverables:**
- Working code
- Passing tests
- Code documentation
- Implementation notes

**Dependencies:**
- Requires: Phase 3 (Test Specs) complete

**Notes:** [Any specific considerations for implementation phase]

---

#### Phase 5: Validation
**Agent:** @validator  
**Duration:** [Estimated time]  
**Status:** ⏳ Pending | 🔄 In Progress | ✅ Complete

**Tasks:**
- [ ] Review original requirements
- [ ] Create acceptance test procedures
- [ ] Test on actual Raspberry Pi hardware
- [ ] Verify all acceptance criteria
- [ ] Document any issues
- [ ] Get user approval

**Deliverables:**
- Validation report
- Test results from hardware
- User approval
- Final documentation

**Dependencies:**
- Requires: Phase 4 (Implementation) complete

**Notes:** [Any specific considerations for validation phase]

---

## 📊 Progress Tracking

### Overall Status
**Current Phase:** [Phase name]  
**Overall Progress:** [X]% complete

| Phase | Status | Start Date | End Date | Notes |
|-------|--------|------------|----------|-------|
| Requirements | ⏳/🔄/✅ | [Date] | [Date] | [Notes] |
| Architecture | ⏳/🔄/✅ | [Date] | [Date] | [Notes] |
| Test Specs | ⏳/🔄/✅ | [Date] | [Date] | [Notes] |
| Implementation | ⏳/🔄/✅ | [Date] | [Date] | [Notes] |
| Validation | ⏳/🔄/✅ | [Date] | [Date] | [Notes] |

### Completed Milestones
- [x] Milestone 1: [Description] - [Date]
- [ ] Milestone 2: [Description] - [Target date]
- [ ] Milestone 3: [Description] - [Target date]

---

## 🔄 Agent Handoffs

### Current Handoff

**From:** @[previous-agent]  
**To:** @[next-agent]  
**Date:** [Date]

**Context for Next Agent:**
[Summary of what has been completed and what the next agent needs to know]

**Key Information:**
- [Important point 1]
- [Important point 2]
- [Important point 3]

**Questions/Clarifications:**
- [Question 1]
- [Question 2]

---

### Handoff History

#### Handoff 1: Manager → Requirements
**Date:** [Date]  
**Summary:** [What was communicated]

#### Handoff 2: Requirements → Architect
**Date:** [Date]  
**Summary:** [What was communicated]

#### Handoff 3: Architect → Tester
**Date:** [Date]  
**Summary:** [What was communicated]

[Continue for each handoff...]

---

## 🚧 Risks & Issues

### Active Risks
| Risk | Severity | Probability | Mitigation | Status |
|------|----------|-------------|------------|--------|
| [Risk 1] | High/Med/Low | High/Med/Low | [Mitigation strategy] | Active/Resolved |
| [Risk 2] | High/Med/Low | High/Med/Low | [Mitigation strategy] | Active/Resolved |

### Active Issues
| Issue | Severity | Assigned To | Status | Resolution |
|-------|----------|-------------|--------|------------|
| [Issue 1] | High/Med/Low | @[agent] | Open/Resolved | [Resolution] |
| [Issue 2] | High/Med/Low | @[agent] | Open/Resolved | [Resolution] |

---

## 📝 Documentation Status

### Documentation Checklist
- [ ] Requirements document created/updated
- [ ] Architecture document created/updated
- [ ] Test plan created/updated
- [ ] Implementation notes documented
- [ ] Validation report created
- [ ] PRD updated
- [ ] README updated (if needed)
- [ ] User guide updated (if needed)

### Documentation Links
- **Requirements:** [Link]
- **Architecture:** [Link]
- **Test Plan:** [Link]
- **Implementation:** [Link]
- **Validation:** [Link]

---

## 🎯 Quality Gates

### Gate 1: Requirements Approved
- [ ] Requirements are clear and complete
- [ ] User has approved requirements
- [ ] Test scenarios defined
- [ ] PRD updated

**Status:** ⏳ Pending | ✅ Passed | ❌ Failed

---

### Gate 2: Architecture Approved
- [ ] Architecture addresses all requirements
- [ ] Technology choices justified
- [ ] Integration points defined
- [ ] Testing strategy clear

**Status:** ⏳ Pending | ✅ Passed | ❌ Failed

---

### Gate 3: Tests Written
- [ ] All test specifications written
- [ ] Tests are failing (TDD Red)
- [ ] Test coverage is comprehensive
- [ ] Hardware test procedures defined

**Status:** ⏳ Pending | ✅ Passed | ❌ Failed

---

### Gate 4: Implementation Complete
- [ ] All tests passing (TDD Green)
- [ ] Code is refactored and clean
- [ ] No regressions
- [ ] Code documented

**Status:** ⏳ Pending | ✅ Passed | ❌ Failed

---

### Gate 5: Validation Complete
- [ ] All acceptance criteria met
- [ ] Hardware testing successful
- [ ] User has approved
- [ ] Documentation complete

**Status:** ⏳ Pending | ✅ Passed | ❌ Failed

---

## 🔍 Scope Management

### In Scope
- [Item 1]
- [Item 2]
- [Item 3]

### Out of Scope
- [Item 1]
- [Item 2]

### Scope Changes
| Change | Date | Reason | Approved By | Impact |
|--------|------|--------|-------------|--------|
| [Change 1] | [Date] | [Reason] | [Name] | [Impact] |

---

## 💬 Communications Log

### Meeting/Discussion 1
**Date:** [Date]  
**Participants:** [Names]  
**Topic:** [Topic]  
**Decisions:** [Key decisions made]  
**Action Items:**
- [ ] Action 1 - Assigned to: [Name]
- [ ] Action 2 - Assigned to: [Name]

---

## 📈 Metrics

### Time Tracking
- **Estimated Total Time:** [Hours]
- **Actual Time Spent:** [Hours]
- **Variance:** [+/- Hours]

### Velocity
- **Planned Features:** [Number]
- **Completed Features:** [Number]
- **Completion Rate:** [Percentage]

### Quality Metrics
- **Test Coverage:** [Percentage]
- **Tests Passing:** [X/Y]
- **Issues Found:** [Number]
- **Issues Resolved:** [Number]

---

## ✅ Project Completion Checklist

### Pre-Deployment
- [ ] All phases complete
- [ ] All quality gates passed
- [ ] All tests passing
- [ ] Hardware tested on Raspberry Pi
- [ ] User approval received
- [ ] Documentation complete

### Deployment
- [ ] Deployment plan created
- [ ] Backup completed
- [ ] Code deployed
- [ ] Services restarted
- [ ] Smoke tests passed

### Post-Deployment
- [ ] Monitoring in place
- [ ] User notified
- [ ] Team notified
- [ ] Retrospective scheduled

---

## 🎓 Lessons Learned

### What Went Well
- [Lesson 1]
- [Lesson 2]

### What Could Be Improved
- [Improvement 1]
- [Improvement 2]

### Action Items for Future Projects
- [ ] Action 1
- [ ] Action 2

---

## 📋 Next Steps

**Immediate Next Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Next Agent:** @[agent-name]

**Handoff Notes:**
[Summary of current state and what the next agent needs to do]

---

## ✅ Sign-Off

**Project Manager:** _______________  
**Date:** _______________

**User Acceptance:** _______________  
**Date:** _______________

---

**Project Status:** ⏳ Planning | 🔄 In Progress | ✅ Completed | ❌ Cancelled


