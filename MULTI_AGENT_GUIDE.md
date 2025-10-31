# Multi-Agent Development System - Quick Start Guide

## 🎯 Overview

This project uses a **multi-agent approach** where different AI agents specialize in different aspects of the development lifecycle. Each agent has specific responsibilities and works together in a coordinated workflow.

## 🤖 The Eight Agents

| Agent | Primary Role | When to Use |
|-------|-------------|-------------|
| **@manager** | Project Manager | Orchestrating complex workflows, coordinating agents |
| **@coach** | Workflow Coach | Improving processes, optimizing workflows |
| **@requirements** | Requirements Engineer | Starting new features, clarifying needs |
| **@architect** | System Architect | Designing solutions, technical decisions |
| **@tester** | Test Engineer | Writing test specs, test strategy |
| **@developer** | Software Developer | Implementing code, fixing bugs |
| **@reviewer** | Code Reviewer (Optional) | Deep code review for critical features |
| **@validator** | Quality Validator | Code review + hardware validation |

## 🚀 Quick Start Examples

### Example 0: Let Manager Orchestrate (Recommended for Complex Features)

```
You: "@manager I want to add a feature that sends me an email alert 
      when the solar panel temperature exceeds 90°C"

Manager Agent:
- Analyzes the request
- Creates project plan
- Routes to @requirements → @architect → @tester → @developer → @validator
- Tracks progress through each phase
- Ensures nothing is skipped
- Updates documentation
- Confirms completion
```

### Example 1: New Feature Development (Direct Agent Access)

```
You: "@requirements I want to add a feature that sends me an email alert 
      when the solar panel temperature exceeds 90°C"

Requirements Agent:
- Asks clarifying questions
- Documents the requirement
- Creates acceptance criteria
- Hands off to @architect

You: "@architect Here are the requirements..."

Architect Agent:
- Designs the solution
- Plans component interactions
- Chooses email library
- Hands off to @tester

You: "@tester Here's the architecture..."

Tester Agent:
- Writes failing test specifications
- Defines test scenarios
- Hands off to @developer

You: "@developer Here are the tests..."

Developer Agent:
- Implements code to pass tests
- Refactors and improves
- Hands off to @validator

You: "@validator The implementation is complete..."

Validator Agent:
- Creates validation procedures
- Provides commands to test on Raspberry Pi
- Confirms feature meets requirements
```

### Example 2: Bug Fix

```
You: "@tester There's a bug - the relay doesn't turn off when temperature 
      drops below threshold"

Tester Agent:
- Writes test that reproduces the bug
- Defines expected behavior
- Hands off to @developer

You: "@developer Here's the failing test..."

Developer Agent:
- Fixes the bug
- Ensures test passes
- Runs regression tests
- Hands off to @validator

You: "@validator The bug is fixed..."

Validator Agent:
- Provides test commands for Raspberry Pi
- Verifies fix works on hardware
- Confirms no side effects
```

### Example 3: Architecture Review

```
You: "@architect I'm concerned about the system's reliability. 
      Can you review the current architecture and suggest improvements?"

Architect Agent:
- Reviews existing system
- Identifies weaknesses
- Proposes improvements
- Documents trade-offs
- Gets your approval
- Hands off to other agents as needed
```

### Example 4: Workflow Improvement

```
You: "@coach Our current development workflow feels slow, and I think 
      we're duplicating work between agents. Can you help?"

Coach Agent:
- Analyzes current workflow
- Identifies bottlenecks (e.g., too much back-and-forth between agents)
- Spots duplication (e.g., multiple agents writing similar docs)
- Recommends specific improvements
- Updates workflow documentation
- Suggests better practices
```

## 📋 How to Use Each Agent

### Using @manager

**Best for:**
- Complex multi-step features
- When you're not sure which agent to start with
- Coordinating work across multiple agents
- Tracking progress on large tasks
- Ensuring nothing gets skipped

**How to invoke:**
```
"@manager [describe your overall goal]"
```

**Example prompts:**
- "@manager I need to add a complete dashboard for monitoring solar energy"
- "@manager We need to refactor the entire sensor system for better reliability"
- "@manager Help me plan and execute a major system upgrade"

**What Manager Does:**
1. Understands your overall goal
2. Creates a project plan
3. Routes work to appropriate agents in order
4. Tracks progress and handoffs
5. Ensures documentation is updated
6. Verifies completion

