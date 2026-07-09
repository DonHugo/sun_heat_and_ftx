# Deployment Runbook

**Purpose:** Step-by-step guide for deploying code to production  
**Last Updated:** October 31, 2025  
**Owner:** @manager / @validator  
**Target Environment:** Raspberry Pi (rpi-solfangare-2)

---

## 📋 Overview

This runbook provides a detailed, step-by-step process for deploying code changes to the production Raspberry Pi. Follow these steps exactly to ensure safe, successful deployments.

**Zero Downtime Goal:** Most deployments should achieve zero downtime.

---

## ⚠️ Prerequisites

Before starting deployment, ensure:

- [ ] Pre-Deployment Checklist completed ([link](PRE_DEPLOYMENT_CHECKLIST.md))
- [ ] Code review passed
- [ ] All tests passing
- [ ] Hardware validation complete (if applicable)
- [ ] Rollback plan documented
- [ ] Current working commit hash noted: `___________`

**If any prerequisite is not met, STOP and complete it first.**

---

## 🚀 Deployment Steps

### Phase 1: Pre-Deployment Verification

#### Step 1.1: Verify Local Changes
```bash
# Check git status
git status

# Review what will be deployed
git diff origin/main

# Ensure you're on main branch
git branch
```

**Expected:** Clean working tree, on main branch

✅ **Checkpoint:** [ ] Local changes verified

---

#### Step 1.2: Test Environment Check
```bash
# Run environment verification
./scripts/test_production_env.sh
```

**Expected Output:**
```
✅ Connected to Raspberry Pi
✅ Production venv exists
✅ Python version: 3.11.x
✅ All dependencies satisfied
✅ Service is running
```

✅ **Checkpoint:** [ ] Environment healthy

---

#### Step 1.3: Document Current State
```bash
# Get current commit on Pi
ssh pi@192.168.0.18 "cd ~/solar_heating && git log --oneline -1"
```

**Document:**
- **Last Known Good Commit:** `_____________`
- **Current Service Status:** Running / Stopped
- **Current Uptime:** `_____________`

✅ **Checkpoint:** [ ] Current state documented

---

### Phase 2: Code Deployment

#### Step 2.1: Stop Service (Optional - for major changes)

**Note:** Skip this for minor changes that support hot reload

```bash
# Stop service
ssh pi@192.168.0.18 "sudo systemctl stop solar_heating_v3.service"

# Verify stopped
ssh pi@192.168.0.18 "systemctl is-active solar_heating_v3.service"
```

**Expected:** `inactive`

✅ **Checkpoint:** [ ] Service stopped (if applicable) / [ ] N/A

---

#### Step 2.2: Pull Latest Code
```bash
# Pull from GitHub
ssh pi@192.168.0.18 "cd ~/solar_heating && git pull"
```

**Expected Output:**
```
From github.com:DonHugo/sun_heat_and_ftx
   abc123..def456  main -> origin/main
Updating abc123..def456
Fast-forward
 python/v3/main_system.py | 10 +++++-----
 1 file changed, 5 insertions(+), 5 deletions(-)
```

**If conflicts occur:**
```bash
# Stash local changes
ssh pi@192.168.0.18 "cd ~/solar_heating && git stash"

# Pull again
ssh pi@192.168.0.18 "cd ~/solar_heating && git pull"

# If you need the local changes back (rare):
ssh pi@192.168.0.18 "cd ~/solar_heating && git stash pop"
```

✅ **Checkpoint:** [ ] Code pulled successfully

---

#### Step 2.3: Sync Code to Runtime Directory (`/opt`) ⚠️ CRITICAL

> **IMPORTANT — the service does NOT run from the git repo.**
> The systemd unit runs from `/opt/solar_heating_v3/` (see `WorkingDirectory`
> and `ExecStart` in the unit file), which holds a **root-owned copy** of the
> code — it is NOT a git checkout. `git pull` in `~/solar_heating` only updates
> the repo; you MUST copy changed files into `/opt/solar_heating_v3/` or the
> running service keeps executing the old code (a restart alone changes nothing).

```bash
# Back up the current runtime file first (rollback point)
ssh pi@192.168.0.18 "sudo cp -p /opt/solar_heating_v3/main_system.py /opt/solar_heating_v3/main_system.py.bak-$(date +%Y%m%d_%H%M%S)"

# Copy the changed file(s) from repo -> /opt (preserve root ownership)
ssh pi@192.168.0.18 "sudo cp ~/solar_heating/python/v3/main_system.py /opt/solar_heating_v3/main_system.py && sudo chown root:root /opt/solar_heating_v3/main_system.py"
```

