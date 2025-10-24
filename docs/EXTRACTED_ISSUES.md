# Extracted Issues from Documentation

This file contains actionable items extracted from documentation that should be converted to GitHub issues.

📄 **docs/getting-started/DEVELOPMENT_ENVIRONMENT_SETUP.md** (Getting Started)

- - **Requires user execution**: All commands must be run by user
- git commit -m "Fix service monitoring issue"
- - Check logs for error messages

📄 **docs/getting-started/PRD.md** (Getting Started)

- - ✅ Alert on system safety issues
- - ✅ Create tasks to predict maintenance needs based on runtime
- - ✅ Enable immediate detection of system failures or communication issues
- - ✅ Automatic error recovery
- - ✅ Clear error messages and notifications
- - ✅ Error and alert messaging
- - ✅ Error handling verification
- - ✅ Software compatibility issues
- - ✅ User error and misuse
- **Issue Identified**: System was displaying unrealistic energy values (800+ kWh) in the dashboard due to incorrect calculation multipliers.

📄 **docs/getting-started/SYSTEM_OVERVIEW.md** (Getting Started)

- - Error handling and diagnostics
- ├── high_temperature    # High temp warnings
- ├── low_temperature     # Low temp warnings
- - **System Alerts**: Immediate notification of issues
- - **Low Temperature**: Warning when system isn't heating effectively
- 2. **Error Recovery**: Automatic recovery from common errors
- 3. **Explore customization** options for your needs
- - **Troubleshooting**: Common issues and solutions
- 3. **Check troubleshooting** for common issues
- 4. **Review logs** for detailed error information

📄 **docs/design/COMPONENT_MAP.md** (Design)

- │   ├── v1/                            # ❌ DEPRECATED
- │   ├── v2/                            # ❌ DEPRECATED

📄 **docs/design/DESIGN_HOME_ASSISTANT.md** (Design)

- C -->|Error Message| F[Process Error Message]
- STATUS --> ERROR[error/]
- return self.error_response(str(e))
- return self.validation_error_response()
- return self.error_response(str(e))
- return self.error_response(str(e))
- elif webhook_type == 'system_error':
- return self.handle_system_error(payload)
- except jwt.InvalidTokenError:

📄 **docs/design/DESIGN_RATE_OF_CHANGE_SENSORS.md** (Design)

- - Configuration errors
- - Log warnings for configuration issues
- - Error handling

📄 **docs/design/DESIGN_SOLAR_HEATING_V3.md** (Design)

- H --> I{Any Safety Issues?}
- # Check if tank needs heating
- | `temp_threshold_high` | High temperature warning | 80.0°C | ✅ Yes |
- | `temp_threshold_low` | Low temperature warning | 20.0°C | ✅ Yes |
- | **High Temperature** | Any temp > 80°C | Warning alert | Automatic monitoring |
- | **Low Temperature** | Any temp < 20°C | Warning alert | Automatic monitoring |
- | **Hardware Error** | Communication failure | Alert and retry | Automatic retry |
- SYS2[SOLAR_DEBUG_MODE]
- # Set defaults for missing values
- | **DEBUG** | Detailed debugging information | Development and troubleshooting |

📄 **docs/design/DESIGN_TASKMASTER_AI.md** (Design)

