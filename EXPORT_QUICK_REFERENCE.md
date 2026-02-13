# 🚀 Workflow Export - Quick Reference Card

## ⚡ One-Command Export

```bash
# From sun_heat_and_ftx repo:
./scripts/export_workflow.sh /path/to/target-repo [minimal|recommended|full]
```

**Export Levels:**
- `minimal` - Core files only (3 files, 2 min setup)
- `recommended` - Core + templates + docs (18 files, 15 min setup) ⭐ **DEFAULT**
- `full` - Everything (22 files, 30 min setup)

---

## 📋 Manual Export Checklist

### ✅ Must Have (Minimal)
```bash
cp .cursorrules /target/
cp MULTI_AGENT_GUIDE.md /target/
cp AGENTS_README.md /target/
```

### ✅ Should Have (Recommended)
```bash
# Add agent templates:
cp -r python/v3/docs/agent_templates /target/docs/

# Add dev docs:
cp docs/development/PRE_DEPLOYMENT_CHECKLIST.md /target/docs/development/
cp docs/development/DEPLOYMENT_RUNBOOK.md /target/docs/development/
cp docs/development/PRODUCTION_ENVIRONMENT.md /target/docs/development/
cp docs/development/MULTI_AGENT_ISSUE_WORKFLOW.md /target/docs/development/
```

### ✅ Nice to Have (Full)
```bash
# Add scripts:
cp scripts/test_production_env.sh /target/scripts/
cp scripts/verify_deps.sh /target/scripts/
cp scripts/create_github_labels.sh /target/scripts/
chmod +x /target/scripts/*.sh

# Add references:
cp WORKFLOW_EXPORT_GUIDE.md /target/
cp SETUP_COMPLETE.md /target/
cp COACH_SUMMARY_WORKFLOW_IMPROVEMENTS.md /target/
cp GITHUB_INTEGRATION_README.md /target/
```

---

## 🎨 Customization Checklist

After copying files to the new repo:

### 1. Update `.cursorrules`
- [ ] Line 1: Project name
- [ ] Line ~550: "Project-Specific Context" section
- [ ] Replace: "Solar heating" → Your project
- [ ] Replace: "Raspberry Pi" → Your platform
- [ ] Replace: "Python, MQTT" → Your tech stack

### 2. Update `MULTI_AGENT_GUIDE.md`
- [ ] Replace examples with your domain
- [ ] Update "System:" description
- [ ] Update "Key Technologies:"
- [ ] Update testing approach

### 3. Update `AGENTS_README.md`
- [ ] Replace all example conversations
- [ ] Update use cases to your domain

### 4. Update Agent Templates
- [ ] All 8 files in `docs/agent_templates/`
- [ ] Replace placeholder examples
- [ ] Update technology references

### 5. Update Development Docs
- [ ] `PRE_DEPLOYMENT_CHECKLIST.md` - Your stack
- [ ] `PRODUCTION_ENVIRONMENT.md` - Your environment
- [ ] `DEPLOYMENT_RUNBOOK.md` - Your process

---

## 🏷️ GitHub Setup (5 min)

### Step 1: Create Labels
```bash
cd scripts
./create_github_labels.sh
```

### Step 2: Create Project Board
1. Go to: `https://github.com/USERNAME/REPO/projects`
2. Click "New project" → Choose "Board"
3. Name: "Development Workflow"

### Step 3: Add Status Field
Add these status values:
- 📋 Requirements
- ⏳ Awaiting Approval
- 🏗️ Architecture
- 🧪 Testing
- 💻 In Progress
- 👀 Code Review
- 🚀 Ready to Deploy
- ✅ Done

### Step 4: Link Labels to Status (8 automations)
For each label → status mapping:

