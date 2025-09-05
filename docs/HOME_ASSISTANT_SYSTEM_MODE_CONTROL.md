# Home Assistant System Mode Control Guide

## 🎯 **Overview**

This guide shows you how to implement system mode control in Home Assistant for the Solar Heating System v3, including Auto Mode, Manual Mode, and Eco Mode with proper safety limits and automation.

## 🔧 **System Mode Implementation**

### **1. Create Mode Selector Entity**

First, you need to add a mode selector to your Home Assistant configuration. Add this to your `configuration.yaml`:

```yaml
# configuration.yaml
input_select:
  solar_heating_mode:
    name: "Solar Heating System Mode"
    options:
      - "auto"
      - "manual" 
      - "eco"
    initial: "auto"
    icon: mdi:thermostat

# Create helper entities for mode states
input_boolean:
  solar_heating_auto_mode:
    name: "Auto Mode Active"
    icon: mdi:robot
  solar_heating_manual_mode:
    name: "Manual Mode Active" 
    icon: mdi:hand-back
  solar_heating_eco_mode:
    name: "Eco Mode Active"
    icon: mdi:leaf
```

### **2. MQTT Integration for Mode Control**

Add these MQTT entities to your `configuration.yaml`:

```yaml
# configuration.yaml
mqtt:
  select:
    - name: "Solar Heating System Mode"
      unique_id: "solar_heating_system_mode_control"
      state_topic: "homeassistant/select/solar_heating_system_mode/state"
      command_topic: "homeassistant/select/solar_heating_system_mode/set"
      options:
        - "auto"
        - "manual"
        - "eco"
      icon: mdi:thermostat
      device:
        identifiers: ["solar_heating_v3"]
        name: "Solar Heating System v3"
        manufacturer: "Custom"
        model: "Solar Heating v3"
```

### **3. Dashboard Configuration**

Add this to your Lovelace dashboard:

```yaml
# dashboard.yaml
title: Solar Heating System v3
views:
  - title: Control
    path: control
    cards:
      # Mode Control Card
      - type: entities
        title: System Mode Control
        entities:
          - input_select.solar_heating_mode
          - input_boolean.solar_heating_auto_mode
          - input_boolean.solar_heating_manual_mode
          - input_boolean.solar_heating_eco_mode
      
      # Mode-Specific Controls
      - type: conditional
        conditions:
          - entity: input_select.solar_heating_mode
            state: "manual"
        card:
          type: entities
          title: Manual Mode Controls
          entities:
            - switch.solar_heating_primary_pump
            - switch.solar_heating_cartridge_heater
            - number.solar_heating_set_temp_tank_1
      
      - type: conditional
        conditions:
          - entity: input_select.solar_heating_mode
            state: "eco"
        card:
          type: entities
          title: Eco Mode Settings
          entities:
            - number.solar_heating_dtstart_tank_1
            - number.solar_heating_dtstop_tank_1
            - number.solar_heating_set_temp_tank_1
```

## 🤖 **Automation Configuration**

### **Auto Mode Automation**

```yaml
# automations.yaml
- id: solar_heating_auto_mode
  alias: "Solar Heating - Auto Mode"
  description: "Enable automatic operation when Auto Mode is selected"
  trigger:
    - platform: state
      entity_id: input_select.solar_heating_mode
      to: "auto"
  action:
    - service: input_boolean.turn_on
      entity_id: input_boolean.solar_heating_auto_mode
    - service: input_boolean.turn_off
      entity_id: input_boolean.solar_heating_manual_mode
    - service: input_boolean.turn_off
      entity_id: input_boolean.solar_heating_eco_mode
    - service: mqtt.publish
      data:
        topic: "solar_heating/control/mode"
        payload: "auto"
    - service: switch.turn_off
      entity_id: switch.solar_heating_primary_pump_manual
    - service: notify.mobile_app_your_phone
      data:
        title: "Solar Heating Mode Change"
        message: "System switched to Auto Mode - Full automatic operation enabled"
```

