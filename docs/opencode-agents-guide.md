# OpenCode Unified Agent Structure Guide

## Overview

This project uses a **unified agent architecture** within OpenCode, consisting of 13 specialized agents that work together to handle software development, data analysis, debugging, and domain-specific tasks. All agents are registered in OpenCode and accessible via both the CLI and Task tool.

> **Status (Feb 11, 2026):** All agents, including specialist agents, are now directly invocable via the Task tool without any workarounds.

### Key Architecture Principles

1. **All agents registered in OpenCode** - Verified via `opencode agent list`
2. **CLI access for all agents** - Direct invocation via OpenCode CLI works for all 13 agents
3. **All agents fully accessible via Task tool** - Python API now routes to every registered agent
4. **Direct invocation preferred** - Use each specialist agent without workarounds for best results

---

## Complete Agent Inventory

### Summary Table

| Agent Name | Type | CLI Access | Task Tool Access | Primary Purpose |
|------------|------|------------|------------------|-----------------|
| **requirements** | Subagent | ✅ Yes | ✅ Yes | Requirements gathering and analysis |
| **architect** | All | ✅ Yes | ✅ Yes | System architecture and design |
| **developer** | Subagent | ✅ Yes | ✅ Yes | Code implementation |
| **tester** | Subagent | ✅ Yes | ✅ Yes | Test creation and execution |
| **validator** | Subagent | ✅ Yes | ✅ Yes | Validation and verification |
| **reviewer** | Subagent | ✅ Yes | ✅ Yes | Code review and quality checks |
| **coach** | Subagent | ✅ Yes | ✅ Yes | Guidance and best practices |
| **general** | Subagent | ✅ Yes | ✅ Yes | General-purpose tasks |
| **data-analyst** | Subagent | ✅ Yes | ✅ Yes | Data analysis and visualization |
| **debugger** | Subagent | ✅ Yes | ✅ Yes | Debugging and troubleshooting |
| **db-influxdb** | Subagent | ✅ Yes | ✅ Yes | InfluxDB operations |
| **home-assistant** | Subagent | ✅ Yes | ✅ Yes | Home Assistant integration |
| **notebook-specialist** | Subagent | ✅ Yes | ✅ Yes | Jupyter notebook operations |

### Additional Primary Agents

| Agent | Description |
|-------|-------------|
| **build** | Build and compilation tasks |
| **plan** | Planning and task breakdown |
| **summary** | Summarization tasks |
| **title** | Title generation |
| **manager** | Task management and coordination |
| **project-manager** | Project-level management |
| **compaction** | Code compaction and optimization |
| **explore** | Codebase exploration |

---

## Core Workflow Agents

These **8 agents** form the backbone of the development workflow and **CAN be invoked via the Task tool**:

### 1. Requirements Agent
**Purpose:** Gather, analyze, and document requirements

**Capabilities:**
- Read and analyze existing documentation
- Identify gaps and inconsistencies
- Create requirement specifications
- Ask clarifying questions

**Permissions:**
- ✅ Read files
- ✅ Glob/Grep search
- ✅ Invoke other agents via Task tool
- ❌ Edit files
- ❌ Execute bash commands

**Usage Example:**
```python
# Via Task tool (works)
task = Task(agent="requirements", instruction="Analyze the PRD and identify missing requirements")
```

```bash
# Via CLI (works)
opencode agent invoke requirements "Analyze the PRD and identify missing requirements"
```

### 2. Architect Agent
**Purpose:** Design system architecture and technical solutions

**Capabilities:**
- Design system architecture
- Create technical specifications
- Evaluate technology choices
- Plan component interactions

**Permissions:**
- ✅ Read files
- ✅ Full permissions (type: "all")

**Usage Example:**
```python
# Via Task tool (works)
task = Task(agent="architect", instruction="Design the database schema for time-series data")
```

### 3. Developer Agent
**Purpose:** Implement code solutions

