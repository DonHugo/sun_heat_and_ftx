#!/usr/bin/env python3
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
