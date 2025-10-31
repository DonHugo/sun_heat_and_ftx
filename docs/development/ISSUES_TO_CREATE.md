# GitHub Issues Ready to Create

**Date:** 2025-10-30  
**Status:** Prepared and ready for creation  
**Total Issues:** 13 initial + 50 high-priority = 63 issues

---

## 📋 How to Create These Issues

### Option 1: Using GitHub Web Interface
1. Go to https://github.com/DonHugo/sun_heat_and_ftx/issues/new/choose
2. Select appropriate template
3. Copy/paste content from sections below
4. Add labels as specified
5. Assign to milestone
6. Create issue

### Option 2: Using GitHub CLI
```bash
# Install GitHub CLI if not already installed
# brew install gh  # macOS
# sudo apt install gh  # Ubuntu/Debian

# Authenticate
gh auth login

# Create issue
gh issue create --title "TITLE" --body "BODY" --label "labels" --milestone "milestone"
```

### Option 3: Bulk Creation Script
See `scripts/create_all_issues.sh` for automated creation

---

## 🐛 INITIAL ISSUES (13 Issues)

### Issue #1: MQTT Connection Leak
**Title:** [BUG] MQTT Connection Leak Over Time  
**Template:** Bug Report  
**Labels:** `bug`, `priority: high`, `component: mqtt`, `milestone: v3.1`  
**Status Note:** According to INITIAL_GITHUB_ISSUES.md, this was "Delvis fixat" (Partially fixed). Need to verify current status.

**Description:**
```markdown
## Bug Description
System creates too many MQTT connections over time, leading to resource exhaustion.

## Steps to Reproduce
1. Start system
2. Monitor MQTT connections over 24-48 hours
3. Observe connection count increasing

## Expected Behavior
Single stable MQTT connection maintained throughout system runtime.

## Actual Behavior
Multiple MQTT connections created, old ones not properly closed.

## Environment
- System: Raspberry Pi 4
- Version: v3.0+
- Python Version: 3.9+

## Logs
Monitor with: `netstat -an | grep 1883`

## Additional Context
Partially fixed in recent commits but requires verification and testing.

## Verification Needed
- [ ] Check if issue still occurs in current version
- [ ] Test MQTT connection lifecycle
- [ ] Monitor for 48+ hours
- [ ] Verify connection cleanup

## Possible Solution
- Ensure proper MQTT client cleanup
- Implement connection pooling if needed
- Add monitoring for connection count
```

---

### Issue #2: Sensor Mapping Issues
**Title:** [BUG] Sensor Mapping Errors Prevent Pump Start  
**Template:** Bug Report  
**Labels:** `bug`, `priority: high`, `component: sensors`, `milestone: v3.1`  
**Status Note:** "Fixat i senaste commits, behöver testning" (Fixed in recent commits, needs testing)

**Description:**
```markdown
## Bug Description
Certain sensors are not mapped correctly, which prevents pump from starting.

## Steps to Reproduce
1. System initialization
2. Sensor reading attempted
3. Mapping fails
4. Pump control blocked

## Expected Behavior
All sensors correctly mapped and accessible for pump control logic.

## Actual Behavior
Some sensors fail to map, causing pump control to abort.

## Environment
- System: Raspberry Pi 4
- Hardware: Sequent Microsystems RTD, MegaBAS
- Version: v3.0+

## Logs
Check sensor initialization logs

## Additional Context
Fixed in recent commits, requires comprehensive testing.

## Testing Checklist
- [ ] Verify all sensor IDs map correctly
- [ ] Test sensor reading on hardware
- [ ] Confirm pump can start
- [ ] Test with all sensor configurations
- [ ] Document sensor mapping
```

---

### Issue #3: Service Startup Failures
**Title:** [BUG] Service Fails to Start When Log Directories Missing  
**Template:** Bug Report  
**Labels:** `bug`, `priority: medium`, `component: systemd`, `milestone: v3.1`  
**Status Note:** "Fixat med automatisk katalogskapande" (Fixed with automatic directory creation)

