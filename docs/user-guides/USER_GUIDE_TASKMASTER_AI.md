# User Guide: TaskMaster AI Integration

## 🎯 **How to Use the AI System**

This guide explains how to use your TaskMaster AI integration, from initial setup to daily operation and optimization. The AI system brings intelligent automation and optimization to your solar heating system.

## 🚀 **Getting Started**

### **Quick Start (5 Minutes)**

1. **Navigate to the TaskMaster directory**:
   ```bash
   cd taskmaster
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your API key**:
   ```bash
   export TASKMASTER_API_KEY="your_api_key_here"
   ```

4. **Run the demo**:
   ```bash
   python taskmaster_demo.py
   ```

5. **Check AI status**: Open your Home Assistant dashboard to see AI insights

### **First-Time Setup (30 Minutes)**

1. **Copy configuration template**:
   ```bash
   cp env.example .env
   ```

2. **Edit configuration**:
   ```bash
   nano .env
   ```

3. **Set your TaskMaster AI credentials**:
   ```bash
   TASKMASTER_API_KEY=your_api_key_here
   TASKMASTER_BASE_URL=https://api.taskmaster.ai
   ```

4. **Configure AI behavior**:
   ```bash
   ENABLE_AI_OPTIMIZATION=true
   AI_ANALYSIS_INTERVAL=3600
   TEMP_THRESHOLD_HIGH=80.0
   TEMP_THRESHOLD_LOW=20.0
   ```

5. **Start the AI service**:
   ```bash
   python taskmaster_service.py
   ```

## 🎛️ **Daily Operation**

### **Monitoring AI Insights**

#### **Home Assistant AI Dashboard**

Your TaskMaster AI automatically creates a comprehensive AI dashboard in Home Assistant:

- **AI System Status**: Current AI operation status and health
- **Temperature Predictions**: AI-predicted temperature trends (24-hour forecast)
- **Recent Optimizations**: Latest AI optimization recommendations
- **Learning Progress**: How AI models are improving over time
- **Efficiency Metrics**: AI-calculated system efficiency improvements

#### **AI Notifications and Alerts**

The AI system provides intelligent notifications:

- **Optimization Alerts**: When AI detects optimization opportunities
- **Maintenance Warnings**: Predictive maintenance recommendations
- **Efficiency Insights**: Performance improvement suggestions
- **Weather Adaptations**: AI adjustments based on weather forecasts

#### **AI Status Monitoring**

Monitor AI system operation:

```bash
# Check AI service status
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
status = service.get_status()
print('AI Status:', status)
"

# View AI logs
tail -f taskmaster_ai.log

# Check AI performance metrics
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
metrics = service.get_performance_metrics()
print('AI Performance:', metrics)
"
```

### **AI Control and Interaction**

#### **Manual AI Optimization**

Trigger AI optimization manually:

```bash
# Request immediate AI analysis
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
service.request_optimization()
print('AI optimization requested')
"

# Get AI recommendations
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
recommendations = service.get_recommendations()
print('AI Recommendations:', recommendations)
"
```

#### **AI Configuration Adjustments**

Modify AI behavior in real-time:

```bash
# Adjust AI sensitivity
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
service.set_ai_sensitivity('high')  # low, medium, high
print('AI sensitivity set to high')
"

# Enable/disable specific AI features
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
service.enable_feature('weather_adaptation', True)
service.enable_feature('predictive_maintenance', True)
print('Weather adaptation and predictive maintenance enabled')
"
```

## 🔧 **Configuration and Customization**

### **AI Behavior Configuration**

#### **Learning and Adaptation Settings**

```bash
# AI Learning Configuration
AI_LEARNING_RATE=0.01                    # How quickly AI learns (0.001-0.1)
AI_ADAPTATION_THRESHOLD=0.1              # When to adapt models (0.05-0.2)
AI_MODEL_UPDATE_FREQUENCY=3600           # How often to update models (seconds)
AI_CONFIDENCE_THRESHOLD=0.85             # Minimum confidence for actions (0.7-0.95)

