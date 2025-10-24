# Technical Design: Rate of Change Sensors

## **Overview**
Implementation of configurable rate-of-change sensors for monitoring stored energy and average temperature changes in real-time.

## **Architecture**

### **Core Components**
1. **Rate Calculator**: Calculates change rates over configurable time windows
2. **Smoothing Engine**: Applies different smoothing algorithms
3. **Configuration Manager**: Handles time windows and smoothing options
4. **MQTT Publisher**: Publishes rates as separate sensors

### **Data Flow**
```
Temperature/Energy Data → Rate Calculator → Smoothing Engine → MQTT Publisher → Home Assistant
```

## **Technical Implementation**

### **1. Rate Calculation Methods**

#### **Time Windows**
- **Fast (30s)**: `RATE_WINDOW_FAST = 30`
- **Medium (2min)**: `RATE_WINDOW_MEDIUM = 120`
- **Slow (5min)**: `RATE_WINDOW_SLOW = 300`

#### **Calculation Formula**
```python
# Energy Rate (kW)
energy_rate = (current_energy - previous_energy) / time_difference_hours

# Temperature Rate (°C/hour)
temp_rate = (current_temp - previous_temp) / time_difference_hours
```

### **2. Smoothing Algorithms**

#### **Raw (No Smoothing)**
- Direct rate values
- Most responsive, potentially noisy

#### **Simple Moving Average**
- 3-point average: `(rate1 + rate2 + rate3) / 3`
- Balanced response and noise reduction

#### **Exponential Smoothing**
- Weighted average: `α × current_rate + (1-α) × previous_smoothed`
- α = 0.3 (configurable)
- Smooths noise while maintaining responsiveness

### **3. Data Storage**
```python
class RateData:
    def __init__(self):
        self.timestamps = []      # List of measurement times
        self.energy_values = []   # List of energy readings
        self.temp_values = []     # List of temperature readings
        self.max_samples = 20     # Maximum samples to store
```

### **4. Configuration Options**
```python
RATE_CONFIG = {
    'time_window': 'medium',     # fast/medium/slow
    'smoothing': 'exponential',  # raw/simple/exponential
    'update_interval': 30,       # Seconds between calculations
    'smoothing_alpha': 0.3       # Exponential smoothing factor
}
```

## **Integration Points**

### **Existing System**
- Integrates with `_read_temperatures()` method
- Extends `self.temperatures` dictionary
- Uses existing MQTT publishing infrastructure

### **New MQTT Topics**
- `solar_heating_v3/energy_change_rate_kw`
- `solar_heating_v3/temperature_change_rate_c_h`

### **Home Assistant Discovery**
- Creates two new sensor entities
- Configurable units and device classes
- Automatic discovery and configuration

## **Performance Considerations**

### **Memory Usage**
- Limited sample storage (max 20 samples)
- Automatic cleanup of old data
- Minimal impact on existing system

### **Calculation Overhead**
- Rate calculations: ~1ms per sensor
- Smoothing: ~0.1ms per sensor
- Total overhead: <5ms per update cycle

### **Data Accuracy**
- Handles sensor noise through smoothing
- Configurable time windows for different use cases
- Real-time vs. averaged data options

## **Error Handling**

### **Edge Cases**
- Insufficient data for calculation
- Division by zero protection
- Invalid sensor readings
- Configuration errors

### **Fallback Behavior**
- Return 0.0 for rates when insufficient data
- Log warnings for configuration issues
- Continue operation with default values

## **Testing Strategy**

### **Unit Tests**
- Rate calculation accuracy
- Smoothing algorithm correctness
- Configuration validation
- Error handling

### **Integration Tests**
- MQTT publishing
- Home Assistant discovery
- System performance impact
- Configuration changes

### **User Testing**
- Different time window configurations
- Smoothing method comparison
- Real-world performance monitoring