---

### Using @coach

**Best for:**
- Workflow feels inefficient
- Agents are duplicating work
- Process improvements needed
- Learning better ways to use agents
- Retrospectives after major features
- Optimizing team productivity

**How to invoke:**
```
"@coach [describe the workflow issue]"
```

**Example prompts:**
- "@coach Our testing workflow is too slow. How can we improve it?"
- "@coach I feel like we're writing too much documentation. Can you streamline?"
- "@coach The handoffs between agents are confusing. Help!"
- "@coach After completing the last feature, what can we do better next time?"

**What Coach Does:**
1. Observes current workflows
2. Identifies inefficiencies
3. Recommends specific improvements
4. Updates process documentation
5. Trains you on better practices
6. Evolves the multi-agent system

---

### Using @requirements

**Best for:**
- Starting new features
- Clarifying what you want
- Documenting user needs
- Creating acceptance criteria

**How to invoke:**
```
"@requirements [describe what you want]"
```

**Example prompts:**
- "@requirements I need better error handling for sensor failures"
- "@requirements What should we consider for mobile app integration?"
- "@requirements Help me document the requirements for energy reporting"

### Using @architect

**Best for:**
- System design decisions
- Technology choices
- Component planning
- Architecture reviews

**How to invoke:**
```
"@architect [describe the design challenge]"
```

**Example prompts:**
- "@architect How should we structure the data pipeline for sensor readings?"
- "@architect What's the best way to handle MQTT reconnection logic?"
- "@architect Review the current watchdog system and suggest improvements"

### Using @tester

**Best for:**
- Test strategy planning
- Writing test specifications (before coding!)
- Defining test scenarios
- Ensuring coverage

**How to invoke:**
```
"@tester [describe what needs testing]"
```

**Example prompts:**
- "@tester Create comprehensive tests for the relay control logic"
- "@tester What edge cases should we test for temperature sensors?"
- "@tester Design integration tests for MQTT communication"

### Using @developer

**Best for:**
- Implementing features
- Writing code
- Refactoring
- Bug fixes

**How to invoke:**
```
"@developer [describe what to implement]"
```

**Example prompts:**
- "@developer Implement the email alert feature based on these tests"
- "@developer Refactor the SensorManager class for better error handling"
- "@developer Fix the bug in relay timing logic"

**Important:** Developer agent should ONLY code when:
- Requirements are clear
- Architecture is defined
- Tests are already written (TDD!)

### Using @reviewer

**Best for:**
- Critical system changes (main_system.py, watchdog)
- Security-sensitive features
- Complex algorithms
- Major refactoring
- When you need deep independent review

**How to invoke:**
```
"@reviewer [describe what to review]"
```

**Example prompts:**
- "@reviewer Review this authentication implementation for security issues"
- "@reviewer Check if this refactoring maintains architectural integrity"
- "@reviewer Deep review of the new sensor algorithm for correctness and performance"

**What Reviewer Does:**
1. Deep architecture compliance verification
2. Comprehensive security analysis
3. Performance optimization review
4. Code quality assessment
5. Best practices enforcement
6. Provides detailed feedback

**Note:** @reviewer is OPTIONAL. Most features use only @validator's built-in code review. Use @reviewer when you need extra scrutiny for critical features.

---

### Using @validator

**Best for:**
- ALL features (two-phase validation)
- Code review before hardware testing
- User acceptance testing
- Hardware validation on Raspberry Pi
- Production readiness checks

**How to invoke:**
```
"@validator [describe what to validate]"
```

**Example prompts:**
- "@validator Review and test the new alert system"
- "@validator Verify the relay control implementation and test on hardware"
- "@validator Validate the energy reporting feature meets requirements"

**What Validator Does (Two Phases):**

**Phase 1: Code Review**
1. Verify architecture compliance
2. Check code quality
3. Review error handling
4. Assess logging
5. Check best practices
6. Approve for hardware testing

**Phase 2: Hardware Validation**
1. Create test procedures for Raspberry Pi
2. Provide SSH commands to run
3. Analyze test results
4. Verify acceptance criteria
5. Get final user approval

**When to use @reviewer vs @validator:**
- **@validator (always)**: Validates ALL features with code review + hardware testing
- **@reviewer (optional)**: Adds deeper review for CRITICAL features only
- **Flow:** @developer → [@reviewer] → @validator → Done

