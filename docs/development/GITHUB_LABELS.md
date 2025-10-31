# GitHub Labels for Solar Heating System

**Date:** 2025-10-30  
**Purpose:** Complete label taxonomy for issue tracking

---

## 📋 Label Categories

### 🏷️ Type Labels

| Label | Color | Description | When to Use |
|-------|-------|-------------|-------------|
| `bug` | `#d73a4a` | Something isn't working | System errors, unexpected behavior, crashes |
| `enhancement` | `#a2eeef` | Improvement to existing feature | Better performance, usability improvements |
| `feature` | `#0e8a16` | New feature request | New functionality, new capabilities |
| `documentation` | `#0075ca` | Documentation update | README, guides, API docs, comments |
| `testing` | `#fbca04` | Test-related work | New tests, test coverage, test fixes |

---

### 🎯 Priority Labels

| Label | Color | Description | Response Time |
|-------|-------|-------------|---------------|
| `priority: critical` | `#b60205` | System down, data loss, security | Immediate (< 4 hours) |
| `priority: high` | `#d93f0b` | Major functionality broken | Same day (< 24 hours) |
| `priority: medium` | `#fbca04` | Important but not urgent | This week (< 7 days) |
| `priority: low` | `#0e8a16` | Nice to have | Next sprint (< 30 days) |

---

### 🔧 Component Labels

| Label | Color | Description | Owner |
|-------|-------|-------------|-------|
| `component: sensors` | `#1d76db` | Temperature sensors, RTD, MegaBAS | Sensor subsystem |
| `component: pumps` | `#5319e7` | Pump control and logic | Control subsystem |
| `component: mqtt` | `#0052cc` | MQTT communication | Integration subsystem |
| `component: home-assistant` | `#41b883` | Home Assistant integration | Integration subsystem |
| `component: watchdog` | `#d4c5f9` | Watchdog monitoring system | Monitoring subsystem |
| `component: gui` | `#ff6b6b` | Web interface, dashboards | UI subsystem |
| `component: systemd` | `#c5def5` | Service management, deployment | Infrastructure |
| `component: testing` | `#fbca04` | Test suite, test infrastructure | Quality |
| `component: logging` | `#7057ff` | Logging system, log management | Infrastructure |
| `component: config` | `#bfd4f2` | Configuration management | Infrastructure |
| `component: api` | `#0e8a16` | API server, REST endpoints | Integration subsystem |
| `component: energy` | `#fef2c0` | Energy calculations, tracking | Core logic |
| `component: control` | `#5319e7` | Control logic, algorithms | Core logic |
| `component: taskmaster` | `#e99695` | TaskMaster AI integration | AI subsystem |

---

### 📊 Status Labels

| Label | Color | Description | When to Use |
|-------|-------|-------------|-------------|
| `status: needs-info` | `#ffc107` | More information needed | Missing details, unclear requirements |
| `status: ready` | `#0e8a16` | Ready to work on | All info present, can start |
| `status: in-progress` | `#1d76db` | Currently being worked on | Active development |
| `status: blocked` | `#d93f0b` | Blocked by other work | Waiting on dependency |
| `status: review` | `#7057ff` | In code review | PR submitted, awaiting review |
| `status: testing` | `#fbca04` | In testing phase | Being tested on hardware |
| `status: duplicate` | `#cfd3d7` | Duplicate of another issue | Already tracked elsewhere |
| `status: wontfix` | `#ffffff` | Won't be fixed | Out of scope, design decision |

---

### 🎨 Category Labels

| Label | Color | Description | Examples |
|-------|-------|-------------|----------|
| `category: security` | `#b60205` | Security-related | Vulnerabilities, auth, encryption |
| `category: performance` | `#ff6b6b` | Performance improvement | Speed, memory, efficiency |
| `category: reliability` | `#0052cc` | Reliability/stability | Crashes, hangs, recovery |
| `category: usability` | `#41b883` | User experience | UI/UX, ease of use |
| `category: maintenance` | `#d4c5f9` | Code maintenance | Refactoring, cleanup |
| `category: integration` | `#0e8a16` | External integration | APIs, third-party systems |
| `category: hardware` | `#fbca04` | Hardware-specific | Raspberry Pi, sensors, relays |

---

### 🚀 Milestone Labels

| Label | Color | Description | Version |
|-------|-------|-------------|---------|
| `milestone: v3.1` | `#5319e7` | Bug fixes & stability | v3.1 |
| `milestone: v3.2` | `#1d76db` | Enhanced monitoring | v3.2 |
| `milestone: v3.3` | `#0052cc` | Advanced features | v3.3 |
| `milestone: v4.0` | `#0e8a16` | Major update | v4.0 |

---

### 🎯 Special Labels

| Label | Color | Description | When to Use |
|-------|-------|-------------|-------------|
| `good first issue` | `#7057ff` | Good for newcomers | Simple, well-defined issues |
| `help wanted` | `#008672` | Extra attention needed | Need community help |
| `question` | `#d876e3` | Question or discussion | Not a bug or feature |
| `breaking change` | `#b60205` | Breaks backward compatibility | API changes, migrations |
| `dependencies` | `#0366d6` | Dependency updates | npm, pip, library updates |

---

## 🎨 Label Usage Guidelines

### How to Label an Issue

1. **Start with Type** (bug, feature, enhancement, etc.)
2. **Add Priority** (critical, high, medium, low)
3. **Add Component** (which part of the system)
4. **Add Status** (needs-info, ready, in-progress, etc.)
5. **Add Category** if relevant (security, performance, etc.)
6. **Add Milestone** if assigned to a version

### Example Label Combinations

**Critical Bug:**
```
bug, priority: critical, component: mqtt, status: ready
```

**New Feature:**
```
feature, priority: medium, component: gui, milestone: v3.2, status: needs-info
```

**Performance Enhancement:**
```
enhancement, priority: high, component: energy, category: performance, status: in-progress
```

**Documentation Update:**
```
documentation, priority: low, status: ready, good first issue
```

---

## 📊 Label Statistics

### By Type
- **Bugs**: Track what's broken
- **Features**: Track new capabilities
- **Enhancements**: Track improvements
- **Documentation**: Track doc needs
- **Testing**: Track test coverage

### By Priority
- **Critical**: < 5% of issues
- **High**: ~20% of issues
- **Medium**: ~50% of issues
- **Low**: ~25% of issues

### By Component
- Most issues should have a component label
- Some issues may have multiple component labels
- Use for filtering and ownership

---

## 🔧 Label Management

### Creating Labels in GitHub

```bash
# Using GitHub CLI
gh label create "priority: critical" --color "b60205" --description "System down, data loss, security"
gh label create "component: sensors" --color "1d76db" --description "Temperature sensors, RTD, MegaBAS"
# ... (repeat for all labels)
```

### Bulk Label Creation Script

See `scripts/create_github_labels.sh` for automated label creation.

---

## 📝 Label Maintenance

### Regular Reviews
- **Monthly**: Review label usage
- **Quarterly**: Clean up unused labels
- **Annually**: Reassess label taxonomy

### Best Practices
- Don't create too many labels (overwhelming)
- Keep color scheme consistent
- Update descriptions as needed
- Remove deprecated labels
- Document changes

---

**Last Updated:** 2025-10-30  
**Total Labels:** 40+  
**Label Categories:** 7 (Type, Priority, Component, Status, Category, Milestone, Special)


