# 📦 Exporting the Multi-Agent Workflow to Another Repository

This guide shows you how to replicate this multi-agent development workflow in any other project.

---

## 🎯 What You're Exporting

A complete **autonomous multi-agent development system** with:
- 8 specialized AI agents (@manager, @coach, @requirements, @architect, @tester, @developer, @reviewer, @validator)
- Automated GitHub project board integration
- TDD workflow (Test-Driven Development)
- Production deployment safeguards
- Documentation templates
- Pre-deployment checklists

**Time to set up:** 15-30 minutes  
**Works with:** Any software project (backend, frontend, embedded, etc.)

---

## 📋 EXPORT CHECKLIST

### Step 1: Copy Core Workflow Files (Required)

These files define the multi-agent system:

```bash
# From root of sun_heat_and_ftx repo:
cp .cursorrules /path/to/new-repo/
cp MULTI_AGENT_GUIDE.md /path/to/new-repo/
cp AGENTS_README.md /path/to/new-repo/
```

**What they do:**
- `.cursorrules` - Defines all 8 agents and their behaviors (used by Cursor IDE)
- `MULTI_AGENT_GUIDE.md` - Quick reference guide for developers
- `AGENTS_README.md` - Comprehensive guide with examples

---

### Step 2: Copy Agent Templates (Required)

These templates guide agents in producing consistent output:

```bash
# Create directory structure
mkdir -p /path/to/new-repo/docs/agent_templates

# Copy all templates
cp python/v3/docs/agent_templates/*.md /path/to/new-repo/docs/agent_templates/
```

**Templates included:**
- `MANAGER_TEMPLATE.md` - Project planning and orchestration
- `COACH_TEMPLATE.md` - Workflow analysis and improvements
- `REQUIREMENTS_TEMPLATE.md` - Requirements documentation
- `ARCHITECTURE_TEMPLATE.md` - Technical design documents
- `TEST_PLAN_TEMPLATE.md` - Test specifications
- `IMPLEMENTATION_TEMPLATE.md` - Implementation notes
- `REVIEW_TEMPLATE.md` - Code review reports
- `VALIDATION_TEMPLATE.md` - Hardware/production validation

---

### Step 3: Copy Development Documentation (Recommended)

These docs support the workflow process:

```bash
# Create directory
mkdir -p /path/to/new-repo/docs/development

# Copy key docs
cp docs/development/PRE_DEPLOYMENT_CHECKLIST.md /path/to/new-repo/docs/development/
cp docs/development/DEPLOYMENT_RUNBOOK.md /path/to/new-repo/docs/development/
cp docs/development/PRODUCTION_ENVIRONMENT.md /path/to/new-repo/docs/development/
cp docs/development/MULTI_AGENT_ISSUE_WORKFLOW.md /path/to/new-repo/docs/development/
```

**What they provide:**
- Pre-deployment checklist (50+ points) for safety
- Step-by-step deployment runbook
- Production environment documentation template
- Issue workflow documentation

---

### Step 4: Copy Helper Scripts (Optional but Useful)

```bash
# Create scripts directory
mkdir -p /path/to/new-repo/scripts

# Copy useful scripts
cp scripts/test_production_env.sh /path/to/new-repo/scripts/
cp scripts/verify_deps.sh /path/to/new-repo/scripts/
cp scripts/create_github_labels.sh /path/to/new-repo/scripts/

# Make them executable
chmod +x /path/to/new-repo/scripts/*.sh
```

**What they do:**
- `test_production_env.sh` - Verify production environment health
- `verify_deps.sh` - Compare requirements vs installed packages
- `create_github_labels.sh` - Set up GitHub labels for workflow

---

### Step 5: Copy Additional Reference Docs (Optional)

```bash
cp SETUP_COMPLETE.md /path/to/new-repo/
cp COACH_SUMMARY_WORKFLOW_IMPROVEMENTS.md /path/to/new-repo/
cp GITHUB_INTEGRATION_README.md /path/to/new-repo/
```

---

## 🔧 CUSTOMIZATION REQUIRED

After copying files, you **must customize** them for your new project:

### 1. Customize `.cursorrules`

**Find and replace project-specific content:**

```bash
# In the new repo's .cursorrules file:

# Replace project description
OLD: "Solar heating control system for Raspberry Pi"
NEW: "Your project description"

# Replace key technologies
OLD: "Python, MQTT, systemd, Home Assistant integration"
NEW: "Your tech stack (e.g., Node.js, React, PostgreSQL)"

# Replace hardware constraints (if not applicable)
OLD: "Hardware**: Raspberry Pi 4, relays, temperature sensors"
NEW: "Target Platform**: Your platform (e.g., AWS, Docker, Desktop)"

# Replace testing context
OLD: "Testing**: Must test hardware directly on Raspberry Pi"
NEW: "Testing**: Your testing requirements"
```

**Sections to customize in `.cursorrules`:**
1. Line 1-3: Project title and description
2. Lines ~550-560: "Project-Specific Context" section
3. Any references to "solar heating", "Raspberry Pi", "MQTT", etc.

