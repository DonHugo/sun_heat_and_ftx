# Multi-Agent Development System - Complete Guide

## 🎯 What Is This?

This project uses a **7-agent system** where specialized AI agents handle different aspects of software development. Think of it like having a complete development team where each member has a specific role.

## 🤖 Meet the Team

### Orchestration Layer (Manage & Improve)

#### @manager - The Project Manager
**Role:** Coordinates all agents and ensures nothing falls through the cracks

**Use when:**
- Starting complex features
- Not sure where to begin
- Want hands-free orchestration
- Need progress tracking

**Example:** `@manager I need to add email alerts for high temperature`

---

#### @coach - The Workflow Coach
**Role:** Makes your development process better over time

**Use when:**
- Workflow feels slow or clunky
- After completing major features (retrospectives)
- Want to optimize processes
- Learning how to use agents better

**Example:** `@coach Our testing workflow feels too slow, can you help?`

---

### Execution Layer (Build the Software)

#### @requirements - The Requirements Engineer
**Role:** Figures out exactly what you need before building anything

**Use when:**
- Starting new features
- Clarifying what you want
- Defining acceptance criteria

**Example:** `@requirements I want better sensor monitoring`

---

#### @architect - The System Architect
**Role:** Designs how the solution will work technically

**Use when:**
- Need technical design
- Making architecture decisions
- Reviewing system structure

**Example:** `@architect How should we structure the alert system?`

---

#### @tester - The Test Engineer
**Role:** Creates tests BEFORE code is written (TDD)

**Use when:**
- Need test specifications
- Planning test strategy
- Writing tests before coding

**Example:** `@tester Create tests for the email alert feature`

---

#### @developer - The Software Developer
**Role:** Writes code to make tests pass

**Use when:**
- Ready to implement
- Tests are already written
- Fixing bugs

**Example:** `@developer Implement the alert feature based on the tests`

---

#### @validator - The Quality Validator
**Role:** Verifies everything works on actual hardware

**Use when:**
- Ready to test on Raspberry Pi
- Need user acceptance testing
- Verifying production readiness

**Example:** `@validator Help me test the alerts on the Raspberry Pi`

---

## 🚀 How to Use

### Option 1: Let Manager Orchestrate (Recommended for Complex Tasks)

```bash
You: "@manager I want to add SMS notifications when power goes out"

Manager:
1. Creates project plan
2. Routes to @requirements (gathers needs)
3. Routes to @architect (designs solution)
4. Routes to @tester (writes tests)
5. Routes to @developer (implements code)
6. Routes to @validator (tests on hardware)
7. Ensures documentation updated
```

**Benefits:**
- Nothing gets skipped
- Progress is tracked
- Handoffs are smooth
- Documentation stays updated

---

### Option 2: Direct Agent Access (For Simple Tasks or When You Know What You Need)

```bash
You: "@requirements I want to add a temperature threshold setting"
     ↓
You: "@architect Here are the requirements..."
     ↓
You: "@tester Here's the architecture..."
     ↓
You: "@developer Here are the tests..."
     ↓
You: "@validator The implementation is ready..."
```

**When to use:** Simple changes, quick iterations, when you're comfortable managing handoffs

---

### Option 3: Workflow Improvement (Continuous Improvement)

```bash
You: "@coach After that last feature, the workflow felt slow. Can you analyze?"

Coach:
1. Analyzes your workflow
2. Identifies bottlenecks
3. Recommends improvements
4. Updates documentation
5. Trains you on better practices
```

**When to use:** After major features, when process feels inefficient, regular quarterly reviews

---

## 🎯 Quick Decision Guide

**I want to...**
- Build a complex new feature → `@manager`
- Improve our workflow → `@coach`
- Define what I need → `@requirements`
- Design a solution → `@architect`
- Write tests → `@tester`
- Write code → `@developer`
- Test on hardware → `@validator`
- I don't know where to start → Just ask! (acts as @manager by default)

---

## 📊 Workflows

### Full Feature Development (Manager-Orchestrated)

```
@manager
   ├─> @requirements  (What to build)
   ├─> @architect     (How to build it)
   ├─> @tester        (Tests to prove it works)
   ├─> @developer     (Build it)
   └─> @validator     (Verify it works)
```

**Timeline:** 2-4 hours (varies by complexity)

---

### Quick Bug Fix

```
@tester     (Write test that shows bug)
   ↓
@developer  (Fix bug to pass test)
   ↓
@validator  (Verify fix on hardware)
```

**Timeline:** 30-60 minutes

---

### Process Improvement

```
@coach
   ├─> Analyze current workflow
   ├─> Identify inefficiencies
   ├─> Recommend changes
   └─> Update documentation
```

**Timeline:** 1-2 hours

---

## 🎓 Best Practices

### 1. **Use Manager for Complex Work**
Let @manager handle multi-step features. It ensures quality and completeness.

### 2. **Don't Skip Agents**
Each agent adds value:
- Requirements prevent building wrong things
- Architecture prevents messy code
- Tests prevent bugs
- Development makes it real
- Validation proves it works

### 3. **Trust the Process**
TDD feels slower initially but saves time overall by preventing bugs and rework.

