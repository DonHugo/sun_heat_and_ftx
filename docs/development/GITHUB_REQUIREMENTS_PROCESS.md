# GitHub Requirements Tracking Process

**Date:** 2025-10-30  
**Purpose:** Define ongoing process for tracking requirements in GitHub  
**Version:** 1.0

---

## 🎯 Overview

This document defines how we track all requirements, features, bugs, and tasks using GitHub Issues, Projects, and Milestones.

### Key Principles
1. **Everything is tracked** - All requirements become GitHub issues
2. **Single source of truth** - GitHub is the authoritative source
3. **Always up to date** - Issues reflect current status
4. **Transparent** - Anyone can see what's being worked on
5. **Integrated** - Multi-agent workflow creates issues automatically

---

## 📋 When to Create a GitHub Issue

### ALWAYS Create an Issue For:
✅ **Bugs** - Anything that's broken or not working as expected  
✅ **Features** - New functionality or capabilities  
✅ **Enhancements** - Improvements to existing features  
✅ **Documentation** - Docs that need updating or creating  
✅ **Tests** - New tests or test improvements needed  
✅ **Security Issues** - Any security concerns  
✅ **Performance Problems** - System slowness or inefficiency  
✅ **Technical Debt** - Code that needs refactoring  

### DON'T Create an Issue For:
❌ **Questions** - Use Discussions instead  
❌ **Conversations** - Use Discussions or comments on existing issues  
❌ **Temporary experiments** - Document in notes, create issue if becomes requirement  
❌ **Duplicate work** - Search first, comment on existing issue  

---

## 🏗️ Multi-Agent Issue Creation Workflow

### When @requirements Agent Identifies a Requirement

**Process:**
1. **Document the requirement** in REQUIREMENTS_TEMPLATE.md
2. **Get user approval** for the requirement
3. **Create GitHub issue** automatically:
   ```
   @requirements creates:
   - Title: Clear, descriptive
   - Body: Complete requirement details
   - Labels: Appropriate labels applied
   - Milestone: Assigned if known
   - Project: Added to project board
   ```

### When @manager Coordinates Work

**Process:**
1. **Review existing issues** for the work needed
2. **Create issues if missing** for any gaps
3. **Link related issues** for traceability
4. **Update issue status** as work progresses
5. **Close issues** when work complete

### When @validator Finds Issues

**Process:**
1. **During validation**, if problems found:
2. **Create bug issue** with validation results
3. **Link to original feature issue**
4. **Assign priority** based on severity
5. **Route back** to @developer

---

## 📝 Issue Creation Guidelines

### Title Format

**Bugs:**
```
[BUG] Brief description of the problem
```

**Features:**
```
[FEATURE] What the feature does
```

**Enhancements:**
```
[ENHANCEMENT] What is being improved
```

**Documentation:**
```
[DOCS] What documentation is needed
```

**Tests:**
```
[TEST] What needs testing
```

### Example Titles
✅ Good:
- `[BUG] MQTT connection drops after 24 hours`
- `[FEATURE] Add mobile responsive dashboard`
- `[ENHANCEMENT] Improve sensor read performance by 50%`
- `[DOCS] Document API authentication process`
- `[TEST] Add integration tests for pump control`

❌ Bad:
- `Fix bug` (too vague)
- `New feature` (not descriptive)
- `Update docs` (which docs?)
- `Test stuff` (what stuff?)

### Issue Body Template

Use the appropriate template from `.github/ISSUE_TEMPLATE/`:
- `bug_report.md`
- `feature_request.md`
- `enhancement.md`
- `documentation.md`
- `testing.md`

---

## 🏷️ Label Application

### Required Labels (Choose One from Each Category)

**1. Type** (Required)
- `bug` OR `feature` OR `enhancement` OR `documentation` OR `testing`

**2. Priority** (Required)
- `priority: critical` OR `priority: high` OR `priority: medium` OR `priority: low`

**3. Component** (Required, can have multiple)
- `component: sensors`
- `component: mqtt`
- `component: watchdog`
- (see GITHUB_LABELS.md for full list)

### Optional Labels

