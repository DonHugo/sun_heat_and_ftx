# User Guide: Home Assistant Integration

## 🎯 **How to Use the Integration**

This guide explains how to use your Home Assistant integration, from initial setup to daily operation and advanced features. The integration brings comprehensive smart home control and monitoring to your solar heating system.

## 🚀 **Getting Started**

### **Quick Start (5 Minutes)**

1. **Open Home Assistant**: Navigate to your Home Assistant instance
2. **Go to Settings**: Click on "Settings" in the sidebar
3. **Add Integration**: Click "Devices & Services" → "Add Integration"
4. **Search for Solar Heating**: Type "Solar Heating v3" in the search box
5. **Configure Integration**: Enter your MQTT broker details and click "Submit"

### **First-Time Setup (15 Minutes)**

1. **Install Required Add-ons**:
   - **MQTT Broker**: If not already installed
   - **File Editor**: For configuration editing
   - **Terminal & SSH**: For troubleshooting

2. **Configure MQTT Broker**:
   ```yaml
   # In your MQTT Broker configuration
   broker: 192.168.1.100  # Your MQTT broker IP
   port: 1883
   username: your_username
   password: your_password
   ```

3. **Add Solar Heating Integration**:
   - Navigate to **Settings** → **Devices & Services**
   - Click **"Add Integration"**
   - Search for **"Solar Heating v3"**
   - Enter your MQTT broker details
   - Click **"Submit"**

4. **Verify Installation**:
   - Check that entities appear in **Settings** → **Entities**
   - Verify dashboard appears in **Overview**

## 🎛️ **Daily Operation**

### **Accessing Your Solar Heating Dashboard**

#### **Main Dashboard Access**

1. **From Home Assistant Home**: Click on "Solar Heating System" card
2. **Direct URL**: Navigate to `/lovelace/solar-heating-system`
3. **Sidebar**: Look for "Solar Heating" in the main navigation

#### **Dashboard Overview**

Your main dashboard includes these key sections:

- **🏠 Overview Tab**: System status, quick controls, key metrics
- **🎛️ Control Tab**: Pump control, temperature settings, mode selection
- **📊 Monitoring Tab**: Temperature charts, efficiency graphs, historical data
- **🤖 AI Insights Tab**: AI recommendations, optimization history
- **⚙️ Settings Tab**: Configuration, preferences, system settings

### **Monitoring System Status**

#### **Real-Time System Monitoring**

1. **System Status Card**:
   - Current operational mode (Auto/Manual/Eco)
   - Pump status (Running/Stopped)
   - System health indicators

2. **Temperature Monitoring**:
   - Collector temperature (real-time)
   - Tank temperature (real-time)
   - Ambient temperature
   - Temperature trends (24-hour graph)

3. **Efficiency Metrics**:
   - Current system efficiency
   - Energy consumption
   - Performance indicators

#### **Quick Status Check**

```bash
# Check system status via Home Assistant API
curl -H "Authorization: Bearer YOUR_LONG_LIVED_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     http://your-ha-ip:8123/api/states/sensor.solar_heating_system_status

# Check pump status
curl -H "Authorization: Bearer YOUR_LONG_LIVED_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     http://your-ha-ip:8123/api/states/switch.solar_heating_pump
```

### **System Control and Automation**

#### **Manual Control**

1. **Pump Control**:
   - **Start Pump**: Click "Start Pump" button on dashboard
   - **Stop Pump**: Click "Stop Pump" button on dashboard
   - **Pump Status**: Real-time status display

2. **Temperature Control**:
   - **Set Target Temperature**: Use temperature slider or input field
   - **Mode Selection**: Choose between Auto, Manual, or Eco modes
   - **Override Settings**: Temporarily override automatic operation

3. **System Mode Control**:
   - **Auto Mode**: Fully automatic operation
   - **Manual Mode**: Manual control with safety limits
   - **Eco Mode**: Energy-saving operation

#### **Automation Examples**

Create intelligent automations in Home Assistant:

```yaml
# Example: Start pump when collector is hot enough
automation:
  - alias: "Start Pump When Hot"
    trigger:
      platform: numeric_state
      entity_id: sensor.solar_heating_collector_temperature
      above: 70
    condition:
      - condition: state
        entity_id: switch.solar_heating_pump
        state: 'off'
      - condition: time
        after: '08:00:00'
        before: '18:00:00'
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.solar_heating_pump

# Example: Stop pump when tank is full
automation:
  - alias: "Stop Pump When Tank Full"
    trigger:
      platform: numeric_state
      entity_id: sensor.solar_heating_tank_temperature
      above: 85
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.solar_heating_pump
      - service: notify.mobile_app
        data:
          title: "Solar Heating"
          message: "Tank temperature reached 85°C, pump stopped"

# Example: Weather-based optimization
automation:
  - alias: "Weather-Based Pump Control"
    trigger:
      platform: state
      entity_id: weather.home
    action:
      - service: input_select.select_option
        target:
          entity_id: input_select.solar_heating_mode
        data:
          option: >
            {% if is_state('weather.home', 'sunny') %}
              auto
            {% else %}
              eco
            {% endif %}
```