---

### 2. Customize `MULTI_AGENT_GUIDE.md`

**Update examples to match your project:**

```markdown
# Find sections like:
**System**: Solar heating control system for Raspberry Pi

# Replace with:
**System**: [Your project description]

# Update technology examples:
**Key Technologies**: [Your tech stack]

# Update hardware references:
**Hardware**: [Your deployment target]

# Update testing approach:
**Testing**: [Your testing strategy]
```

---

### 3. Customize `AGENTS_README.md`

Update all example conversations to use your domain:

```markdown
# OLD Example:
"@manager I need to add email alerts for high temperature"

# NEW Example (for e-commerce project):
"@manager I need to add email alerts for low inventory"

# OLD Example:
"@requirements I want better sensor monitoring"

# NEW Example (for web app):
"@requirements I want better user analytics"
```

---

### 4. Customize Agent Templates

Each template in `docs/agent_templates/` has placeholder examples:

**Example from REQUIREMENTS_TEMPLATE.md:**
```markdown
# OLD:
## Example: Temperature Alert System

# NEW:
## Example: [Feature relevant to your project]
```

**Do this for all 8 templates** - replace examples with your domain.

---

### 5. Customize Development Docs

**`PRE_DEPLOYMENT_CHECKLIST.md`:**
- Update language-specific checks (Python → your language)
- Update environment checks (virtualenv → your env)
- Update service checks (systemd → your deployment)

**`PRODUCTION_ENVIRONMENT.md`:**
- Document YOUR production environment
- Update paths, services, and infrastructure

**`DEPLOYMENT_RUNBOOK.md`:**
- Document YOUR deployment process
- Update commands for your stack

---

## 🏷️ GITHUB SETUP

### Step 1: Create GitHub Labels

Run the label creation script (after customizing if needed):

```bash
cd /path/to/new-repo/scripts
./create_github_labels.sh
```

**This creates:**
- `status: requirements` (🔵 blue)
- `status: awaiting-approval` (🟡 yellow)
- `status: architecture` (🟣 purple)
- `status: testing` (🟠 orange)
- `status: in-progress` (🟢 green)
- `status: code-review` (🟤 brown)
- `status: ready-to-deploy` (🔴 red)
- `status: deployed` (⚫ black)

---

### Step 2: Create GitHub Project Board

1. Go to: `https://github.com/USERNAME/REPO/projects`
2. Click **"New project"**
3. Choose **"Board"** layout
4. Name it: `Development Workflow`

---

### Step 3: Configure Project Board Status Field

1. In your project board, click **"⋮"** → **"Settings"**
2. Go to **"Fields"**
3. Add/edit **"Status"** field with these values:
   - 📋 Requirements
   - ⏳ Awaiting Approval
   - 🏗️ Architecture
   - 🧪 Testing
   - 💻 In Progress
   - 👀 Code Review
   - 🚀 Ready to Deploy
   - ✅ Done

---

### Step 4: Set Up Workflow Automations

For EACH status label, create an automation:

**Example: Link "status: requirements" label → "📋 Requirements"**

1. Click **"⋮"** → **"Workflows"**
2. Click **"+ Add workflow"**
3. Choose **"Label is added to issue"**
4. Select label: `status: requirements`
5. Action: **"Set status to"** → `📋 Requirements`
6. Save

**Repeat for all 8 labels** (takes ~5 minutes)

---

### Step 5: Set Up Project Board View Filters (Optional)

Create filtered views:
- **"In Progress"** - Status = In Progress OR Code Review
- **"Needs Attention"** - Status = Awaiting Approval
- **"Deployed"** - Status = Done

---

## ✅ VERIFICATION CHECKLIST

After setup, verify everything works:

### Local Verification
- [ ] `.cursorrules` exists in new repo root
- [ ] `MULTI_AGENT_GUIDE.md` exists
- [ ] `docs/agent_templates/` has 8 template files
- [ ] Project-specific references updated in all files
- [ ] Scripts are executable (`chmod +x`)

### Cursor IDE Verification
- [ ] Open new repo in Cursor
- [ ] Type `@manager` - should show agent in autocomplete
- [ ] Try: `@coach analyze workflow` - agent should respond
- [ ] Try: `@requirements help` - agent should respond

### GitHub Verification
- [ ] Run: `gh label list` - shows 8 status labels
- [ ] GitHub project board exists
- [ ] Project board has Status field with 8 values
- [ ] Workflows are configured (8 automations)

### End-to-End Test
- [ ] Create test issue: `gh issue create -t "Test workflow" -b "Testing multi-agent"`
- [ ] Update label: `gh issue edit <NUM> --add-label "status: requirements"`
- [ ] Check project board - issue should move to "📋 Requirements"
- [ ] Success! 🎉

---

## 🎯 QUICK START (After Export)

In your new repo, try this:

```
@manager I want to add [some feature]
```