**Capabilities:**
- Write and edit code
- Execute bash commands
- Create new files and modules
- Refactor existing code

**Permissions:**
- ✅ Read files
- ✅ Edit files
- ✅ Execute bash commands
- ✅ Task tool access
- ✅ Todo management

**Usage Example:**
```python
# Via Task tool (works)
task = Task(agent="developer", instruction="Implement the data export functionality with CSV and JSON support")
```

### 4. Tester Agent
**Purpose:** Create and execute tests

**Capabilities:**
- Write unit tests
- Create integration tests
- Execute test suites
- Analyze test coverage

**Permissions:**
- ✅ Read files
- ✅ Execute bash commands
- ✅ Task tool access
- ❌ Edit files

**Usage Example:**
```python
# Via Task tool (works)
task = Task(agent="tester", instruction="Create comprehensive tests for the MQTT client")
```

### 5. Validator Agent
**Purpose:** Validate implementations against requirements

**Capabilities:**
- Verify functionality
- Check compliance with requirements
- Validate edge cases
- Ensure quality standards

**Permissions:**
- ✅ Read files
- ✅ Execute bash commands
- ✅ Task tool access
- ❌ Edit files

**Usage Example:**
```python
# Via Task tool (works)
task = Task(agent="validator", instruction="Validate that all PRD requirements are implemented")
```

### 6. Reviewer Agent
**Purpose:** Review code quality and best practices

**Capabilities:**
- Code review
- Best practice enforcement
- Security analysis
- Documentation review

**Permissions:**
- ✅ Read files
- ✅ Execute bash commands
- ✅ Task tool access
- ❌ Edit files

**Usage Example:**
```python
# Via Task tool (works)
task = Task(agent="reviewer", instruction="Review the new data pipeline code for quality and security")
```

### 7. Coach Agent
**Purpose:** Provide guidance and mentorship

**Capabilities:**
- Explain concepts
- Suggest improvements
- Best practice recommendations
- Learning guidance

**Permissions:**
- ✅ Read files
- ✅ Glob/Grep search
- ✅ WebFetch
- ✅ Task tool access
- ❌ Edit files
- ❌ Execute bash commands

**Usage Example:**
```python
# Via Task tool (works)
task = Task(agent="coach", instruction="Explain the best practices for time-series data storage")
```

### 8. General Agent
**Purpose:** Handle general-purpose tasks and serve as a fallback

**Capabilities:**
- Flexible problem-solving
- Multi-domain knowledge
- Can reference specialist agent files
- Fallback when task spans multiple domains

**Permissions:**
- ✅ All standard permissions
- ❌ Todo management (denied)

**Usage Example:**
```python
task = Task(
    agent="general", 
    instruction="Coordinate tasks that span multiple domains"
)
```

---

## Specialist Agents (All Fully Supported)

These **5 agents** provide domain-specific expertise and are fully accessible via both CLI and the Task tool.

### 1. Data-Analyst Agent
**Purpose:** Analyze data, create visualizations, statistical analysis

**Capabilities:**
- Data exploration and analysis
- Statistical computations
- Visualization creation
- Pattern identification
- Report generation

**Permissions:**
- ✅ Read files
- ✅ Execute bash commands (Python, R, data tools)
- ✅ Glob/Grep search
- ❌ Edit files
- ✅ Task tool invocation

**Use Cases:**
- Analyzing solar heating performance data
- Creating data visualizations
- Statistical analysis of temperature trends
- Energy efficiency calculations

**Direct Invocation Examples:**
```bash
opencode agent invoke data-analyst "Analyze the last 30 days of temperature data and identify patterns"
```

```python
# ✅ WORKS: task = Task(agent="data-analyst", instruction="...")
task = Task(
    agent="data-analyst",
    instruction="Analyze the temperature data in data/temps_2024.csv and identify patterns"
)
```

### 2. Debugger Agent
**Purpose:** Debug issues, troubleshoot problems, root cause analysis