## 🔧 **Configuration and Customization**

### **Integration Configuration**

#### **Basic Configuration**

Access integration settings:

1. **Go to Settings**: **Settings** → **Devices & Services**
2. **Find Integration**: Click on "Solar Heating v3" integration
3. **Configure**: Click "Configure" button

#### **Configuration Options**

```yaml
# Example configuration.yaml entry
solar_heating_v3:
  mqtt:
    broker: 192.168.1.100
    port: 1883
    username: your_username
    password: your_password
    discovery: true
    discovery_prefix: "solar_heating_v3/discovery"
  
  sensors:
    temperature_update_interval: 30
    history_retention_days: 30
  
  dashboard:
    auto_create: true
    theme: "solar_heating"
    refresh_interval: 5
  
  notifications:
    enabled: true
    temperature_alerts: true
    efficiency_alerts: true
    maintenance_reminders: true
```

#### **Advanced Configuration**

```yaml
# Advanced configuration options
solar_heating_v3:
  # MQTT Configuration
  mqtt:
    broker: 192.168.1.100
    port: 1883
    username: your_username
    password: your_password
    use_tls: false
    keepalive: 60
    discovery: true
    discovery_prefix: "solar_heating_v3/discovery"
    status_topic: "solar_heating_v3/status"
    control_topic: "solar_heating_v3/control"
    sensor_topic: "solar_heating_v3/sensors"
  
  # Sensor Configuration
  sensors:
    temperature_update_interval: 30
    history_retention_days: 30
    temperature_units: "celsius"
    pressure_units: "bar"
    flow_units: "lpm"
  
  # Dashboard Configuration
  dashboard:
    auto_create: true
    theme: "solar_heating"
    refresh_interval: 5
    default_view: "overview"
    show_ai_insights: true
    show_advanced_controls: false
  
  # Notification Configuration
  notifications:
    enabled: true
    temperature_alerts: true
    temperature_threshold_high: 90
    temperature_threshold_low: 20
    efficiency_alerts: true
    efficiency_threshold: 70
    maintenance_reminders: true
    maintenance_interval_days: 30
  
  # Automation Configuration
  automations:
    auto_optimization: true
    weather_integration: true
    schedule_integration: true
    occupancy_integration: false
  
  # Security Configuration
  security:
    require_authentication: true
    allowed_users: ["admin", "family"]
    api_access: true
    webhook_security: true
```

### **Dashboard Customization**

#### **Custom Dashboard Layout**

1. **Edit Dashboard**: Click "Edit Dashboard" button
2. **Add Cards**: Click "+" button to add new cards
3. **Customize Cards**: Click on cards to edit properties
4. **Save Changes**: Click "Save" button

#### **Custom Card Examples**

```yaml
# Custom temperature display card
type: custom:mini-graph-card
title: "Collector Temperature"
entity: sensor.solar_heating_collector_temperature
hours_to_show: 24
points_per_hour: 2
aggregate_func: avg
line_width: 2
color: orange
show_points: false

# Custom pump control card
type: custom:button-card
title: "Pump Control"
entity: switch.solar_heating_pump
show_state: true
show_icon: true
icon: mdi:pump
color: >
  [[[
    if (entity.state == 'on') return 'green';
    return 'red';
  ]]]
```

#### **Theme Customization**

Create a custom theme for your solar heating dashboard:

```yaml
# In your themes.yaml file
solar_heating_theme:
  # Primary colors
  primary-color: "#ff6b35"
  primary-background-color: "#2c3e50"
  
  # Secondary colors
  secondary-background-color: "#34495e"
  secondary-text-color: "#ecf0f1"
  
  # Accent colors
  accent-color: "#e74c3c"
  accent-color-transparent: "#e74c3c80"
  
  # Text colors
  primary-text-color: "#ffffff"
  text-primary-color: "#ffffff"
  
  # Card colors
  card-background-color: "#34495e"
  card-rgb-color: "52, 73, 94"
  
  # State colors
  state-icon-active-color: "#27ae60"
  state-icon-inactive-color: "#e74c3c"
  
  # Custom variables
  solar-heating-primary: "#ff6b35"
  solar-heating-secondary: "#f39c12"
  solar-heating-success: "#27ae60"
  solar-heating-warning: "#f39c12"
  solar-heating-danger: "#e74c3c"
```