## 🔄 Standard Workflows

### Manager-Orchestrated Feature Development (Recommended)

**Standard Features (90%):**
```
@manager → coordinates all agents automatically
  ├─> @requirements → gather & document
  ├─> @architect → design solution
  ├─> @tester → write test specs
  ├─> @developer → implement code (with self-review checklist)
  └─> @validator → TWO-PHASE validation:
       ├─> Phase 1: Code review
       └─> Phase 2: Hardware testing
```

**Critical Features (10%):**
```
@manager → flags as critical, coordinates agents
  ├─> @requirements → gather & document
  ├─> @architect → design solution
  ├─> @tester → write test specs
  ├─> @developer → implement code (with self-review checklist)
  ├─> @reviewer → deep independent code review
  └─> @validator → TWO-PHASE validation:
       ├─> Phase 1: Code review (lighter, since @reviewer did deep review)
       └─> Phase 2: Hardware testing
```

**Benefits:**
- Manager ensures no steps are skipped
- Automatic progress tracking
- Better coordination between agents
- Clear project plan from the start
- Code review catches issues before hardware testing

**Timeline example:**
1. Manager planning (5-10 min)
2. Requirements (15-30 min discussion)
3. Architecture (30-60 min design)
4. Test specs (30-45 min writing tests)
5. Development with self-review (varies by complexity)
6. Code Review by @reviewer (10-20 min for critical features only)
7. Validation Phase 1: Code review (5-10 min)
8. Validation Phase 2: Hardware testing (15-30 min)

---

### Complete Feature Development (Direct Agent Access)

```
@requirements → @architect → @tester → @developer → @validator
```

**When to use:** When you're comfortable managing handoffs yourself

**Timeline example:**
1. Requirements (15-30 min discussion)
2. Architecture (30-60 min design)
3. Test specs (30-45 min writing tests)
4. Development (varies by complexity)
5. Validation (15-30 min testing)

---

### Quick Change/Bug Fix

```
@requirements (quick) → @tester → @developer → @validator (quick)
```

**Or with Manager:**
```
@manager → quick plan → @tester → @developer → @validator
```

---

### Architecture Improvement

```
@architect → @requirements (update) → @tester → @developer → @validator
```

---

### Workflow Improvement

```
@coach → analyze → recommend → update documentation → implement changes
```

**When to use:**
- After completing major features (retrospective)
- When workflow feels inefficient
- Regular quarterly reviews

---

### Emergency Fix

```
@developer (with immediate test) → @validator (quick verify)
```
*Note: Still write tests, but may code first in emergencies. Document as tech debt.*

## 💡 Tips for Effective Agent Use

### 1. **Be Clear About Which Agent You Need**

❌ Bad: "I want to add a new feature"
✅ Good: "@requirements I want to add a new feature for [description]"

### 2. **Let Agents Complete Their Work**

Don't rush through agents. Each agent's work is valuable:
- Requirements prevent building wrong things
- Architecture prevents messy code
- Tests prevent bugs
- Development makes it real
- Validation proves it works

### 3. **Trust the Process**

The multi-agent approach may feel slower initially, but it:
- Reduces rework
- Catches issues early
- Produces better quality
- Makes maintenance easier

### 4. **Ask Agents for Help**

Agents can help you understand their domain:
- "@requirements What questions should I be asking about this feature?"
- "@architect What are the trade-offs of this approach?"
- "@tester What test scenarios am I missing?"
- "@developer What's the cleanest way to implement this?"
- "@validator How should I validate this on the hardware?"

### 5. **Use Multiple Agents in One Session**

You can work with multiple agents in sequence:
```
"Let's develop a new feature. Start with @requirements to gather needs,
then @architect for design, then @tester for tests, and @developer for
implementation."
```

## 📁 Project-Specific Context

All agents understand your project context:

**System:** Solar heating control system
**Hardware:** Raspberry Pi 4 with relays and temperature sensors
**Key Technologies:** Python, MQTT, systemd, Home Assistant
**Current Location:** `/opt/solar_heating_v3` on Raspberry Pi
**Access:** SSH via `ssh pi@192.168.0.18`