- | **Predictor** | Future predictions | Predict temperatures, usage, and system needs |
- +error_message: str
- error_result = TaskResult(
- error_message=str(e)
- self.record_execution_result(task, error_result)
- return error_result
- if self.needs_adaptation(performance):
- def needs_adaptation(self, performance):
- """Determine if model needs adaptation"""

📄 **docs/implementation/COLLECTOR_COOLING_IMPLEMENTATION.md** (Implementation)

- This document describes the implementation of collector cooling functionality from V1 to V3, restoring an important safety and efficiency feature that was missing in the V3 rewrite.
- **Missing Functionality**: The V3 system lacked the proactive collector cooling feature from V1, which could lead to:
- - Potential safety issues
- logger.warning(f"Collector cooling activated: Collector temperature {solar_collector}°C >= {self.control_params['kylning_kollektor']}°C. Cycle #{self.system_state['heating_cycles_count']}")
- - ✅ Better error handling

📄 **docs/implementation/IMPLEMENTATION_HOME_ASSISTANT.md** (Implementation)

- self.logger.error(f"Failed to connect to MQTT broker: {e}")
- self.logger.error(f"Error disconnecting from MQTT broker: {e}")
- self.logger.error(f"Failed to connect to MQTT broker with code {rc}")
- self.logger.warning(f"Unexpected disconnection from MQTT broker with code {rc}")
- self.logger.warning("Cannot subscribe: not connected to MQTT broker")
- self.logger.error(f"Failed to subscribe to topic {topic}")
- self.logger.error(f"Error subscribing to topic {topic}: {e}")
- self.logger.warning("Cannot publish: not connected to MQTT broker")
- self.logger.debug(f"Published to topic {topic}: {payload}")
- self.logger.error(f"Failed to publish to topic {topic}")

📄 **docs/implementation/IMPLEMENTATION_RATE_OF_CHANGE_SENSORS.md** (Implementation)

- - Error handling
- - Error conditions
- - ✅ Comprehensive error handling

📄 **docs/implementation/IMPLEMENTATION_SOLAR_HEATING_V3.md** (Implementation)

- self.logger.error(f"System error: {e}")
- self.logger.error(f"Error reading sensor {sensor_id}: {e}")
- return {"pump_primary": "error"}
- """Check for high temperature warnings"""
- self.logger.warning(f"High temperature on {sensor_id}: {temp}°C")
- except ImportError:
- self.logger.error("RTD library not available")
- self.logger.error(f"Failed to initialize RTD board: {e}")
- raise RuntimeError("RTD board not initialized")
- self.logger.error(f"Error reading RTD sensor {sensor_id}: {e}")

📄 **docs/implementation/IMPLEMENTATION_TASKMASTER_AI.md** (Implementation)

- self.logger.error(f"Failed to start TaskMaster AI service: {e}")
- self.logger.error(f"Data collection error: {e}")
- self.logger.error(f"AI processing error: {e}")
- except ImportError:
- self.logger.warning("NumPy/Scipy not available, using basic analysis")
- except ImportError:
- self.logger.warning("Scikit-learn not available, using basic models")
- except ImportError:
- self.logger.warning("Neural network not available")
- self.logger.error(f"Error with {model_name}: {e}")

📄 **docs/user-guides/HOME_ASSISTANT_SETUP.md** (User Guides)

- - `sensor.solar_heating_v3_system_mode` - System mode (normal, manual, overheated, error, maintenance)
- 4. **Check Logs**: Look for MQTT-related errors in Home Assistant logs
- 1. **YAML Syntax**: Check for YAML syntax errors
- 4. **System Health**: Regular monitoring prevents issues
- For issues with the v3 system itself, check the system logs:
- For Home Assistant issues, check the Home Assistant logs in the web interface.

📄 **docs/user-guides/HOME_ASSISTANT_SYSTEM_MODE_CONTROL.md** (User Guides)

- logger.error(f"Error handling MQTT command: {e}")

📄 **docs/user-guides/USER_GUIDE_HOME_ASSISTANT.md** (User Guides)

- solar-heating-warning: "#f39c12"
- - Look for error messages related to solar heating
- - Check card configuration for errors
- 2. **Pump Protection**: Automatic shutdown on system errors
- 4. **Contact Support**: Get help if issues persist
- - [ ] Review any error notifications
- - [ ] Review system logs for errors

📄 **docs/user-guides/USER_GUIDE_RATE_OF_CHANGE_SENSORS.md** (User Guides)

- The Rate of Change Sensors provide real-time monitoring of how quickly energy and temperature are changing in your solar heating system. These sensors help you understand system performance, detect issues, and optimize operation.
- - **Use when**: Debugging, testing, need immediate visibility
- - **Best for**: Debugging, seeing real data
- - **Cons**: More complex, requires tuning
- - **Check**: Look for error messages in system logs
- 3. **Match Time Window to Needs**: Fast for debugging, Slow for trends
- 4. **Monitor Performance**: Watch system logs for any issues
- message: "Warning: Rapid energy loss detected!"
- A: Start with "medium" for general use, "fast" for debugging, "slow" for trend analysis.
- The Rate of Change Sensors provide valuable insights into your solar heating system's performance. Start with the default settings and adjust based on your monitoring needs. These sensors will help you:

📄 **docs/user-guides/USER_GUIDE_SOLAR_HEATING_V3.md** (User Guides)

- - **System Error**: Critical system errors
- - **High Temperature**: Warning when > 80°C
- - **Low Temperature**: Warning when < 20°C
- - [ ] Review system logs for any errors
- SOLAR_DEBUG_MODE=true SOLAR_LOG_LEVEL=debug python main_system.py
- grep "ERROR" /home/pi/solar_heating/logs/solar_heating_v3.log
- grep "WARNING" /home/pi/solar_heating/logs/solar_heating_v3.log

📄 **docs/user-guides/USER_GUIDE_TASKMASTER_AI.md** (User Guides)

- - **Maintenance Warnings**: Predictive maintenance recommendations
- learning_issues = service.diagnose_learning_issues()
- print('Learning Issues:', learning_issues)
- AI_DEBUG_MODE=true AI_LOG_LEVEL=debug python taskmaster_service.py
- tail -f taskmaster_ai_debug.log

📄 **docs/deployment/DETAILED_DEPLOYMENT_GUIDE.md** (Deployment)

- ERRORS=$(tail -n 1000 "$LOG_FILE" | grep -i "error" | tail -n 10)
- if [ ! -z "$ERRORS" ]; then
- echo "Solar Heating System Errors Detected:" | mail -s "Solar Heating Alert" "$ALERT_EMAIL"
- echo "$ERRORS" | mail -s "Solar Heating Error Details" "$ALERT_EMAIL"
- WARNINGS=$(tail -n 1000 "$LOG_FILE" | grep -i "warning" | tail -n 5)
- if [ ! -z "$WARNINGS" ]; then
- echo "Solar Heating System Warnings:" | mail -s "Solar Heating Warning" "$ALERT_EMAIL"
- echo "$WARNINGS" | mail -s "Solar Heating Warning Details" "$ALERT_EMAIL"
- log_type error
- log_type warning

📄 **docs/deployment/DETAILED_HARDWARE_SETUP.md** (Deployment)

- if raw_value == 60:  # Error value
- logger.error(f"Error reading RTD channel {channel}: {e}")
- logger.error(f"Error setting relay {channel}: {e}")
- logger.error(f"Error reading relay {channel}: {e}")
- if raw_value == 60:  # Error value
- logger.error(f"Error reading MegaBAS channel {channel}: {e}")
- print(f"  RTD {sensor_id}: ERROR ❌")
- print(f"  Relay {relay_id}: OFF ERROR ❌")
- print(f"  Relay {relay_id}: ON ERROR ❌")
- print(f"  MegaBAS {channel}: ERROR ❌")

📄 **docs/deployment/UPTIME_KUMA_MQTT_MONITORING.md** (Deployment)

- - **System state errors**: Application running but in error state
- 2. **Warning**: No heartbeat for > 1 minute
- 3. **Info**: System state changed to error/maintenance
- - Check system is running and not in error state
- 3. **MQTT connection issues**:

📄 **docs/deployment/WATCHDOG_MQTT_PREVENTION.md** (Deployment)

- - False "MQTT unhealthy" warnings
- - Better error handling and logging
- - Automatic restart when issues detected
- - Early detection of connection issues
- 5. **Prevention**: Proactive measures to avoid issues
- - Check for any recurring issues

📄 **docs/deployment/WATCHDOG_SYSTEM.md** (Deployment)

- missingok
- 4. **Set up log rotation** to prevent disk space issues

📄 **docs/troubleshooting/COMPREHENSIVE_ERROR_FIXES.md** (Troubleshooting)

- This document provides a comprehensive summary of all errors found in the solar heating system logs and the fixes implemented to resolve them.
- Error creating TaskMaster AI task: [Errno -2] Name or service not known
- - **Enhanced error handling**: Specific exception handling for network failures
- Error publishing Home Assistant discovery: MQTTHandler.publish() got an unexpected keyword argument 'retain'
- Error publishing status: 'MQTTHandler' object has no attribute 'publish_status'
- - **Missing methods**: New MQTT handler missing required methods
- - **Added missing methods**: `publish_status()`, `publish_system_status()`, etc.
- Error handling MQTT command: 'sensor'
- WARNING - Error reading MegaBAS sensor 5 (every 30 seconds)
- WARNING - No system callback registered for pellet stove data

📄 **docs/troubleshooting/ERROR_FIXES_SUMMARY.md** (Troubleshooting)

- This document summarizes the errors found in the solar heating system logs and the fixes implemented to resolve them.
- - Maintain backward compatibility while fixing the subscription errors
- 3. **Enhanced error handling** for MQTT operations
- Error creating TaskMaster AI task system_optimization: [Errno -2] Name or service not known
- Error creating TaskMaster AI task temperature_monitoring: [Errno -2] Name or service not known
- Error creating TaskMaster AI task safety_monitoring: [Errno -2] Name or service not known
- 2. **Enhanced error handling**:
- - Added specific exception handling for `httpx.ConnectError` (connection failures)
- - Connection failures logged as warnings (not errors)
- - `python/v3/taskmaster_integration.py` - Enhanced error handling

📄 **docs/troubleshooting/TROUBLESHOOTING_GUIDE.md** (Troubleshooting)

- 1. **User describes the issue**
- - MQTT connection errors in logs
- - Hardware errors in logs
- - Sensor data missing
- - [ ] Check if it's a new issue or recurring
- - [ ] Service logs (error messages)
- - [ ] Hardware logs (connection issues)
- - [ ] Network logs (connectivity issues)
- - [ ] No error messages in logs
- 5. **Report any issues** encountered

📄 **docs/troubleshooting/WARNING_FIXES_SUMMARY.md** (Troubleshooting)

- This document summarizes the warnings found in the solar heating system logs and the fixes implemented to resolve them.
- WARNING - No system callback registered for pellet stove data
- - The warning was misleading - the callback was actually working
- WARNING - Error reading MegaBAS sensor 5
- **Log Spam**: Generates excessive warning messages
- 1. **Physical disconnection** - Sensor wire disconnected or broken
- 3. **Configuration issue** - Incorrect sensor setup or calibration
- 4. **Power issue** - Insufficient power to sensor
- - **Before**: Warning logged every 30 seconds for same sensor
- - **After**: Warning logged only once per sensor until it recovers

📄 **docs/troubleshooting/WARNING_REDUCTION_SUMMARY.md** (Troubleshooting)

- Your solar heating system logs are filled with warnings like:
- WARNING - Invalid JSON payload on topic homeassistant/sensor/home_hugo_direction_of_travel/state: stationary
- WARNING - Invalid JSON payload on topic homeassistant/sensor/smartmeter_phase_power_current_l1/state: 005.8
- WARNING - Pellet stove sensor homeassistant/sensor/pelletskamin_last_seen/state: invalid numeric value '2025-09-04T08:51:47+00:00'
- - This caused warnings for normal string sensor values
- # These are raw string values - store without warnings
- logger.debug(f"Pellet stove timestamp sensor: {value}")
- except ValueError:
- logger.debug(f"Pellet stove string sensor: {value}")
- Warnings are now only shown for topics that **should** contain JSON:

📄 **docs/development/CHANGELOG.md** (Development)

- - **Energy Calculation Bug**: Fixed unrealistic energy values (800+ kWh) in dashboard
- - **Enhanced Logging**: Better energy calculation logging with validation warnings
- - Comprehensive error handling

📄 **docs/development/ENHANCED_COLLABORATION_WORKFLOW.md** (Development)

- - I ask clarifying questions to understand your needs
- - Confirm the approach meets your needs
- User: "I'm having an issue with [specific problem]"
- AI: "I've identified the issue. Here's the solution approach: [plan]"
- 1. **Reproduce Bug** → Write test that demonstrates the bug
- 2. **Fix Bug** → Make the test pass
- 3. **Regression Tests** → Ensure no other functionality is broken
- - **User trying to analyze complex technical issues** without AI guidance
- - **Bug fixes**: Quick fixes for obvious issues (but still write tests first)
- - **Emergency fixes**: Critical system issues (but still add tests after the fix)

📄 **docs/development/GITHUB_PROJECT_MANAGEMENT.md** (Development)

- Vi använder följande etiketter för att kategorisera issues:
- - `bug` - Något fungerar inte som det ska
- - `status: needs-info` - Behöver mer information
- Vi skapar mallar för olika typer av issues:
- - Issues som väntar på att börja arbeta med
- - Issues som är redo att arbeta med
- - Max 2-3 issues samtidigt
- - **Filtrera**: Aktiva issues (inte stängda)
- - Kritiska bugfixes
- 1. **Använd rätt template** (Bug Report eller Feature Request)

📄 **docs/development/GITHUB_PROJECT_SETUP.md** (Development)

- - **Syfte**: Issues som väntar på att börja arbeta med
- - **Syfte**: Issues som har all nödvändig information
- - **Syfte**: Max 2-3 issues samtidigt
- - **Begränsning**: Max 3 issues i denna kolumn
- - `bug` - Röd (#d73a4a) - Något fungerar inte som det ska
- - `status: needs-info` - Gul (#ffc107) - Behöver mer information
- - **Beskrivning**: Kritiska bugfixes och stabilitetsförbättringar
- - **Issues**: #1, #2, #3, #7, #10, #12
- - **Issues**: #4, #5, #8, #13
- - **Issues**: #6, #9, #11

📄 **docs/development/GITHUB_WORKFLOW_SUMMARY.md** (Development)

- - **Typ**: `bug`, `enhancement`, `feature`, `documentation`, `testing`
- - **Status**: `status: needs-info`, `status: ready`, `status: blocked`
- - **Fokus**: Kritiska bugfixes och stabilitet
- - **Issues**: #1, #2, #3, #7, #10, #12
- - **Issues**: #4, #5, #8, #13
- - **Issues**: #6, #9, #11
- 1. **Använd rätt template** (Bug Report, Feature Request, Enhancement)
- 3. **Stäng issue** med lämplig kommentar
- - Antal stängda issues denna vecka
- - **Länka till commits** - Koppla kod till issues

📄 **docs/development/INITIAL_GITHUB_ISSUES.md** (Development)

- Detta dokument listar de första issues som vi ska skapa på GitHub för att organisera utvecklingen.
- - **Typ**: `bug`
- - **Typ**: `bug`
- - **Typ**: `bug`
- - **Status**: `status: needs-info`
- - Issues: #1, #2, #3, #7, #10, #12
- - Fokus: Stabilitet och bugfixes
- - Issues: #4, #5, #8, #13
- - Issues: #6, #9, #11
- 1. **Skapa issues på GitHub** med ovanstående information

📄 **docs/python/deployment/AUTOMATED_DEPLOYMENT_GUIDE.md** (Python)

- 2. **Python dependencies missing:**
- 3. **Permission issues:**
- - **v2 System**: ❌ DEPRECATED (not maintained)

📄 **docs/python/deployment/FRESH_PI_DEPLOYMENT_STEPS.md** (Python)

- print(f"RTD error: {e}")
- print(f"MegaBAS error: {e}")
- 3. **Configure alerts** for temperature/pump issues

📄 **docs/python/deployment/README.md** (Python)

- - **v2 system**: ❌ DEPRECATED (not maintained)
- - ❌ `git_deployment_guide.md` - Complex, outdated process
- - ❌ `GIT_DEPLOYMENT_QUICK_REFERENCE.md` - Outdated reference
- - ✅ **Removed outdated references** - No more v1 system confusion

📄 **docs/python/deployment/TESTING_GUIDE.md** (Python)

- - ⚠️ Some tests will show warnings (expected on non-Pi systems)
- ⚠️  If any tests failed, check the warnings above before proceeding.
- **Common Warnings:**
- ❌ TEST ERROR: [specific error message]
- **Critical errors to fix:**
- - [ ] Test script runs without errors

📄 **docs/python/v1/README.md** (Python)

- - **`fix_v1_service.sh`** - Script to fix v1 service issues (682B)
- 3. **Enhanced features** - Real-time energy monitoring, better error handling
- - **Status**: DEPRECATED - Reference only

📄 **docs/python/v1/notes.md** (Python)

- logging.debug("solfangare_manuell_styrning: %s", solfangare_manuell_styrning)
- logging.error("%s. message from topic == %s", err, msg.topic)
- logging.debug("elpatron: %s", elpatron)
- logging.error("%s. message from topic == %s", err, msg.topic)

📄 **docs/python/v3/COMPREHENSIVE_TEST_IMPLEMENTATION_SUMMARY.md** (Python)

- | Error Recovery Testing | ✅ PASS | 43.67s | System recovery from failures |
- - Error handling in data flow
- - Tests error handling for missing/invalid data
- - Handles floating point precision issues
- - Error handling and graceful degradation (4 tests)
- - Handles errors gracefully
- python3 test_error_recovery.py
- - ❌ **Error recovery testing** - System recovery from failures
- - ✅ **Error recovery testing** - System recovery from failures
- 4. **Error Handling** - System gracefully handles failures and errors

📄 **docs/python/v3/CONTROL_SETUP_GUIDE.md** (Python)

- 1. MQTT connection issues
- 3. Hardware interface issues
- - Error messages
- 3. Hardware connection issues
- WARNING:root:Sequent Microsystems libraries not available. Running in simulation mode.
- 2. MQTT broker issues
- If you continue to have issues:
- The following files were updated to fix control issues:
- - `mqtt_handler.py` - Added missing topic subscriptions

📄 **docs/python/v3/DEPLOYMENT_GUIDE.md** (Python)

- - **Home Assistant**: Will receive alerts if watchdog issues occur
- - **Weekly**: Check health logs for any recurring issues
- If you encounter issues:
- The system is designed to be robust and self-healing, but these steps will help diagnose any issues.

📄 **docs/python/v3/ENHANCED_COMPREHENSIVE_TEST_STRATEGY.md** (Python)

- def test_sensor_error_handling(self):
- """TDD: Test sensor error handling"""
- # Add error handling, improve readability, etc.
- 4. **Error handling tests** - Test failure scenarios
- - ✅ **Early detection** of regressions and issues
- - ✅ **Error handling validation** and improvement

📄 **docs/python/v3/ENHANCED_TEST_ENVIRONMENT_FINAL_SUMMARY.md** (Python)

- - Error recovery testing
- - Likely behind firewall or requires authentication
- - ✅ **Error Handling** - Comprehensive failure scenario testing
- - ✅ **Error resilience** - Failure scenario testing

📄 **docs/python/v3/IMPLEMENTATION_SUMMARY.md** (Python)

- - **Auto-recovery**: Gracefully handles missing or corrupted files
- - Monitor logs for save/load errors
- 5. **✅ Reliable Operation** - Graceful handling of file system issues
- If you encounter any issues:
- 1. Check the logs for error messages

📄 **docs/python/v3/INSIGHTS_GUIDE.md** (Python)

- - Priority issues and alerts
- - Safety condition warnings
- if 'health_issues' in insights:
- for issue in insights['health_issues']:
- print(f"  ⚠️  {issue}")
- - ✅ **Detects issues before they become problems**
- - Check system logs for errors

📄 **docs/python/v3/MIDNIGHT_RESET_IMPLEMENTATION.md** (Python)

- # Handles missing file gracefully
- - **Graceful Fallback:** Continues with defaults if file missing
- ❌ Failed to save operational state: [error details]
- ❌ Failed to load operational state: [error details]
- - Handles file I/O errors gracefully
- 4. **Reliability:** Graceful handling of file system issues

📄 **docs/python/v3/README.md** (Python)

- SOLAR_DEBUG_MODE=false
- 3. **Run with debug logging**:
- SOLAR_DEBUG_MODE=true python main.py
- - **Temperature Alerts**: High/low temperature warnings
- - Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Enable debug logging for detailed troubleshooting:
- SOLAR_DEBUG_MODE=true SOLAR_LOG_LEVEL=debug python main.py

📄 **docs/python/v3/SENSOR_MAPPING.md** (Python)

- - Detection of mixing or stratification issues
- **Medium Priority (Requires additional data):**
- 1. `solar_collector_efficiency` - Needs solar radiation data
- 3. `energy_remaining_hours` - Needs consumption rate data
- 4. `freeze_protection_status` - Needs freeze threshold setting
- 3. `energy_cost_saved` - Needs electricity rate data
- 2. **Predictive Maintenance**: Runtime and health metrics predict maintenance needs
- 5. **Error Handling**: v3 includes better error handling and validation
- Use the debug script to verify sensor readings:
- python3 debug_sensors.py

📄 **docs/python/v3/TASKMASTER_INTEGRATION.md** (Python)

- - Check system logs for error messages
- SOLAR_DEBUG_MODE=true python main_system.py
- - **Predictive Alerts**: Early warning of issues

📄 **docs/python/v3/TEST_SUITE_README.md** (Python)

- - **Hardware Interface** - Sensor reading, relay control, error handling
- - **Error Handling** - Software error handling and recovery
- - **Hardware Error Handling** - Physical hardware error conditions
- - Error handling (invalid sensors, relays)
- If you encounter issues with the test suite:
- 4. **Review test output** for specific error messages

