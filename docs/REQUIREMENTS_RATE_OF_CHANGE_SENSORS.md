# Requirements: Rate of Change Sensors

## **Requirement:** Add sensors for momentary change of stored energy and average temperature

## **Problem:** 
- Need to monitor how quickly energy is being added/removed from the tank
- Need to monitor how quickly average temperature is changing
- Current system only shows absolute values, not rates of change
- Difficult to detect system performance issues or efficiency changes in real-time

## **Desired Outcome:**
- **Energy Change Rate Sensor**: Shows power being added/removed (kW) - positive for heating, negative for cooling/loss
- **Temperature Change Rate Sensor**: Shows temperature change rate (°C/hour) - positive for warming, negative for cooling
- **Configurable Options**: Multiple time windows and smoothing methods to test and optimize
- **Separate MQTT Sensors**: Easy integration with Home Assistant
- **Real-time Monitoring**: Immediate visibility into system performance

## **Context:**
- Current v3 system calculates stored energy and average temperature
- System has 8 RTD sensors for temperature monitoring
- Energy calculations use water volume × temperature difference × specific heat
- MQTT integration already exists for sensor publishing

## **Constraints:**
- Must integrate with existing v3 system architecture
- Must not impact existing sensor performance
- Must be configurable without system restart
- Must handle sensor noise and provide meaningful data

## **Questions:**
1. **Time Windows**: Test 30s, 2min, 5min intervals?
2. **Smoothing**: Test raw, simple average, exponential smoothing?
3. **Units**: kW for energy rate, °C/hour for temperature rate?
4. **Integration**: Separate MQTT sensors for Home Assistant?

## **Success Criteria:**
- ✅ Two new rate-of-change sensors working
- ✅ Configurable time windows and smoothing
- ✅ Positive/negative values showing direction of change
- ✅ Integration with existing MQTT system
- ✅ Home Assistant discovery working
- ✅ User can test different configurations
- ✅ No impact on existing system performance