**Description:**
```markdown
## Bug Description
Systemd services fail to start if log directories don't exist.

## Steps to Reproduce
1. Fresh Pi deployment
2. Log directory not created
3. Service start attempted
4. Failure occurs

## Expected Behavior
Service creates log directories automatically if they don't exist.

## Actual Behavior
Service fails to start, requires manual directory creation.

## Environment
- System: Raspberry Pi 4
- OS: Raspberry Pi OS
- Python Version: 3.9+

## Solution Implemented
Automatic directory creation added. Requires verification.

## Verification Needed
- [ ] Test on fresh Pi deployment
- [ ] Verify directory creation
- [ ] Check permissions
- [ ] Test service restart scenarios
- [ ] Update deployment docs
```

---

### Issue #4: Enhanced Error Recovery
**Title:** [FEATURE] Implement Enhanced Automatic Error Recovery  
**Template:** Feature Request  
**Labels:** `feature`, `priority: medium`, `component: watchdog`, `milestone: v3.2`

**Description:**
```markdown
## Feature Description
Implement comprehensive automatic error recovery system for common failure scenarios.

## Problem/Use Case
System currently requires manual intervention for many error conditions. Need automated recovery.

## Proposed Solution
- Automatic sensor reconnection on communication failure
- MQTT reconnection with exponential backoff
- Service self-healing for common errors
- State recovery after unexpected shutdown
- Watchdog-driven recovery procedures

## Expected Benefits
- Reduced manual intervention
- Higher system uptime
- Faster recovery from transient errors
- Better user experience

## Acceptance Criteria
- [ ] Sensor failures auto-recover
- [ ] MQTT disconnections auto-recover
- [ ] Service crashes auto-restart
- [ ] State correctly restored
- [ ] Recovery actions logged
- [ ] User notified of recoveries

## Technical Considerations
- Implement retry logic with backoff
- State persistence for recovery
- Recovery action logging
- Alert on repeated failures
```

---

### Issue #5: Advanced Monitoring Dashboard
**Title:** [FEATURE] Advanced Home Assistant Monitoring Dashboard  
**Template:** Feature Request  
**Labels:** `feature`, `priority: medium`, `component: home-assistant`, `component: gui`, `milestone: v3.2`

**Description:**
```markdown
## Feature Description
Create comprehensive monitoring dashboard in Home Assistant with real-time metrics and historical data.

## Problem/Use Case
Current dashboard provides basic monitoring. Need advanced visualizations and analytics.

## Proposed Solution
- Real-time system health metrics
- Historical temperature charts
- Energy production/savings graphs
- Pump operation timeline
- Alert/warning history
- System performance metrics

## Expected Benefits
- Better system visibility
- Easier troubleshooting
- Performance optimization insights
- User engagement

## Acceptance Criteria
- [ ] All sensors visualized
- [ ] Historical data graphed
- [ ] Energy metrics displayed
- [ ] System health indicators
- [ ] Mobile-responsive design
- [ ] Performance optimized

## Additional Context
- Use Lovelace custom cards
- Consider Grafana integration
- Historical data from InfluxDB
```

---

### Issue #6: Energy Usage Analytics
**Title:** [FEATURE] Comprehensive Energy Usage Analytics  
**Template:** Feature Request  
**Labels:** `feature`, `priority: low`, `component: energy`, `milestone: v3.3`

**Description:**
```markdown
## Feature Description
Advanced analytics for energy production, usage, and savings.

## Problem/Use Case
Need detailed insights into system efficiency and energy savings.

## Proposed Solution
- Daily/weekly/monthly energy reports
- Efficiency calculations
- Cost savings estimates
- Trend analysis
- Predictive analytics (AI-driven)
- Comparison with previous periods

## Expected Benefits
- Understanding of system performance
- ROI calculations
- Optimization opportunities
- User satisfaction

## Acceptance Criteria
- [ ] Energy reports generated
- [ ] Efficiency metrics calculated
- [ ] Cost savings estimated
- [ ] Historical comparisons
- [ ] Export to CSV/PDF
- [ ] Email reports (optional)

## Technical Considerations
- Historical data storage
- Calculation accuracy
- Report generation performance
- Data export formats
```