**Expected behavior:**
1. Manager analyzes the request
2. Routes to @requirements
3. Requirements gathers info collaboratively with you
4. **PAUSE** - You approve requirements
5. Manager autonomously runs: Architecture → Testing → Implementation → Review
6. Updates GitHub labels automatically at each phase
7. **PAUSE** - You approve production deployment
8. Manager closes issue as deployed

**You should see:**
- GitHub issue labels changing automatically
- Project board card moving between columns
- Progress updates every 2-5 minutes
- Clear indication when your approval is needed (⚠️)

---

## 🔄 PROJECT-TYPE CUSTOMIZATIONS

### For Web Applications
- Update hardware testing → browser/E2E testing
- Update production env → cloud/container deployment
- Update pre-deployment checks → frontend build, backend migrations

### For APIs/Backend Services
- Update hardware testing → integration/API testing
- Update production env → server/container deployment
- Update pre-deployment checks → database migrations, API versioning

### For Desktop Applications
- Update hardware testing → cross-platform testing
- Update production env → installer/packaging process
- Update pre-deployment checks → code signing, dependencies

### For Mobile Applications
- Update hardware testing → device testing (iOS/Android)
- Update production env → app store deployment
- Update pre-deployment checks → app review guidelines, certificates

### For Embedded/IoT (Like This Project!)
- Keep hardware testing requirements
- Update production env → your target hardware
- Update pre-deployment checks → flashing process, bootloader

---

## 🆘 TROUBLESHOOTING

### Issue: Agents not responding in Cursor
**Solution:** 
1. Close and reopen Cursor
2. Ensure `.cursorrules` is in repo root
3. Try: `@manager help`

### Issue: GitHub labels not moving issues
**Solution:**
1. Verify workflows exist: Project → ⋮ → Workflows
2. Check label names match exactly (case-sensitive)
3. Test manually: `gh issue edit <NUM> --add-label "status: requirements"`

### Issue: Agents mention wrong technology/project
**Solution:**
- You missed customizing `.cursorrules`
- Search for old project references and replace them

### Issue: Pre-deployment checklist doesn't match my stack
**Solution:**
- Customize `docs/development/PRE_DEPLOYMENT_CHECKLIST.md`
- Update language-specific sections
- Update environment sections

---

## 📚 ADDITIONAL RESOURCES

After exporting, reference these docs:

1. **For developers on the team:**
   - Share `MULTI_AGENT_GUIDE.md` (quick start)
   - Share `AGENTS_README.md` (comprehensive guide)

2. **For understanding the workflow:**
   - Read `docs/development/MULTI_AGENT_ISSUE_WORKFLOW.md`

3. **For workflow improvements:**
   - Use `@coach` to analyze and optimize
   - Reference `COACH_SUMMARY_WORKFLOW_IMPROVEMENTS.md`

---

## 🎓 BEST PRACTICES

### Do's ✅
- **Do** customize examples to match your domain
- **Do** update technology references in all files
- **Do** test the workflow with a simple issue first
- **Do** train your team on agent usage
- **Do** use `@coach` regularly for retrospectives
- **Do** update documentation as you evolve the workflow

### Don'ts ❌
- **Don't** skip customization - generic examples confuse agents
- **Don't** modify agent role definitions without understanding them
- **Don't** skip GitHub setup - automation is key
- **Don't** ignore the pre-deployment checklist
- **Don't** forget to make scripts executable

---

## 🚀 GOING FURTHER

### Evolving Your Workflow

This workflow is designed to evolve! Use `@coach` to:
- Identify bottlenecks
- Optimize processes
- Add new agent specializations
- Customize templates further

### Example Evolution:
```
@coach Our deployment process takes too long. Can you analyze and suggest improvements?
```

**Coach will:**
1. Analyze your current deployment workflow
2. Identify time sinks
3. Suggest automation opportunities
4. Update documentation with improvements

---

## ✨ SUMMARY

**Minimum Export (Core Workflow):**
```bash
# 3 files - 2 minutes
.cursorrules
MULTI_AGENT_GUIDE.md
AGENTS_README.md
```

**Recommended Export (Full System):**
```bash
# Core files
.cursorrules
MULTI_AGENT_GUIDE.md  
AGENTS_README.md

# Templates (8 files)
docs/agent_templates/*.md

# Development docs (4 files)
docs/development/PRE_DEPLOYMENT_CHECKLIST.md
docs/development/DEPLOYMENT_RUNBOOK.md
docs/development/PRODUCTION_ENVIRONMENT.md
docs/development/MULTI_AGENT_ISSUE_WORKFLOW.md

# Scripts (3 files)
scripts/test_production_env.sh
scripts/verify_deps.sh
scripts/create_github_labels.sh
```

**Total setup time:** 15-30 minutes  
**Benefit:** Autonomous, consistent, high-quality development workflow

---

## 📞 Questions?

After exporting, you can ask:

```
@coach I exported the workflow to my new repo. Can you help me customize it for [project type]?
```

The coach will guide you through project-specific customizations! 🎉

---

**Next Step:** Start copying files using the checklist above! 📦