# AI Optimization Configuration
AI_OPTIMIZATION_INTERVAL=300             # How often to optimize (seconds)
AI_PREDICTION_HORIZON=86400              # Prediction time horizon (seconds)
AI_OPTIMIZATION_OBJECTIVES=efficiency,cost,comfort  # Optimization goals
AI_OPTIMIZATION_METHOD=genetic_algorithm # Optimization algorithm
```

#### **Safety and Validation Settings**

```bash
# AI Safety Configuration
AI_SAFETY_ENABLED=true                   # Enable AI safety systems
AI_MAX_TEMPERATURE=90.0                  # Maximum temperature AI can set
AI_MIN_TEMPERATURE=20.0                  # Minimum temperature AI can set
AI_REQUIRE_USER_APPROVAL=false           # Require approval for AI actions
AI_AUTOMATIC_ROLLBACK=true               # Auto-rollback failed optimizations
AI_SAFETY_MONITORING=true                # Continuous safety monitoring
```

#### **Integration Settings**

```bash
# System Integration
AI_SOLAR_HEATING_ENABLED=true            # Enable Solar Heating v3 integration
AI_HOME_ASSISTANT_ENABLED=true           # Enable Home Assistant integration
AI_MQTT_ENABLED=true                     # Enable MQTT communication
AI_EXTERNAL_APIS_ENABLED=true            # Enable external API integration

# Data Collection
AI_DATA_COLLECTION_INTERVAL=60           # Data collection frequency (seconds)
AI_WEATHER_API_ENABLED=true              # Enable weather data collection
AI_USAGE_PATTERN_ANALYSIS=true           # Enable usage pattern analysis
AI_HISTORICAL_DATA_ANALYSIS=true         # Enable historical data analysis
```

### **AI Model Configuration**

#### **Prediction Models**

```bash
# Model Selection
AI_USE_LINEAR_REGRESSION=true            # Use linear regression model
AI_USE_TIME_SERIES=true                  # Use time series model
AI_USE_NEURAL_NETWORK=true               # Use neural network model
AI_USE_ENSEMBLE=true                     # Use ensemble prediction

# Model Weights (for ensemble)
AI_LINEAR_REGRESSION_WEIGHT=0.3          # Weight for linear regression
AI_TIME_SERIES_WEIGHT=0.3                # Weight for time series
AI_NEURAL_NETWORK_WEIGHT=0.4             # Weight for neural network
```

#### **Optimization Algorithms**

```bash
# Optimization Method
AI_OPTIMIZATION_METHOD=genetic_algorithm # genetic_algorithm, gradient_descent, basic

# Genetic Algorithm Settings
AI_GA_POPULATION_SIZE=50                 # Population size
AI_GA_GENERATIONS=100                    # Number of generations
AI_GA_CROSSOVER_RATE=0.7                # Crossover probability
AI_GA_MUTATION_RATE=0.3                 # Mutation probability
AI_GA_SELECTION_METHOD=nsga2            # Selection method
```

## 🧪 **Testing and Development**

### **AI Testing Mode**

Run AI features without affecting your real system:

```bash
# Enable AI testing mode
AI_TEST_MODE=true python taskmaster_service.py

# Test AI with simulated data
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
service.enable_test_mode()
service.run_simulation()
print('AI simulation completed')
"
```

### **AI Component Testing**

Test individual AI components:

```bash
# Test pattern analysis
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
patterns = service.test_pattern_analysis()
print('Pattern Analysis Results:', patterns)
"

# Test prediction models
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
predictions = service.test_predictions()
print('Prediction Test Results:', predictions)
"

# Test optimization algorithms
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
optimizations = service.test_optimization()
print('Optimization Test Results:', optimizations)
"
```

### **AI Performance Testing**

Measure AI system performance:

```bash
# Test AI response time
python -c "
import time
from taskmaster_service import TaskMasterService
service = TaskMasterService()

start_time = time.time()
recommendations = service.get_recommendations()
end_time = time.time()

response_time = end_time - start_time
print(f'AI Response Time: {response_time:.3f} seconds')
"

# Test AI accuracy
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
accuracy = service.test_prediction_accuracy()
print(f'AI Prediction Accuracy: {accuracy:.2%}')
"
```

## 📊 **AI Monitoring and Diagnostics**

### **AI System Health Monitoring**

#### **Check AI System Status**

```bash
# Get comprehensive AI status
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
status = service.get_comprehensive_status()

print('=== AI System Status ===')
print(f"Service Status: {status['service_status']}")
print(f"AI Engine: {status['ai_engine_status']}")
print(f"Data Collection: {status['data_collection_status']}")
print(f"Task Management: {status['task_management_status']}")
print(f"Learning System: {status['learning_system_status']}")
print(f"Integration Status: {status['integration_status']}")
"
```

#### **Monitor AI Performance Metrics**

```bash
# Get AI performance metrics
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
metrics = service.get_performance_metrics()

