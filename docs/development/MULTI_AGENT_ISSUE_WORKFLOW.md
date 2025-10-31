# Multi-Agent Issue Creation Workflow

**Guide:** How to use the multi-agent system for automatic GitHub issue creation  
**Date:** 2025-10-31  
**Status:** Active

---

## 🎯 Overview

The multi-agent system **automatically creates and tracks GitHub issues** when you use the `@requirements` agent. No manual issue creation needed!

### What Gets Automated

✅ **GitHub Issue Creation** - Issues created automatically  
✅ **Proper Labeling** - Labels assigned based on type and priority  
✅ **Milestone Assignment** - Added to correct milestone (v3.1, v3.2, v3.3)  
✅ **Acceptance Criteria** - Clear success criteria defined  
✅ **Full Tracking** - Linked through entire development lifecycle

---

## 🚀 Quick Start

### For New Features

```
@requirements I need to add a notification system that alerts me 
when the solar system has errors or needs maintenance.
```

**What happens:**
1. @requirements asks clarifying questions
2. Documents the requirement
3. **Creates GitHub Issue automatically** 
4. Assigns labels: `feature`, `priority: medium`, `component: home-assistant`
5. Adds to milestone: `v3.2 - Enhanced Monitoring`
6. Hands off to @architect for design

**Result:** GitHub Issue #XX created and ready to work on!

---

### For Bug Reports

```
@requirements The system is showing negative energy values in the 
energy calculation. It happens randomly, maybe 2-3 times per week.
```

**What happens:**
1. @requirements asks detailed questions (when, what conditions, logs?)
2. Documents reproduction steps
3. **Creates GitHub Issue with [BUG] tag**
4. Assigns labels: `bug`, `priority: high`, `component: energy`
5. Adds to milestone: `v3.1 - Bug Fixes & Stability`
6. Creates test scenario

**Result:** GitHub Issue #XX created with full bug documentation!

---

### For Enhancements

```
@requirements I want to improve the logging system. Right now it's 
hard to debug issues because logs aren't structured well.
```

**What happens:**
1. @requirements asks about current problems
2. Defines improvement goals
3. **Creates GitHub Issue with [ENHANCEMENT] tag**
4. Assigns labels: `enhancement`, `priority: medium`, `component: logging`
5. Adds to milestone based on priority
6. Defines acceptance criteria

**Result:** GitHub Issue #XX created with improvement specs!

---

## 📚 Complete Workflow Examples

### Example 1: Feature Development (Weather Integration)

#### Step 1: Create Requirement

**You:**
```
@requirements I want to integrate weather forecasting so the system 
can preheat water before sunny days and optimize pump scheduling.
```

**@requirements Agent:**
```
Great idea! Let me gather some details:

1. What weather data do you need? (temperature, cloud cover, precipitation?)
2. How far ahead should we forecast? (24h, 48h, 7 days?)
3. What weather API should we use? (OpenWeatherMap, Weather.gov?)
4. How should this affect pump operation?
5. Should this be user-configurable?

Please answer these questions so I can create proper requirements.
```

**You:**
```
1. Cloud cover and temperature for solar prediction
2. 48 hours ahead is good
3. OpenWeatherMap API (I have a free key)
4. Start preheating 2 hours before predicted sunny period
5. Yes, user should be able to enable/disable
```

**@requirements Agent:**
```markdown
# Requirement: Weather Integration for Predictive Heating

## Problem Statement
System doesn't anticipate weather conditions, missing opportunities to 
preheat before sunny periods.

## Desired Outcome
System uses weather forecast to optimize heating schedule, preheating 
before predicted sunny weather.

## Acceptance Criteria
- [ ] OpenWeatherMap API integrated
- [ ] 48-hour forecast retrieved hourly
- [ ] Cloud cover and temperature analyzed
- [ ] Pump preheats 2h before sunny periods
- [ ] User can enable/disable feature
- [ ] Forecast shown in Home Assistant dashboard

## Technical Considerations
- API rate limits (free tier: 60 calls/min)
- Error handling for API failures
- Forecast accuracy tracking
- User configuration in config file

**GitHub Issue Created: #47 - [FEATURE] Weather Integration for Predictive Heating**
- Labels: feature, priority: medium, component: control
- Milestone: v3.3 - Advanced Features

Handing off to @architect for design...
```

