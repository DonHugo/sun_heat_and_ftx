# Solar Heating System REST API Design Specification

## Overview
This document defines the REST API design for the Solar Heating System v3, following TDD principles.

## API Endpoints

### 1. GET /api/status
**Description:** Get complete system status including temperatures, MQTT status, and hardware status.

**Response:**
```json
{
  "system_state": {
    "mode": "auto",
    "primary_pump": false,
    "cartridge_heater": false,
    "manual_control": false
  },
  "temperatures": {
    "tank": 65.5,
    "solar_collector": 72.1,
    "ambient": 15.0,
    "heat_exchanger_in": 68.9
  },
  "mqtt_status": {
    "connected": true,
    "broker": "Connected",
    "last_message": {
      "topic": "homeassistant/sensor/tank_temperature/state",
      "payload": "65.5",
      "timestamp": "2025-10-25T10:30:00",
      "qos": 0
    }
  },
  "hardware_status": {
    "rtd_boards": "Connected",
    "relays": "Connected",
    "sensors": "Active"
  },
  "service_status": {
    "solar_heating_v3": "active",
    "mqtt": "active",
    "solar_heating_watchdog": "active"
  },
  "timestamp": "2025-10-25T10:30:00Z"
}
```

### 2. POST /api/control
**Description:** Control system actions (pump start/stop, emergency stop).

**Request:**
```json
{
  "action": "pump_start" | "pump_stop" | "emergency_stop"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Pump started successfully",
  "system_state": {
    "primary_pump": true,
    "mode": "manual"
  }
}
```

### 3. POST /api/mode
**Description:** Change system mode (auto/manual/eco).

**Request:**
```json
{
  "mode": "auto" | "manual" | "eco"
}
```

**Response:**
```json
{
  "success": true,
  "message": "System mode set to auto",
  "system_state": {
    "mode": "auto",
    "manual_control": false
  }
}
```

### 4. GET /api/temperatures
**Description:** Get real-time temperature data.

**Response:**
```json
{
  "temperatures": {
    "tank": 65.5,
    "solar_collector": 72.1,
    "ambient": 15.0,
    "heat_exchanger_in": 68.9
  },
  "timestamp": "2025-10-25T10:30:00Z"
}
```

### 5. GET /api/mqtt
**Description:** Get MQTT connection status and last message.

**Response:**
```json
{
  "mqtt_status": {
    "connected": true,
    "broker": "Connected",
    "last_message": {
      "topic": "homeassistant/sensor/tank_temperature/state",
      "payload": "65.5",
      "timestamp": "2025-10-25T10:30:00",
      "qos": 0
    }
  },
  "timestamp": "2025-10-25T10:30:00Z"
}
```

## Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-10-25T10:30:00Z"
}
```

### Common Error Codes
- `INVALID_ACTION`: Invalid control action
- `INVALID_MODE`: Invalid mode value
- `SYSTEM_ERROR`: Internal system error
- `HARDWARE_ERROR`: Hardware communication error

## HTTP Status Codes
- `200 OK`: Successful request
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: System error

## Design Principles
1. **RESTful Design**: Use proper HTTP methods and status codes
2. **JSON Format**: All requests and responses in JSON
3. **Consistent Structure**: All responses follow the same format
4. **Error Handling**: Comprehensive error responses
5. **Timestamping**: All responses include timestamps
6. **Thread Safety**: API endpoints are thread-safe
7. **MQTT Integration**: All changes published to MQTT for Home Assistant sync

## Implementation Notes
- API will be integrated into main_system.py
- Single source of truth for system state
- Thread-safe operations
- MQTT publishing for Home Assistant synchronization
- No duplicate system instances
- Clean separation of concerns