**Copy every file your change touched** (e.g. `config.py`, `mqtt_handler.py`,
`hardware_interface.py`, `api_server.py`). To see what changed:

```bash
ssh pi@192.168.0.18 "cd ~/solar_heating && git diff --name-only HEAD~1 -- python/v3/"
```

> **Note on dependencies:** the production venv also lives at
> `/opt/solar_heating_v3/bin/`. If `requirements.txt` changed, install into it
> (see Phase 3) — NOT into `~/solar_heating/python/v3/venv`, which is unused.

✅ **Checkpoint:** [ ] Changed files copied to `/opt/solar_heating_v3/`

---

#### Step 2.4: Verify Deployed Code
```bash
# Verify correct commit is deployed in the repo
ssh pi@192.168.0.18 "cd ~/solar_heating && git log --oneline -1"

# Syntax check the file that ACTUALLY runs (in /opt), using the production venv
ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/python3 -m py_compile /opt/solar_heating_v3/main_system.py"

# Confirm /opt matches the repo (no diff = copy succeeded)
ssh pi@192.168.0.18 "diff ~/solar_heating/python/v3/main_system.py /opt/solar_heating_v3/main_system.py && echo 'IN SYNC' || echo 'MISMATCH - re-copy'"
```

**Expected:** Commit hash matches what you deployed, no syntax errors, `IN SYNC`

✅ **Checkpoint:** [ ] Deployed code verified in `/opt`

---

### Phase 3: Dependency Management

#### Step 3.1: Check for New Dependencies
```bash
# Check if requirements.txt changed
ssh pi@192.168.0.18 "cd ~/solar_heating && git diff HEAD~1 python/v3/requirements.txt"
```

**If requirements.txt changed, proceed to Step 3.2**  
**If unchanged, skip to Phase 4**

✅ **Checkpoint:** [ ] Dependencies checked

---

#### Step 3.2: Install New Dependencies (if needed)
```bash
# Install from requirements.txt
ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/pip3 install -r ~/solar_heating/python/v3/requirements.txt --break-system-packages"
```

**Expected Output:**
```
Requirement already satisfied: package1==1.2.3
Collecting package2==4.5.6
  Using cached ...
Successfully installed package2-4.5.6
```

✅ **Checkpoint:** [ ] Dependencies installed

---

#### Step 3.3: Verify Dependencies
```bash
# Run dependency verification
./scripts/verify_deps.sh
```

**Expected:** All dependencies satisfied

✅ **Checkpoint:** [ ] Dependencies verified

---

### Phase 4: Service Restart & Verification

#### Step 4.1: Restart Service
```bash
# Restart the service
ssh pi@192.168.0.18 "sudo systemctl restart solar_heating_v3.service"

# Wait for service to initialize
sleep 8
```

✅ **Checkpoint:** [ ] Service restarted

---

#### Step 4.2: Verify Service Started
```bash
# Check service status
ssh pi@192.168.0.18 "sudo systemctl status solar_heating_v3.service --no-pager | head -20"
```

**Expected Output:**
```
● solar_heating_v3.service - Solar Heating System v3
     Loaded: loaded (/etc/systemd/system/solar_heating_v3.service; enabled)
     Active: active (running) since ...
     Main PID: 12345
     Tasks: 7
```

**If service failed:**
1. Check logs immediately (Step 4.4)
2. Identify error
3. Consider rollback (Phase 6)

✅ **Checkpoint:** [ ] Service running

---

#### Step 4.3: Quick Smoke Tests

##### Test 1: API Responds
```bash
ssh pi@192.168.0.18 "curl -s http://localhost:5001/api/status | python3 -m json.tool | head -20"
```

**Expected:** Valid JSON with system status

✅ **Status:** [ ] PASS / [ ] FAIL

---

##### Test 2: Check for Immediate Errors
```bash
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service --since '2 minutes ago' --no-pager | grep -i 'error\|failed\|exception' | head -20"
```

**Expected:** No errors (or only expected/known errors)

✅ **Status:** [ ] PASS / [ ] FAIL

---

##### Test 3: Core Functionality (if applicable)
```bash
# Test main feature deployed
[Add specific test command for the feature]
```

**Expected:** [Expected behavior]

✅ **Status:** [ ] PASS / [ ] FAIL / [ ] N/A

---

#### Step 4.4: Monitor Service Logs
```bash
# Watch logs for 5 minutes
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service -f"
```

