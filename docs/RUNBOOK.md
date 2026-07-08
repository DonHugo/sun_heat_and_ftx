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
- **CSS:** v=37
- **JS:** v=27

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
```

##### 4a. Deploy BACKEND code (⚠️ CRITICAL — git pull is NOT enough)

**The backend runs from `/opt/solar_heating_v3/` which is a PLAIN COPY, not a
git checkout.** `git pull` in `/home/pi/solar_heating` updates the *source* but
NOT what the service executes. You MUST copy changed backend `.py` files into
`/opt/solar_heating_v3/` with the rm+cp pattern, then restart the service.

```bash
# Copy each changed backend file (example: all 5 that night cooling touched)
ssh pi@192.168.0.18 'SRC=/home/pi/solar_heating/python/v3; DST=/opt/solar_heating_v3; \
  for f in config.py main_system.py mqtt_handler.py api_server.py api_models.py; do \
    sudo rm "$DST/$f" && sudo cp "$SRC/$f" "$DST/$f" && echo "deployed $f"; \
  done'

# Restart the service so it loads the new backend code
ssh pi@192.168.0.18 "sudo systemctl restart solar_heating_v3.service && sleep 6 && systemctl is-active solar_heating_v3.service"

# Verify :5001 is bound by main_system.py (NOT the mock) and no fatal errors
ssh pi@192.168.0.18 "sudo ss -ltnp | grep 5001"
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service --since '1 min ago' --no-pager | grep -iE 'error|traceback' | grep -viE 'MegaBAS sensor 5|TaskMaster AI connection'"
```

##### 4b. Deploy FRONTEND files
```bash
# Deploy index.html
ssh pi@192.168.0.18 "sudo rm /opt/solar_heating/frontend/index.html && sudo cp /home/pi/solar_heating/python/v3/frontend/index.html /opt/solar_heating/frontend/index.html"

# Deploy JavaScript
ssh pi@192.168.0.18 "sudo rm /opt/solar_heating/frontend/static/js/dashboard.js && sudo cp /home/pi/solar_heating/python/v3/frontend/static/js/dashboard.js /opt/solar_heating/frontend/static/js/dashboard.js"

# Deploy CSS (if changed)
ssh pi@192.168.0.18 "sudo rm /opt/solar_heating/frontend/static/css/style.css && sudo cp /home/pi/solar_heating/python/v3/frontend/static/css/style.css /opt/solar_heating/frontend/static/css/style.css"

# Fix ownership to www-data (rm+cp as root leaves files root-owned)
ssh pi@192.168.0.18 "sudo chown www-data:www-data /opt/solar_heating/frontend/index.html /opt/solar_heating/frontend/static/js/dashboard.js /opt/solar_heating/frontend/static/css/style.css"

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

### Issue: Two Services Competing for Port 5001 (MQTT/HA "Disconnected")
**Symptom:** Web GUI "System Diagnostics" panel shows MQTT Status = **Disconnected** and Home Assistant Status = **Disconnected**, even though the broker is reachable and `main_system.py` is running.

**Root Cause:** Two systemd units were both trying to bind port 5001:
- `solar_heating_api.service` — ran `python/v3/run_api_server.py`, a standalone mock using `MockSolarSystem` (no `.mqtt` attribute).
- `solar_heating_v3.service` — runs `main_system.py`, which embeds the real API server (see `main_system.py` lines ~692-717) backed by the live `SolarHeatingSystem`.

Whichever bound first won the port. When the mock won, the GUI's dashboard polled `/api/mqtt` on the mock and got `connected: false` because `MockSolarSystem` has no MQTT handler. The frontend (`dashboard.js` lines 819-822) derives HA status from the MQTT status, so both indicators flipped to Disconnected together.

**Immediate Solution:**
1. `sudo systemctl stop solar_heating_api.service`
2. `sudo systemctl restart solar_heating_v3.service` (so it binds :5001)
3. Verify: `curl http://localhost:5001/api/mqtt` → `{"connected": true, ...}`

**⚠️ `disable` is NOT enough — it will come back on reboot.** (Confirmed 2026-07-03.)
`solar_heating_web_gui.service` pulled the mock in via `Wants=solar_heating_api.service`
with `After=...solar_heating_v3.service`, so on every boot the mock started *after* v3
and could win the port race. A `disabled` unit still starts when another enabled unit
`Wants` it. Two additional steps are required for a permanent fix:

4. **Remove the dependency at the source** — delete the `Wants=solar_heating_api.service`
   line from `/etc/systemd/system/solar_heating_web_gui.service` and change its
   `After=network.target solar_heating_api.service` to `After=network.target solar_heating_v3.service`,
   then `sudo systemctl daemon-reload`.