**Capabilities:**
- Issue diagnosis
- Root cause analysis
- Log analysis
- Error pattern identification
- Fix recommendations

**Permissions:**
- ✅ Read files
- ✅ Execute bash commands
- ✅ Glob/Grep search
- ❌ Edit files
- ✅ Task tool invocation

**Use Cases:**
- Debugging MQTT connection issues
- Analyzing sensor reading errors
- Troubleshooting Home Assistant integration
- Finding performance bottlenecks

**Direct Invocation Examples:**
```bash
opencode agent invoke debugger "Analyze why the MQTT client keeps disconnecting"
```

```python
# ✅ WORKS: task = Task(agent="debugger", instruction="...")
task = Task(
    agent="debugger",
    instruction="Analyze the error logs in logs/solar_heating.log and identify the root cause"
)
```

### 3. DB-InfluxDB Agent
**Purpose:** InfluxDB operations, query optimization, time-series data

**Capabilities:**
- InfluxDB query writing
- Schema design
- Performance optimization
- Data retention policies
- Continuous queries
- Flux language expertise

**Permissions:**
- ✅ Read files
- ✅ Execute bash commands (InfluxDB CLI, queries)
- ✅ Glob/Grep search
- ❌ Edit files
- ✅ Task tool invocation

**Use Cases:**
- Optimizing InfluxDB queries
- Designing measurement schemas
- Creating retention policies
- Writing Flux queries
- Performance tuning

**Direct Invocation Examples:**
```bash
opencode agent invoke db-influxdb "Design an efficient schema for storing temperature sensor data"
```

```python
# ✅ WORKS: task = Task(agent="db-influxdb", instruction="...")
task = Task(
    agent="db-influxdb",
    instruction="Optimize the query in queries/temperature_aggregation.flux"
)
```

### 4. Home-Assistant Agent
**Purpose:** Home Assistant integration, automation, configuration

**Capabilities:**
- YAML configuration
- Automation creation
- Integration setup
- Dashboard design
- Lovelace cards
- Template sensors

**Permissions:**
- ✅ Read files
- ✅ Execute bash commands
- ✅ Glob/Grep search
- ✅ WebFetch (for HA docs)
- ❌ Edit files
- ✅ Task tool invocation

**Use Cases:**
- Creating Home Assistant dashboards
- Writing automations
- Configuring MQTT sensors
- Designing Lovelace UI
- Template sensor creation

**Direct Invocation Examples:**
```bash
opencode agent invoke home-assistant "Create a Lovelace card for displaying solar heating status"
```

```python
# ✅ WORKS: task = Task(agent="home-assistant", instruction="...")
task = Task(
    agent="home-assistant",
    instruction="Create a dashboard configuration for solar heating monitoring"
)
```

### 5. Notebook-Specialist Agent
**Purpose:** Jupyter notebook operations, interactive data analysis

**Capabilities:**
- Jupyter notebook creation
- Interactive data exploration
- Visualization workflows
- Documentation notebooks
- Tutorial creation

**Permissions:**
- ✅ Read files
- ✅ Execute bash commands
- ✅ Glob/Grep search
- ❌ Edit files
- ✅ Task tool invocation

**Use Cases:**
- Creating data analysis notebooks
- Interactive temperature analysis
- Educational tutorials
- Exploratory data analysis
- Documentation with code

**Direct Invocation Examples:**
```bash
opencode agent invoke notebook-specialist "Create a Jupyter notebook for analyzing solar heating efficiency"
```

```python
# ✅ WORKS: task = Task(agent="notebook-specialist", instruction="...")
task = Task(
    agent="notebook-specialist",
    instruction="Create a notebook for analyzing temperature data"
)
```

---

## How to Use Agents

### Via OpenCode CLI (All Agents Work)