---

### Issue #7: Improved Test Coverage
**Title:** [ENHANCEMENT] Increase Test Coverage for All Components  
**Template:** Enhancement  
**Labels:** `enhancement`, `priority: medium`, `component: testing`, `milestone: v3.1`

**Description:**
```markdown
## Enhancement Description
Increase test coverage from current levels to 80%+ for all core components.

## Current Behavior
- Test coverage varies by component
- Some components have minimal tests
- Hardware tests incomplete

## Proposed Improvement
- Unit tests for all modules
- Integration tests for component interactions
- Hardware tests for Raspberry Pi
- E2E tests for complete workflows
- Performance tests

## Expected Impact
- **Quality**: Fewer bugs in production
- **Confidence**: Safe refactoring
- **Documentation**: Tests as examples
- **Maintainability**: Easier changes

## Acceptance Criteria
- [ ] 80%+ unit test coverage
- [ ] Integration tests complete
- [ ] Hardware tests on Pi
- [ ] E2E tests for key workflows
- [ ] Test documentation updated
- [ ] CI/CD integration

## Technical Details
- Use pytest framework
- Mock external dependencies
- Test on actual hardware
- Measure coverage with pytest-cov
```

---

### Issue #8: Better Logging System
**Title:** [ENHANCEMENT] Implement Structured Logging System  
**Template:** Enhancement  
**Labels:** `enhancement`, `priority: medium`, `component: logging`, `milestone: v3.2`

**Description:**
```markdown
## Enhancement Description
Replace current logging with structured logging for better analysis and debugging.

## Current Behavior
- Simple text logs
- Inconsistent formats
- Hard to parse
- Limited context

## Proposed Improvement
- Structured JSON logging
- Consistent log levels
- Rich context (correlation IDs, timestamps)
- Log aggregation support
- Better filtering/searching

## Expected Impact
- **Debugging**: Faster issue resolution
- **Monitoring**: Better alerts
- **Analytics**: Log analysis possible
- **Compliance**: Audit trails

## Acceptance Criteria
- [ ] JSON-structured logs
- [ ] Consistent format
- [ ] Correlation IDs
- [ ] Log rotation configured
- [ ] Searchable logs
- [ ] Integration with log viewers

## Technical Considerations
- Use structlog or python-json-logger
- Backward compatibility
- Performance impact minimal
- Log storage considerations
```

---

### Issue #9: Configuration Management
**Title:** [ENHANCEMENT] Flexible Configuration Management System  
**Template:** Enhancement  
**Labels:** `enhancement`, `priority: low`, `component: config`, `milestone: v3.3`

**Description:**
```markdown
## Enhancement Description
Implement flexible configuration system with validation and hot-reloading.

## Current Behavior
- Configuration scattered
- No validation
- Requires restart for changes
- No environment-specific configs

## Proposed Improvement
- Centralized configuration
- Schema validation
- Hot-reload capability
- Environment-specific configs
- Configuration versioning
- Web UI for config (future)

## Expected Impact
- **Usability**: Easier configuration
- **Reliability**: Fewer config errors
- **Flexibility**: Environment-specific settings
- **Maintenance**: Easier updates

## Acceptance Criteria
- [ ] Centralized config file(s)
- [ ] JSON schema validation
- [ ] Hot-reload for non-critical settings
- [ ] Environment overrides
- [ ] Config documentation
- [ ] Migration tool for old configs

## Technical Considerations
- Use pydantic for validation
- Support YAML and JSON
- Environment variable overrides
- Config change notifications
```

---

### Issue #10: User Manual Update
**Title:** [DOCS] Update User Manual for v3 Features  
**Template:** Documentation  
**Labels:** `documentation`, `priority: medium`, `milestone: v3.1`

