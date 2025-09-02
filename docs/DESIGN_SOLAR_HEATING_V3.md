# Design: Solar Heating System v3

## 🏗️ **How the System Works**

This document explains the technical design and architecture of the Solar Heating v3 system, including how all components interact, the control logic, and the data flow.

## 🏛️ **System Architecture**

### **High-Level Architecture**

```mermaid
graph TB
    subgraph "User Interface"
        HA[Home Assistant]
        API[REST API]
        MQTT_CLIENT[MQTT Client]
    end
    
    subgraph "Control System"
        MAIN[Main Controller]
        LOGIC[Control Logic]
        SAFETY[Safety Systems]
        AI[TaskMaster AI]
    end
    
    subgraph "Hardware Interface"
        HW[Hardware Interface]
        RTD[RTD Interface]
        RELAY[Relay Interface]
        MEGA[MegaBAS Interface]
    end
    
    subgraph "Hardware"
        SENSORS[Temperature Sensors]
        PUMPS[Water Pumps]
        HEATERS[Cartridge Heaters]
        TANKS[Storage Tanks]
    end
    
    subgraph "Communication"
        MQTT[MQTT Broker]
        LOGS[Logging System]
        CONFIG[Configuration]
    end
    
    HA --> MQTT
    API --> MAIN
    MQTT_CLIENT --> MQTT
    MAIN --> LOGIC
    MAIN --> SAFETY
    MAIN --> AI
    LOGIC --> HW
    SAFETY --> HW
    HW --> RTD
    HW --> RELAY
    HW --> MEGA
    RTD --> SENSORS
    RELAY --> PUMPS
    RELAY --> HEATERS
    MAIN --> MQTT
    MAIN --> LOGS
    CONFIG --> MAIN
    
    style MAIN fill:#e1f5fe
    style AI fill:#f3e5f5
    style HA fill:#e8f5e8
    style HW fill:#fff3e0
```

### **Component Responsibilities**

| Component | Responsibility | Key Functions |
|-----------|----------------|---------------|
| **Main Controller** | System orchestration | Temperature monitoring, pump control, safety monitoring |
| **Control Logic** | Temperature-based decisions | Pump start/stop logic, threshold management |
| **Safety Systems** | System protection | Emergency shutdown, temperature limits, hardware monitoring |
| **Hardware Interface** | Hardware abstraction | Sensor reading, relay control, hardware testing |
| **MQTT Handler** | Communication | Status publishing, command processing, Home Assistant integration |
| **TaskMaster AI** | Intelligence | Optimization, task creation, predictive insights |

## 🔄 **System Workflow**

### **Main Control Loop**

```mermaid
flowchart TD
    A[System Start] --> B[Initialize Hardware]
    B --> C[Initialize MQTT]
    C --> D[Initialize AI]
    D --> E[Main Loop Start]
    
    E --> F[Read All Sensors]
    F --> G[Apply Control Logic]
    G --> H[Check Safety Conditions]
    H --> I{Any Safety Issues?}
    
    I -->|Yes| J[Emergency Shutdown]
    I -->|No| K[Update Pump States]
    
    K --> L[Send Data to AI]
    L --> M[Publish MQTT Status]
    M --> N[Process Commands]
    N --> O[Wait for Next Cycle]
    O --> F
    
    J --> P[Log Emergency]
    P --> Q[Wait for Reset]
    Q --> E
    
    style J fill:#ffcdd2
    style K fill:#c8e6c9
    style M fill:#e3f2fd
```

### **Temperature Control Logic**

```mermaid
flowchart TD
    A[Read Temperatures] --> B[Calculate dT]
    B --> C{Tank < Set Temp?}
    
    C -->|Yes| D{dT >= Start Threshold?}
    C -->|No| E[Stop Pump]
    
    D -->|Yes| F[Start Pump]
    D -->|No| G[Keep Current State]
    
    F --> H[Monitor Safety]
    G --> H
    
    H --> I{Temp > Boiling?}
    I -->|Yes| J[Emergency Shutdown]
    I -->|No| K[Continue Operation]
    
    K --> L[Wait for Next Cycle]
    L --> A
    
    J --> M[Log Emergency]
    M --> N[Wait for Manual Reset]
    
    style J fill:#ffcdd2
    style F fill:#c8e6c9
    style E fill:#fff9c4
```

