# User Guide: Rate of Change Sensors

## **Overview**
The Rate of Change Sensors provide real-time monitoring of how quickly energy and temperature are changing in your solar heating system. These sensors help you understand system performance, detect issues, and optimize operation.

## **What You Get**

### **Two New Sensors**
1. **Energy Change Rate** - Shows power being added/removed (kW)
   - **Positive values**: Energy increasing (heating)
   - **Negative values**: Energy decreasing (cooling/water usage)
   
2. **Temperature Change Rate** - Shows temperature change speed (°C/hour)
   - **Positive values**: Temperature rising (warming)
   - **Negative values**: Temperature falling (cooling)

### **Configurable Options**
- **Time Windows**: Fast (30s), Medium (2min), Slow (5min)
- **Smoothing**: Raw, Simple Average, Exponential
- **Update Intervals**: Configurable calculation frequency

## **How to Use**

### **1. View the Sensors in Home Assistant**
The sensors automatically appear in Home Assistant as:
- `sensor.solar_heating_v3_energy_change_rate_kw`
- `sensor.solar_heating_v3_temperature_change_rate_c_h`

### **2. Understand the Values**

#### **Energy Change Rate (kW)**
- **+2.5 kW**: System gaining 2.5 kW of power (heating)
- **-1.8 kW**: System losing 1.8 kW of power (water usage)
- **0.0 kW**: No change in stored energy

#### **Temperature Change Rate (°C/hour)**
- **+3.2 °C/h**: Temperature rising at 3.2°C per hour
- **-2.1 °C/h**: Temperature falling at 2.1°C per hour
- **0.0 °C/h**: Temperature stable

### **3. Configure the Sensors**

#### **Environment Variables**
Create or update your `.env` file:
```bash
# Time window for rate calculation
SOLAR_RATE_TIME_WINDOW=medium    # fast/medium/slow

# Smoothing method
SOLAR_RATE_SMOOTHING=exponential # raw/simple/exponential

# Update interval (seconds)
SOLAR_RATE_UPDATE_INTERVAL=30

# Exponential smoothing factor (0.1-0.9)
SOLAR_RATE_SMOOTHING_ALPHA=0.3
```

#### **Runtime Configuration**
You can change settings while the system is running:
```python
# Update time window
system._update_rate_config({'time_window': 'fast'})

# Change smoothing method
system._update_rate_config({'smoothing': 'simple'})

# Adjust smoothing sensitivity
system._update_rate_config({'smoothing_alpha': 0.5})
```

## **Configuration Options Explained**

### **Time Windows**

#### **Fast (30 seconds)**
- **Best for**: Real-time monitoring, quick response
- **Pros**: Immediate feedback, shows rapid changes
- **Cons**: More noise, may be jumpy
- **Use when**: Debugging, testing, need immediate visibility

#### **Medium (2 minutes)**
- **Best for**: General monitoring, balanced view
- **Pros**: Good balance of responsiveness and stability
- **Cons**: Slight delay in detecting changes
- **Use when**: Normal operation, general monitoring

#### **Slow (5 minutes)**
- **Best for**: Trend analysis, stable readings
- **Pros**: Very stable, shows clear trends
- **Cons**: Slower response to changes
- **Use when**: Long-term monitoring, trend analysis

### **Smoothing Methods**

#### **Raw (No Smoothing)**
- **What it does**: Shows actual calculated rates
- **Best for**: Debugging, seeing real data
- **Pros**: No data modification, immediate response
- **Cons**: Can be noisy, may fluctuate

#### **Simple Average**
- **What it does**: 3-point moving average
- **Best for**: Balanced monitoring
- **Pros**: Reduces noise, maintains responsiveness
- **Cons**: Slight delay, may miss rapid changes

#### **Exponential Smoothing**
- **What it does**: Weighted average favoring recent data
- **Best for**: Production use, stable monitoring
- **Pros**: Smooth output, configurable sensitivity
- **Cons**: More complex, requires tuning

## **Real-World Examples**

### **Example 1: Normal Solar Heating**
- **Energy Rate**: +1.2 kW (positive = heating)
- **Temperature Rate**: +2.1 °C/h (positive = warming)
- **What it means**: System is actively heating, gaining energy and temperature

### **Example 2: Water Usage**
- **Energy Rate**: -2.8 kW (negative = losing energy)
- **Temperature Rate**: -1.5 °C/h (negative = cooling)
- **What it means**: Hot water is being used, system is cooling down

### **Example 3: System Stable**
- **Energy Rate**: 0.0 kW (no change)
- **Temperature Rate**: 0.0 °C/h (no change)
- **What it means**: System is in equilibrium, no heating or cooling

### **Example 4: Rapid Heating**
- **Energy Rate**: +4.5 kW (high positive = rapid heating)
- **Temperature Rate**: +5.2 °C/h (high positive = rapid warming)
- **What it means**: System is heating very quickly, possibly high solar input

## **Troubleshooting**

### **Common Issues**

