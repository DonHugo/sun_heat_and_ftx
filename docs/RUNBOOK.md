# Manager Agent Workflow

## SECTION 1: MANDATORY QUERY ROUTING

**Before ANY response, classify the request and follow the required verification steps:**

### Type A: State Inquiry
**Triggers:** "What did we do?", "Where are we?", "What's the status?", "Are we ready?", "What changed?", "What's deployed?", "Next steps?"

**REQUIRED TOOLS (in order):**
1. `git status` - Check for uncommitted changes
2. `Read` - Check relevant workflow files, code files
3. `Grep` - Search for recent changes (if applicable)
4. **THEN** synthesize response with Pre-Flight Checklist

### Type B: Action Request
**Triggers:** "Deploy X", "Update Y", "Create Z", "Fix W"

**REQUIRED TOOLS (in order):**
1. `Read` - Current config/state files
2. `git status` - Verify working tree state
3. Verify prerequisites exist (check dependencies, configs)
4. **THEN** execute or ask for clarification

### Type C: Troubleshooting
**Triggers:** "Why isn't X working?", "Debug Y", "Error in Z"

**REQUIRED TOOLS (in order):**
1. `Read` - Logs/error outputs
2. `bash` - Check service status
3. `Read` - Verify configuration files
4. **THEN** diagnose and propose solution

---

## SECTION 2: PRE-FLIGHT CHECKLIST (MANDATORY)

Every response to **State Inquiry** queries MUST include:

```
### Pre-Flight Verification
- [ ] Git status checked: [clean | X uncommitted files | list them]
- [ ] Relevant files read: [list files with line ranges]
- [ ] Current state matches assumption: [YES/NO + details]

### Current Status
[Your actual analysis here]

### Next Steps
[Actions with verified prerequisites]
```

---

## SECTION 3: INVESTIGATION MODE KEYWORDS

If user query contains **ANY** of these keywords, you **MUST** enter Investigation Mode:

- "what did we do"
- "where are we"
- "current status"
- "what's deployed"
- "what changed"
- "are we ready"
- "next steps"
- "what's left"
- "progress"
- "summary"

**Investigation Mode Protocol:**
1. Run `git status` first
2. Read last modified files (check timestamps)
3. Compare against known workflow checkpoints
4. Show Pre-Flight Checklist
5. Provide factual status report

---

## SECTION 4: SYSTEM ARCHITECTURE

### Production Server
- **Host:** `pi@192.168.0.18` (hostname: rpi-solfangare-2)
- **Main Service:** `solar_heating_v3.service` 
  - Runs: `/opt/solar_heating_v3/bin/python3 main_system.py`
  - Embeds Flask API server on port 5001
- **Frontend:** nginx serving from `/opt/solar_heating/frontend/` on port 80
- **Git Repo on Pi:** `/home/pi/solar_heating/`
- **Local Dev:** `/Users/hafs/Documents/Github/sun_heat_and_ftx/`

### Current Versions
- **CSS:** v=35
- **JS:** v=24

---

## SECTION 5: DEPLOYMENT WORKFLOW

### ⚠️ SAFETY GATE: File Caching on Pi

**NEVER use:** `cp -f` or `mv -f` (file system caching can prevent updates)

**ALWAYS use:**
```bash
sudo rm /target/file
sudo cp /source/file /target/file
```

**Verification Required:** After every copy, verify with `grep` or `wc -l` that the file actually changed.

### Step-by-Step Deployment Process

#### 1. Verify Current State (MANDATORY)
```bash
# Check git status
git status

# Check current file versions
Read python/v3/frontend/index.html  # Check cache versions
Read python/v3/frontend/static/js/dashboard.js  # Check recent changes
```

#### 2. Make Changes Locally
- Edit files in `/Users/hafs/Documents/Github/sun_heat_and_ftx/`
- Test changes if possible
- Increment cache versions when updating CSS/JS:
  - CSS: Update `?v=X` in index.html
  - JS: Update `?v=Y` in index.html

#### 3. Commit and Push
```bash
git add <files>
git commit -m "Clear description of changes"
git push origin main
```

#### 4. Deploy to Production
```bash
# Pull changes on Pi
ssh pi@192.168.0.18 "cd /home/pi/solar_heating && git pull origin main"

# Deploy index.html
ssh pi@192.168.0.18 "sudo rm /opt/solar_heating/frontend/index.html && sudo cp /home/pi/solar_heating/python/v3/frontend/index.html /opt/solar_heating/frontend/index.html"

# Deploy JavaScript
ssh pi@192.168.0.18 "sudo rm /opt/solar_heating/frontend/static/js/dashboard.js && sudo cp /home/pi/solar_heating/python/v3/frontend/static/js/dashboard.js /opt/solar_heating/frontend/static/js/dashboard.js"

# Deploy CSS (if changed)
ssh pi@192.168.0.18 "sudo rm /opt/solar_heating/frontend/static/css/style.css && sudo cp /home/pi/solar_heating/python/v3/frontend/static/css/style.css /opt/solar_heating/frontend/static/css/style.css"

# Deploy images (if new ones added)
ssh pi@192.168.0.18 "sudo rm /opt/solar_heating/frontend/static/images/<image> && sudo cp /home/pi/solar_heating/python/v3/frontend/static/images/<image> /opt/solar_heating/frontend/static/images/<image>"
```

#### 5. Verify Deployment (MANDATORY)
```bash
# Verify cache versions
ssh pi@192.168.0.18 "grep 'dashboard.js' /opt/solar_heating/frontend/index.html"

# Verify specific code changes
ssh pi@192.168.0.18 "grep -A2 '<search_pattern>' /opt/solar_heating/frontend/static/js/dashboard.js"

# Check line counts if major changes
ssh pi@192.168.0.18 "wc -l /opt/solar_heating/frontend/static/js/dashboard.js"
```