## 🔧 **Control Logic Details**

### **Pump Control Algorithm**

The system uses a sophisticated temperature difference (dT) algorithm for pump control:

```python
def calculate_pump_state(solar_temp, tank_temp, set_temp, dT_start, dT_stop):
    dT = solar_temp - tank_temp
    
    # Safety check - emergency shutdown at boiling
    if solar_temp > BOILING_TEMPERATURE:
        return "EMERGENCY_SHUTDOWN"
    
    # Check if tank needs heating
    if tank_temp < set_temp:
        # Start pump if temperature difference is sufficient
        if dT >= dT_start:
            return "START_PUMP"
        else:
            return "KEEP_CURRENT_STATE"
    else:
        # Stop pump if tank is hot enough or dT is too low
        if dT <= dT_stop:
            return "STOP_PUMP"
        else:
            return "KEEP_CURRENT_STATE"
```

### **Temperature Thresholds**

| Parameter | Description | Default Value | Configurable |
|-----------|-------------|---------------|--------------|
| `set_temp_tank_1` | Target tank temperature | 70.0°C | ✅ Yes |
| `dTStart_tank_1` | Start pump threshold | 8.0°C | ✅ Yes |
| `dTStop_tank_1` | Stop pump threshold | 4.0°C | ✅ Yes |
| `temp_threshold_high` | High temperature warning | 80.0°C | ✅ Yes |
| `temp_threshold_low` | Low temperature warning | 20.0°C | ✅ Yes |
| `temp_kok` | Boiling temperature | 150.0°C | ✅ Yes |

## 🏗️ **Hardware Interface Design**

### **Hardware Abstraction Layer**

```mermaid
classDiagram
    class HardwareInterface {
        +read_temperature(sensor_id)
        +set_relay_state(relay_id, state)
        +get_relay_state(relay_id)
        +test_hardware_connection()
        +simulation_mode
    }
    
    class RTDInterface {
        +read_rtd_sensor(address)
        +calibrate_sensor(sensor_id)
        +get_sensor_status(sensor_id)
    }
    
    class RelayInterface {
        +set_relay(relay_id, state)
        +get_relay_status(relay_id)
        +test_relay(relay_id)
    }
    
    class MegaBASInterface {
        +read_input(input_id)
        +set_output(output_id, value)
        +get_board_status()
    }
    
    HardwareInterface --> RTDInterface
    HardwareInterface --> RelayInterface
    HardwareInterface --> MegaBASInterface
```

### **Hardware Mapping**

| Hardware Component | Interface | Address | Purpose |
|-------------------|-----------|---------|---------|
| **RTD Board** | RTD Interface | 0 | Temperature sensors |
| **MegaBAS Board** | MegaBAS Interface | 3 | Input/output control |
| **Relay Board** | Relay Interface | 2 | Pump and heater control |

### **Sensor Configuration**

| Sensor ID | Location | Type | Purpose |
|-----------|----------|------|---------|
| 0 | Solar Collector | RTD | Solar panel temperature |
| 1 | Storage Tank | RTD | Tank water temperature |
| 2 | Return Line | RTD | Return water temperature |
| 3 | Heat Exchanger | RTD | Heat exchanger temperature |

## 📡 **MQTT Communication Design**

### **Topic Structure**

```mermaid
graph LR
    subgraph "Published Topics"
        TEMP[solar_heating_v3/temperature/*]
        STATUS[solar_heating_v3/status/*]
        CONTROL[solar_heating_v3/control/*]
        ALERTS[solar_heating_v3/alerts/*]
        HA[homeassistant/*]
    end
    
    subgraph "Subscribed Topics"
        HASS[hass/*/control]
        COMMAND[control/*]
        TASKMASTER[taskmaster/*]
    end
    
    subgraph "Message Types"
        JSON[JSON Payloads]
        DISCOVERY[HA Discovery]
        COMMANDS[Control Commands]
    end
    
    TEMP --> JSON
    STATUS --> JSON
    CONTROL --> JSON
    ALERTS --> JSON
    HA --> DISCOVERY
    HASS --> COMMANDS
    COMMAND --> COMMANDS
    TASKMASTER --> COMMANDS
```