### **Manual Mode Automation**

```yaml
- id: solar_heating_manual_mode
  alias: "Solar Heating - Manual Mode"
  description: "Enable manual control with safety limits when Manual Mode is selected"
  trigger:
    - platform: state
      entity_id: input_select.solar_heating_mode
      to: "manual"
  action:
    - service: input_boolean.turn_off
      entity_id: input_boolean.solar_heating_auto_mode
    - service: input_boolean.turn_on
      entity_id: input_boolean.solar_heating_manual_mode
    - service: input_boolean.turn_off
      entity_id: input_boolean.solar_heating_eco_mode
    - service: mqtt.publish
      data:
        topic: "solar_heating/control/mode"
        payload: "manual"
    - service: switch.turn_on
      entity_id: switch.solar_heating_primary_pump_manual
    - service: notify.mobile_app_your_phone
      data:
        title: "Solar Heating Mode Change"
        message: "System switched to Manual Mode - Manual control enabled with safety limits"
```

### **Eco Mode Automation**

```yaml
- id: solar_heating_eco_mode
  alias: "Solar Heating - Eco Mode"
  description: "Enable energy-saving operation when Eco Mode is selected"
  trigger:
    - platform: state
      entity_id: input_select.solar_heating_mode
      to: "eco"
  action:
    - service: input_boolean.turn_off
      entity_id: input_boolean.solar_heating_auto_mode
    - service: input_boolean.turn_off
      entity_id: input_boolean.solar_heating_manual_mode
    - service: input_boolean.turn_on
      entity_id: input_boolean.solar_heating_eco_mode
    - service: mqtt.publish
      data:
        topic: "solar_heating/control/mode"
        payload: "eco"
    - service: switch.turn_off
      entity_id: switch.solar_heating_primary_pump_manual
    # Set eco-friendly parameters
    - service: number.set_value
      entity_id: number.solar_heating_dtstart_tank_1
      value: 10  # Higher threshold for energy saving
    - service: number.set_value
      entity_id: number.solar_heating_dtstop_tank_1
      value: 6   # Higher stop threshold
    - service: number.set_value
      entity_id: number.solar_heating_set_temp_tank_1
      value: 55  # Lower target temperature
    - service: notify.mobile_app_your_phone
      data:
        title: "Solar Heating Mode Change"
        message: "System switched to Eco Mode - Energy-saving operation enabled"
```

## 🛡️ **Safety Limits and Monitoring**

### **Safety Limits Automation**

```yaml
# Safety limits that apply in all modes
- id: solar_heating_safety_limits
  alias: "Solar Heating - Safety Limits"
  description: "Enforce safety limits regardless of mode"
  trigger:
    - platform: numeric_state
      entity_id: sensor.solar_heating_solar_collector_temp
      above: 95  # Emergency temperature
  condition:
    - condition: state
      entity_id: sensor.solar_heating_solar_collector_temp
      state: "95"
  action:
    - service: switch.turn_off
      entity_id: switch.solar_heating_primary_pump
    - service: switch.turn_off
      entity_id: switch.solar_heating_cartridge_heater
    - service: mqtt.publish
      data:
        topic: "solar_heating/control/emergency_stop"
        payload: "true"
    - service: notify.mobile_app_your_phone
      data:
        title: "🚨 Solar Heating Emergency Stop"
        message: "Emergency stop activated - Collector temperature too high: {{ states('sensor.solar_heating_solar_collector_temp') }}°C"
    - service: logbook.log
      data:
        name: Solar Heating System
        message: "Emergency stop - High temperature safety limit exceeded"
```

### **Manual Mode Safety Limits**

