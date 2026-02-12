/**
 * Solar Heating System v3 - Frontend JavaScript
 * Handles API communication and UI updates
 */

class SolarHeatingDashboard {
    constructor() {
        // API configuration will be loaded dynamically
        this.apiBaseUrl = null;
        this.updateInterval = 5000; // 5 seconds (default)
        this.updateTimer = null;
        this.isLoading = false;
        this.configLoaded = false;
        
        this.init();
    }
    
    async init() {
        console.log('🌞 Solar Heating Dashboard v3 - Initializing...');
        
        // Load configuration first
        await this.loadConfig();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup tab navigation
        this.setupTabNavigation();
        
        // Initial data load
        await this.loadSystemData();
        
        // Start auto-update
        this.startAutoUpdate();
        
        console.log('✅ Dashboard initialized successfully');
        
        // Hide loading overlay after initial load
        this.hideLoading();
    }
    
    async loadConfig() {
        try {
            // Fetch configuration from web server
            const response = await fetch('/api/config');
            const config = await response.json();
            
            this.apiBaseUrl = config.api_base_url;
            this.updateInterval = config.update_interval || 5000;
            
            console.log('Configuration loaded:', config);
            console.log('API Base URL:', this.apiBaseUrl);
            
            this.configLoaded = true;
        } catch (error) {
            console.error('Failed to load configuration, using defaults:', error);
            // Fallback to localhost if config fails
            this.apiBaseUrl = 'http://localhost:5001/api';
            this.configLoaded = true;
        }
    }
    