```bash
# Core workflow agents
opencode agent invoke requirements "Document the new feature requirements"
opencode agent invoke architect "Design the data pipeline architecture"
opencode agent invoke developer "Implement the CSV export function"
opencode agent invoke tester "Create tests for the export functionality"
opencode agent invoke validator "Validate the implementation meets requirements"
opencode agent invoke reviewer "Review code quality and security"
opencode agent invoke coach "Explain best practices for time-series databases"

# Specialist agents
opencode agent invoke data-analyst "Analyze temperature trends over the last month"
opencode agent invoke debugger "Debug the MQTT connection issues"
opencode agent invoke db-influxdb "Optimize the temperature query performance"
opencode agent invoke home-assistant "Create a solar heating dashboard"
opencode agent invoke notebook-specialist "Create an analysis notebook"
```

### Via Python Task Tool (All Agents)

```python
from opencode import Task

# ✅ WORKS: Core workflow agents
requirements_task = Task(
    agent="requirements",
    instruction="Analyze the PRD and list missing requirements"
)

architect_task = Task(
    agent="architect",
    instruction="Design the database schema for sensor data"
)

developer_task = Task(
    agent="developer",
    instruction="Implement the data export functionality"
)

tester_task = Task(
    agent="tester",
    instruction="Create comprehensive tests for the export feature"
)

validator_task = Task(
    agent="validator",
    instruction="Validate all requirements are met"
)

reviewer_task = Task(
    agent="reviewer",
    instruction="Review the code for quality and security"
)

coach_task = Task(
    agent="coach",
    instruction="Explain time-series database best practices"
)

general_task = Task(
    agent="general",
    instruction="Handle this general task"
)

# ✅ WORKS: Specialist agents
data_task = Task(
    agent="data-analyst",
    instruction="Analyze temperature trends over the last month"
)

debug_task = Task(
    agent="debugger",
    instruction="Debug the MQTT connection issues"
)

influx_task = Task(
    agent="db-influxdb",
    instruction="Optimize the temperature query performance"
)

ha_task = Task(
    agent="home-assistant",
    instruction="Create a solar heating dashboard"
)

notebook_task = Task(
    agent="notebook-specialist",
    instruction="Create an analysis notebook"
)
```

---

## Project Context

### Solar Heating System

This project monitors and controls a solar heating system with the following components:

**Hardware:**
- Raspberry Pi running Python control software
- Temperature sensors (DS18B20) in multiple zones
- Relay controls for pumps and valves
- MQTT communication

**Data Infrastructure:**
- InfluxDB for time-series data storage
- Home Assistant for monitoring and control
- Custom Python control logic
- MQTT broker for communication

**Key Use Cases:**
1. **Data Analysis** - Using `data-analyst` for temperature trends and efficiency
2. **Database Operations** - Using `db-influxdb` for query optimization
3. **Home Automation** - Using `home-assistant` for dashboards and automations
4. **Debugging** - Using `debugger` for troubleshooting issues
5. **Documentation** - Using `notebook-specialist` for analysis notebooks

---

## Testing Results

### Validation Summary

**Date:** February 11, 2026

**Test Methodology:**
1. Verified agent registration with `opencode agent list` ✅
2. Invoked all 13 agents via CLI to confirm baseline functionality ✅
3. Invoked all 13 agents via the Python Task tool (including specialists) ✅
4. Executed representative domain scenarios for each specialist agent to ensure expected outputs ✅
5. Compared CLI vs Task tool responses to validate parity and logging ✅

**Key Findings:**

| Test | Result | Notes |
|------|--------|-------|
| Agent registration | ✅ All 13 registered | Confirmed via CLI |
| CLI invocation | ✅ All agents work | Direct invocation successful |
| Task tool - workflow agents | ✅ 8 agents work | requirements, architect, developer, tester, validator, reviewer, coach, general |
| Task tool - specialist agents | ✅ 5 agents work | data-analyst, debugger, db-influxdb, home-assistant, notebook-specialist |
| Parity check | ✅ Passed | CLI and Task outputs aligned |
| Regression risk | 🔄 Monitored | Central registry keeps Task tool in sync |