## 📱 **Mobile and Remote Access**

### **Home Assistant Mobile App**

1. **Install App**: Download from App Store or Google Play
2. **Connect to Instance**: Enter your Home Assistant URL
3. **Login**: Use your Home Assistant credentials
4. **Access Dashboard**: Navigate to Solar Heating dashboard

### **Remote Access Setup**

#### **Secure Remote Access**

1. **Enable HTTPS**: Configure SSL certificate in Home Assistant
2. **Set Up DuckDNS**: For dynamic DNS (if needed)
3. **Configure Port Forwarding**: Forward port 8123 to your Home Assistant server
4. **Set Up Authentication**: Enable two-factor authentication

#### **Remote Access Configuration**

```yaml
# In your configuration.yaml
http:
  ssl_cert: /path/to/your/certificate.crt
  ssl_key: /path/to/your/private.key
  base_url: https://your-domain.duckdns.org:8123
  trusted_proxies:
    - 127.0.0.1
    - ::1
    - 192.168.1.0/24

# Enable external access
homeassistant:
  allowlist_external_dirs:
    - /config/www
    - /media
```

### **Voice Control Integration**

#### **Google Assistant Setup**

1. **Enable Google Assistant**: In Home Assistant settings
2. **Link Account**: Connect your Google account
3. **Discover Devices**: Google will discover your solar heating entities
4. **Voice Commands**: Use voice to control your system

#### **Voice Command Examples**

- **"Hey Google, what's the solar heating temperature?"**
- **"Hey Google, start the solar heating pump"**
- **"Hey Google, set solar heating to auto mode"**
- **"Hey Google, what's the solar heating efficiency?"**

#### **Alexa Integration**

1. **Install Alexa Skill**: Add Home Assistant skill to Alexa
2. **Link Account**: Connect your Home Assistant instance
3. **Discover Devices**: Alexa will find your solar heating devices
4. **Voice Control**: Use Alexa to control your system

## 🔍 **Monitoring and Diagnostics**

### **System Health Monitoring**

#### **Check Integration Status**

1. **Integration Status**: **Settings** → **Devices & Services** → **Solar Heating v3**
2. **Entity Status**: **Settings** → **Entities** → Search for "solar_heating"
3. **System Logs**: **Settings** → **System** → **Logs**

#### **Performance Monitoring**

```bash
# Check Home Assistant performance
# In Home Assistant Terminal or SSH add-on
ha core info
ha system info

# Check MQTT connection
mosquitto_sub -h your-broker -t "solar_heating_v3/status/#" -u username -P password

# Check system resources
htop
df -h
free -h
```

### **Troubleshooting Common Issues**

#### **Integration Not Working**

1. **Check MQTT Connection**:
   - Verify MQTT broker is running
   - Check credentials and connection settings
   - Test MQTT connection manually

2. **Check Entity States**:
   - Go to **Settings** → **Entities**
   - Search for "solar_heating"
   - Check if entities show as "unavailable"

3. **Check Logs**:
   - **Settings** → **System** → **Logs**
   - Look for error messages related to solar heating

#### **Dashboard Not Loading**

1. **Check Dashboard Configuration**:
   - Verify dashboard exists in **Overview**
   - Check dashboard configuration in **Lovelace**

2. **Check Custom Cards**:
   - Ensure required custom cards are installed
   - Check card configuration for errors

3. **Clear Browser Cache**:
   - Hard refresh the page (Ctrl+F5)
   - Clear browser cache and cookies

#### **Entities Not Updating**

1. **Check MQTT Topics**:
   - Verify MQTT topics are correct
   - Check if messages are being published

2. **Check Integration Configuration**:
   - Verify MQTT broker settings
   - Check entity discovery settings

3. **Restart Integration**:
   - **Settings** → **Devices & Services** → **Solar Heating v3**
   - Click "Reload" button

## 🚨 **Safety and Security**

### **Security Best Practices**

1. **Strong Passwords**: Use strong, unique passwords
2. **Two-Factor Authentication**: Enable 2FA for your Home Assistant account
3. **Network Security**: Use secure Wi-Fi and firewall protection
4. **Regular Updates**: Keep Home Assistant and add-ons updated
5. **Access Control**: Limit access to trusted users only

### **Safety Features**

1. **Temperature Limits**: System won't exceed safe temperature limits
2. **Pump Protection**: Automatic shutdown on system errors
3. **Manual Override**: Easy manual control when needed
4. **Safety Notifications**: Alerts for dangerous conditions

### **Emergency Procedures**