**Status:**
- `status: needs-info` - More information needed
- `status: ready` - Ready to work on
- `status: in-progress` - Currently being worked on
- `status: blocked` - Blocked by something
- `status: review` - In code review
- `status: testing` - Being tested

**Category:**
- `category: security`
- `category: performance`
- `category: reliability`
- `category: usability`

**Special:**
- `good first issue` - Good for newcomers
- `help wanted` - Need help
- `breaking change` - Breaks compatibility

### Label Examples

**Critical Bug:**
```
bug, priority: critical, component: mqtt, category: security
```

**Medium Priority Feature:**
```
feature, priority: medium, component: gui, milestone: v3.2, status: ready
```

---

## 🎯 Milestone Assignment

### When to Assign Milestones

**Assign Immediately:**
- Critical and high-priority bugs → Current milestone (v3.1)
- Planned features → Appropriate future milestone (v3.2, v3.3)
- Security issues → Current milestone

**Assign Later:**
- Low priority items → Backlog first, assign milestone when prioritized
- Enhancements → Based on capacity and priority

### Milestone Guidelines

| Milestone | Types of Issues | Target Date |
|-----------|----------------|-------------|
| v3.1 | Critical bugs, high-priority fixes, urgent features | 2025-12-01 |
| v3.2 | Monitoring, recovery, performance | 2026-02-01 |
| v3.3 | Advanced features, analytics | 2026-04-01 |
| v4.0 | Major architectural changes | 2026-08-01 |
| Backlog | Not yet prioritized | N/A |

---

## 📊 GitHub Project Board

### Column Definitions

**1. Backlog**
- All new issues start here (unless urgent)
- Regularly reviewed for prioritization
- Groomed during planning sessions

**2. To Do**
- Issues ready to work on
- All information present
- Prioritized order (top = highest priority)
- Pull from here when starting work

**3. In Progress**
- Currently being worked on
- **Limit: Max 3 issues per person** (WIP limit)
- Update regularly with progress

**4. Review**
- Code complete, in code review
- Awaiting @reviewer or @validator
- Must pass review to proceed

**5. Testing**
- Being tested on Raspberry Pi hardware
- User acceptance testing
- Must pass all tests to proceed

**6. Done**
- Completed and verified
- Documented
- Deployed (if applicable)

### Moving Issues Through Board

**Automated:**
- New issues → Backlog
- Issue assigned → To Do
- PR created → In Progress
- PR merged → Testing
- Issue closed → Done

**Manual:**
- Backlog → To Do (when prioritized)
- To Do → In Progress (when starting)
- In Progress → Review (when code complete)
- Review → Testing (when review approved)
- Testing → Done (when validated)

---

## 🔄 Issue Lifecycle

### 1. Creation
```
New requirement identified
    ↓
Issue created with template
    ↓
Labels applied
    ↓
Milestone assigned (if known)
    ↓
Added to Project board → Backlog
```

### 2. Refinement
```
Issue in Backlog
    ↓
Reviewed in planning
    ↓
Priority assigned
    ↓
Information added
    ↓
Moved to To Do when ready
```

### 3. Development
```
Developer picks from To Do
    ↓
Moves to In Progress
    ↓
Work performed (TDD)
    ↓
PR created, linked to issue
    ↓
Moves to Review
```

### 4. Validation
```
Code review by @reviewer/@validator
    ↓
If approved → Moves to Testing
    ↓
Testing on Raspberry Pi
    ↓
If passes → Ready to close
```

### 5. Completion
```
All acceptance criteria met
    ↓
Documentation updated
    ↓
Issue closed with summary
    ↓
Moved to Done
```

---

## ✅ Issue Closure Checklist

Before closing an issue, verify:

**For Bugs:**
- [ ] Bug is fixed
- [ ] Fix tested on hardware
- [ ] No regression introduced
- [ ] Root cause documented
- [ ] Prevention measures implemented

**For Features:**
- [ ] All acceptance criteria met
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Validated by user
- [ ] No breaking changes (or documented)

**For Enhancements:**
- [ ] Improvement implemented
- [ ] Performance measured
- [ ] Tests updated
- [ ] Documentation updated

