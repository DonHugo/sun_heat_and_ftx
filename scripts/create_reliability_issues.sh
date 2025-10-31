#!/bin/bash
# Create High-Priority Reliability Issues
# This script creates 5 critical reliability issues

set -e

echo "🛡️  Creating High-Priority Reliability Issues..."
echo ""

# Issue F: Memory Leak
echo "=== Creating Issue F: Memory Leak in Long-Running Process ==="
gh issue create \
  --title "[BUG] Memory Leak in Long-Running Process" \
  --label "bug,priority: high,category: performance" \
  --milestone "v3.1 - Bug Fixes & Stability" \
  --body "## Bug Description

Memory usage grows continuously over days of operation.

**Observed Behavior:**
- Memory usage increases over time
- No plateau reached
- Eventually causes system slowdown or OOM

**Reproduction:**
- Run system for 7+ days
- Monitor memory with top/htop
- Observe continuous growth

**Expected Behavior:**
- Memory usage stabilizes after initial startup
- Garbage collection works properly
- No unbounded growth

**Impact:** High - Eventually requires restart

**Investigation Needed:**
- [ ] Profile memory usage
- [ ] Check for unclosed resources
- [ ] Review circular references
- [ ] Test with memory profiler (memory_profiler)
- [ ] Identify leak source

**Acceptance Criteria:**
- [ ] Memory leak identified
- [ ] Leak fixed
- [ ] 7-day stability test passes
- [ ] Memory usage documented