| GitHub Label | → | Project Status |
|--------------|---|----------------|
| `status: requirements` | → | 📋 Requirements |
| `status: awaiting-approval` | → | ⏳ Awaiting Approval |
| `status: architecture` | → | 🏗️ Architecture |
| `status: testing` | → | 🧪 Testing |
| `status: in-progress` | → | 💻 In Progress |
| `status: code-review` | → | 👀 Code Review |
| `status: ready-to-deploy` | → | 🚀 Ready to Deploy |
| `status: deployed` | → | ✅ Done |

**How:** Project → ⋮ → Workflows → Add workflow → "Label is added to issue"

---

## 🧪 Testing Your Export

### Local Test (Cursor IDE)
```bash
# Open new repo in Cursor
# In chat, type:
@manager help

# Expected: Manager agent responds with capabilities
```

### GitHub Test
```bash
# Create test issue
gh issue create -t "Test workflow" -b "Testing export"

# Update label
gh issue edit <NUM> --add-label "status: requirements"

# Check project board - should move to "📋 Requirements"
```

### End-to-End Test
```
@manager I want to add [simple feature]
```

**Expected:**
1. Routes to @requirements
2. Gathers requirements
3. Asks for approval (⚠️)
4. After approval: Runs autonomously
5. Updates GitHub labels automatically
6. Asks for deployment approval (⚠️)

---

## 🎯 Project-Type Quick Customizations

### Web App (React/Node.js)
```bash
# In .cursorrules, replace:
"Raspberry Pi" → "Browser/Cloud"
"MQTT, systemd" → "React, Node.js, PostgreSQL"
"Hardware testing" → "E2E testing (Playwright/Cypress)"
"systemd service" → "PM2/Docker deployment"
```

### Mobile App (iOS/Android)
```bash
# In .cursorrules, replace:
"Raspberry Pi" → "iOS/Android Devices"
"Python, MQTT" → "Swift/Kotlin, Firebase"
"Hardware testing" → "Device testing (Xcode/Android Studio)"
"systemd service" → "App Store/Play Store deployment"
```

### API/Backend
```bash
# In .cursorrules, replace:
"Raspberry Pi" → "AWS/Docker"
"Hardware testing" → "Integration/API testing"
"systemd service" → "Container/serverless deployment"
```

### Desktop App
```bash
# In .cursorrules, replace:
"Raspberry Pi" → "Windows/Mac/Linux"
"Hardware testing" → "Cross-platform testing"
"systemd service" → "Installer/packaging (MSI/DMG)"
```

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Copy files (script) | 1 min |
| Customize .cursorrules | 5-10 min |
| Update examples in guides | 5 min |
| Customize templates | 5-10 min |
| Set up GitHub labels | 1 min |
| Configure project board | 5 min |
| Test workflow | 5 min |
| **Total (Recommended)** | **15-30 min** |

---

## 🆘 Common Issues

### "Agent not responding"
- ✅ Close/reopen Cursor IDE
- ✅ Ensure `.cursorrules` is in repo root
- ✅ Try: `@manager help`

### "Wrong technology mentioned"
- ✅ Search `.cursorrules` for old project name
- ✅ Update all references

### "Labels not moving issues"
- ✅ Check workflows exist (Project → ⋮ → Workflows)
- ✅ Verify label names match exactly
- ✅ Test: `gh issue edit <NUM> --add-label "status: requirements"`

---

## 📚 Full Documentation

For detailed information, see:
- **Complete guide:** `WORKFLOW_EXPORT_GUIDE.md`
- **Workflow details:** `MULTI_AGENT_GUIDE.md`
- **Agent reference:** `AGENTS_README.md`
- **Issue workflow:** `docs/development/MULTI_AGENT_ISSUE_WORKFLOW.md`

---

## 🎓 After Export

### Train Your Team
Share these files:
1. `MULTI_AGENT_GUIDE.md` - Quick start
2. `AGENTS_README.md` - Comprehensive guide

### First Sprint
```
@manager Let's work on issue #1
```

### Optimize Workflow
```
@coach After 2 weeks:
Can you analyze our workflow and suggest improvements?
```

---

**Ready? Run the export script! 🚀**

```bash
./scripts/export_workflow.sh /path/to/your-repo
```