print('=== AI Performance Metrics ===')
print(f"Prediction Accuracy: {metrics['prediction_accuracy']:.2%}")
print(f"Task Success Rate: {metrics['task_success_rate']:.2%}")
print(f"Optimization Impact: {metrics['optimization_impact']:.2%}")
print(f"Learning Progress: {metrics['learning_progress']:.2%}")
print(f"System Efficiency: {metrics['system_efficiency']:.2%}")
"
```

### **AI Learning Progress Monitoring**

#### **Track Model Improvements**

```bash
# Monitor AI model learning
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
learning_status = service.get_learning_status()

print('=== AI Learning Status ===')
print(f"Models Trained: {learning_status['models_trained']}")
print(f"Training Data Points: {learning_status['training_data_points']}")
print(f"Last Model Update: {learning_status['last_model_update']}")
print(f"Model Performance Trend: {learning_status['performance_trend']}")
print(f"Adaptation Frequency: {learning_status['adaptation_frequency']}")
"
```

#### **Analyze AI Decision Quality**

```bash
# Analyze AI decision quality
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
decision_quality = service.analyze_decision_quality()

print('=== AI Decision Quality ===')
print(f"Overall Quality Score: {decision_quality['overall_score']:.2f}/10")
print(f"Temperature Predictions: {decision_quality['temperature_predictions']:.2f}/10")
print(f"Optimization Decisions: {decision_quality['optimization_decisions']:.2f}/10")
print(f"Safety Compliance: {decision_quality['safety_compliance']:.2f}/10")
print(f"User Satisfaction: {decision_quality['user_satisfaction']:.2f}/10")
"
```

### **AI Data Analysis**

#### **Review Collected Data**

```bash
# Review AI data collection
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
data_summary = service.get_data_summary()

print('=== AI Data Summary ===')
print(f"Temperature Data Points: {data_summary['temperature_points']}")
print(f"Weather Data Points: {data_summary['weather_points']}")
print(f"Usage Pattern Data: {data_summary['usage_patterns']}")
print(f"Historical Data Range: {data_summary['historical_range']}")
print(f"Data Quality Score: {data_summary['data_quality']:.2f}/10")
"
```

#### **Analyze AI Patterns**

```bash
# Analyze AI-detected patterns
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
patterns = service.get_detected_patterns()

print('=== AI Detected Patterns ===')
for pattern_type, pattern_data in patterns.items():
    print(f"\n{pattern_type.upper()}:")
    print(f"  Confidence: {pattern_data['confidence']:.2f}")
    print(f"  Description: {pattern_data['description']}")
    print(f"  Optimization Potential: {pattern_data['optimization_potential']:.2f}")
"
```

## 🚨 **AI Safety and Troubleshooting**

### **AI Safety Features**

Your TaskMaster AI includes multiple safety layers:

1. **Validation Systems**: All AI recommendations are validated before execution
2. **Safety Limits**: AI cannot exceed configured temperature and safety limits
3. **Fallback Mechanisms**: Automatic fallback to manual control if AI fails
4. **User Approval**: Optional user approval for AI actions
5. **Rollback Systems**: Automatic rollback of failed optimizations

### **AI Safety Monitoring**

#### **Check AI Safety Status**

```bash
# Verify AI safety systems
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
safety_status = service.get_safety_status()

print('=== AI Safety Status ===')
print(f"Safety Systems Active: {safety_status['safety_systems_active']}")
print(f"Validation Rules: {safety_status['validation_rules']}")
print(f"Safety Limits: {safety_status['safety_limits']}")
print(f"Fallback Systems: {safety_status['fallback_systems']}")
print(f"Last Safety Check: {safety_status['last_safety_check']}")
"
```

#### **Test AI Safety Systems**

```bash
# Test AI safety validation
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
safety_test = service.test_safety_systems()

print('=== AI Safety Test Results ===')
print(f"Temperature Validation: {safety_test['temperature_validation']}")
print(f"Pump Safety Validation: {safety_test['pump_safety_validation']}")
print(f"System Health Validation: {safety_test['system_health_validation']}")
print(f"User Preference Validation: {safety_test['user_preference_validation']}")
print(f"Overall Safety Score: {safety_test['overall_safety_score']:.2f}/10")
"
```

### **AI Troubleshooting**

#### **Common AI Issues**

1. **AI Not Learning**
   ```bash
   # Check learning system status
   python -c "
   from taskmaster_service import TaskMasterService
   service = TaskMasterService()
   learning_issues = service.diagnose_learning_issues()
   print('Learning Issues:', learning_issues)
   "
   ```

2. **Poor Prediction Accuracy**
   ```bash
   # Analyze prediction accuracy
   python -c "
   from taskmaster_service import TaskMasterService
   service = TaskMasterService()
   accuracy_analysis = service.analyze_prediction_accuracy()
   print('Accuracy Analysis:', accuracy_analysis)
   "
   ```

3. **AI Recommendations Not Executing**
   ```bash
   # Check task execution status
   python -c "
   from taskmaster_service import TaskMasterService
   service = TaskMasterService()
   execution_status = service.get_task_execution_status()
   print('Task Execution Status:', execution_status)
   "
   ```

#### **AI Debug Mode**

Enable detailed AI logging for troubleshooting:

```bash
# Enable AI debug mode
AI_DEBUG_MODE=true AI_LOG_LEVEL=debug python taskmaster_service.py