5. **Mask the mock** so nothing can ever start it (belt-and-braces):
   ```bash
   # `mask` refuses when a real file exists at the unit path, so move it aside first:
   sudo mv /etc/systemd/system/solar_heating_api.service /etc/systemd/system/solar_heating_api.service.disabled.$(date +%Y%m%d)
   sudo systemctl mask solar_heating_api.service    # -> symlink to /dev/null
   ```
6. **Prove it survives reboot:** `sudo systemctl reboot`, then after boot verify
   `sudo ss -ltnp | grep 5001` shows `main_system.py` (not `run_api_server.py`) and
   `/api/status` returns `system_state` with ~66 keys incl. `solar_energy_today`
   (the mock's `system_state` has only 6 keys and no energy fields — a fast tell).

**Diagnostic fast-tells that the mock (not the real system) is answering :5001:**
- `temperatures.tank == 65.5` and `solar_collector == 72.1` — these are the hardcoded
  fallback values in `api_server.py` (the mock lacks a `.temperatures` dict).
- `mqtt_status.connected == false` while `mosquitto` is `active`.
- `system_state` has 6 keys (`cartridge_heater, last_update, manual_control, mode, primary_pump, test_mode`) instead of ~66.

The standalone script `python/v3/run_api_server.py` has been marked DEPRECATED with a module-level header and a runtime guard that exits if invoked directly. Do not re-enable `solar_heating_api.service`.

**Also removed during this incident:** the dead `solar-heating-gui.service` unit — it
pointed at a deleted file (`web_interface/app_improved_mqtt.py`) and was in a systemd
restart loop (32,500+ restarts). It was `disable --now`'d and the unit file removed.

**Related commits:**
- `99227d5` — `api_server.py::_get_mqtt_status()` uses `getattr(self.solar_system, "mqtt", None)` for defensive attribute access.
- `38a1eca` — `mqtt_handler.py` reconnect refactor (daemon thread, lock-guarded).
- `bb8d218` — `mqtt_handler.py::is_connected()` delegates to paho client state.

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

### Phase 5: MQTT/HA Diagnostics Fix & API Service Consolidation
- **Issue:** System Diagnostics panel showed MQTT and Home Assistant as Disconnected.
- **Root cause:** `solar_heating_api.service` (mock) and `solar_heating_v3.service` (real) both competed for port 5001; mock has no MQTT handler.
- **Fix:**
  - Hardened `api_server.py::_get_mqtt_status()` with `getattr` (`99227d5`).
  - Refactored `mqtt_handler.py` reconnect logic (`38a1eca`).
  - `is_connected()` now delegates to paho's own state (`bb8d218`).
  - Disabled `solar_heating_api.service`; deprecated `run_api_server.py`.
- **Verification:** `/api/mqtt` returns `connected: true`; zero DEBUG log noise; GUI polls succeed.
- **Status:** ✅ DEPLOYED

### Phase 6: Port 5001 Race — Permanent Hardening (2026-07-03)
- **Issue:** Regression of Phase 5 — GUI again showed MQTT/HA Disconnected, tank 65.5°C /
  collector 72.1°C (fallback values), and Energy Today 0.0 kWh. `disable` from Phase 5 had
  NOT prevented recurrence.
- **Root cause (deeper than Phase 5):** `run_api_server.py` (mock, PID 533) held :5001 while
  the real `main_system.py` (PID 532) ran without the port. The mock was still running
  despite being `disabled` because `solar_heating_web_gui.service` had
  `Wants=solar_heating_api.service` — an enabled unit's `Wants` starts a disabled unit.
- **Permanent fix (reboot-proven):**
  - Removed `Wants=solar_heating_api.service` from `solar_heating_web_gui.service`; set its
    `After=` to `solar_heating_v3.service`.
  - `mask`ed `solar_heating_api.service` (moved real file aside → symlink to /dev/null).
  - `disable --now` + removed the dead `solar-heating-gui.service` (deleted target file,
    32,500+ restart loop).
  - Synced Pi from `bb8d218` → `6f73903` (26 commits). Pi had uncommitted local edits to
    `api_server.py` (an older intermediate version) and `mqtt_handler.py` (identical to
    origin). Backed both up to `/home/pi/solar_backups/` + `git stash@{0}` before syncing.
    The sync also fixed `service_status.mqtt` reporting `inactive` (now maps `mqtt`→`mosquitto`)
    and raised the API rate limits.
- **Verification:** Rebooted the Pi; confirmed `main_system.py` (not the mock) binds :5001,
  `mqtt.connected: true`, `service_status.mqtt: active`, real temps, energy present, GUI HTTP 200.
- **Status:** ✅ DEPLOYED & REBOOT-VERIFIED
- **Lesson:** For a unit that must never run, `disable` alone is insufficient if any enabled
  unit `Wants`/`Requires` it. Break the dependency at the source AND `mask` the unit, then
  prove it with a reboot.

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