1. **Immediate Shutdown**: Use emergency stop button on dashboard
2. **Manual Control**: Switch to manual mode for direct control
3. **System Reset**: Restart Home Assistant if needed
4. **Contact Support**: Get help if issues persist

## 🔄 **Maintenance and Updates**

### **Regular Maintenance**

#### **Daily Checks**

- [ ] Check dashboard for system status
- [ ] Verify temperature readings are normal
- [ ] Check pump operation status
- [ ] Review any error notifications

#### **Weekly Maintenance**

- [ ] Review system performance metrics
- [ ] Check efficiency trends
- [ ] Verify automation rules are working
- [ ] Update dashboard if needed

#### **Monthly Maintenance**

- [ ] Review system logs for errors
- [ ] Check MQTT connection stability
- [ ] Update Home Assistant and add-ons
- [ ] Backup configuration

### **System Updates**

#### **Home Assistant Updates**

1. **Check for Updates**: **Settings** → **System** → **Updates**
2. **Review Release Notes**: Read about new features and changes
3. **Create Backup**: Backup before updating
4. **Update System**: Click "Update" button

#### **Integration Updates**

1. **Check Integration Updates**: **Settings** → **Devices & Services**
2. **Update Integration**: Click "Update" if available
3. **Test Functionality**: Verify everything works after update

### **Backup and Recovery**

#### **Configuration Backup**

```bash
# Backup Home Assistant configuration
# In Terminal add-on
cd /config
tar -czf backup-$(date +%Y%m%d).tar.gz .

# Backup to external location
scp backup-*.tar.gz user@backup-server:/backups/
```

#### **Recovery Procedures**

1. **Restore Configuration**: Extract backup to `/config` directory
2. **Restart Home Assistant**: Restart the system
3. **Verify Integration**: Check that solar heating integration works
4. **Test Functionality**: Verify all features are working

## 📊 **Advanced Features**

### **Custom Automations**

#### **Advanced Automation Examples**

```yaml
# Weather-based optimization
automation:
  - alias: "Weather-Based Solar Optimization"
    trigger:
      - platform: time
        at: "06:00:00"
      - platform: state
        entity_id: weather.home
    condition:
      - condition: time
        after: "06:00:00"
        before: "18:00:00"
    action:
      - service: input_select.select_option
        target:
          entity_id: input_select.solar_heating_mode
        data:
          option: >
            {% if is_state('weather.home', 'sunny') %}
              auto
            {% elif is_state('weather.home', 'partlycloudy') %}
              eco
            {% else %}
              manual
            {% endif %}

# Efficiency-based scheduling
automation:
  - alias: "Efficiency-Based Pump Control"
    trigger:
      platform: numeric_state
      entity_id: sensor.solar_heating_efficiency
      below: 60
    condition:
      - condition: state
        entity_id: switch.solar_heating_pump
        state: 'on'
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.solar_heating_pump
      - service: notify.mobile_app
        data:
          title: "Solar Heating Alert"
          message: "Low efficiency detected, pump stopped for optimization"
```

### **Data Export and Analysis**

#### **Export Historical Data**

```bash
# Export temperature data via Home Assistant API
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://your-ha-ip:8123/api/history/period/2024-01-01T00:00:00/2024-01-31T23:59:59?filter_entity_id=sensor.solar_heating_collector_temperature" \
     | jq '.[0].state' > temperature_data.json

# Export efficiency data
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://your-ha-ip:8123/api/history/period/2024-01-01T00:00:00/2024-01-31T23:59:59?filter_entity_id=sensor.solar_heating_efficiency" \
     | jq '.[0].state' > efficiency_data.json
```

#### **Data Analysis Tools**

1. **Home Assistant Analytics**: Built-in analytics dashboard
2. **Grafana Integration**: Advanced data visualization
3. **InfluxDB**: Time-series database for historical data
4. **Custom Scripts**: Python scripts for data analysis

## 🔗 **Related Documentation**

- **[Requirements Document](REQUIREMENTS_HOME_ASSISTANT.md)** - What we built and why
- **[Design Document](DESIGN_HOME_ASSISTANT.md)** - How the integration works
- **[Implementation Guide](IMPLEMENTATION_HOME_ASSISTANT.md)** - Technical implementation details
- **[Summary](SUMMARY_HOME_ASSISTANT.md)** - Complete integration overview
- **[System Overview](../SYSTEM_OVERVIEW.md)** - Complete system understanding
- **[Component Map](../COMPONENT_MAP.md)** - System component relationships

---

**This guide explains how to use your Home Assistant integration for daily operation, configuration, monitoring, and troubleshooting. For technical details, refer to the Design and Implementation documents.**