**Description:**
```markdown
## Documentation Issue
User manual needs comprehensive update for all v3 features and changes.

## Affected Documentation
- [ ] USER_GUIDE_SOLAR_HEATING_V3.md
- [ ] HOME_ASSISTANT_SETUP.md
- [ ] DEPLOYMENT_GUIDE.md
- [ ] TROUBLESHOOTING_GUIDE.md
- [ ] README.md

## Type of Update
- [x] New feature documentation
- [x] Updated procedures
- [x] New screenshots needed
- [x] Configuration examples
- [x] Troubleshooting additions

## Desired State
Complete, accurate documentation covering:
- All v3 features
- Updated installation procedures
- Configuration examples
- Troubleshooting guides
- Home Assistant integration
- Multi-agent development workflow

## Acceptance Criteria
- [ ] All v3 features documented
- [ ] Screenshots updated
- [ ] Examples tested
- [ ] Links verified
- [ ] Reviewed by user
- [ ] Published

## Additional Context
Priority sections:
1. Installation/deployment
2. Home Assistant integration
3. Troubleshooting common issues
4. Configuration reference
```

---

### Issue #11: API Documentation
**Title:** [DOCS] Create Comprehensive API Documentation  
**Template:** Documentation  
**Labels:** `documentation`, `priority: low`, `component: api`, `milestone: v3.3`

**Description:**
```markdown
## Documentation Issue
Create complete API documentation for developers and integrators.

## Affected Documentation
- [ ] API_DESIGN_SPECIFICATION.md (expand)
- [ ] New: API_REFERENCE.md
- [ ] New: API_EXAMPLES.md
- [ ] Update: README.md

## Type of Update
- [x] Missing documentation
- [x] API reference
- [x] Code examples
- [x] Integration guides

## Desired State
Complete API documentation including:
- REST API endpoints
- MQTT topics and payloads
- WebSocket API (if applicable)
- Authentication
- Rate limiting
- Error codes
- Example requests/responses
- Client libraries (future)

## Acceptance Criteria
- [ ] All endpoints documented
- [ ] Request/response examples
- [ ] Authentication documented
- [ ] Error handling explained
- [ ] Integration examples
- [ ] OpenAPI/Swagger spec

## Technical Considerations
- Generate from code if possible
- Use OpenAPI 3.0 standard
- Interactive API explorer
- Keep in sync with code
```

---

### Issue #12: Hardware Test Suite
**Title:** [TEST] Comprehensive Hardware Test Suite for Raspberry Pi  
**Template:** Testing  
**Labels:** `testing`, `priority: high`, `component: testing`, `component: hardware`, `milestone: v3.1`

**Description:**
```markdown
## Test Issue Description
Develop comprehensive hardware test suite that runs on actual Raspberry Pi.

## Type of Testing
- [x] Hardware tests (Raspberry Pi)
- [x] Integration tests
- [x] End-to-end tests

## Component Being Tested
- Sensor reading (RTD, MegaBAS)
- Relay control
- MQTT communication
- State persistence
- Watchdog integration
- Complete workflows

## Current Test Status
- **Current Coverage**: ~60%
- **Existing Tests**: Some unit tests, limited hardware tests
- **Gaps**: Hardware integration, E2E workflows

## Test Requirements

### Hardware Test Scenarios
1. **Sensor Reading**
   - Given: RTD board connected
   - When: Read all sensors
   - Then: Valid temperature values returned

2. **Relay Control**
   - Given: Relay board connected
   - When: Control relay states
   - Then: Relays respond correctly

3. **MQTT Integration**
   - Given: MQTT broker running
   - When: Publish sensor data
   - Then: Data received by Home Assistant

4. **Complete Workflow**
   - Given: System running
   - When: Temperature conditions met
   - Then: Pump activates correctly

## Acceptance Criteria
- [ ] All hardware components tested
- [ ] Tests run on actual Raspberry Pi
- [ ] Automated test execution
- [ ] Test documentation complete
- [ ] CI/CD integration (where possible)
- [ ] Coverage > 80%

## Testing Infrastructure
- **Hardware Required**: Raspberry Pi 4, Sequent boards
- **Test Data**: Temperature profiles, scenarios
- **Execution**: SSH-based test runner

## Technical Considerations
- Safety: No destructive tests
- Cleanup: Reset state after tests
- Isolation: Tests don't interfere
- Reporting: Clear pass/fail results
```