---

#### Step 2: Architecture Design

**You:**
```
@architect Design the weather integration from issue #47
```

**@architect Agent:**
```markdown
# Architecture Design: Weather Integration

## Components

### WeatherService
- Responsibility: Fetch and parse weather data
- API: OpenWeatherMap
- Caching: 1-hour cache to respect rate limits
- Error handling: Fallback to last known forecast

### PredictiveController
- Responsibility: Analyze forecast and adjust pump schedule
- Input: Weather forecast + current system state
- Output: Adjusted pump schedule with preheat times

### Configuration
- New config section: `weather_integration`
- Options: enabled, api_key, preheat_hours, min_sun_threshold

## Data Flow
1. WeatherService fetches forecast every hour
2. Forecast analyzed by PredictiveController
3. If sunny period predicted, schedule preheat
4. Preheat status published to MQTT
5. Dashboard shows forecast and scheduled preheats

**Updated GitHub Issue #47 with architecture design**
```

---

#### Step 3: Test Specification

**You:**
```
@tester Write tests for issue #47
```

**@tester Agent:**
```markdown
# Test Plan: Weather Integration

## Unit Tests

### Test 1: Weather API Fetch
- **Given**: WeatherService configured with valid API key
- **When**: fetch_forecast() called
- **Then**: Returns 48-hour forecast with cloud cover and temp

### Test 2: Preheat Schedule Calculation
- **Given**: Forecast shows sunny weather in 6 hours
- **When**: PredictiveController analyzes forecast
- **Then**: Schedules preheat to start in 4 hours

### Test 3: API Failure Handling
- **Given**: OpenWeatherMap API is down
- **When**: fetch_forecast() called
- **Then**: Uses last known forecast, logs warning

## Integration Tests

### Test 4: End-to-End Workflow
- **Given**: System running with weather integration enabled
- **When**: Sunny weather predicted in 6 hours
- **Then**: Pump preheats 2 hours before, MQTT updated

## Hardware Tests (Raspberry Pi)

### Test 5: Real API Integration
- Test with actual OpenWeatherMap API on Pi
- Verify rate limiting respected
- Confirm pump activates based on real forecast

**Created test file: python/v3/tests/test_weather_integration.py**
**Updated GitHub Issue #47 with test specs**
```

---

#### Step 4: Implementation

**You:**
```
@developer Implement issue #47
```

**@developer Agent:**
```markdown
# Implementation: Weather Integration

## Changes Made

**File 1: python/v3/weather_service.py** (NEW)
- WeatherService class
- API integration with OpenWeatherMap
- Forecast caching and parsing

**File 2: python/v3/predictive_controller.py** (NEW)
- PredictiveController class
- Forecast analysis
- Preheat schedule calculation

**File 3: python/v3/main_system.py** (MODIFIED)
- Integrated WeatherService
- Added predictive scheduling
- MQTT publishing for forecasts

**File 4: python/v3/config_example.yaml** (MODIFIED)
- Added weather_integration section

## Test Results
✅ Unit tests: 12/12 passed
✅ Integration tests: 3/3 passed
✅ No regressions

## Commits
- feat: Add WeatherService for forecast fetching (#47)
- feat: Add PredictiveController for schedule optimization (#47)
- feat: Integrate weather-based preheating into main_system (#47)

**Updated GitHub Issue #47 with implementation details**
```

---

#### Step 5: Validation

**You:**
```
@validator Validate issue #47
```

**@validator Agent:**
```markdown
# User Validation: Weather Integration (Issue #47)

## Phase 1: Code Review ✅

### Architecture Compliance
- [x] Implementation follows architecture document
- [x] WeatherService and PredictiveController as designed
- [x] Proper error handling

### Code Quality
- [x] Clean, readable code
- [x] Type hints used
- [x] Good documentation
- [x] No code smells

### Error Handling & Logging
- [x] API failures handled gracefully
- [x] Appropriate logging
- [x] User-friendly error messages

**Code Review Result:** ✅ Approved for Hardware Testing

---

## Phase 2: Hardware Validation

### Test 1: API Integration
**Goal:** Verify weather data fetches correctly on Raspberry Pi

**Steps to Execute:**
```bash
# Test 1: Check weather API
ssh pi@192.168.0.18 "cd /home/pi/sun_heat_and_ftx/python/v3 && \
  python3 -c 'from weather_service import WeatherService; \
  ws = WeatherService(); \
  forecast = ws.fetch_forecast(); \
  print(forecast)'"