### **Message Format**

**Temperature Data**:
```json
{
    "temperature": 75.2,
    "unit": "°C",
    "timestamp": "2024-01-15T10:30:00Z",
    "sensor_id": "solar_collector",
    "status": "normal"
}
```

**Pump Status**:
```json
{
    "pump_id": "primary",
    "status": "running",
    "power": 120,
    "flow_rate": 2.5,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

**Control Commands**:
```json
{
    "action": "start_pump",
    "pump_id": "primary",
    "reason": "manual_override",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🤖 **AI Integration Design**

### **TaskMaster AI Integration**

```mermaid
sequenceDiagram
    participant V3 as Solar Heating v3
    participant AI as TaskMaster AI
    participant API as AI API
    participant TASKS as Task Manager
    
    V3->>AI: Send temperature data
    AI->>API: Analyze patterns
    API->>AI: Return insights
    AI->>TASKS: Create optimization tasks
    TASKS->>V3: Execute tasks
    V3->>AI: Report task results
    AI->>API: Learn from results
    API->>AI: Update optimization model
```

### **AI Data Flow**

1. **Data Collection**: System sends real-time temperature and status data
2. **Pattern Analysis**: AI analyzes temperature patterns and system behavior
3. **Task Creation**: AI creates optimization tasks based on analysis
4. **Task Execution**: System executes AI-recommended tasks
5. **Result Learning**: AI learns from task results to improve future recommendations

## 🚨 **Safety System Design**

### **Safety Layers**

```mermaid
graph TD
    subgraph "Layer 1: Hardware Limits"
        HW1[Hardware Temperature Limits]
        HW2[Hardware Current Limits]
    end
    
    subgraph "Layer 2: Software Monitoring"
        SW1[Temperature Thresholds]
        SW2[Pump Monitoring]
        SW3[Hardware Health]
    end
    
    subgraph "Layer 3: Emergency Systems"
        EM1[Emergency Shutdown]
        EM2[Manual Override]
        EM3[Alert System]
    end
    
    HW1 --> SW1
    HW2 --> SW2
    SW1 --> EM1
    SW2 --> EM1
    SW3 --> EM1
    EM1 --> EM2
    EM1 --> EM3
    
    style EM1 fill:#ffcdd2
    style EM2 fill:#fff9c4
    style EM3 fill:#e1f5fe
```

### **Safety Triggers**

| Safety Condition | Trigger | Action | Recovery |
|------------------|---------|--------|----------|
| **Boiling Temperature** | Solar temp > 150°C | Emergency shutdown | Manual reset required |
| **High Temperature** | Any temp > 80°C | Warning alert | Automatic monitoring |
| **Low Temperature** | Any temp < 20°C | Warning alert | Automatic monitoring |
| **Pump Failure** | Pump not responding | Alert and stop | Manual intervention |
| **Hardware Error** | Communication failure | Alert and retry | Automatic retry |

## 🔧 **Configuration Management**

### **Environment Variables**

```mermaid
graph LR
    subgraph "Hardware Config"
        HW1[SOLAR_HARDWARE_PLATFORM]
        HW2[SOLAR_RTD_BOARD_ADDRESS]
        HW3[SOLAR_MEGABAS_BOARD_ADDRESS]
        HW4[SOLAR_RELAY_BOARD_ADDRESS]
    end
    
    subgraph "Temperature Config"
        TEMP1[SOLAR_TEMPERATURE_UPDATE_INTERVAL]
        TEMP2[SOLAR_TEMPERATURE_THRESHOLD_HIGH]
        TEMP3[SOLAR_TEMPERATURE_THRESHOLD_LOW]
        TEMP4[SOLAR_SET_TEMP_TANK_1]
    end
    
    subgraph "Integration Config"
        INT1[SOLAR_MQTT_BROKER]
        INT2[SOLAR_TASKMASTER_ENABLED]
        INT3[SOLAR_HASS_ENABLED]
    end
    
    subgraph "System Config"
        SYS1[SOLAR_TEST_MODE]
        SYS2[SOLAR_DEBUG_MODE]
        SYS3[SOLAR_LOG_LEVEL]
    end
```

### **Configuration Loading**

```python
def load_configuration():
    config = {
        'hardware': load_hardware_config(),
        'temperature': load_temperature_config(),
        'integration': load_integration_config(),
        'system': load_system_config()
    }
    
    # Validate configuration
    validate_config(config)
    
    # Set defaults for missing values
    set_defaults(config)
    
    return config
```

## 📊 **Monitoring and Logging Design**

### **Logging Architecture**

```mermaid
graph TB
    subgraph "Log Sources"
        MAIN[Main Controller]
        HW[Hardware Interface]
        MQTT[MQTT Handler]
        AI[TaskMaster AI]
        SAFETY[Safety Systems]
    end
    
    subgraph "Log Processing"
        FORMAT[Log Formatting]
        LEVEL[Log Level Filtering]
        TIMESTAMP[Timestamp Addition]
        CONTEXT[Context Information]
    end
    
    subgraph "Log Outputs"
        FILE[Log Files]
        CONSOLE[Console Output]
        MQTT_LOG[MQTT Logging]
        EXTERNAL[External Systems]
    end
    
    MAIN --> FORMAT
    HW --> FORMAT
    MQTT --> FORMAT
    AI --> FORMAT
    SAFETY --> FORMAT
    
    FORMAT --> LEVEL
    LEVEL --> TIMESTAMP
    TIMESTAMP --> CONTEXT
    
    CONTEXT --> FILE
    CONTEXT --> CONSOLE
    CONTEXT --> MQTT_LOG
    CONTEXT --> EXTERNAL
```

### **Log Levels**

| Level | Description | Use Case |
|-------|-------------|----------|
| **DEBUG** | Detailed debugging information | Development and troubleshooting |
| **INFO** | General information messages | Normal operation monitoring |
| **WARNING** | Warning conditions | Potential issues |
| **ERROR** | Error conditions | System errors |
| **CRITICAL** | Critical conditions | Safety and emergency situations |

## 🧪 **Testing and Simulation Design**

### **Simulation Mode**

```mermaid
graph LR
    subgraph "Real Hardware"
        REAL[Hardware Interface]
        SENSORS[Physical Sensors]
        RELAYS[Physical Relays]
    end
    
    subgraph "Simulation Mode"
        SIM[Simulated Interface]
        SIM_SENSORS[Simulated Sensors]
        SIM_RELAYS[Simulated Relays]
    end
    
    subgraph "System Logic"
        LOGIC[Control Logic]
        SAFETY[Safety Systems]
        MQTT[MQTT Handler]
    end
    
    REAL --> LOGIC
    SIM --> LOGIC
    LOGIC --> SAFETY
    LOGIC --> MQTT
    
    style SIM fill:#e8f5e8
    style REAL fill:#fff3e0
```

### **Testing Capabilities**

1. **Unit Testing**: Individual component testing
2. **Integration Testing**: Component interaction testing
3. **System Testing**: Full system functionality testing
4. **Performance Testing**: Response time and throughput testing
5. **Safety Testing**: Emergency condition testing

## 🔗 **Related Documentation**

- **[Requirements Document](REQUIREMENTS_SOLAR_HEATING_V3.md)** - What we built and why
- **[Implementation Guide](IMPLEMENTATION_SOLAR_HEATING_V3.md)** - Technical implementation details
- **[User Guide](USER_GUIDE_SOLAR_HEATING_V3.md)** - How to use the system
- **[System Overview](../SYSTEM_OVERVIEW.md)** - Complete system understanding
- **[Component Map](../COMPONENT_MAP.md)** - System component relationships

---

**This document explains how the Solar Heating v3 system works at a technical level, including the architecture, control logic, and integration points. It serves as the technical foundation for implementation and maintenance.**