#### **Sensors Show 0.0**
- **Cause**: Insufficient data for calculation
- **Solution**: Wait 1-2 minutes for data to accumulate
- **Check**: Ensure system is running and collecting temperature data

#### **Values Are Too Noisy**
- **Cause**: Raw smoothing with fast time window
- **Solution**: Switch to exponential smoothing or slower time window
- **Example**: Change from `fast` + `raw` to `medium` + `exponential`

#### **Values Are Too Slow to Respond**
- **Cause**: Slow time window or heavy smoothing
- **Solution**: Use faster time window or raw smoothing
- **Example**: Change from `slow` + `exponential` to `medium` + `simple`

#### **Configuration Changes Not Taking Effect**
- **Cause**: Invalid configuration values
- **Solution**: Check environment variable format and restart system
- **Check**: Look for error messages in system logs

### **Performance Monitoring**

#### **Check System Logs**
Look for rate calculation messages:
```
Rate calculation: Energy: 1.234 kW, Temp: 2.100 °C/h
Rate time window updated to: fast
Rate smoothing updated to: exponential
```

#### **Monitor MQTT Topics**
Verify sensors are publishing:
- `homeassistant/sensor/solar_heating_energy_change_rate_kw/state`
- `homeassistant/sensor/solar_heating_temperature_change_rate_c_h/state`

## **Best Practices**

### **For Different Use Cases**

#### **Daily Monitoring**
- **Time Window**: Medium (2 minutes)
- **Smoothing**: Exponential
- **Alpha**: 0.3
- **Update Interval**: 30 seconds

#### **Debugging/Troubleshooting**
- **Time Window**: Fast (30 seconds)
- **Smoothing**: Raw
- **Update Interval**: 15 seconds

#### **Trend Analysis**
- **Time Window**: Slow (5 minutes)
- **Smoothing**: Exponential
- **Alpha**: 0.2
- **Update Interval**: 60 seconds

### **Configuration Tips**

1. **Start with Medium + Exponential**: Good balance for most users
2. **Adjust Alpha for Sensitivity**: Lower = smoother, Higher = more responsive
3. **Match Time Window to Needs**: Fast for debugging, Slow for trends
4. **Monitor Performance**: Watch system logs for any issues

## **Integration with Home Assistant**

### **Automations**
Create automations based on rate changes:
```yaml
# Alert on rapid energy loss
automation:
  - alias: "Alert Rapid Energy Loss"
    trigger:
      platform: numeric_state
      entity_id: sensor.solar_heating_v3_energy_change_rate_kw
      below: -3.0
    action:
      - service: notify.mobile_app
        data:
          message: "Warning: Rapid energy loss detected!"
```

### **Dashboards**
Add rate sensors to your dashboard:
```yaml
# Dashboard card for rate sensors
type: entities
entities:
  - entity: sensor.solar_heating_v3_energy_change_rate_kw
    name: Energy Change Rate
  - entity: sensor.solar_heating_v3_temperature_change_rate_c_h
    name: Temperature Change Rate
```

### **History and Trends**
- **Energy Rate**: Shows heating efficiency over time
- **Temperature Rate**: Shows system responsiveness
- **Combined Analysis**: Identify optimal operating conditions

## **Advanced Usage**

### **Custom Calculations**
Use the rate data for advanced analysis:
- **Efficiency Monitoring**: Energy rate vs. solar input
- **Performance Tracking**: Temperature rate vs. pump operation
- **Usage Patterns**: Identify peak usage times
- **System Health**: Detect unusual rate changes

### **Integration with Other Systems**
- **InfluxDB**: Store rate data for long-term analysis
- **Grafana**: Create custom dashboards
- **External APIs**: Send alerts or data to other services
- **Machine Learning**: Use rate data for predictive maintenance

## **Support and Troubleshooting**

### **Getting Help**
1. **Check System Logs**: Look for rate calculation messages
2. **Verify Configuration**: Ensure environment variables are correct
3. **Test Different Settings**: Try different time windows and smoothing
4. **Monitor MQTT**: Verify sensors are publishing data

### **Common Questions**

**Q: Why do I see negative values?**
A: Negative values are normal! They indicate energy loss (water usage) or temperature decrease (cooling).

**Q: Which time window should I use?**
A: Start with "medium" for general use, "fast" for debugging, "slow" for trend analysis.

**Q: How do I make the values less jumpy?**
A: Use exponential smoothing with a lower alpha value (0.2-0.3) or switch to a slower time window.

**Q: Can I change settings without restarting?**
A: Yes! Use the `_update_rate_config()` method to change settings at runtime.

## **Conclusion**

The Rate of Change Sensors provide valuable insights into your solar heating system's performance. Start with the default settings and adjust based on your monitoring needs. These sensors will help you:

- **Monitor System Performance**: See how efficiently your system is heating
- **Detect Issues Early**: Identify unusual energy or temperature changes
- **Optimize Operation**: Understand what conditions work best
- **Track Usage Patterns**: See when and how much hot water is used

Experiment with different configurations to find what works best for your specific use case!
