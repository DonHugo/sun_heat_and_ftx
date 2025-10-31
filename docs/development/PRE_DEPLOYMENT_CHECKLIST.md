# Pre-Deployment Checklist

**Purpose:** Catch issues before they reach production  
**When to Use:** Before every commit that will be deployed to Raspberry Pi  
**Mandatory:** YES - No exceptions!

---

## 🔍 Phase 1: Local Code Validation

### Syntax Check (MANDATORY)
```bash
# Check syntax of modified files
python3 -m py_compile python/v3/main_system.py
python3 -m py_compile python/v3/api_server.py
python3 -m py_compile python/v3/api_models.py

# Or check all Python files
find python/v3 -name "*.py" -exec python3 -m py_compile {} \;
```

**Status:** [ ] PASS / [ ] FAIL

### Import Check
```bash
# Test that all imports work
cd python/v3
python3 -c "from api_server import create_api_server; print('✅ OK')"
python3 -c "from api_models import ControlRequest; print('✅ OK')"
python3 -c "import main_system; print('✅ OK')"
```

**Status:** [ ] PASS / [ ] FAIL

### Linting (if time permits)
```bash
pylint python/v3/api_server.py
```

**Status:** [ ] PASS / [ ] SKIP / [ ] FAIL

---

## 🔧 Phase 2: Environment Verification

### Check Production Python Environment
```bash
# Run environment verification script
./scripts/test_production_env.sh
```

**Expected Output:**
```
✅ Production venv exists
✅ Python version: 3.11.x
✅ Required packages installed
```

**Status:** [ ] PASS / [ ] FAIL

### Verify Dependencies
```bash
# Check all requirements.txt dependencies are available
./scripts/verify_deps.sh
```

**Expected Output:**
```
✅ All dependencies satisfied
```

**Status:** [ ] PASS / [ ] FAIL

### Test with Production Python (if accessible)
```bash
# SSH to Pi and test imports
ssh pi@192.168.0.18 "cd ~/solar_heating/python/v3 && \
  /opt/solar_heating_v3/bin/python3 -c 'import flask; import pydantic; print(\"✅ OK\")'"
```

**Status:** [ ] PASS / [ ] SKIP / [ ] FAIL

---

## 📝 Phase 3: Code Review

### Self-Review Checklist
- [ ] No duplicate code sections
- [ ] All try/except blocks properly closed
- [ ] All if/else blocks properly closed
- [ ] All function definitions complete
- [ ] All class definitions complete
- [ ] No commented-out code (unless intentional)
- [ ] Indentation is consistent
- [ ] No merge conflict markers (<<<, ===, >>>)

### Git Diff Review
```bash
# Review what you're about to commit
git diff python/v3/main_system.py
```

**Checklist:**
- [ ] Only intended changes present
- [ ] No accidental deletions
- [ ] No debug print statements left in
- [ ] Comments are clear and helpful

**Status:** [ ] REVIEWED / [ ] NEEDS CHANGES

---

## 📦 Phase 4: Dependency Management

### If Adding New Dependencies

**Dependencies Added:** _______________

- [ ] Added to `requirements.txt`
- [ ] Verified available on piwheels.org (for ARM)
- [ ] Documented version requirements
- [ ] Tested installation on similar environment
- [ ] Checked for dependency conflicts

### Installation Command for Production
```bash
/opt/solar_heating_v3/bin/pip3 install <package> --break-system-packages
```

**Status:** [ ] N/A / [ ] DOCUMENTED

---

## 🧪 Phase 5: Testing

### Unit Tests
```bash
cd python/v3
pytest tests/
```

**Status:** [ ] PASS / [ ] SKIP / [ ] FAIL

### Integration Tests (if applicable)
```bash
pytest tests/api/test_api_validation.py
```

**Status:** [ ] PASS / [ ] SKIP / [ ] FAIL