```

**Expected Results:**
- 48-hour forecast returned
- Cloud cover values 0-100%
- Temperature in Celsius
- No errors

---

### Test 2: Preheat Scheduling
**Goal:** Verify system schedules preheat based on forecast

**Steps to Execute:**
```bash
# Test 2: Check preheat schedule
ssh pi@192.168.0.18 "cd /home/pi/sun_heat_and_ftx/python/v3 && \
  python3 -c 'from predictive_controller import PredictiveController; \
  pc = PredictiveController(); \
  schedule = pc.calculate_preheat(forecast); \
  print(schedule)'"
```

**Expected Results:**
- Preheat scheduled if sunny weather predicted
- Time is 2 hours before sunny period
- No preheat if cloudy/rainy

---

### Test 3: Live System Test
**Goal:** Verify feature works in production

**Steps to Execute:**
1. Enable weather integration in config
2. Restart service
3. Monitor logs for forecast fetches
4. Check Home Assistant for forecast display
5. Verify preheat occurs when scheduled

```bash
# Enable and restart
ssh pi@192.168.0.18 "cd /home/pi/sun_heat_and_ftx/python/v3 && \
  sudo systemctl restart solar_heating.service && \
  sudo journalctl -u solar_heating.service -f | grep -i weather"
```

**Success Criteria:**
- [x] Forecast fetched successfully
- [x] Preheat scheduled correctly
- [x] MQTT updates published
- [x] Dashboard shows forecast
- [x] Feature can be disabled

## Final Approval Status
- [x] Code review passed
- [x] Feature meets requirements
- [x] Hardware testing successful
- [x] User is satisfied
- [x] Ready for production

**GitHub Issue #47 CLOSED ✅**
```

---

## 🎯 Issue Type Quick Reference

### Bug Reports
```
@requirements I found a bug: [description of issue]
```
**Creates:** `[BUG]` issue with:
- Labels: `bug`, `priority: high`, `component: X`
- Milestone: `v3.1` (high priority bugs)
- Reproduction steps
- Expected vs actual behavior

---

### Feature Requests
```
@requirements I need a new feature: [feature description]
```
**Creates:** `[FEATURE]` issue with:
- Labels: `feature`, `priority: medium`, `component: X`
- Milestone: `v3.2` or `v3.3` (based on complexity)
- User stories
- Acceptance criteria

---

### Enhancements
```
@requirements I want to improve [component]: [improvement description]
```
**Creates:** `[ENHANCEMENT]` issue with:
- Labels: `enhancement`, `priority: medium`, `component: X`
- Milestone: Based on priority
- Current vs desired state
- Benefits analysis

---

### Documentation
```
@requirements The documentation for [topic] needs updating
```
**Creates:** `[DOCS]` issue with:
- Labels: `documentation`, `priority: medium`
- Milestone: Same as related feature
- Affected documentation files
- Update requirements

---

### Testing
```
@requirements We need better tests for [component]
```
**Creates:** `[TEST]` issue with:
- Labels: `testing`, `priority: medium`, `component: X`
- Milestone: `v3.1` (test coverage priority)
- Test scenarios
- Coverage goals

---

## 💡 Pro Tips

### Tip 1: Be Specific in Initial Request
**Good:**
```
@requirements I need weather integration for predictive heating using 
OpenWeatherMap API, with 48-hour forecasts to schedule pump preheating.
```

**Not as good:**
```
@requirements Add weather stuff
```

The more context you provide, the faster the agent can create a complete issue.

---

### Tip 2: Reference Existing Issues
```
@requirements Issue #19 is about energy calculation bugs. I want to 
rewrite the energy calculation module to fix this properly.
```

Agent will link the new issue to the existing one.

---

### Tip 3: Specify Priority
```
@requirements [CRITICAL] The system is crashing every few hours, 
I think it's a memory leak.
```

Agent will assign `priority: critical` and milestone `v3.1`.

---

