#!/usr/bin/env python3
"""
Local GUI Starter Script
Creates the initial structure for the Raspberry Pi local web interface
"""

import os
import sys
from pathlib import Path

def create_local_gui_structure():
    """Create the basic structure for the local web GUI"""
    
    # Base paths
    base_dir = Path("python/v3")
    web_dir = base_dir / "web_interface"
    
    print("🌐 Creating Local GUI Structure...")
    print("=" * 50)
    
    # Create directory structure
    directories = [
        web_dir,
        web_dir / "api",
        web_dir / "templates", 
        web_dir / "static" / "css",
        web_dir / "static" / "js",
        web_dir / "static" / "images",
        web_dir / "utils"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created: {directory}")
    
    # Create Flask app
    app_content = '''#!/usr/bin/env python3
"""
Local Web GUI for Solar Heating System
Direct access to Raspberry Pi system monitoring and control
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import time
import logging
from datetime import datetime

# Import existing system modules
sys.path.append('/home/pi/solar_heating/python/v3')
from main_system import SolarHeatingSystem
from hardware_interface import HardwareInterface
from mqtt_handler import MQTTHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'solar_heating_local_gui'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global system instance
solar_system = None

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/system/status')
def system_status():
    """Get current system status"""
    if not solar_system:
        return jsonify({'error': 'System not initialized'}), 500
    
    try:
        # Get system data
        status = {
            'timestamp': datetime.now().isoformat(),
            'system_state': solar_system.system_state,
            'temperatures': solar_system.temperatures,
            'hardware_status': get_hardware_status(),
            'service_status': get_service_status(),
            'mqtt_status': get_mqtt_status()
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/control', methods=['POST'])
def system_control():
    """Control system components"""
    data = request.get_json()
    action = data.get('action')
    
    try:
        if action == 'pump_start':
            solar_system.hardware.set_relay_state(1, True)
            return jsonify({'success': True, 'message': 'Pump started'})
        elif action == 'pump_stop':
            solar_system.hardware.set_relay_state(1, False)
            return jsonify({'success': True, 'message': 'Pump stopped'})
        elif action == 'emergency_stop':
            solar_system.hardware.set_relay_state(1, False)
            solar_system.system_state['mode'] = 'emergency'
            return jsonify({'success': True, 'message': 'Emergency stop activated'})
        else:
            return jsonify({'error': 'Invalid action'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print('Client connected')
    emit('status', {'message': 'Connected to Solar Heating System'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print('Client disconnected')

def get_hardware_status():
    """Get hardware status information"""
    try:
        if solar_system and solar_system.hardware:
            return {
                'rtd_boards': 'Connected',
                'relays': 'Connected', 
                'sensors': 'Active'
            }
        return {'status': 'Not connected'}
    except:
        return {'status': 'Error'}

def get_service_status():
    """Get systemd service status"""
    import subprocess
    try:
        result = subprocess.run(['systemctl', 'is-active', 'solar_heating_v3.service'], 
                              capture_output=True, text=True)
        return {
            'solar_heating': result.stdout.strip(),
            'watchdog': 'active',
            'mqtt': 'active'
        }
    except:
        return {'status': 'Unknown'}

def get_mqtt_status():
    """Get MQTT connection status"""
    try:
        if solar_system and solar_system.mqtt:
            return {
                'connected': solar_system.mqtt.connected,
                'last_message': 'Recent',
                'broker': 'Connected'
            }
        return {'connected': False}
    except:
        return {'connected': False}

def initialize_system():
    """Initialize the solar heating system"""
    global solar_system
    try:
        solar_system = SolarHeatingSystem()
        print("✅ Solar Heating System initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return False

if __name__ == '__main__':
    print("🌐 Starting Solar Heating Local GUI...")
    
    # Initialize system
    if initialize_system():
        print("🚀 Starting web server on http://0.0.0.0:5000")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    else:
        print("❌ Failed to initialize system. Exiting.")
        sys.exit(1)
'''
    
    # Write Flask app
    app_file = web_dir / "app.py"
    with open(app_file, 'w') as f:
        f.write(app_content)
    os.chmod(app_file, 0o755)
    print(f"📄 Created: {app_file}")
    
    # Create HTML template
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solar Heating System - Local Control</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏠 Solar Heating System - Local Control</h1>
            <div class="status-indicator" id="systemStatus">
                <span class="status-dot"></span>
                <span class="status-text">Connecting...</span>
            </div>
        </header>
        
        <main>
            <!-- System Overview -->
            <section class="overview">
                <h2>📊 System Overview</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>🌡️ Tank Temperature</h3>
                        <div class="metric-value" id="tankTemp">--°C</div>
                    </div>
                    <div class="metric-card">
                        <h3>🔥 Collector Temperature</h3>
                        <div class="metric-value" id="collectorTemp">--°C</div>
                    </div>
                    <div class="metric-card">
                        <h3>⚡ Pump Status</h3>
                        <div class="metric-value" id="pumpStatus">--</div>
                    </div>
                    <div class="metric-card">
                        <h3>🎛️ System Mode</h3>
                        <div class="metric-value" id="systemMode">--</div>
                    </div>
                </div>
            </section>
            
            <!-- Controls -->
            <section class="controls">
                <h2>🎛️ System Controls</h2>
                <div class="control-buttons">
                    <button id="pumpStart" class="btn btn-primary">Start Pump</button>
                    <button id="pumpStop" class="btn btn-danger">Stop Pump</button>
                    <button id="emergencyStop" class="btn btn-warning">Emergency Stop</button>
                </div>
            </section>
            
            <!-- Diagnostics -->
            <section class="diagnostics">
                <h2>🔍 System Diagnostics</h2>
                <div class="diagnostics-grid">
                    <div class="diagnostic-card">
                        <h3>🔧 Services</h3>
                        <div id="serviceStatus">Loading...</div>
                    </div>
                    <div class="diagnostic-card">
                        <h3>📡 MQTT</h3>
                        <div id="mqttStatus">Loading...</div>
                    </div>
                    <div class="diagnostic-card">
                        <h3>🏠 Home Assistant</h3>
                        <div id="haStatus">Loading...</div>
                    </div>
                </div>
            </section>
        </main>
    </div>
    
    <script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
</body>
</html>'''
    
    # Write HTML template
    template_file = web_dir / "templates" / "dashboard.html"
    with open(template_file, 'w') as f:
        f.write(dashboard_html)
    print(f"📄 Created: {template_file}")
    
    # Create CSS
    css_content = '''/* Solar Heating System Local GUI Styles */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background: rgba(255, 255, 255, 0.95);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

h1 {
    color: #2c3e50;
    font-size: 2rem;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
}

.status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #e74c3c;
    animation: pulse 2s infinite;
}