---

### Issue #13: Performance Testing
**Title:** [TEST] Long-term Performance and Stability Testing  
**Template:** Testing  
**Labels:** `testing`, `priority: medium`, `component: testing`, `category: performance`, `milestone: v3.2`

**Description:**
```markdown
## Test Issue Description
Implement long-term performance and stability testing to ensure system reliability.

## Type of Testing
- [x] Performance tests
- [x] Load tests
- [x] Stability tests (long-running)
- [x] Memory leak detection

## Component Being Tested
- System runtime stability
- Memory usage over time
- CPU usage patterns
- MQTT message throughput
- Database performance
- Log file growth

## Current Test Status
- **Current Coverage**: Limited
- **Existing Tests**: Short-duration only
- **Gaps**: Long-term stability, resource monitoring

## Test Requirements

### Performance Test Scenarios
1. **7-Day Continuous Run**
   - Monitor: Memory, CPU, disk, network
   - Check: No memory leaks, stable performance

2. **High-Frequency Sensor Reading**
   - Load: Read sensors every 1 second
   - Verify: System handles load, no degradation

3. **MQTT Message Flood**
   - Load: 100 messages/second for 1 hour
   - Verify: All messages processed, no loss

4. **Database Growth**
   - Monitor: Database size over 30 days
   - Verify: Growth is linear and manageable

## Acceptance Criteria
- [ ] 7-day stability test passes
- [ ] No memory leaks detected
- [ ] CPU usage remains < 50%
- [ ] All messages processed
- [ ] Performance benchmarks met
- [ ] Results documented

## Testing Infrastructure
- **Monitoring**: Prometheus + Grafana
- **Test Duration**: 7-30 days
- **Automated**: Scheduled tests

## Expected Outcomes
- Performance baseline established
- Resource usage predictable
- System stable long-term
- Bottlenecks identified
```

---

## 🔥 HIGH-PRIORITY EXTRACTED ISSUES (50 Issues)

*Note: These are summarized high-priority issues from EXTRACTED_ISSUES.md. Full details available in that file.*

### Security Issues (5 issues - CRITICAL)

#### Issue: Input Validation Missing
**Labels:** `bug`, `priority: critical`, `category: security`, `component: api`  
**Description:** API endpoints lack input validation, potential security vulnerability.

#### Issue: Error Messages Expose System Info
**Labels:** `bug`, `priority: high`, `category: security`, `component: logging`  
**Description:** Error messages leak sensitive system information.

#### Issue: MQTT Authentication Not Enforced
**Labels:** `bug`, `priority: critical`, `category: security`, `component: mqtt`  
**Description:** MQTT connections don't always enforce authentication.

#### Issue: Hardcoded Secrets in Configuration
**Labels:** `bug`, `priority: critical`, `category: security`, `component: config`  
**Description:** Some configuration files contain hardcoded secrets.

#### Issue: No Rate Limiting on API
**Labels:** `enhancement`, `priority: high`, `category: security`, `component: api`  
**Description:** API lacks rate limiting, vulnerable to abuse.

---

### Error Handling Issues (10 issues - HIGH)

#### Issue: Bare Except Clauses Throughout Codebase
**Labels:** `bug`, `priority: medium`, `category: reliability`, `component: control`  
**Description:** Many bare `except:` clauses catch all exceptions indiscriminately.

#### Issue: Sensor Read Errors Not Handled
**Labels:** `bug`, `priority: high`, `component: sensors`, `category: reliability`  
**Description:** Sensor reading errors cause system crashes.

#### Issue: MQTT Publish Failures Silently Ignored
**Labels:** `bug`, `priority: high`, `component: mqtt`, `category: reliability`  
**Description:** Failed MQTT publishes are not logged or retried.