**Watch for:**
- ✅ Normal operation logs
- ❌ Error messages
- ❌ Warnings
- ❌ Unexpected behavior
- ❌ Resource issues

**Duration:** Monitor for at least 5 minutes

✅ **Checkpoint:** [ ] Service stable (5 min)

---

### Phase 5: Post-Deployment Verification

#### Step 5.1: Service Health Check
```bash
# Check service is still running
ssh pi@192.168.0.18 "systemctl is-active solar_heating_v3.service && echo '✅ Service Running' || echo '❌ Service Down'"
```

**Expected:** `✅ Service Running`

✅ **Checkpoint:** [ ] Service healthy

---

#### Step 5.2: Resource Usage Check
```bash
# Check CPU and memory
ssh pi@192.168.0.18 "top -b -n 1 | head -20"
```

**Normal Values:**
- **CPU:** < 50% under normal load
- **Memory:** < 500MB
- **No zombie processes**

**If abnormal:** Investigate before declaring success

✅ **Checkpoint:** [ ] Resources normal

---

#### Step 5.3: Extended Monitoring (15-30 minutes)

For critical deployments, monitor for extended period:

```bash
# Monitor logs for 15-30 minutes
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service -f"
```

**Watch for:**
- Memory leaks (increasing memory over time)
- Repeated errors
- Performance degradation
- Unexpected behavior

✅ **Checkpoint:** [ ] Extended monitoring complete

---

### Phase 6: Rollback Procedure (If Needed)

**Use this procedure if deployment fails or causes issues**

#### Step 6.1: Stop Service
```bash
ssh pi@192.168.0.18 "sudo systemctl stop solar_heating_v3.service"
```

---

#### Step 6.2: Rollback Code

> **Remember:** the service runs from `/opt/solar_heating_v3/`, so a rollback
> must restore the file(s) there — resetting only the git repo is not enough.

**Option A — fastest: restore the `.bak` backup taken in Step 2.3**
```bash
# List available runtime backups
ssh pi@192.168.0.18 "ls -la /opt/solar_heating_v3/main_system.py.bak-*"

# Restore the pre-deploy backup (pick the right timestamp)
ssh pi@192.168.0.18 "sudo cp -p /opt/solar_heating_v3/main_system.py.bak-<TIMESTAMP> /opt/solar_heating_v3/main_system.py && sudo chown root:root /opt/solar_heating_v3/main_system.py"
```

**Option B — from git: reset the repo, then re-sync to `/opt`**
```bash
# Roll the repo back to the last known good commit
ssh pi@192.168.0.18 "cd ~/solar_heating && git reset --hard <last-good-commit>"
ssh pi@192.168.0.18 "cd ~/solar_heating && git log --oneline -1"

# CRITICAL: copy the rolled-back file(s) into /opt (repo reset alone does nothing)
ssh pi@192.168.0.18 "sudo cp ~/solar_heating/python/v3/main_system.py /opt/solar_heating_v3/main_system.py && sudo chown root:root /opt/solar_heating_v3/main_system.py"
```

**Rollback to Commit:** `<from Step 1.3>`

---

#### Step 6.3: Rollback Dependencies (if needed)
```bash
# If dependencies were changed, reinstall old versions
ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/pip3 install -r ~/solar_heating/python/v3/requirements.txt --break-system-packages --force-reinstall"
```

---

#### Step 6.4: Restart Service
```bash
ssh pi@192.168.0.18 "sudo systemctl start solar_heating_v3.service"
```

---

#### Step 6.5: Verify Rollback
```bash
# Check service is running with old code
ssh pi@192.168.0.18 "sudo systemctl status solar_heating_v3.service --no-pager | head -20"
```

---

#### Step 6.6: Document Rollback
**Reason for Rollback:** `_________________`  
**Rolled back to:** `<commit-hash>`  
**Timestamp:** `_________________`

✅ **Checkpoint:** [ ] Rollback complete and documented

---

## 📊 Deployment Checklist

Use this quick checklist during deployment:

### Pre-Deployment
- [ ] Pre-deployment checklist completed
- [ ] Code review passed
- [ ] Tests passing
- [ ] Rollback plan ready
- [ ] Current commit documented

### Deployment
- [ ] Environment verified
- [ ] Code pulled successfully
- [ ] Dependencies updated (if needed)
- [ ] Service restarted successfully
- [ ] Service is running

### Post-Deployment
- [ ] Smoke tests passed
- [ ] No errors in logs
- [ ] Service stable (5+ min)
- [ ] Resource usage normal
- [ ] Extended monitoring complete (if critical)