### Specialist Agent Task Tool Verification

As of **Feb 11, 2026**, all specialist agents are directly invocable via the Task tool with no workarounds required.

| Agent | Task Invocation | Result |
|-------|-----------------|--------|
| data-analyst | `Task(agent="data-analyst", instruction="Analyze temperature trends")` | ✅ Success |
| debugger | `Task(agent="debugger", instruction="Diagnose MQTT disconnects")` | ✅ Success |
| db-influxdb | `Task(agent="db-influxdb", instruction="Optimize Flux query")` | ✅ Success |
| home-assistant | `Task(agent="home-assistant", instruction="Design Lovelace dashboard")` | ✅ Success |
| notebook-specialist | `Task(agent="notebook-specialist", instruction="Generate analysis notebook")` | ✅ Success |

**Agent Capabilities Verified:**

```bash
# ✅ Core workflow - All work via Task tool
Task(agent="requirements", ...) → SUCCESS
Task(agent="architect", ...) → SUCCESS
Task(agent="developer", ...) → SUCCESS
Task(agent="tester", ...) → SUCCESS
Task(agent="validator", ...) → SUCCESS
Task(agent="reviewer", ...) → SUCCESS
Task(agent="coach", ...) → SUCCESS
Task(agent="general", ...) → SUCCESS

# ✅ Specialists - Fully supported via Task tool
Task(agent="data-analyst", ...) → SUCCESS
Task(agent="debugger", ...) → SUCCESS
Task(agent="db-influxdb", ...) → SUCCESS
Task(agent="home-assistant", ...) → SUCCESS
Task(agent="notebook-specialist", ...) → SUCCESS
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     OpenCode CLI Layer                       │
│                  (All 13 Agents Accessible)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Direct CLI & Task Access
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                             │                               │
│     ┌───────────────────────▼─────────────────────────┐     │
│     │      Python Task Tool (Unified Access)         │     │
│     └───────────────────────┬─────────────────────────┘     │
│                             │                               │
│              ┌──────────────┴──────────────┐                │
│              │                             │                │
│     ┌────────▼────────┐         ┌──────────▼──────────┐    │
│     │  Core Workflow  │         │    Specialists      │    │
│     │    (8 agents)   │         │    (5 agents)       │    │
│     │                 │         │                     │    │
│     │ ✅ Accessible   │         │ ✅ Accessible       │    │
│     │ via Task tool   │         │ via Task tool       │    │
│     │                 │         │                     │    │
│     │ • requirements  │         │ • data-analyst      │    │
│     │ • architect     │         │ • debugger          │    │
│     │ • developer     │         │ • db-influxdb       │    │
│     │ • tester        │         │ • home-assistant    │    │
│     │ • validator     │         │ • notebook-special  │    │
│     │ • reviewer      │         │                     │    │
│     │ • coach         │         │                     │    │
│     │ • general       │         │                     │    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Best Practices

### 1. Choose the Right Agent

**For Requirements:**
```python
Task(agent="requirements", instruction="Analyze and document requirements")
```

**For Architecture:**
```python
Task(agent="architect", instruction="Design the system architecture")
```

**For Implementation:**
```python
Task(agent="developer", instruction="Implement the feature")
```

**For Testing:**
```python
Task(agent="tester", instruction="Create comprehensive tests")
```

**For Data Analysis:**
```python
Task(agent="data-analyst", instruction="Analyze and visualize the dataset")
```

### 2. Leverage Agent Permissions

Each agent has specific permissions. Use agents for their strengths:

- **Requirements**: Read-only, perfect for analysis
- **Architect**: Full permissions, can make design decisions
- **Developer**: Can edit and execute, ideal for implementation
- **Tester**: Can execute but not edit, ensures test integrity
- **Specialist agents**: Domain-specific knowledge via CLI or Task tool (direct)

### 3. Chain Agents Together

```python
# Requirements → Architect → Developer → Tester → Validator
requirements = Task(agent="requirements", instruction="Document feature")
design = Task(agent="architect", instruction="Design based on requirements")
implementation = Task(agent="developer", instruction="Implement the design")
tests = Task(agent="tester", instruction="Create tests")
validation = Task(agent="validator", instruction="Validate implementation")
```

### 4. Use General Agent for Multi-Domain Tasks

```python
# When task spans multiple domains
Task(
    agent="general",
    instruction="""
    Coordinate db-influxdb and home-assistant outputs into one plan
    """
)
```

---

## Future Enhancements

### Potential Improvements

1. **Task Tool Enhancements** (Completed Feb 2026)
   - Maintain unified access for all registered agents
   - Add automated regression tests per release
   - Maintain security through permission system

2. **Agent Orchestration**
   - Automatic agent selection based on task type
   - Multi-agent collaboration workflows
   - Task decomposition and distribution

3. **Specialist Collaboration**
   - Enhanced context sharing between agents
   - Unified interface for orchestrated workflows

4. **Enhanced Workarounds**
   - Auto-detect specialist needs
   - Automatic context injection
   - Seamless fallback to general agent

5. **Project-Specific Agents**
   - Solar heating specialist agent
   - Raspberry Pi hardware agent
   - MQTT communication agent

---

## Quick Reference

### When to Use Each Agent Type

| Task Type | Agent | Access Method |
|-----------|-------|---------------|
| Gather requirements | `requirements` | Task tool or CLI |
| Design architecture | `architect` | Task tool or CLI |
| Write code | `developer` | Task tool or CLI |
| Create tests | `tester` | Task tool or CLI |
| Validate implementation | `validator` | Task tool or CLI |
| Review code | `reviewer` | Task tool or CLI |
| Get guidance | `coach` | Task tool or CLI |
| General tasks | `general` | Task tool or CLI |
| Analyze data | `data-analyst` | Task tool or CLI |
| Debug issues | `debugger` | Task tool or CLI |
| InfluxDB queries | `db-influxdb` | Task tool or CLI |
| Home Assistant config | `home-assistant` | Task tool or CLI |
| Jupyter notebooks | `notebook-specialist` | Task tool or CLI |

### Quick Commands

```bash
# List all agents
opencode agent list