**Testing Command:**
\`\`\`bash
# Monitor memory over time
watch -n 60 'ps aux | grep python | grep main_system'
\`\`\`"

echo "✅ Issue F created"
echo ""

# Issue G: TaskMaster Crashes
echo "=== Creating Issue G: TaskMaster AI Errors Crash Main System ==="
gh issue create \
  --title "[BUG] TaskMaster AI Errors Crash Main System" \
  --label "bug,priority: high,component: taskmaster,category: reliability" \
  --milestone "v3.1 - Bug Fixes & Stability" \
  --body "## Bug Description

Errors in TaskMaster AI component can crash the entire system.

**Current Behavior:**
- TaskMaster exceptions propagate to main system
- No error isolation
- System goes down completely

**Expected Behavior:**
- TaskMaster errors isolated
- Main system continues operating
- Errors logged and reported
- Graceful degradation

**Impact:** High - Full system outage

**Required Actions:**
- [ ] Isolate TaskMaster in try/catch blocks
- [ ] Add error boundaries
- [ ] Implement fallback behavior (disable TaskMaster if failing)
- [ ] Test error scenarios
- [ ] Add TaskMaster health monitoring

**Acceptance Criteria:**
- [ ] TaskMaster errors don't crash main system
- [ ] Errors properly logged with context
- [ ] System continues operating without TaskMaster
- [ ] User notified of degradation via MQTT
- [ ] Automatic recovery attempts with backoff

**Test Scenarios:**
- TaskMaster API timeout
- TaskMaster returns invalid data
- TaskMaster process crash"

echo "✅ Issue G created"
echo ""

# Issue H: Sensor Errors
echo "=== Creating Issue H: Sensor Read Errors Cause System Crashes ==="
gh issue create \
  --title "[BUG] Sensor Read Errors Not Handled - Cause Crashes" \
  --label "bug,priority: high,component: sensors,category: reliability" \
  --milestone "v3.1 - Bug Fixes & Stability" \
  --body "## Bug Description

Errors when reading sensors cause system crashes instead of graceful handling.

**Current Behavior:**
- Sensor communication failure crashes system
- No retry logic
- No fallback behavior
- System requires restart

**Expected Behavior:**
- Sensor errors caught and logged
- Retry with exponential backoff (3 retries)
- Use last known good value temporarily
- Alert user but continue operating

**Impact:** High - Frequent system outages

**Affected Sensors:**
- RTD temperature sensors
- MegaBAS sensors
- Any I2C communication errors

**Required Actions:**
- [ ] Add error handling to all sensor reads
- [ ] Implement retry logic with exponential backoff
- [ ] Add sensor health monitoring
- [ ] Test communication failure scenarios
- [ ] Document error scenarios

**Acceptance Criteria:**
- [ ] Sensor errors don't crash system
- [ ] Automatic retry implemented (max 3 attempts)
- [ ] Errors logged with sensor ID and error type
- [ ] User notified via MQTT
- [ ] System stays operational with degraded sensors
- [ ] Last known good values used temporarily

**Test Scenarios:**
- Unplug sensor during operation
- I2C bus busy
- Invalid sensor reading (out of range)"

echo "✅ Issue H created"
echo ""

# Issue I: MQTT Publish Failures
echo "=== Creating Issue I: MQTT Publish Failures Silently Ignored ==="
gh issue create \
  --title "[BUG] MQTT Publish Failures Silently Ignored" \
  --label "bug,priority: high,component: mqtt,category: reliability" \
  --milestone "v3.1 - Bug Fixes & Stability" \
  --body "## Bug Description

Failed MQTT publishes are not logged or retried, causing silent data loss.

**Current Behavior:**
- Publish failures ignored
- No logging of failures
- No retry mechanism
- Data lost silently
- Home Assistant misses updates

**Expected Behavior:**
- Publish failures logged
- Automatic retry with backoff
- Alert on repeated failures
- Data queued for retry (limited queue)
- User notified

**Impact:** High - Silent data loss, unreliable monitoring

**Required Actions:**
- [ ] Add error handling to MQTT publish
- [ ] Implement retry queue (max 100 messages)
- [ ] Log all publish failures
- [ ] Add publish success/failure monitoring
- [ ] Test network failure scenarios

**Acceptance Criteria:**
- [ ] Publish failures logged with topic and error
- [ ] Automatic retry implemented (max 3 attempts)
- [ ] User notified of persistent failures
- [ ] No silent data loss
- [ ] Monitoring dashboard shows publish health
- [ ] Queue overflow handled gracefully

**Test Scenarios:**
- MQTT broker offline
- Network disconnection
- Broker disk full
- QoS level testing"

echo "✅ Issue I created"
echo ""

# Issue J: Hardware Test Automation
echo "=== Creating Issue J: Hardware Tests Not Automated ==="
gh issue create \
  --title "[TEST] Hardware Tests Not Automated - Manual Execution Required" \
  --label "testing,priority: high,component: hardware" \
  --milestone "v3.1 - Bug Fixes & Stability" \
  --body "## Test Issue

Hardware tests require manual execution on Raspberry Pi, slowing development.

**Current State:**
- Hardware tests must be run manually
- No automated test runs
- Easy to skip testing
- Inconsistent test coverage
- No regression detection

**Desired State:**
- Automated test execution on Pi
- Scheduled test runs (nightly)
- Automatic test reporting
- CI/CD integration where possible
- Test results tracked in GitHub

**Benefits:**
- Catch regressions faster
- Consistent test execution
- Less manual work
- Better quality assurance
- Confidence in deployments

**Implementation Plan:**
- [ ] Create SSH-based test runner script
- [ ] Schedule automated test runs (cron)
- [ ] Set up test result reporting
- [ ] Create test failure notifications
- [ ] Document test infrastructure
- [ ] Integrate with GitHub Actions (if possible)

**Test Categories to Automate:**
- Sensor reading tests
- Relay control tests
- MQTT integration tests
- State persistence tests
- Complete workflow tests

**Acceptance Criteria:**
- [ ] Tests run automatically daily
- [ ] Results reported clearly (pass/fail counts)
- [ ] Failed tests trigger alerts
- [ ] Test logs archived
- [ ] Documentation complete
- [ ] Coverage > 80%

**Infrastructure Needs:**
- SSH access to Raspberry Pi
- Cron job for scheduling
- Test result storage
- Notification system (MQTT/Email)"

echo "✅ Issue J created"
echo ""

echo "🎉 All 5 reliability issues created!"
echo ""
echo "Summary:"
echo "- 5 HIGH priority reliability issues"
echo "- Focus: System stability and error handling"
echo "- All assigned to milestone: v3.1 - Bug Fixes & Stability"
echo ""
echo "Next steps:"
echo "1. Review issues: gh issue list --label 'category: reliability'"
echo "2. View all v3.1 issues: gh issue list --milestone 'v3.1 - Bug Fixes & Stability'"
echo "3. Start fixing: @requirements I need to fix issue #[number]"