#### 6. Reload nginx
```bash
ssh pi@192.168.0.18 "sudo systemctl reload nginx"
```

#### 7. Test in Browser
- Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- Verify changes are visible
- Check browser console for errors

---

## SECTION 6: RESPONSE PROTOCOL ("Verify First")

**BEFORE responding to ANY user query:**

1. **Mentally prepend** `VERIFY:` to your response plan
2. **Execute verification tools first** (git status, Read, Grep)
3. **Show verification results** (use Pre-Flight Checklist for State Inquiries)
4. **THEN** provide analysis/action

**Example:**

User: "What did we do so far?"

Agent (internal): "VERIFY: git status, read recent files, check cache versions"

Agent (response):
```
### Pre-Flight Verification
- [x] Git status checked: clean, all changes committed
- [x] Relevant files read: dashboard.js (lines 650-670), index.html (line 652)
- [x] Current state: CSS v35, JS v24, last commit e84a0d2

### Current Status
[Analysis based on verified facts...]

### Next Steps
[Actions with prerequisites confirmed...]
```

---

## SECTION 7: COMMON PATTERNS

### Pattern: Updating Dashboard JavaScript
1. **Verify:** Read current dashboard.js, check cache version
2. **Edit:** Make changes locally
3. **Increment:** Cache version in index.html (JS v=X → v=X+1)
4. **Commit:** Both files together
5. **Deploy:** Use rm+cp pattern for both files
6. **Verify:** Grep for changes, check cache version
7. **Reload:** nginx
8. **Test:** Hard refresh browser

### Pattern: Fixing API Data Display Issues
1. **Check API:** `curl http://192.168.0.18:5001/api/status | python3 -m json.tool`
2. **Read frontend:** Check how data is extracted in dashboard.js
3. **Identify issue:** Backend stale data vs frontend display logic
4. **Fix appropriate layer:** Backend (main_system.py) or Frontend (dashboard.js)
5. **Test:** Verify fix addresses root cause

### Pattern: Replacing Emoji with Material Design Icons
1. **Search:** Grep for emoji in HTML/JS/CSS
2. **Replace:** With `<span class="mdi mdi-icon-name"></span>` or equivalent
3. **Verify:** MDI CSS is loaded (index.html includes MDI stylesheet)
4. **Test:** Visual confirmation in browser

---

## SECTION 8: KNOWN ISSUES & DISCOVERIES

### Issue: File Copy Doesn't Update
**Symptom:** `sudo cp -f source dest` completes without error but destination file unchanged

**Root Cause:** File system caching on Raspberry Pi

**Solution:** Always use `sudo rm dest && sudo cp source dest`

**Verification:** After copy, run `grep` or `wc -l` to confirm content changed

### Issue: Browser Shows Old Version
**Symptom:** Changes deployed but browser shows old dashboard

**Root Cause:** Browser caching of static assets

**Solution:** 
1. Increment cache version (`?v=X`) in index.html
2. Hard refresh browser (Ctrl+Shift+R)

### Issue: Stale API Data Displayed
**Symptom:** Frontend shows non-zero rate when device is OFF

**Root Cause:** Backend doesn't reset rate fields when devices turn off

**Solution:** Frontend checks device status before displaying rate:
```javascript
const deviceOn = data.system_state?.device_status ?? false;
const rate = deviceOn ? (data.system_state?.device_rate ?? 0) : 0;
```

---

## SECTION 9: PROJECT HISTORY

### Phase 1: Material Design Icons & BOB Branding
- Replaced all emoji with MDI icons
- Added BOB robot mascot (84x84px, bob1.png)
- Dark blue gradient theme
- Card-based layout with sidebar navigation

### Phase 2: Status Tab Data Fixes
- **Issue:** Runtime/energy fields showed `--` dashes
- **Fix:** Added field population in `updateSystemStatus()`
- **Commits:** `ed44b71`, `39ab40b`

### Phase 3: Tip Message Update
- **Issue:** Tip referenced non-existent "Dashboard tab"
- **Fix:** Updated to reference "toggle switches above"
- **Commit:** `b29930a`

### Phase 4: Energy Rate Display Fix
- **Issue:** Pellet stove rate showed 2.46 kW/h when stove OFF
- **Fix:** Check device status before displaying rates
- **Commit:** `e84a0d2`
- **Status:** ✅ DEPLOYED (JS v24)

---

## SECTION 10: CRITICAL REMINDERS

### Always Follow This Order:
1. 🔍 **VERIFY** current state (git status, Read files)
2. ✏️ **EDIT** files locally
3. 📝 **COMMIT** with clear message
4. 🚀 **DEPLOY** using rm+cp pattern
5. ✅ **VERIFY** deployment with grep/wc
6. 🔄 **RELOAD** nginx
7. 🧪 **TEST** in browser

### Never Do This:
- ❌ Make assumptions without checking files
- ❌ Use `cp -f` or `mv -f` on Pi
- ❌ Skip cache version increments
- ❌ Skip deployment verification
- ❌ Forget to reload nginx

### Always Do This:
- ✅ Run git status before responding to "what did we do"
- ✅ Read actual file contents, not just context
- ✅ Use Pre-Flight Checklist for state inquiries
- ✅ Verify file changes with grep after deployment
- ✅ Hard refresh browser after frontend changes

---

**This workflow document MUST be followed for every interaction. No exceptions.**