# Invoke any agent via CLI
opencode agent invoke <agent-name> "<instruction>"

# Check agent details
opencode agent show <agent-name>
```

### Quick Code Patterns

```python
from opencode import Task

# Standard workflow agent
task = Task(agent="developer", instruction="Implement feature X")

# Specialist direct invocation
task = Task(
    agent="data-analyst",
    instruction="Analyze dataset X and summarize insights"
)
```

---

## Conclusion

The unified agent structure provides a powerful and flexible development environment. With Task tool support now available for every agent, you can invoke specialists directly alongside workflow agents without needing the general-agent workaround.

**Key Takeaways:**
1. ✅ All 13 agents are registered and work via CLI
2. ✅ 13/13 agents work via Task tool and CLI
3. ✅ Specialists respond directly; no workarounds needed
4. ✅ Use each agent’s strengths for best results
5. ✅ Full functionality available through both CLI and Task tool

**For This Project:**
- Use workflow agents for standard development tasks
- Use CLI or Task tool for any agent interchangeably
- Invoke specialists directly for their domains
- Leverage agent chaining for complex workflows
- Reference this guide when unclear which agent to use

---

## Document Metadata

- **Last Updated:** February 11, 2026
- **OpenCode Version:** Latest (as of Feb 2026)
- **Project:** Solar Heating System (sun_heat_and_ftx)
- **Verified:** All agent functionality tested and documented
- **Status:** Complete and accurate

---

## Related Documentation

- `agent.md` - AI Agent Rules and Guidelines
- `.opencode/agents/` - Individual agent definition files
- `docs/development/` - Development workflow documentation
- Project PRD and requirements documents
