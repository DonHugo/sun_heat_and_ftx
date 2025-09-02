# 🧠 TaskMaster AI Insights Guide

## 📍 **Where to Get Insights & Recommendations**

Your TaskMaster AI integration provides insights in **3 main ways**:

### **1. 🚀 On-Demand Insights** 
Get insights whenever you want:

```bash
cd python/v3
source venv/bin/activate
python get_insights.py
```

**What you get:**
- 🏥 System health score
- ⚡ Energy efficiency metrics  
- 💡 Intelligent recommendations
- 🎯 Action items with priorities
- 📈 Performance trends

### **2. 📊 Continuous Monitoring**
Watch insights update in real-time:

```bash
cd python/v3
source venv/bin/activate
python monitor_insights.py
```

**Features:**
- Updates every 30 seconds
- Real-time system analysis
- Continuous health monitoring
- Live recommendations
- Press `Ctrl+C` to stop

### **3. 📝 System Logs**
Insights are automatically logged as your system runs:

```bash
# View real-time logs
python main_system.py

# Look for these log entries:
# [INFO] TaskMaster AI: System optimization recommendation
# [INFO] TaskMaster AI: Energy efficiency insight  
# [INFO] TaskMaster AI: Maintenance recommendation
```

## 🎯 **Types of Insights You'll Get**

### **🏥 System Health Analysis**
- Overall health score (0-100)
- Priority issues and alerts
- Safety condition warnings
- System reliability metrics

### **⚡ Energy Efficiency Insights**
- Solar collector efficiency
- Heat exchanger performance
- Water stratification quality
- Overall system efficiency
- Potential savings opportunities

### **🔧 Operational Performance**
- Pump efficiency metrics
- Heating cycle optimization
- Maintenance scheduling
- Component health status

### **💡 Intelligent Recommendations**
- Energy optimization suggestions
- Performance improvement actions
- Preventive maintenance plans
- Cost reduction opportunities

### **🎯 Action Items**
- Prioritized tasks (CRITICAL, HIGH, MEDIUM)
- Estimated effort and duration
- Specific maintenance actions
- Safety inspection requirements

## 🚀 **Quick Start Examples**

### **Get Current Insights:**
```bash
python get_insights.py
```

### **Monitor Continuously:**
```bash
python monitor_insights.py
```

### **Run Full System with AI:**
```bash
python main_system.py
```

## 🔧 **Customization Options**

### **Change Update Frequency:**
Edit `monitor_insights.py` line 25:
```python
monitor = InsightsMonitor(update_interval=60)  # 60 seconds
```

### **Filter Specific Insights:**
Modify `get_insights.py` to show only certain types:
```python
# Show only health issues
if 'health_issues' in insights:
    for issue in insights['health_issues']:
        print(f"  ⚠️  {issue}")
```

### **Export Insights to File:**
```bash
python get_insights.py > insights_report.txt
```

## 📱 **Integration with Home Assistant**

The insights are also available through:
- **MQTT topics** for real-time monitoring
- **Home Assistant sensors** for dashboard display
- **Automation triggers** based on AI recommendations

## 🎉 **What You're Getting**

**Real AI-powered analysis** that:
- ✅ **Monitors your system 24/7**
- ✅ **Detects issues before they become problems**
- ✅ **Optimizes energy efficiency automatically**
- ✅ **Schedules maintenance intelligently**
- ✅ **Provides actionable recommendations**
- ✅ **Tracks performance trends over time**

## 🆘 **Troubleshooting**

### **"No insights available"**
- Make sure the service is initialized
- Check that sensors are providing data
- Verify the virtual environment is activated

### **"Service not responding"**
- Restart the TaskMaster service
- Check system logs for errors
- Verify all dependencies are installed

### **"Insights seem outdated"**
- The system updates automatically
- Force refresh by restarting the service
- Check the last optimization timestamp

---

**🎯 Your TaskMaster AI is now your personal solar heating system consultant!** 🧠✨
