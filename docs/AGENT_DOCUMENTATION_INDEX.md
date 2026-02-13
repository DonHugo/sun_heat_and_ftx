# OpenCode Agent Documentation Index

**Last Updated:** February 11, 2026  
**Status:** ✅ All agents working and documented

---

## 📚 Documentation Structure

### 1. Main Comprehensive Guide
**Location:** `/Users/hafs/Documents/Github/sun_heat_and_ftx/docs/opencode-agents-guide.md`

**Contents:**
- Complete agent inventory (all 13 agents)
- Detailed agent descriptions and capabilities
- Usage examples for all agents
- Project-specific context
- Best practices and patterns
- Quick reference tables

**Size:** 26 KB (870+ lines)  
**Audience:** Developers, agents, system administrators

---

### 2. Per-Repo Quick Start Guides

Each repository has a standardized `.opencode/README.md` for quick agent onboarding:

| Repository | Location | Status |
|------------|----------|--------|
| **sun_heat_and_ftx** | `.opencode/README.md` | ✅ Created |
| **opencode_agent_workflow** | `.opencode/README.md` | ✅ Created |
| **hot_water_management** | `.opencode/README.md` | ✅ Created |
| **influxdb_data_analysis** | `.opencode/README.md` | ✅ Created |

**Each contains:**
- Quick reference to unified agent structure
- List of all 13 available agents
- Direct invocation examples
- Link to main comprehensive guide
- **Repo-specific project context**
- Related documentation links

---

### 3. Root README References

Each repository's main `README.md` includes a **"🤖 OpenCode Agents"** section that:
- Points to `.opencode/README.md`
- Lists key information about agents
- Makes documentation discoverable

---

## 🗂️ Agent Definition Files

**Location:** `~/.config/opencode/agents/agent/`

All 13 agent definition files (`.md` format):

### Primary Agent (1):
- `project-manager.md` - Main orchestrator (gpt-5.1-codex)

### Core Workflow Agents (7):
- `requirements.md` - Requirements gathering (claude-sonnet-4.5)
- `architect.md` - Architecture design (claude-sonnet-4.5)
- `developer.md` - Implementation (gpt-5.1-codex)
- `tester.md` - Testing strategy (gpt-5.1-codex)
- `validator.md` - Validation (claude-sonnet-4.5)
- `reviewer.md` - Code review (claude-sonnet-4.5)
- `coach.md` - Workflow guidance (claude-sonnet-4.5)

### Specialist Agents (5):
- `data-analyst.md` - Statistical analysis (claude-sonnet-4.5)
- `debugger.md` - Bug diagnosis (gpt-5.1-codex)
- `db-influxdb.md` - InfluxDB optimization (claude-sonnet-4.5)
- `home-assistant.md` - HA entity discovery (claude-sonnet-4.5)
- `notebook-specialist.md` - Jupyter validation (gpt-5.1-codex)

**Status:** ✅ All agents registered and working via Task tool

---

## 🎯 How Agents Find Documentation

### Discovery Path for New Agents:

1. **Agent starts in repo** → Sees root `README.md` → **"🤖 OpenCode Agents"** section
2. **Follows link** → Opens `.opencode/README.md` → Gets quick start info
3. **Needs details** → Opens main guide at `docs/opencode-agents-guide.md`
4. **Wants definitions** → Reads agent files at `~/.config/opencode/agents/agent/`

### File Discovery Priority:

```
1. .opencode/README.md          ← First check (quick start)
2. README.md (root)              ← Root references .opencode/README.md
3. docs/opencode-agents-guide.md ← Comprehensive reference
4. ~/.config/opencode/agents/    ← Agent definitions
```

---

## 📍 Quick Links by Repository

### sun_heat_and_ftx
- **Quick Start:** [.opencode/README.md](../.opencode/README.md)
- **Main Guide:** [docs/opencode-agents-guide.md](./opencode-agents-guide.md)
- **Root README:** [README.md](../README.md#-opencode-agents)
- **Context:** Solar heating, pellet consumption, InfluxDB analysis

### opencode_agent_workflow
- **Quick Start:** `/Users/hafs/Documents/Github/opencode_agent_workflow/.opencode/README.md`
- **Root README:** `/Users/hafs/Documents/Github/opencode_agent_workflow/README.md`
- **Context:** Agent workflow development, testing, documentation

### hot_water_management
- **Quick Start:** `/Users/hafs/Documents/Github/hot_water_management/.opencode/README.md`
- **Root README:** `/Users/hafs/Documents/Github/hot_water_management/README.md`
- **Context:** Water heating system monitoring, efficiency analysis

### influxdb_data_analysis
- **Quick Start:** `/Users/hafs/Documents/Github/influxdb_data_analysis/.opencode/README.md`
- **Root README:** `/Users/hafs/Documents/Github/influxdb_data_analysis/README.md`
- **Context:** Time-series data analysis, query optimization

---

## ✅ Documentation Verification

### Verification Commands:

```bash
# Check all .opencode/README.md files exist
ls -lh ~/.config/opencode/agents/agent/
ls -lh ~/Documents/Github/*/. opencode/README.md

# Verify main guide
cat ~/Documents/Github/sun_heat_and_ftx/docs/opencode-agents-guide.md | head -50

# List all agent definitions
ls -1 ~/.config/opencode/agents/agent/*.md

# Verify OpenCode recognizes agents
opencode agent list
```

### Expected Results:
- ✅ 13 agent definition files in `~/.config/opencode/agents/agent/`
- ✅ 4 `.opencode/README.md` files (one per repo)
- ✅ 1 main guide (`docs/opencode-agents-guide.md`)
- ✅ All agents shown in `opencode agent list`

---

## 🔄 Maintenance

### When to Update Documentation:

1. **New agent added** → Update all `.opencode/README.md` files + main guide
2. **Agent capabilities change** → Update main guide + agent definition file
3. **New repo created** → Create `.opencode/README.md` + update root README
4. **OpenCode version update** → Verify agent compatibility, update notes

### Documentation Owners:
- **Main guide:** sun_heat_and_ftx repo maintainers
- **Agent definitions:** System-wide (affects all repos)
- **Per-repo guides:** Individual repo maintainers

---

## 📊 Current Status Summary

| Component | Status | Last Updated |
|-----------|--------|--------------|
| Agent definitions (13 files) | ✅ Valid | Feb 11, 2026 |
| Main guide | ✅ Updated | Feb 11, 2026 |
| sun_heat_and_ftx guide | ✅ Created | Feb 11, 2026 |
| opencode_agent_workflow guide | ✅ Created | Feb 11, 2026 |
| hot_water_management guide | ✅ Created | Feb 11, 2026 |
| influxdb_data_analysis guide | ✅ Created | Feb 11, 2026 |
| Root README references | ✅ Added | Feb 11, 2026 |
| Agent invocation testing | ✅ All working | Feb 11, 2026 |

---

## 🎉 Success Criteria (All Met)

✅ **Unified structure** - All agents in single location  
✅ **Documentation coverage** - All agents documented  
✅ **Easy discovery** - .opencode/README.md in each repo  
✅ **Root references** - README.md points to agent docs  
✅ **Comprehensive guide** - Detailed reference available  
✅ **Agent accessibility** - All 13 agents working via Task tool  
✅ **Cross-repo consistency** - Same structure everywhere  

---

**The OpenCode agent documentation structure is complete and production-ready!** 🚀