```yaml
- id: solar_heating_manual_safety_limits
  alias: "Solar Heating - Manual Mode Safety Limits"
  description: "Additional safety limits for manual mode"
  trigger:
    - platform: state
      entity_id: switch.solar_heating_primary_pump
      to: "on"
    - platform: state
      entity_id: switch.solar_heating_cartridge_heater
      to: "on"
  condition:
    - condition: state
      entity_id: input_boolean.solar_heating_manual_mode
      state: "on"
    - condition: numeric_state
      entity_id: sensor.solar_heating_solar_collector_temp
      above: 85  # Manual mode safety limit
  action:
    - service: switch.turn_off
      entity_id: switch.solar_heating_primary_pump
    - service: switch.turn_off
      entity_id: switch.solar_heating_cartridge_heater
    - service: notify.mobile_app_your_phone
      data:
        title: "⚠️ Manual Mode Safety Limit"
        message: "Device turned off due to safety limit - Collector: {{ states('sensor.solar_heating_solar_collector_temp') }}°C"
```

## 📊 **Mode-Specific Dashboards**

### **Auto Mode Dashboard**

```yaml
- type: conditional
  conditions:
    - entity: input_boolean.solar_heating_auto_mode
      state: "on"
  card:
    type: entities
    title: "Auto Mode - Automatic Operation"
    entities:
      - sensor.solar_heating_system_mode
      - sensor.solar_heating_solar_collector_temp
      - sensor.solar_heating_storage_tank_temp
      - sensor.solar_heating_solar_collector_dt
      - binary_sensor.solar_heating_is_heating
      - sensor.solar_heating_energy_collected_today_kwh
    card_mod:
      type: button
      name: "Force Manual Override"
      icon: mdi:hand-back
      tap_action:
        action: call-service
        service: input_select.select_option
        service_data:
          entity_id: input_select.solar_heating_mode
          option: "manual"
```

### **Manual Mode Dashboard**

```yaml
- type: conditional
  conditions:
    - entity: input_boolean.solar_heating_manual_mode
      state: "on"
  card:
    type: entities
    title: "Manual Mode - Manual Control"
    entities:
      - sensor.solar_heating_system_mode
      - switch.solar_heating_primary_pump
      - switch.solar_heating_cartridge_heater
      - number.solar_heating_set_temp_tank_1
      - sensor.solar_heating_solar_collector_temp
      - sensor.solar_heating_storage_tank_temp
    card_mod:
      type: button
      name: "Return to Auto"
      icon: mdi:robot
      tap_action:
        action: call-service
        service: input_select.select_option
        service_data:
          entity_id: input_select.solar_heating_mode
          option: "auto"
```

### **Eco Mode Dashboard**

```yaml
- type: conditional
  conditions:
    - entity: input_boolean.solar_heating_eco_mode
      state: "on"
  card:
    type: entities
    title: "Eco Mode - Energy Saving"
    entities:
      - sensor.solar_heating_system_mode
      - number.solar_heating_dtstart_tank_1
      - number.solar_heating_dtstop_tank_1
      - number.solar_heating_set_temp_tank_1
      - sensor.solar_heating_energy_collected_today_kwh
      - sensor.solar_heating_solar_energy_today_kwh
    card_mod:
      type: button
      name: "Return to Auto"
      icon: mdi:robot
      tap_action:
        action: call-service
        service: input_select.select_option
        service_data:
          entity_id: input_select.solar_heating_mode
          option: "auto"
```

## 🔔 **Notifications and Alerts**

### **Mode Change Notifications**

```yaml
- id: solar_heating_mode_change_notification
  alias: "Solar Heating - Mode Change Notification"
  description: "Notify when system mode changes"
  trigger:
    - platform: state
      entity_id: input_select.solar_heating_mode
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "Solar Heating Mode Changed"
        message: |
          System mode changed to: {{ states('input_select.solar_heating_mode') | title }}
          
          {% if is_state('input_select.solar_heating_mode', 'auto') %}
          🤖 Auto Mode: Full automatic operation
          {% elif is_state('input_select.solar_heating_mode', 'manual') %}
          ✋ Manual Mode: Manual control with safety limits
          {% elif is_state('input_select.solar_heating_mode', 'eco') %}
          🌱 Eco Mode: Energy-saving operation
          {% endif %}
```

