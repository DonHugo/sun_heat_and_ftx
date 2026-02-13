# OpenCode Agent Setup for sun_heat_and_ftx

## 🎯 Quick Start for Agents

This repository uses the **unified OpenCode agent structure** located at:
```
~/.config/opencode/agents/agent/
```

**All agents are user-level (not repo-level)** - there are NO agent definitions in this repo's `.opencode/agent/` directory.

## 📚 Agent Documentation

**Main Guide:** `/Users/hafs/Documents/Github/sun_heat_and_ftx/docs/opencode-agents-guide.md`

This comprehensive guide documents:
- All 13 available agents
- How to invoke each agent
- Agent capabilities and permissions
- Project-specific usage patterns

## ✅ Available Agents (All Working via Task Tool)

### Core Workflow (8 agents):
- `requirements` - Requirements gathering
- `architect` - System architecture design
- `developer` - Code implementation
- `tester` - Test creation
- `validator` - Validation & verification
- `reviewer` - Code review
- `coach` - Workflow guidance
- `general` - General-purpose tasks

### Specialists (5 agents):
- `data-analyst` - Statistical analysis & forecasting
- `debugger` - Debugging & root cause analysis
- `db-influxdb` - InfluxDB optimization
- `home-assistant` - Home Assistant entity discovery
- `notebook-specialist` - Jupyter notebook validation

## 🚀 Usage Examples

### Direct Invocation (All Agents):
```python
from opencode import Task

# Core agent
result = Task(agent="requirements", instruction="Your task")

# Specialist agent (works directly now!)
result = Task(agent="data-analyst", instruction="Analyze correlation...")
```

## 📋 Project Context: Solar Heating & FTX Data Analysis

**Domain:** Home energy management, solar heating, pellet consumption
**Tech Stack:** InfluxDB, Home Assistant, Python, pandas, Jupyter
**Key Sensors:** outdoor temp, pellet consumption, solar production
**Common Tasks:** Forecasting, correlation analysis, cost optimization

## 🔗 Related Documentation

- **Main Agent Guide:** `~/Documents/Github/sun_heat_and_ftx/docs/opencode-agents-guide.md`
- **Agent Definitions:** `~/.config/opencode/agents/agent/`
- **OpenCode Config:** `~/.config/opencode/opencode.jsonc`

---

**Last Updated:** Feb 11, 2026
**Agent Structure Version:** 1.0 (Unified)