### Manual Testing Completed
- [ ] Tested main functionality locally
- [ ] Tested error handling
- [ ] Tested edge cases

---

## 🔄 Phase 6: Rollback Preparation

### Rollback Plan
**Last Known Good Commit:** _______________

```bash
# Know how to rollback if needed
git log --oneline -5
```

**Rollback Commands:**
```bash
# On local machine
git checkout <commit-hash> python/v3/main_system.py
git commit -m "Rollback: <reason>"
git push

# On Raspberry Pi
ssh pi@192.168.0.18 "cd ~/solar_heating && git pull && \
  sudo systemctl restart solar_heating_v3.service"
```

**Status:** [ ] DOCUMENTED

---

## 📋 Phase 7: Documentation

### Documentation Updated
- [ ] Code comments added/updated
- [ ] CHANGELOG updated
- [ ] Architecture docs updated (if needed)
- [ ] API docs updated (if applicable)
- [ ] README updated (if needed)

---

## ✅ Phase 8: Final Checks

### Before Committing
- [ ] All above phases completed
- [ ] No known issues remaining
- [ ] Commit message is clear and descriptive
- [ ] Ready for production deployment

### Commit Message Format
```
<type>(#issue): <subject>

<body>

Changes:
- Change 1
- Change 2

Tests: <status>
Syntax: ✅ Verified
Production: Ready
```

**Example:**
```
feat(#43): Add pydantic validation to API endpoints

Implements strict input validation using pydantic models
to prevent SQL injection and other attacks.

Changes:
- Added api_models.py with validation models
- Integrated validation decorator in api_server.py
- Updated requirements.txt

Tests: 120+ tests passing
Syntax: ✅ Verified
Production: Ready
```

---

## 🚀 Phase 9: Deployment Readiness

### Pre-Deployment Confirmation
- [ ] All checklist items completed
- [ ] Code reviewed and approved
- [ ] Tests passing
- [ ] Documentation complete
- [ ] Rollback plan ready
- [ ] Production environment verified

### Deployment Plan
- [ ] Deployment steps documented
- [ ] Service restart plan ready
- [ ] Monitoring plan in place
- [ ] Expected downtime: _____ (should be 0)

---

## ⚠️ RED FLAGS - DO NOT DEPLOY

If any of these are true, **STOP and fix before deploying:**

- ❌ Syntax errors present
- ❌ Import errors
- ❌ Tests failing
- ❌ Dependencies missing
- ❌ No rollback plan
- ❌ Unclosed try/except blocks
- ❌ Duplicate code sections
- ❌ Production environment not verified
- ❌ Git diff contains unexpected changes
- ❌ "Quick fix" without testing

---

## 📊 Checklist Summary

**Total Items:** 50+  
**Required for Deployment:** 40+ must be completed  

### Quick Status Check
```
✅ Syntax: ____
✅ Imports: ____
✅ Environment: ____
✅ Code Review: ____
✅ Dependencies: ____
✅ Testing: ____
✅ Rollback: ____
✅ Documentation: ____
✅ Final Checks: ____
```

**Overall Status:** [ ] READY TO DEPLOY / [ ] NOT READY

---

## 💡 Tips

1. **Use this checklist for EVERY production deployment**
2. **Don't skip steps to save time** - they save time by preventing issues
3. **If unsure, ask** - better to ask than to break production
4. **Document issues found** - improve the process continuously
5. **Automate what you can** - scripts in `/scripts/` directory

---

## 🔗 Related Documents

- [Production Environment](PRODUCTION_ENVIRONMENT.md)
- [Deployment Runbook](DEPLOYMENT_RUNBOOK.md)
- [Verification Scripts](../../scripts/)
- [Multi-Agent Guide](../../MULTI_AGENT_GUIDE.md)

---

**Remember:** Following this checklist would have prevented all 3 deployment failures in Issue #43!

*Last Updated: October 31, 2025*  
*Owner: @coach*