**Important Constraints:**
- All hardware testing must be done on actual Raspberry Pi
- Real-time requirements for sensor monitoring
- Service must be reliable (systemd + watchdog)
- Integration with Home Assistant via MQTT

## 🎓 Learning From Agents

Each agent not only does work but also teaches:

- **@requirements** teaches you to think about user needs first
- **@architect** teaches you system design principles
- **@tester** teaches you to think about edge cases and validation
- **@developer** teaches you clean code practices
- **@validator** teaches you to verify assumptions

## 🔧 Customizing Agent Behavior

If you need an agent to focus on something specific:

```
"@architect Focus on performance and scalability when designing this"
"@tester Prioritize hardware integration tests for this feature"
"@developer Use async/await for this implementation"
```

## 📞 Getting Help

If you're unsure which agent to use:

```
"Which agent should I use for [task]?"
```

Or just describe your need, and the system will suggest the right agent.

## 🎯 Success Metrics

You're using the multi-agent system effectively when:

✅ Requirements are clear before coding starts
✅ Tests are written before implementation
✅ Architecture is documented and agreed upon
✅ Code changes don't break existing features
✅ Features work correctly on actual hardware
✅ Documentation stays up to date
✅ You feel confident in the quality of the work

## 🚫 Common Mistakes to Avoid

❌ **Skipping directly to @developer** without requirements, architecture, or tests
❌ **Not running tests on actual Raspberry Pi** hardware
❌ **Rushing through agent workflows** to "save time"
❌ **Ignoring agent questions** or clarifications
❌ **Not updating documentation** as work progresses

## 📈 Evolution

This multi-agent system will evolve as you use it:

- Agent roles may be refined
- New agents might be added (e.g., @deployer, @documenter)
- Workflows may be optimized
- Project-specific patterns will emerge

Keep the `.cursorrules` file updated based on what works best for your project.

---

## Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  MULTI-AGENT QUICK REFERENCE (8 Agents)                 │
├──────────────────────────────────────────────────────────┤
│  ORCHESTRATION AGENTS:                                   │
│  @manager      → Orchestrate workflows, coordinate       │
│  @coach        → Improve workflows, optimize process     │
├──────────────────────────────────────────────────────────┤
│  EXECUTION AGENTS:                                       │
│  @requirements → Requirements gathering & docs           │
│  @architect    → System design & tech decisions          │
│  @tester       → Test strategy & specifications          │
│  @developer    → Code implementation (with checklist)    │
│  @reviewer     → Deep code review (critical only)        │
│  @validator    → Code review + hardware validation       │
├──────────────────────────────────────────────────────────┤
│  Recommended Flow (Manager-Orchestrated):                │
│  Standard (90%):                                         │
│  manager → requirements → architect → tester →           │
│  developer → validator (2 phases)                        │
│                                                          │
│  Critical (10%):                                         │
│  manager → requirements → architect → tester →           │
│  developer → reviewer → validator (2 phases)             │
├──────────────────────────────────────────────────────────┤
│  Direct Flow (You Coordinate):                           │
│  requirements → architect → tester →                     │
│  developer → [reviewer] → validator                      │
├──────────────────────────────────────────────────────────┤
│  Validation (Two Phases):                                │
│  Phase 1: Code Review → Approve for hardware            │
│  Phase 2: Hardware Testing → Final approval              │
├──────────────────────────────────────────────────────────┤
│  Continuous Improvement:                                 │
│  coach → analyze → recommend → improve                   │
├──────────────────────────────────────────────────────────┤
│  Key Principles:                                         │
│  ✓ Use @manager for complex features                    │
│  ✓ Use @coach for workflow improvements                 │
│  ✓ @developer completes self-review checklist           │
│  ✓ @validator does code review BEFORE hardware          │
│  ✓ Use @reviewer for critical features only             │
│  ✓ Requirements first, coding last                      │
│  ✓ Write tests before code (TDD)                        │
│  ✓ Test hardware on Raspberry Pi                        │
│  ✓ Update docs continuously                             │
│  ✓ Trust the process                                    │
└──────────────────────────────────────────────────────────┘
```

**Ready to start?**
- **Complex feature:** `@manager I want to [your idea]`
- **Simple feature:** `@requirements I want to [your idea]`
- **Critical feature:** `@manager [describe critical feature] - needs thorough review`
- **Improve workflow:** `@coach Our [process] feels inefficient`