### 4. **Regular Retrospectives**
Use @coach after major features to continuously improve your workflow.

### 5. **Hardware Testing is Mandatory**
Always test on actual Raspberry Pi. Simulated tests aren't enough.

---

## 📁 Documentation

Each agent has a template:

- **Manager:** `python/v3/docs/agent_templates/MANAGER_TEMPLATE.md`
- **Coach:** `python/v3/docs/agent_templates/COACH_TEMPLATE.md`
- **Requirements:** `python/v3/docs/agent_templates/REQUIREMENTS_TEMPLATE.md`
- **Architecture:** `python/v3/docs/agent_templates/ARCHITECTURE_TEMPLATE.md`
- **Test Plan:** `python/v3/docs/agent_templates/TEST_PLAN_TEMPLATE.md`
- **Implementation:** `python/v3/docs/agent_templates/IMPLEMENTATION_TEMPLATE.md`
- **Validation:** (Coming soon - was recently deleted, needs recreation)

---

## 🔧 Configuration Files

The multi-agent system is configured in:

1. **`.cursorrules`** - Main agent definitions and workflows (used by Cursor IDE)
2. **`MULTI_AGENT_GUIDE.md`** - Detailed user guide with examples
3. **`agent.md`** - Legacy agent rules (being superseded by multi-agent system)

---

## 💡 Examples

### Example 1: Add New Feature (Complex)

```
You: "@manager I need to add a web dashboard for monitoring solar panel 
      performance with graphs and alerts"

Manager: "I'll orchestrate this complex feature. Here's the plan:

Phase 1: @requirements (30 min) - Define dashboard requirements
Phase 2: @architect (60 min) - Design frontend + backend architecture  
Phase 3: @tester (45 min) - Create test specifications
Phase 4: @developer (3-4 hours) - Implement dashboard
Phase 5: @validator (30 min) - Test on Raspberry Pi

Let's begin with @requirements..."
```

---

### Example 2: Quick Bug Fix (Simple)

```
You: "@tester The relay doesn't turn off when it should"

Tester: "I'll write a test that reproduces this bug..."
[Creates failing test]

You: "@developer Fix this bug"

Developer: "I've fixed the bug. The issue was..."
[Code fixed, test passes]

You: "@validator Verify on hardware"

Validator: "Run this command on your Raspberry Pi..."
[User tests, confirms fix]
```

---

### Example 3: Improve Workflow

```
You: "@coach I feel like we're writing too much documentation 
      and it's slowing us down"

Coach: "Let me analyze your current documentation workflow...

Observations:
- You're duplicating information across 3 documents
- 40% of documentation isn't being used
- Handoff notes could be streamlined

Recommendations:
1. Consolidate into single source of truth
2. Use templates for handoffs (saves 15 min each)
3. Auto-generate some docs from code

Would you like me to implement these changes?"
```

---

## 📈 Success Metrics

### You're Using the System Well When:

✅ Requirements are clear before coding  
✅ Tests are written before implementation  
✅ Architecture is documented  
✅ Hardware testing is on actual Raspberry Pi  
✅ No features break existing functionality  
✅ Documentation stays up to date  
✅ You feel confident in code quality

---

## 🆘 Troubleshooting

**"I don't know which agent to use"**
→ Just ask `@manager` or describe your need without specifying an agent

**"The workflow feels too slow"**
→ Ask `@coach` to analyze and streamline

**"Can I skip the requirements phase?"**
→ Only for very simple changes. When in doubt, don't skip.

**"Do I really need to write tests first?"**
→ Yes! TDD prevents bugs and serves as documentation. Trust the process.

**"How do I test hardware without the Raspberry Pi?"**
→ You can't. All hardware tests must run on actual device via SSH.

---

## 🔄 Evolution

This multi-agent system will evolve based on usage:

- New agents may be added (e.g., @deployer, @documenter)
- Workflows will be optimized based on @coach recommendations
- Templates will be refined
- Automation will increase

Keep `.cursorrules` updated as the system evolves.

---

## 📞 Quick Reference

```
┌─────────────────────────────────────────────────┐
│  AGENT QUICK REFERENCE                          │
├─────────────────────────────────────────────────┤
│  ORCHESTRATION:                                 │
│    @manager → Coordinate everything             │
│    @coach   → Improve workflows                 │
├─────────────────────────────────────────────────┤
│  EXECUTION:                                     │
│    @requirements → What to build                │
│    @architect    → How to build                 │
│    @tester       → Tests first (TDD)            │
│    @developer    → Build it                     │
│    @validator    → Verify it works              │
└─────────────────────────────────────────────────┘
```

**Start here:**
- Complex: `@manager [describe feature]`
- Simple: `@requirements [describe feature]`
- Improve: `@coach [describe issue]`

---

## 📚 Learn More

- **Detailed Guide:** `MULTI_AGENT_GUIDE.md`
- **Agent Rules:** `.cursorrules`
- **Templates:** `python/v3/docs/agent_templates/`
- **Legacy Rules:** `agent.md` (being phased out)

---

**Version:** 2.0  
**Last Updated:** 2025-10-30  
**Agents:** 7 (Manager, Coach, Requirements, Architect, Tester, Developer, Validator)


