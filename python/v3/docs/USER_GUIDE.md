# Solar Heating System v3 - User Guide

## 👋 Welcome to Solar Heating System v3

This guide helps you use the new web interface for monitoring and controlling your solar heating system.

## 🌐 Accessing the System

### Local Access
- **URL**: http://localhost
- **Port**: 80 (default HTTP port)
- **Device**: Any device on the same network

### Remote Access
- **URL**: http://[PI_IP_ADDRESS]
- **Example**: http://192.168.1.100
- **Network**: Same network as Raspberry Pi

## 🖥️ Web Interface Overview

### Main Dashboard
The main dashboard provides:
- **System Status**: Current mode and health
- **Temperature Readings**: Real-time sensor data
- **Control Buttons**: Pump and system control
- **MQTT Status**: Connection status and last message
- **Home Assistant**: Integration status

### Navigation
- **Dashboard**: Main system overview
- **Sensors**: All sensor readings
- **Controllers**: System control interface
- **Settings**: System configuration

## 🌡️ Temperature Monitoring

### Temperature Display
The system shows temperatures for:
- **Tank Temperature**: Water storage temperature
- **Solar Collector**: Solar panel temperature
- **Ambient**: Outside temperature
- **Heat Exchanger**: Heat exchanger temperature

### Temperature Updates
- **Update Frequency**: Every 5 seconds
- **Real-time**: Automatic updates
- **Accuracy**: ±0.1°C

## 🎛️ System Control

### System Modes
- **Auto Mode**: Automatic control based on temperature
- **Manual Mode**: Manual control of pump and heater
- **Eco Mode**: Energy-efficient operation

### Control Actions
- **Pump Start**: Start the circulation pump
- **Pump Stop**: Stop the circulation pump
- **Emergency Stop**: Stop all operations immediately

### Mode Changes
1. **Click the mode button** (Auto/Manual/Eco)
2. **Confirm the change** in the popup
3. **Wait for confirmation** that the mode has changed

## 🔧 Pump Control

### Manual Pump Control
1. **Switch to Manual Mode** first
2. **Click "Pump Start"** to start the pump
3. **Click "Pump Stop"** to stop the pump
4. **Monitor the status** in the dashboard

### Automatic Pump Control
- **Auto Mode**: Pump controlled automatically
- **Temperature-based**: Starts when solar collector is hot
- **Safety**: Stops when tank is full or system is cold

## 📡 MQTT Integration

### MQTT Status
- **Connected**: MQTT broker is connected
- **Disconnected**: MQTT broker is not connected
- **Last Message**: Shows the last MQTT message received

### Home Assistant Integration
- **Status**: Shows Home Assistant connection status
- **Synchronization**: Changes are reflected in Home Assistant
- **Control**: Home Assistant can control the system

## 📱 Mobile Interface

### Responsive Design
- **Mobile-friendly**: Works on phones and tablets
- **Touch controls**: Easy to use on touch screens
- **Portrait/Landscape**: Adapts to screen orientation

### Mobile Features
- **Swipe navigation**: Easy navigation between sections
- **Touch buttons**: Large, easy-to-tap buttons
- **Real-time updates**: Automatic data refresh

## 🔍 Troubleshooting

### Common Issues

#### Page Not Loading
- **Check network connection**
- **Verify Raspberry Pi is running**
- **Try refreshing the page**

#### Buttons Not Working
- **Check if system is in Manual Mode**
- **Verify MQTT connection**
- **Check system logs**

#### Temperature Not Updating
- **Check sensor connections**
- **Verify system is running**
- **Check for error messages**

### Getting Help
1. **Check the troubleshooting guide**
2. **Review system logs**
3. **Contact support if needed**

## ⚙️ Settings and Configuration

### System Settings
- **Update Frequency**: How often data refreshes
- **Temperature Units**: Celsius or Fahrenheit
- **Display Options**: What information to show

### User Preferences
- **Theme**: Light or dark mode
- **Language**: Interface language
- **Notifications**: Alert preferences

## 📊 Monitoring and Alerts

### System Monitoring
- **Health Status**: Overall system health
- **Performance**: System performance metrics
- **Errors**: Any system errors or warnings

### Alerts and Notifications
- **Temperature Alerts**: High or low temperature warnings
- **System Alerts**: Pump or heater issues
- **Connection Alerts**: MQTT or network issues

## 🔒 Security

### Access Control
- **Local Network**: Access from local network only
- **No Authentication**: Currently no password protection
- **Firewall**: Basic firewall protection

### Data Privacy
- **Local Data**: All data stays on your network
- **No Cloud**: No data sent to external services
- **Secure**: HTTPS support available

## 📈 Performance

### System Performance
- **Fast Loading**: Optimized for speed
- **Low Resource Usage**: Minimal system impact
- **Reliable**: Stable operation

### Network Performance
- **Fast Response**: Quick API responses
- **Efficient**: Minimal network usage
- **Scalable**: Handles multiple users

## 🎯 Best Practices

### Daily Use
1. **Check system status** regularly
2. **Monitor temperatures** for optimal performance
3. **Use Manual Mode** when needed
4. **Keep system updated**

### Maintenance
1. **Check connections** periodically
2. **Clean sensors** as needed
3. **Monitor logs** for issues
4. **Update system** when available

## 📞 Support

### Self-Service
1. **Check this user guide**
2. **Review troubleshooting guide**
3. **Check system logs**
4. **Test basic functionality**

### Getting Help
- **GitHub Issues**: Create an issue with details
- **Documentation**: Check the API documentation
- **Community**: Ask questions in the community

## 🎉 Conclusion

The new web interface provides a modern, user-friendly way to monitor and control your solar heating system. Enjoy the improved experience!

**Happy heating!** 🌞