#### Issue: No Graceful Degradation on Component Failure
**Labels:** `enhancement`, `priority: medium`, `category: reliability`  
**Description:** Single component failure can bring down entire system.

#### Issue: Database Connection Errors Not Recovered
**Labels:** `bug`, `priority: medium`, `component: logging`, `category: reliability`  
**Description:** Database connection loss not handled gracefully.

#### Issue: Missing Error Context in Logs
**Labels:** `enhancement`, `priority: low`, `component: logging`  
**Description:** Error logs lack sufficient context for debugging.

#### Issue: No Circuit Breaker Pattern
**Labels:** `enhancement`, `priority: low`, `category: reliability`  
**Description:** No circuit breakers for failing external services.

#### Issue: TaskMaster AI Errors Crash Main System
**Labels:** `bug`, `priority: high`, `component: taskmaster`, `category: reliability`  
**Description:** TaskMaster failures can crash the main system.

#### Issue: Watchdog False Positives
**Labels:** `bug`, `priority: medium`, `component: watchdog`  
**Description:** Watchdog reports false "unhealthy" status.

#### Issue: Incomplete Exception Documentation
**Labels:** `documentation`, `priority: low`, `component: api`  
**Description:** API exceptions not documented for users.

---

### Performance Issues (5 issues - MEDIUM)

#### Issue: Energy Calculation Performance Degradation
**Labels:** `bug`, `priority: medium`, `component: energy`, `category: performance`  
**Description:** Energy calculations slow down over time with large datasets.

#### Issue: Inefficient Sensor Polling
**Labels:** `enhancement`, `priority: medium`, `component: sensors`, `category: performance`  
**Description:** Sensors polled unnecessarily, wasting CPU.

#### Issue: MQTT Message Queue Buildup
**Labels:** `bug`, `priority: medium`, `component: mqtt`, `category: performance`  
**Description:** MQTT messages queue up under high load.

#### Issue: Memory Leak in Long-Running Process
**Labels:** `bug`, `priority: high`, `category: performance`  
**Description:** Memory usage grows continuously over days.

#### Issue: Slow Dashboard Loading
**Labels:** `enhancement`, `priority: low`, `component: gui`, `category: performance`  
**Description:** Dashboard takes too long to load with historical data.

---

### Testing Gaps (8 issues - MEDIUM)

#### Issue: No Integration Tests for MQTT
**Labels:** `testing`, `priority: medium`, `component: mqtt`  
**Description:** MQTT integration lacks comprehensive tests.

#### Issue: Edge Cases Not Tested
**Labels:** `testing`, `priority: medium`, `component: control`  
**Description:** Control logic edge cases not covered by tests.

#### Issue: Mock-Heavy Tests Don't Catch Real Issues
**Labels:** `testing`, `priority: low`  
**Description:** Too many mocks, real integration issues missed.

#### Issue: No Load Testing
**Labels:** `testing`, `priority: medium`, `category: performance`  
**Description:** System not tested under high load.

#### Issue: Hardware Tests Not Automated
**Labels:** `testing`, `priority: high`, `component: hardware`  
**Description:** Hardware tests require manual execution.

#### Issue: No Chaos Engineering Tests
**Labels:** `testing`, `priority: low`, `category: reliability`  
**Description:** System not tested against random failures.

#### Issue: Test Data Management Poor
**Labels:** `testing`, `priority: low`  
**Description:** Test data not managed well, tests flaky.

#### Issue: No Visual Regression Testing for GUI
**Labels:** `testing`, `priority: low`, `component: gui`  
**Description:** GUI changes not tested for visual regressions.

---

### Documentation Gaps (12 issues - MEDIUM/LOW)

#### Issue: API Examples Missing
**Labels:** `documentation`, `priority: medium`, `component: api`

#### Issue: Troubleshooting Guide Incomplete
**Labels:** `documentation`, `priority: medium`

#### Issue: Architecture Diagrams Outdated
**Labels:** `documentation`, `priority: low`

#### Issue: Deployment Automation Not Documented
**Labels:** `documentation`, `priority: medium`