### Tip 4: Include Context
```
@requirements I've been monitoring logs and seeing "Sensor timeout" 
errors about 10 times per day. Need to add retry logic to sensor reads.
```

Context helps agent create better requirements and acceptance criteria.

---

## 📊 Benefits Summary

### Before Multi-Agent System
1. Manually create GitHub issue
2. Remember to add labels
3. Assign milestone
4. Write acceptance criteria
5. Link to other issues
6. Update project board
7. **Time: 10-15 minutes per issue**

### With Multi-Agent System
1. `@requirements I need to add [feature]`
2. Answer clarifying questions
3. **Done! Issue created automatically**
4. **Time: 2-3 minutes total**

**Savings:** 80% time reduction + higher quality issues

---

## 🎓 Learning by Example

### Example: Real Bug Fix

**You discover an issue:**
```
The pump is running at night when it shouldn't. I checked the logs 
and it seems like the temperature comparison is inverted somehow.
```

**Using the system:**
```
@requirements I found a bug: The pump is running at night even when 
solar collector temperature is lower than storage tank. Looking at 
the logs, it seems like the temperature comparison logic is inverted.
```

**@requirements response:**
```
Got it! Let me gather some details:

1. When did you first notice this?
2. Does it happen every night or randomly?
3. What are typical temperature values when this happens?
4. Which pump is affected (solar or auxiliary)?
5. Do you have any relevant log excerpts?
```

**You answer, then:**
- ✅ GitHub Issue created: #48 - [BUG] Inverted Temperature Comparison Logic
- ✅ Labels: bug, priority: critical, component: control
- ✅ Milestone: v3.1
- ✅ Reproduction steps documented
- ✅ Test scenario defined
- ✅ Ready for @tester and @developer

**Total time:** 3 minutes  
**Quality:** Professional issue tracking  
**Next step:** `@tester Write a failing test for issue #48`

---

## 🚀 Getting Started Now

Try it right now with one of your current needs:

### Option 1: Pick an Existing Problem
Think of something that's bothering you about the system, then:
```
@requirements [describe the problem]
```

### Option 2: Pick a Wishlist Feature
Something you've wanted to add:
```
@requirements I want to add [feature]
```

### Option 3: Document a Known Bug
Something that's been bugging you:
```
@requirements I found a bug: [description]
```

---

## 📋 Integration with Development Flow

### Complete Flow
```
1. @requirements [your need]
   ↓ Creates GitHub Issue #XX ✅
   
2. @architect design issue #XX
   ↓ Adds architecture to issue
   
3. @tester write tests for issue #XX
   ↓ Links tests to issue
   
4. @developer implement issue #XX
   ↓ References issue in commits
   
5. @validator validate issue #XX
   ↓ Closes issue when complete ✅
```

### Issue Lifecycle
- **Created:** By @requirements
- **Designed:** Architecture added by @architect
- **Tested:** Test specs added by @tester
- **Implemented:** Code commits reference issue
- **Validated:** Hardware tested by @validator
- **Closed:** Automatically when merged to main

---

## 🎉 Success Stories

### Story 1: Security Audit
Instead of manually creating 5 security issues, used:
```
@requirements Based on security audit, we have 5 critical issues: 
[listed all 5 issues]
```

Result: All 5 issues created in 10 minutes instead of 1+ hour

### Story 2: Feature Request from User
User requested mobile app access. Instead of notes:
```
@requirements User wants mobile app for monitoring system while away from home
```

Result: Complete feature spec with acceptance criteria, ready for development

### Story 3: Bug Marathon
System had 10 known bugs. Instead of fixing ad-hoc:
```
@requirements for each bug: [bug description]
```

Result: All bugs tracked, prioritized, and systematically fixed

---

## 📖 Additional Resources

- **Full Multi-Agent Guide:** `/MULTI_AGENT_GUIDE.md`
- **Agent Templates:** `/python/v3/docs/agent_templates/`
- **Requirements Process:** `/docs/development/GITHUB_REQUIREMENTS_PROCESS.md`
- **Action Plan:** `/docs/development/GITHUB_INTEGRATION_ACTION_PLAN.md`

---

**Ready to try it?** Start with:
```
@requirements I need to [your first requirement]
```

The system handles the rest! 🚀