.status-dot.connected {
    background: #27ae60;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

main {
    display: grid;
    gap: 20px;
}

section {
    background: rgba(255, 255, 255, 0.95);
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

h2 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 1.5rem;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

.metric-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    border: 2px solid transparent;
    transition: all 0.3s ease;
}

.metric-card:hover {
    border-color: #3498db;
    transform: translateY(-2px);
}

.metric-card h3 {
    color: #495057;
    margin-bottom: 10px;
    font-size: 1rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #2c3e50;
}

.control-buttons {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 120px;
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-primary:hover {
    background: #2980b9;
    transform: translateY(-2px);
}

.btn-danger {
    background: #e74c3c;
    color: white;
}

.btn-danger:hover {
    background: #c0392b;
    transform: translateY(-2px);
}

.btn-warning {
    background: #f39c12;
    color: white;
}

.btn-warning:hover {
    background: #e67e22;
    transform: translateY(-2px);
}

.diagnostics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.diagnostic-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 20px;
    border-radius: 10px;
    border-left: 4px solid #3498db;
}

.diagnostic-card h3 {
    color: #495057;
    margin-bottom: 10px;
    font-size: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    header {
        flex-direction: column;
        gap: 15px;
        text-align: center;
    }
    
    h1 {
        font-size: 1.5rem;
    }
    
    .control-buttons {
        justify-content: center;
    }
    
    .btn {
        flex: 1;
        min-width: 100px;
    }
}'''
    
    # Write CSS
    css_file = web_dir / "static" / "css" / "style.css"
    with open(css_file, 'w') as f:
        f.write(css_content)
    print(f"📄 Created: {css_file}")
    
    # Create JavaScript
    js_content = '''// Solar Heating System Local GUI JavaScript

class SolarHeatingGUI {
    constructor() {
        this.socket = io();
        this.updateInterval = null;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupWebSocket();
        this.startDataUpdates();
    }
    
    setupEventListeners() {
        // Control buttons
        document.getElementById('pumpStart').addEventListener('click', () => this.controlSystem('pump_start'));
        document.getElementById('pumpStop').addEventListener('click', () => this.controlSystem('pump_stop'));
        document.getElementById('emergencyStop').addEventListener('click', () => this.controlSystem('emergency_stop'));
    }
    
    setupWebSocket() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateStatus('connected', 'Connected');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateStatus('disconnected', 'Disconnected');
        });
        
        this.socket.on('status', (data) => {
            console.log('Status update:', data);
        });
    }
    
    startDataUpdates() {
        // Update data every 5 seconds
        this.updateInterval = setInterval(() => {
            this.fetchSystemData();
        }, 5000);
        
        // Initial data fetch
        this.fetchSystemData();
    }
    
    async fetchSystemData() {
        try {
            const response = await fetch('/api/system/status');
            const data = await response.json();
            
            if (data.error) {
                console.error('Error fetching system data:', data.error);
                return;
            }
            
            this.updateDisplay(data);
        } catch (error) {
            console.error('Failed to fetch system data:', error);
            this.updateStatus('error', 'Connection Error');
        }
    }
    
    updateDisplay(data) {
        // Update temperatures
        if (data.temperatures) {
            document.getElementById('tankTemp').textContent = 
                (data.temperatures.tank || '--') + '°C';
            document.getElementById('collectorTemp').textContent = 
                (data.temperatures.solar_collector || '--') + '°C';
        }
        
        // Update pump status
        if (data.system_state) {
            const pumpStatus = data.system_state.primary_pump ? 'ON' : 'OFF';
            document.getElementById('pumpStatus').textContent = pumpStatus;
            document.getElementById('pumpStatus').className = 
                'metric-value ' + (data.system_state.primary_pump ? 'status-on' : 'status-off');
            
            // Update system mode
            document.getElementById('systemMode').textContent = 
                data.system_state.mode || 'Unknown';
        }
        
        // Update diagnostics
        if (data.service_status) {
            document.getElementById('serviceStatus').innerHTML = 
                this.formatServiceStatus(data.service_status);
        }
        
        if (data.mqtt_status) {
            document.getElementById('mqttStatus').innerHTML = 
                this.formatMqttStatus(data.mqtt_status);
        }
        
        // Update connection status
        this.updateStatus('connected', 'Connected');
    }
    
    formatServiceStatus(services) {
        let html = '<div class="service-list">';
        for (const [service, status] of Object.entries(services)) {
            const statusClass = status === 'active' ? 'status-active' : 'status-inactive';
            html += `<div class="service-item ${statusClass}">${service}: ${status}</div>`;
        }
        html += '</div>';
        return html;
    }
    
    formatMqttStatus(mqtt) {
        const connected = mqtt.connected ? 'Connected' : 'Disconnected';
        const statusClass = mqtt.connected ? 'status-active' : 'status-inactive';
        return `<div class="mqtt-status ${statusClass}">MQTT: ${connected}</div>`;
    }
    
    updateStatus(status, text) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');
        
        statusDot.className = 'status-dot ' + status;
        statusText.textContent = text;
    }
    
    async controlSystem(action) {
        try {
            const response = await fetch('/api/system/control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ action: action })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('Control action successful:', result.message);
                // Show success feedback
                this.showNotification(result.message, 'success');
            } else {
                console.error('Control action failed:', result.error);
                this.showNotification(result.error, 'error');
            }
        } catch (error) {
            console.error('Failed to send control command:', error);
            this.showNotification('Failed to send command', 'error');
        }
    }
    
    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize GUI when page loads