# View AI debug logs
tail -f taskmaster_ai_debug.log

# Analyze AI decision logs
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
decision_logs = service.get_decision_logs()
for log in decision_logs[-10:]:  # Last 10 decisions
    print(f"Decision: {log['decision']}, Confidence: {log['confidence']:.2f}")
"
```

## 🔄 **AI Maintenance and Updates**

### **Regular AI Maintenance**

#### **Daily AI Checks**

- [ ] Check AI dashboard for system status
- [ ] Review AI notifications and alerts
- [ ] Verify AI optimization recommendations
- [ ] Monitor AI learning progress

#### **Weekly AI Maintenance**

- [ ] Review AI performance metrics
- [ ] Check AI model accuracy trends
- [ ] Verify AI safety systems
- [ ] Review AI optimization impact

#### **Monthly AI Maintenance**

- [ ] Analyze AI learning effectiveness
- [ ] Review AI model performance
- [ ] Update AI configuration if needed
- [ ] Backup AI models and data

### **AI Model Updates**

#### **Manual Model Updates**

```bash
# Force AI model update
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
service.force_model_update()
print('AI model update initiated')
"

# Check model update status
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
update_status = service.get_model_update_status()
print('Model Update Status:', update_status)
"
```

#### **AI Configuration Updates**

```bash
# Update AI configuration
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
service.update_configuration({
    'ai_learning_rate': 0.02,
    'ai_confidence_threshold': 0.9,
    'ai_optimization_interval': 600
})
print('AI configuration updated')
"
```

### **AI Backup and Recovery**

#### **Backup AI Models**

```bash
# Backup AI models
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
backup_path = service.backup_models()
print(f'AI models backed up to: {backup_path}')
"

# Backup AI data
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
backup_path = service.backup_data()
print(f'AI data backed up to: {backup_path}')
"
```

#### **Restore AI Models**

```bash
# Restore AI models from backup
python -c "
from taskmaster_service import TaskMasterService
service = TaskMasterService()
service.restore_models('/path/to/backup/models')
print('AI models restored from backup')
"
```

## 📱 **Mobile and Remote AI Access**

### **Home Assistant Mobile App**

1. **Install Home Assistant app** on your mobile device
2. **Connect to your Home Assistant instance**
3. **Access AI Insights dashboard** from anywhere
4. **Receive AI notifications** for alerts and recommendations
5. **Control AI features** remotely

### **Remote AI Monitoring**

#### **MQTT AI Monitoring**

Monitor your AI system remotely via MQTT:

```bash
# Monitor AI system remotely
mosquitto_sub -h your_broker -t "taskmaster/ai/#" -u username -P password

# Monitor AI recommendations
mosquitto_sub -h your_broker -t "taskmaster/recommendations/#" -u username -P password

# Monitor AI task execution
mosquitto_sub -h your_broker -t "taskmaster/tasks/#" -u username -P password
```

#### **Web Dashboard Access**

Access your AI dashboard from any web browser:
- Navigate to `http://your-home-assistant-ip:8123`
- Log in with your credentials
- Access the AI Insights dashboard
- Monitor AI performance and recommendations

## 🔗 **Related Documentation**

- **[Requirements Document](REQUIREMENTS_TASKMASTER_AI.md)** - What we built and why
- **[Design Document](DESIGN_TASKMASTER_AI.md)** - How the AI system works
- **[Implementation Guide](IMPLEMENTATION_TASKMASTER_AI.md)** - Technical implementation details
- **[Summary](SUMMARY_TASKMASTER_AI.md)** - Complete AI system overview
- **[System Overview](../SYSTEM_OVERVIEW.md)** - Complete system understanding
- **[Component Map](../COMPONENT_MAP.md)** - System component relationships

---

**This guide explains how to use your TaskMaster AI integration for daily operation, configuration, monitoring, and troubleshooting. For technical details, refer to the Design and Implementation documents.**