**For Documentation:**
- [ ] Documentation written
- [ ] Reviewed for accuracy
- [ ] Examples tested
- [ ] Links verified

**For Tests:**
- [ ] Tests written
- [ ] Tests passing
- [ ] Coverage improved
- [ ] Test documentation updated

---

## 🔍 Issue Search and Filtering

### Useful Filters

**By Status:**
```
is:open is:issue label:"status: ready"
is:open is:issue label:"status: blocked"
is:open is:issue no:milestone
```

**By Priority:**
```
is:open is:issue label:"priority: critical"
is:open is:issue label:"priority: high"
```

**By Component:**
```
is:open is:issue label:"component: mqtt"
is:open is:issue label:"component: sensors"
```

**By Milestone:**
```
is:open is:issue milestone:v3.1
is:open is:issue no:milestone
```

**Assigned to Me:**
```
is:open is:issue assignee:@me
```

**Recently Updated:**
```
is:issue updated:>2025-10-01
```

---

## 📈 Metrics and Reporting

### Weekly Metrics

Track:
- Issues created this week
- Issues closed this week
- Average time to close
- Open issues by priority
- Velocity (issues/week)

### Milestone Health

Monitor:
- % complete
- Days remaining
- Risk level (Red/Yellow/Green)
- Blockers
- Scope changes

### Quality Indicators

Watch for:
- Bug reopens (should be <5%)
- Time to first response (<24 hours)
- Stale issues (no update in 30 days)
- Documentation coverage

---

## 🤝 Integration with Multi-Agent Workflow

### Agent Responsibilities

**@requirements:**
- Creates issues for new requirements
- Ensures issue has all necessary information
- Links to requirement documents

**@manager:**
- Reviews and prioritizes issues
- Assigns to milestones
- Coordinates work across agents
- Tracks progress

**@architect:**
- Reviews technical feasibility
- Adds technical details to issues
- Links related architecture docs

**@tester:**
- Adds test scenarios to issues
- Creates test issues
- Validates acceptance criteria

**@developer:**
- Picks issues from "To Do"
- Updates status as work progresses
- Links PRs to issues
- Closes issues when complete

**@reviewer:**
- Reviews code for critical issues
- Provides feedback in issue comments
- Approves or requests changes

**@validator:**
- Validates on hardware
- Confirms acceptance criteria met
- Provides final approval

**@coach:**
- Reviews process effectiveness
- Suggests improvements
- Updates this document

---

## 🔄 Continuous Improvement

### Monthly Review

Review:
- Issue creation patterns
- Label usage
- Milestone progress
- Process bottlenecks
- Team feedback

Adjust:
- Label taxonomy
- Templates
- Workflow
- Automation

### Quarterly Review

Assess:
- Overall process effectiveness
- Milestone planning accuracy
- Issue quality
- Documentation completeness

Improve:
- Process documentation
- Agent integration
- Automation opportunities
- Team training

---

## 📚 Related Documentation

- **GITHUB_LABELS.md** - Complete label taxonomy
- **GITHUB_MILESTONES.md** - Milestone definitions
- **ISSUES_TO_CREATE.md** - Prepared issues ready to create
- **INITIAL_GITHUB_ISSUES.md** - Initial 13 issues planned
- **GITHUB_PROJECT_MANAGEMENT.md** - Project board setup
- **MULTI_AGENT_GUIDE.md** - Agent workflow integration

---

## 🎯 Quick Reference

### Create Issue
```bash
gh issue create --title "[TYPE] Description" --body "Details" --label "labels" --milestone "milestone"
```

### Update Issue
```bash
gh issue edit NUMBER --add-label "new-label"
gh issue edit NUMBER --milestone "v3.1"
```

### Close Issue
```bash
gh issue close NUMBER --comment "Closing because..."
```

### List Issues
```bash
gh issue list --label "priority: high"
gh issue list --milestone "v3.1"
```

---

**Process Owner:** @manager  
**Last Updated:** 2025-10-30  
**Version:** 1.0  
**Next Review:** 2025-11-30