#### Issue: Error Code Reference Missing
**Labels:** `documentation`, `priority: low`

#### Issue: Configuration Options Not All Documented
**Labels:** `documentation`, `priority: medium`, `component: config`

#### Issue: MQTT Topics Not Fully Documented
**Labels:** `documentation`, `priority: medium`, `component: mqtt`

#### Issue: Home Assistant Setup Needs Update
**Labels:** `documentation`, `priority: medium`, `component: home-assistant`

#### Issue: Multi-Agent Workflow Examples Needed
**Labels:** `documentation`, `priority: low`

#### Issue: Performance Tuning Guide Missing
**Labels:** `documentation`, `priority: low`, `category: performance`

#### Issue: Security Best Practices Not Documented
**Labels:** `documentation`, `priority: high`, `category: security`

#### Issue: Backup and Recovery Procedures Missing
**Labels:** `documentation`, `priority: medium`

---

### Feature Requests (10 issues - VARIOUS)

#### Issue: Notification System for Alerts
**Labels:** `feature`, `priority: medium`, `component: home-assistant`

#### Issue: Mobile App
**Labels:** `feature`, `priority: low`, `component: gui`

#### Issue: Weather Integration for Predictions
**Labels:** `feature`, `priority: low`, `component: control`

#### Issue: Multi-Zone Support
**Labels:** `feature`, `priority: low`, `component: control`

#### Issue: Advanced Scheduling
**Labels:** `feature`, `priority: medium`, `component: control`

#### Issue: Cost Tracking and ROI Calculator
**Labels:** `feature`, `priority: low`, `component: energy`

#### Issue: Backup Heating Source Integration
**Labels:** `feature`, `priority: medium`, `component: control`

#### Issue: Vacation Mode
**Labels:** `feature`, `priority: low`, `component: control`

#### Issue: Remote System Management
**Labels:** `feature`, `priority: medium`, `component: api`

#### Issue: Historical Data Export
**Labels:** `feature`, `priority: low`, `component: energy`

---

## 📊 Issue Creation Summary

**Total Issues to Create:** 63

**By Priority:**
- Critical: 3
- High: 15
- Medium: 30
- Low: 15

**By Component:**
- sensors: 5
- mqtt: 8
- watchdog: 3
- home-assistant: 4
- gui: 4
- testing: 12
- documentation: 12
- energy: 4
- control: 6
- api: 5

**By Milestone:**
- v3.1: 20 issues (focus)
- v3.2: 18 issues
- v3.3: 15 issues
- Future/Backlog: 10 issues

---

## ⚡ Quick Start Commands

### Create Labels First
```bash
cd /Users/hafs/Documents/Github/sun_heat_and_ftx
chmod +x scripts/create_github_labels.sh
./scripts/create_github_labels.sh
```

### Create Milestones
```bash
gh api repos/DonHugo/sun_heat_and_ftx/milestones -f title='v3.1 - Bug Fixes & Stability' -f due_on='2025-12-01T00:00:00Z' -f description='Critical bug fixes and system stability'

gh api repos/DonHugo/sun_heat_and_ftx/milestones -f title='v3.2 - Enhanced Monitoring' -f due_on='2026-02-01T00:00:00Z' -f description='Improved monitoring, alerting, and error recovery'

gh api repos/DonHugo/sun_heat_and_ftx/milestones -f title='v3.3 - Advanced Features' -f due_on='2026-04-01T00:00:00Z' -f description='New features and advanced capabilities'
```

### Create Issues (Example)
```bash
# Example: Create Issue #1
gh issue create \
  --title "[BUG] MQTT Connection Leak Over Time" \
  --body-file issue_templates/issue_01.md \
  --label "bug,priority: high,component: mqtt,milestone: v3.1"
```

---

**Next Steps:**
1. Run label creation script
2. Create milestones
3. Create issues (start with v3.1 high-priority)
4. Set up GitHub Project board
5. Begin working on issues

---

**Prepared by:** @manager  
**Date:** 2025-10-30  
**Status:** Ready for creation