document.addEventListener('DOMContentLoaded', () => {
    new SolarHeatingGUI();
});'''
    
    # Write JavaScript
    js_file = web_dir / "static" / "js" / "dashboard.js"
    with open(js_file, 'w') as f:
        f.write(js_content)
    print(f"📄 Created: {js_file}")
    
    # Create requirements file
    requirements_content = '''# Local GUI Requirements
Flask==2.3.3
Flask-SocketIO==5.3.6
python-socketio==5.8.0
eventlet==0.33.3'''
    
    req_file = web_dir / "requirements.txt"
    with open(req_file, 'w') as f:
        f.write(requirements_content)
    print(f"📄 Created: {req_file}")
    
    # Create startup script
    startup_script = '''#!/bin/bash
# Solar Heating Local GUI Startup Script

echo "🌐 Starting Solar Heating Local GUI..."

# Change to the web interface directory
cd /home/pi/solar_heating/python/v3/web_interface

# Activate virtual environment if it exists
if [ -f "/home/pi/solar_heating/.venv/bin/activate" ]; then
    source /home/pi/solar_heating/.venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Requirements installed"
fi

# Start the Flask application
echo "🚀 Starting web server on http://0.0.0.0:5000"
python3 app.py
'''
    
    startup_file = web_dir / "start_gui.sh"
    with open(startup_file, 'w') as f:
        f.write(startup_script)
    os.chmod(startup_file, 0o755)
    print(f"📄 Created: {startup_file}")
    
    print("\n✅ Local GUI structure created successfully!")
    print("\n🚀 Next Steps:")
    print("1. Copy files to Raspberry Pi")
    print("2. Install requirements: pip install -r requirements.txt")
    print("3. Run: python3 app.py")
    print("4. Access: http://192.168.0.18:5000")
    print("\n📁 Files created:")
    for directory in directories:
        print(f"   {directory}")

if __name__ == "__main__":
    create_local_gui_structure()
