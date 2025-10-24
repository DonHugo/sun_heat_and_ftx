// Solar Heating System Local GUI JavaScript

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
});