### **Mode-Specific Alerts**

```yaml
# Auto Mode Efficiency Alert
- id: solar_heating_auto_efficiency_alert
  alias: "Solar Heating - Auto Mode Efficiency Alert"
  description: "Alert when auto mode efficiency is low"
  trigger:
    - platform: numeric_state
      entity_id: sensor.solar_heating_energy_collected_today_kwh
      below: 8
      for:
        hours: 2
  condition:
    - condition: state
      entity_id: input_boolean.solar_heating_auto_mode
      state: "on"
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "Auto Mode Efficiency Alert"
        message: "Low energy collection in Auto Mode - Consider switching to Manual or Eco Mode"

# Manual Mode Safety Alert
- id: solar_heating_manual_safety_alert
  alias: "Solar Heating - Manual Mode Safety Alert"
  description: "Alert when manual mode safety limits are approached"
  trigger:
    - platform: numeric_state
      entity_id: sensor.solar_heating_solar_collector_temp
      above: 80
  condition:
    - condition: state
      entity_id: input_boolean.solar_heating_manual_mode
      state: "on"
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "Manual Mode Safety Alert"
        message: "High temperature in Manual Mode - Safety limits may activate soon"
```

## 🎨 **Custom Cards for Mode Control**

### **Mode Selector Card**

```yaml
- type: custom:button-card
  name: "System Mode"
  entity: input_select.solar_heating_mode
  show_state: true
  show_name: true
  icon: mdi:thermostat
  tap_action:
    action: more-info
  styles:
    card:
      - background: |
          [[[
            if (states['input_select.solar_heating_mode'].state === 'auto') return 'linear-gradient(45deg, #4CAF50, #8BC34A)';
            if (states['input_select.solar_heating_mode'].state === 'manual') return 'linear-gradient(45deg, #FF9800, #FFC107)';
            if (states['input_select.solar_heating_mode'].state === 'eco') return 'linear-gradient(45deg, #4CAF50, #2E7D32)';
            return 'linear-gradient(45deg, #9E9E9E, #607D8B)';
          ]]]
      - color: white
      - border-radius: 10px
      - box-shadow: 0 4px 8px rgba(0,0,0,0.2)
```

### **Mode Status Cards**

```yaml
# Auto Mode Status
- type: custom:button-card
  name: "Auto Mode"
  entity: input_boolean.solar_heating_auto_mode
  show_state: true
  show_name: true
  icon: mdi:robot
  tap_action:
    action: call-service
    service: input_select.select_option
    service_data:
      entity_id: input_select.solar_heating_mode
      option: "auto"
  styles:
    card:
      - background: |
          [[[
            if (states['input_boolean.solar_heating_auto_mode'].state === 'on') return 'linear-gradient(45deg, #4CAF50, #8BC34A)';
            return 'linear-gradient(45deg, #9E9E9E, #607D8B)';
          ]]]
      - color: white
      - border-radius: 10px

# Manual Mode Status
- type: custom:button-card
  name: "Manual Mode"
  entity: input_boolean.solar_heating_manual_mode
  show_state: true
  show_name: true
  icon: mdi:hand-back
  tap_action:
    action: call-service
    service: input_select.select_option
    service_data:
      entity_id: input_select.solar_heating_mode
      option: "manual"
  styles:
    card:
      - background: |
          [[[
            if (states['input_boolean.solar_heating_manual_mode'].state === 'on') return 'linear-gradient(45deg, #FF9800, #FFC107)';
            return 'linear-gradient(45deg, #9E9E9E, #607D8B)';
          ]]]
      - color: white
      - border-radius: 10px

# Eco Mode Status
- type: custom:button-card
  name: "Eco Mode"
  entity: input_boolean.solar_heating_eco_mode
  show_state: true
  show_name: true
  icon: mdi:leaf
  tap_action:
    action: call-service
    service: input_select.select_option
    service_data:
      entity_id: input_select.solar_heating_mode
      option: "eco"
  styles:
    card:
      - background: |
          [[[
            if (states['input_boolean.solar_heating_eco_mode'].state === 'on') return 'linear-gradient(45deg, #4CAF50, #2E7D32)';
            return 'linear-gradient(45deg, #9E9E9E, #607D8B)';
          ]]]
      - color: white
      - border-radius: 10px
```