### Documentation
- [ ] Deployment logged
- [ ] Issues documented (if any)
- [ ] GitHub issue updated
- [ ] Team notified (if applicable)

---

## 📝 Deployment Log Template

**Date:** [YYYY-MM-DD HH:MM]  
**Deployed by:** [Name/Agent]  
**Issue:** #[number]  
**Feature:** [Brief description]

**Commits Deployed:**
- `abc123` - [Commit message]
- `def456` - [Commit message]

**Dependencies Changed:** Yes / No  
**Service Downtime:** 0 seconds / [duration]

**Smoke Tests:**
- API Status: ✅ PASS
- Error Check: ✅ PASS
- Core Function: ✅ PASS

**Post-Deployment:**
- Service Status: ✅ Running
- Resource Usage: ✅ Normal
- Stability (5 min): ✅ Stable

**Issues Encountered:** None / [Description]

**Overall Status:** ✅ Success / ⚠️ Success with Issues / ❌ Failed (Rolled Back)

---

## 🎯 Deployment Types

### Type 1: Hot Deployment (Zero Downtime)
**Use for:** Minor code changes, bug fixes, non-breaking changes

**Process:**
1. Pull code
2. Restart service
3. Verify

**Downtime:** 0 seconds (service restart is quick)

---

### Type 2: Standard Deployment
**Use for:** Feature additions, moderate changes

**Process:**
1. Verify environment
2. Pull code
3. Update dependencies (if needed)
4. Restart service
5. Extended monitoring

**Downtime:** ~5-10 seconds during restart

---

### Type 3: Major Deployment
**Use for:** Breaking changes, major refactoring, architectural changes

**Process:**
1. Schedule maintenance window
2. Notify users (if applicable)
3. Stop service
4. Backup database/state
5. Deploy changes
6. Extensive testing
7. Extended monitoring (30+ minutes)

**Downtime:** May require scheduled downtime

---

## ⚠️ Troubleshooting

### Service Won't Start

**Symptoms:** Service status shows "failed"

**Steps:**
1. Check logs: `ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service -n 100 --no-pager"`
2. Look for specific error
3. Common causes:
   - Syntax error (run py_compile)
   - Missing dependency
   - Configuration error
   - Hardware access issue

**Solution:** Fix issue or rollback

---

### Syntax Error After Deployment

**Symptoms:** `SyntaxError` in logs

**Immediate Action:** ROLLBACK (Phase 6)

**Prevention:** Always run pre-deployment checklist

---

### Import Error

**Symptoms:** `ModuleNotFoundError` or `ImportError`

**Cause:** Missing dependency in production venv

**Solution:**
```bash
ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/pip3 install <missing-module> --break-system-packages"
ssh pi@192.168.0.18 "sudo systemctl restart solar_heating_v3.service"
```

---

### High Resource Usage

**Symptoms:** High CPU or memory usage

**Investigation:**
```bash
# Check processes
ssh pi@192.168.0.18 "top -b -n 1 | head -30"

# Check for memory leaks
ssh pi@192.168.0.18 "ps aux | grep python3"
```

**Action:** Monitor closely, consider rollback if degrading

---

## 📚 Related Documentation

- [Pre-Deployment Checklist](PRE_DEPLOYMENT_CHECKLIST.md)
- [Production Environment](PRODUCTION_ENVIRONMENT.md)
- [Validation Template](../../python/v3/docs/agent_templates/VALIDATION_TEMPLATE.md)
- [Multi-Agent Guide](../../MULTI_AGENT_GUIDE.md)

---

## 💡 Best Practices

1. **Always complete pre-deployment checklist**
2. **Test locally first** (syntax, imports)
3. **Deploy during low-traffic periods** (if possible)
4. **Have rollback plan ready**
5. **Monitor after deployment** (minimum 5 minutes)
6. **Document everything** (deployment log)
7. **Communicate status** (especially for major deployments)
8. **Learn from issues** (update runbook with lessons)

---

## ✅ Success Criteria

A deployment is considered successful when:

- [x] Service is running and stable
- [x] All smoke tests pass
- [x] No errors in logs
- [x] Resource usage is normal
- [x] Stable for at least 5 minutes
- [x] Core functionality works
- [x] No rollback required

---

**Questions?**
- Review [Production Environment](PRODUCTION_ENVIRONMENT.md) for environment details
- Check [Pre-Deployment Checklist](PRE_DEPLOYMENT_CHECKLIST.md) for preparation steps
- Ask @manager or @validator for guidance

*Last Updated: October 31, 2025 by @coach*

