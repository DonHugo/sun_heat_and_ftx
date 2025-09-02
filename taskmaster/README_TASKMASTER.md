# TaskMaster AI Integration for Solar Heating System

This integration brings AI-powered task management and optimization to your solar heating system using TaskMaster AI.

## Overview

TaskMaster AI provides intelligent task management, automated decision-making, and system optimization for your solar heating infrastructure. The integration monitors temperature sensors, controls pumps and valves, and provides AI-driven recommendations for optimal system performance.

## Features

- **Intelligent Temperature Monitoring**: Automatically creates tasks when temperature thresholds are exceeded
- **AI-Powered Optimization**: Provides recommendations for system efficiency improvements
- **Automated Task Management**: Handles pump control, valve control, and data logging tasks
- **Real-time System Analysis**: Continuous monitoring and analysis of system performance
- **Configurable Thresholds**: Customizable temperature and performance thresholds

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   ```bash
   cp env.example .env
   # Edit .env with your TaskMaster AI API key and other settings
   ```

3. **Set Your API Key**:
   ```bash
   export TASKMASTER_API_KEY="your_taskmaster_api_key_here"
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TASKMASTER_API_KEY` | Your TaskMaster AI API key | Required |
| `TASKMASTER_BASE_URL` | TaskMaster AI API base URL | `https://api.taskmaster.ai` |
| `MQTT_BROKER` | MQTT broker address | `localhost` |
| `MQTT_PORT` | MQTT broker port | `1883` |
| `TEMP_THRESHOLD_HIGH` | High temperature threshold (°C) | `80.0` |
| `TEMP_THRESHOLD_LOW` | Low temperature threshold (°C) | `20.0` |
| `ENABLE_AI_OPTIMIZATION` | Enable AI optimization | `true` |
| `AI_ANALYSIS_INTERVAL` | AI analysis interval (seconds) | `3600` |

### System Tasks

The integration defines several task types:

- **temperature_monitoring**: Monitors temperature sensors and triggers alerts
- **pump_control**: Controls water circulation pumps based on temperature
- **valve_control**: Controls valves for optimal heat distribution
- **data_logging**: Logs system data for analysis and optimization
- **system_optimization**: AI-powered system optimization recommendations

## Usage

### Running the Demo

```bash
python taskmaster_demo.py
```

This will demonstrate:
- Temperature monitoring with automatic task creation
- AI-powered system optimization
- Task management and execution

### Integration with Existing System

To integrate with your existing temperature monitoring system:

```python
from taskmaster_service import taskmaster_service

# Initialize the service
await taskmaster_service.initialize()

# Process temperature data
temperature_data = {
    "solar_collector": 75.2,
    "storage_tank": 62.8,
    "heat_exchanger": 58.9
}

await taskmaster_service.process_temperature_data(temperature_data)

# Get system status
status = await taskmaster_service.get_system_status()
print(f"Active tasks: {status['active_tasks']}")
```

### API Integration

The integration provides several key methods:

```python
# Create a custom task
task = await taskmaster_service.taskmaster.create_task(
    "pump_control",
    {"action": "increase_flow", "reason": "manual_override"}
)

# Get AI recommendations
recommendations = await taskmaster_service.taskmaster.optimize_system(system_data)

# Update task results
await taskmaster_service.taskmaster.update_task_result(task.id, {"status": "completed"})
```

## Architecture

### Components

1. **taskmaster_config.py**: Configuration management and environment variables
2. **taskmaster_integration.py**: Core TaskMaster AI API integration
3. **taskmaster_service.py**: Service layer for business logic and task execution
4. **taskmaster_demo.py**: Demonstration script showcasing all features

### Data Flow

1. Temperature data is received from sensors
2. TaskMaster AI processes the data and creates tasks if thresholds are exceeded
3. Tasks are executed based on their type (pump control, valve control, etc.)
4. AI optimization provides recommendations for system improvements
5. Results are logged and can be used for further analysis

## Integration with Hardware

The integration is designed to work with your existing Sequent Microsystems hardware:

- **RTD Data Acquisition**: Temperature sensor monitoring
- **Building Automation V4**: Relay and input control
- **Four Relays four HV Inputs**: Pump and valve control

### Hardware Integration Points

```python
# Example: Integrate with your existing hardware interface
from python.v2.hardware_interface import HardwareInterface

class TaskMasterHardwareIntegration:
    def __init__(self):
        self.hardware = HardwareInterface()
    
    async def execute_pump_control(self, action, parameters):
        if action == "increase_flow":
            # Control pump via your hardware interface
            self.hardware.set_relay_state(1, True)
        elif action == "decrease_flow":
            self.hardware.set_relay_state(1, False)
    
    async def execute_valve_control(self, action, parameters):
        # Control valves via your hardware interface
        valve_position = parameters.get("position", 0.5)
        self.hardware.set_analog_output(1, valve_position)
```

## Monitoring and Logging

The integration provides comprehensive logging and monitoring:

```python
# Get system status
status = await taskmaster_service.get_system_status()

# Access task history
for task in status['task_history']:
    print(f"Task: {task['name']}, Created: {task['created_at']}")
```

## Troubleshooting

### Common Issues

1. **API Key Not Set**: Ensure `TASKMASTER_API_KEY` is set in your environment
2. **Network Connectivity**: Check internet connection for API calls
3. **Hardware Integration**: Verify hardware interface connections

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Contributing

To extend the integration:

1. Add new task types in `taskmaster_config.py`
2. Implement task handlers in `taskmaster_service.py`
3. Update the demo script to showcase new features

## License

This integration is part of your solar heating system project and follows the same licensing terms.

## Support

For TaskMaster AI support, refer to the official TaskMaster AI documentation and API reference.