## 🔧 **System Integration**

### **Update Solar Heating System**

You'll need to update your Solar Heating System v3 to handle mode commands. Add this to your `main_system.py`:

```python
def _handle_mqtt_command(self, command_type, data):
    """Handle MQTT commands including mode control"""
    try:
        if command_type == 'mode_control':
            mode = data.get('mode', 'auto')
            self._set_system_mode(mode)
            logger.info(f"System mode changed to: {mode}")
            
        elif command_type == 'select_command':
            # Handle Home Assistant select entity commands
            if data.get('entity_id') == 'solar_heating_system_mode':
                mode = data.get('option', 'auto')
                self._set_system_mode(mode)
                logger.info(f"System mode changed via HA to: {mode}")
        
        # ... existing command handling ...
        
    except Exception as e:
        logger.error(f"Error handling MQTT command: {e}")

def _set_system_mode(self, mode):
    """Set system operating mode"""
    if mode == 'auto':
        self.system_state['manual_control'] = False
        self.system_state['eco_mode'] = False
        # Reset to default parameters
        self.control_params['dTStart_tank_1'] = 8.0
        self.control_params['dTStop_tank_1'] = 4.0
        self.control_params['set_temp_tank_1'] = 60.0
        
    elif mode == 'manual':
        self.system_state['manual_control'] = True
        self.system_state['eco_mode'] = False
        # Enable manual control
        
    elif mode == 'eco':
        self.system_state['manual_control'] = False
        self.system_state['eco_mode'] = True
        # Set eco-friendly parameters
        self.control_params['dTStart_tank_1'] = 10.0
        self.control_params['dTStop_tank_1'] = 6.0
        self.control_params['set_temp_tank_1'] = 55.0
    
    # Update system mode
    self.system_state['mode'] = mode
    self._update_system_mode()
```

## 📱 **Mobile App Integration**

### **Quick Actions**

Add these to your mobile app configuration:

```yaml
# mobile_app.yaml
quick_actions:
  - name: "Auto Mode"
    icon: mdi:robot
    action: call_service
    service: input_select.select_option
    service_data:
      entity_id: input_select.solar_heating_mode
      option: "auto"
  
  - name: "Manual Mode"
    icon: mdi:hand-back
    action: call_service
    service: input_select.select_option
    service_data:
      entity_id: input_select.solar_heating_mode
      option: "manual"
  
  - name: "Eco Mode"
    icon: mdi:leaf
    action: call_service
    service: input_select.select_option
    service_data:
      entity_id: input_select.solar_heating_mode
      option: "eco"
```

## 🎯 **Summary**

This implementation provides:

1. **Three distinct modes** with clear visual indicators
2. **Safety limits** that apply in all modes
3. **Mode-specific controls** and parameters
4. **Automated notifications** for mode changes
5. **Custom dashboard cards** for easy mode switching
6. **Mobile app integration** for remote control

The system will automatically:
- Switch between modes based on user selection
- Apply appropriate safety limits
- Send notifications for mode changes
- Update system parameters for each mode
- Provide mode-specific control interfaces

**Auto Mode**: Full automatic operation with standard parameters
**Manual Mode**: Manual control with enhanced safety limits
**Eco Mode**: Energy-saving operation with optimized parameters

All modes include safety monitoring and emergency stop capabilities to ensure safe operation regardless of the selected mode.