    setupEventListeners() {
        // Pump control buttons
        document.getElementById('pump-start-btn')?.addEventListener('click', () => {
            this.controlPump('start');
        });
        
        document.getElementById('pump-stop-btn')?.addEventListener('click', () => {
            this.controlPump('stop');
        });
        
        document.getElementById('emergency-stop-btn')?.addEventListener('click', () => {
            this.emergencyStop();
        });
        
        // Control tab buttons
        document.getElementById('control-pump-start')?.addEventListener('click', () => {
            this.controlPump('start');
        });
        
        document.getElementById('control-pump-stop')?.addEventListener('click', () => {
            this.controlPump('stop');
        });
        
        document.getElementById('control-emergency-stop')?.addEventListener('click', () => {
            this.emergencyStop();
        });
        
        // Mode buttons
        document.querySelectorAll('[data-mode]').forEach(button => {
            button.addEventListener('click', (e) => {
                const mode = e.target.getAttribute('data-mode');
                this.setSystemMode(mode);
            });
        });
    }
    
    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                
                // Remove active class from all buttons and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked button and corresponding content
                button.classList.add('active');
                document.getElementById(targetTab)?.classList.add('active');
            });
        });
    }
    
    async loadSystemData() {
        if (this.isLoading || !this.configLoaded) return;
        
        this.isLoading = true;
        
        try {
            // Load system status
            const statusResponse = await this.apiRequest('GET', '/status');
            if (statusResponse) {
                this.updateSystemStatus(statusResponse);
            }
            
            // Load temperatures
            const tempResponse = await this.apiRequest('GET', '/temperatures');
            if (tempResponse) {
                this.updateTemperatures(tempResponse);
            }
            
            // Load MQTT status
            const mqttResponse = await this.apiRequest('GET', '/mqtt');
            if (mqttResponse) {
                this.updateMQTTStatus(mqttResponse);
            }
            
            // Update API status indicator
            document.getElementById('api-status').textContent = 'Connected';
            document.getElementById('api-status').className = 'value connected';
            
        } catch (error) {
            console.error('Error loading system data:', error);
            document.getElementById('api-status').textContent = 'Disconnected';
            document.getElementById('api-status').className = 'value disconnected';
            this.showNotification('Failed to connect to API server', 'error');
        } finally {
            this.isLoading = false;
        }
    }
    
    async apiRequest(method, endpoint, data = null) {
        if (!this.configLoaded) {
            throw new Error('Configuration not loaded yet');
        }
        
        const url = `${this.apiBaseUrl}${endpoint}`;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    updateSystemStatus(data) {
        // Update system mode
        const mode = data.system_state?.mode || 'unknown';
        const modeDisplay = mode.charAt(0).toUpperCase() + mode.slice(1);
        
        document.getElementById('system-mode').textContent = modeDisplay;
        document.getElementById('current-mode').textContent = modeDisplay;
        document.getElementById('control-current-mode').textContent = modeDisplay;
        
        // Update pump status
        const pumpStatus = data.system_state?.primary_pump ? 'ON' : 'OFF';
        document.getElementById('pump-status').textContent = pumpStatus;
        document.getElementById('control-pump-status').textContent = pumpStatus;
        
        // Update heater status
        const heaterStatus = data.system_state?.cartridge_heater ? 'ON' : 'OFF';
        document.getElementById('heater-status').textContent = heaterStatus;
        
        // Update mode buttons
        document.querySelectorAll('[data-mode]').forEach(button => {
            const buttonMode = button.getAttribute('data-mode');
            if (buttonMode === mode) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        // Update hardware status from diagnostics
        if (data.hardware_status) {
            document.getElementById('rtd-status').textContent = data.hardware_status.rtd_boards || 'Unknown';
            document.getElementById('relay-status').textContent = data.hardware_status.relays || 'Unknown';
            document.getElementById('sensor-status').textContent = data.hardware_status.sensors || 'Unknown';
        }
        
        // Update service status
        if (data.service_status) {
            document.getElementById('solar-service-status').textContent = data.service_status.solar_heating_v3 || 'unknown';
            document.getElementById('mqtt-service-status').textContent = data.service_status.mqtt || 'unknown';
            document.getElementById('watchdog-service-status').textContent = data.service_status.solar_heating_watchdog || 'unknown';
        }
        
        // Update last update time
        document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
    }
    
    updateTemperatures(data) {
        const temperatures = data.temperatures || {};
        
        // Update dashboard temperatures
        document.getElementById('temp-tank').textContent = `${temperatures.tank?.toFixed(1) || '--'}°C`;
        document.getElementById('temp-collector').textContent = `${temperatures.solar_collector?.toFixed(1) || '--'}°C`;
        document.getElementById('temp-ambient').textContent = `${temperatures.ambient?.toFixed(1) || '--'}°C`;
        document.getElementById('temp-heat-exchanger').textContent = `${temperatures.heat_exchanger_in?.toFixed(1) || '--'}°C`;
        
        // Update temperature tab details
        document.getElementById('temp-tank-detail').textContent = `${temperatures.tank?.toFixed(1) || '--'}°C`;
        document.getElementById('temp-collector-detail').textContent = `${temperatures.solar_collector?.toFixed(1) || '--'}°C`;
        document.getElementById('temp-ambient-detail').textContent = `${temperatures.ambient?.toFixed(1) || '--'}°C`;
        document.getElementById('temp-heat-exchanger-detail').textContent = `${temperatures.heat_exchanger_in?.toFixed(1) || '--'}°C`;
        
        // Update temperature status indicators
        this.updateTemperatureStatus('tank', temperatures.tank);
        this.updateTemperatureStatus('collector', temperatures.solar_collector);
        this.updateTemperatureStatus('ambient', temperatures.ambient);
        this.updateTemperatureStatus('heat-exchanger', temperatures.heat_exchanger_in);
    }
    
    updateTemperatureStatus(sensor, temperature) {
        if (temperature === null || temperature === undefined) return;
        
        let status = 'Normal';
        let statusClass = 'normal';
        
        if (sensor === 'tank') {
            if (temperature > 80) {
                status = 'Hot';
                statusClass = 'hot';
            } else if (temperature < 20) {
                status = 'Cold';
                statusClass = 'cold';
            }
        } else if (sensor === 'collector') {
            if (temperature > 100) {
                status = 'Very Hot';
                statusClass = 'very-hot';
            } else if (temperature > 80) {
                status = 'Hot';
                statusClass = 'hot';
            }
        }
        
        const statusElement = document.getElementById(`${sensor}-status`);
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `temp-status ${statusClass}`;
        }
    }
    
    updateMQTTStatus(data) {
        const mqttStatus = data.mqtt_status || {};
        const connected = mqttStatus.connected || false;
        const broker = mqttStatus.broker || 'Unknown';
        const lastMessage = mqttStatus.last_message || {};
        
        // Update MQTT connection status
        document.getElementById('mqtt-connection').textContent = connected ? 'Connected' : 'Disconnected';
        document.getElementById('mqtt-connection').className = `status-value ${connected ? 'connected' : 'disconnected'}`;
        
        // Update MQTT status detail
        document.getElementById('mqtt-text').textContent = connected ? 'Connected' : 'Disconnected';
        document.getElementById('mqtt-indicator').className = `status-indicator ${connected ? 'connected' : 'disconnected'}`;
        
        // Update last message
        const messageDetails = document.getElementById('mqtt-message-details');
        if (lastMessage.topic && lastMessage.payload) {
            messageDetails.innerHTML = `
                <strong>Topic:</strong> ${lastMessage.topic}<br>
                <strong>Payload:</strong> ${lastMessage.payload}<br>
                <strong>Time:</strong> ${lastMessage.timestamp || 'Unknown'}
            `;
        } else {
            messageDetails.textContent = 'No messages available';
        }
        
        // Update Home Assistant status (simplified)
        const haStatus = connected ? 'Connected' : 'Disconnected';
        document.getElementById('ha-connection').textContent = haStatus;
        document.getElementById('ha-connection').className = `status-value ${connected ? 'connected' : 'disconnected'}`;
    }
    
    async controlPump(action) {
        try {
            this.showLoading();
            
            const response = await this.apiRequest('POST', '/control', {
                action: action === 'start' ? 'pump_start' : 'pump_stop'
            });
            
            if (response.success) {
                this.showNotification(`Pump ${action} successful`, 'success');
                // Refresh system data
                setTimeout(() => this.loadSystemData(), 1000);
            } else {
                this.showNotification(`Pump ${action} failed: ${response.error}`, 'error');
            }
            
        } catch (error) {
            console.error(`Error controlling pump:`, error);
            this.showNotification(`Pump ${action} failed: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async setSystemMode(mode) {
        try {
            this.showLoading();
            
            const response = await this.apiRequest('POST', '/mode', { mode });
            
            if (response.success) {
                this.showNotification(`Mode changed to ${mode}`, 'success');
                // Refresh system data
                setTimeout(() => this.loadSystemData(), 1000);
            } else {
                this.showNotification(`Mode change failed: ${response.error}`, 'error');
            }
            
        } catch (error) {
            console.error(`Error setting mode:`, error);
            this.showNotification(`Mode change failed: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async emergencyStop() {
        if (!confirm('Are you sure you want to perform an emergency stop? This will turn off all systems and reset to auto mode.')) {
            return;
        }
        
        try {
            this.showLoading();
            
            const response = await this.apiRequest('POST', '/control', {
                action: 'emergency_stop'
            });
            
            if (response.success) {
                this.showNotification('Emergency stop activated', 'warning');
                // Refresh system data
                setTimeout(() => this.loadSystemData(), 1000);
            } else {
                this.showNotification(`Emergency stop failed: ${response.error}`, 'error');
            }
            
        } catch (error) {
            console.error(`Error performing emergency stop:`, error);
            this.showNotification(`Emergency stop failed: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    startAutoUpdate() {
        this.updateTimer = setInterval(() => {
            this.loadSystemData();
        }, this.updateInterval);
    }
    
    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }
    
    showLoading() {
        document.getElementById('loading-overlay')?.classList.remove('hidden');
    }
    
    hideLoading() {
        document.getElementById('loading-overlay')?.classList.add('hidden');
    }
    
    showNotification(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        const messageElement = document.getElementById('toast-message');
        
        if (toast && messageElement) {
            messageElement.textContent = message;
            
            // Set icon based on type
            const icon = toast.querySelector('.toast-icon');
            if (icon) {
                switch (type) {
                    case 'success':
                        icon.textContent = '✅';
                        toast.style.background = 'rgba(39, 174, 96, 0.95)';
                        break;
                    case 'error':
                        icon.textContent = '❌';
                        toast.style.background = 'rgba(231, 76, 60, 0.95)';
                        break;
                    case 'warning':
                        icon.textContent = '⚠️';
                        toast.style.background = 'rgba(243, 156, 18, 0.95)';
                        break;
                    default:
                        icon.textContent = 'ℹ️';
                        toast.style.background = 'rgba(52, 152, 219, 0.95)';
                }
            }
            
            toast.classList.add('show');
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SolarHeatingDashboard();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (window.dashboard) {
        if (document.hidden) {
            window.dashboard.stopAutoUpdate();
        } else {
            window.dashboard.startAutoUpdate();
            window.dashboard.loadSystemData();
        }
    }
});
