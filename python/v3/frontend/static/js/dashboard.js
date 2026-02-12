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
        
        this.heaterToggle = null;
        this.manualControlEnabled = false;
        this.heaterState = false;
        this.heaterPending = false;
        this.heaterLockoutUntil = 0;
        this.heaterLockoutTimer = null;
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
        
        // Heater toggle control
        this.heaterToggle = document.getElementById('heater-toggle');
        if (this.heaterToggle) {
            this.heaterToggle.addEventListener('change', (e) => {
                const checked = e.target.checked;
                const action = checked ? 'heater_start' : 'heater_stop';
                this.controlHeater(action, checked);
            });
        }
        
        // Control tab buttons
        document.getElementById('control-pump-start')?.addEventListener('click', () => {
            this.controlPump('start');
        });
        
        document.getElementById('control-pump-stop')?.addEventListener('click', () => {
            this.controlPump('stop');
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
        
        // Update pump status with status dots
        const pumpStatus = data.system_state?.primary_pump ? 'ON' : 'OFF';
        const pumpStatusClass = data.system_state?.primary_pump ? 'status-active' : 'status-inactive';
        this.updateStatusWithDot('pump-status', pumpStatus, pumpStatusClass);
        this.updateStatusWithDot('control-pump-status', pumpStatus, pumpStatusClass);
        
        // Update heater status with status dots
        const heaterStatus = data.system_state?.cartridge_heater ? 'ON' : 'OFF';
        const heaterStatusClass = data.system_state?.cartridge_heater ? 'status-active' : 'status-inactive';
        this.updateStatusWithDot('heater-status', heaterStatus, heaterStatusClass);
        this.updateStatusWithDot('control-heater-status', heaterStatus, heaterStatusClass);
        
        // Update mode buttons
        document.querySelectorAll('[data-mode]').forEach(button => {
            const buttonMode = button.getAttribute('data-mode');
            if (buttonMode === mode) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });

        // Update manual mode UI + heater toggle state
        this.manualControlEnabled = Boolean(data.system_state?.manual_control ?? (mode === 'manual'));
        const actualHeaterState = Boolean(data.system_state?.cartridge_heater);
        if (!this.heaterPending) {
            this.heaterState = actualHeaterState;
        }
        this.updateHeaterToggle();
        
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
        
        // Update hero card
        this.updateHeroCard(data);
    }
    
    // UX Fix #4: Update hero card with system status
    updateHeroCard(data) {
        // Update hero status indicator
        const pumpOn = data.system_state?.primary_pump;
        const mode = data.system_state?.mode || 'auto';
        const temperatures = data.temperatures || {};
        
        // Determine overall system status
        let statusClass = 'status-active';
        let statusText = 'Operating Normally';
        
        // Check for warnings or errors
        if (temperatures.tank > 85) {
            statusClass = 'status-warning';
            statusText = 'Tank Temperature High';
        } else if (temperatures.solar_collector > 110) {
            statusClass = 'status-warning';
            statusText = 'Collector Temperature High';
        } else if (pumpOn && mode === 'auto') {
            statusText = 'Actively Heating';
        } else if (!pumpOn && mode === 'manual') {
            statusText = 'Manual Control';
        }
        
        const heroDot = document.querySelector('.hero-dot');
        if (heroDot) {
            heroDot.className = `hero-dot ${statusClass}`;
        }
        
        const heroStatusText = document.getElementById('hero-status-text');
        if (heroStatusText) {
            heroStatusText.textContent = statusText;
            heroStatusText.style.color = statusClass === 'status-active' ? '#27ae60' : 
                                          statusClass === 'status-warning' ? '#f39c12' : '#e74c3c';
        }
        
        // Update tank temperature in hero
        const heroTempTank = document.getElementById('hero-temp-tank');
        if (heroTempTank && temperatures.tank) {
            heroTempTank.textContent = `${temperatures.tank.toFixed(1)}°C`;
        }
        
        const heroTempTankStatus = document.getElementById('hero-temp-tank-status');
        if (heroTempTankStatus && temperatures.tank) {
            if (temperatures.tank < 40) heroTempTankStatus.textContent = 'Cold - needs heating';
            else if (temperatures.tank < 60) heroTempTankStatus.textContent = 'Normal operating range';
            else if (temperatures.tank < 75) heroTempTankStatus.textContent = 'Good temperature';
            else heroTempTankStatus.textContent = 'Hot - caution';
        }
        
        // Update collector temperature in hero
        const heroTempCollector = document.getElementById('hero-temp-collector');
        if (heroTempCollector && temperatures.solar_collector) {
            heroTempCollector.textContent = `${temperatures.solar_collector.toFixed(1)}°C`;
        }
        
        const heroTempCollectorStatus = document.getElementById('hero-temp-collector-status');
        if (heroTempCollectorStatus && temperatures.solar_collector) {
            const diff = temperatures.solar_collector - temperatures.tank;
            if (diff > 10) heroTempCollectorStatus.textContent = `+${diff.toFixed(1)}°C vs tank`;
            else if (diff > 0) heroTempCollectorStatus.textContent = `Slightly warmer than tank`;
            else heroTempCollectorStatus.textContent = 'Cooler than tank';
        }
        
        // Update pump status in hero
        const heroPumpStatus = document.getElementById('hero-pump-status');
        if (heroPumpStatus) {
            heroPumpStatus.textContent = pumpOn ? 'RUNNING' : 'STOPPED';
            heroPumpStatus.style.color = pumpOn ? '#27ae60' : '#95a5a6';
        }
        
        const heroPumpMode = document.getElementById('hero-pump-mode');
        if (heroPumpMode) {
            heroPumpMode.textContent = mode === 'auto' ? 'Auto Mode' : 'Manual Mode';
        }
        
        // Update energy status in hero
        const heroEnergyStatus = document.getElementById('hero-energy-status');
        const heroEnergyDetail = document.getElementById('hero-energy-detail');
        
        if (heroEnergyStatus && heroEnergyDetail) {
            if (pumpOn && temperatures.solar_collector > temperatures.tank) {
                heroEnergyStatus.textContent = 'Collecting';
                heroEnergyDetail.textContent = 'Solar heating active';
                heroEnergyStatus.style.color = '#27ae60';
            } else if (pumpOn) {
                heroEnergyStatus.textContent = 'Circulating';
                heroEnergyDetail.textContent = 'Pump running';
                heroEnergyStatus.style.color = '#3498db';
            } else {
                heroEnergyStatus.textContent = 'Idle';
                heroEnergyDetail.textContent = 'Waiting for conditions';
                heroEnergyStatus.style.color = '#95a5a6';
            }
        }
    }
    
    updateTemperatures(data) {
        const temperatures = data.temperatures || {};
        
        // Update dashboard temperatures with color coding
        this.updateTempElement('temp-tank', temperatures.tank, 'tank');
        this.updateTempElement('temp-collector', temperatures.solar_collector, 'collector');
        this.updateTempElement('temp-ambient', temperatures.ambient, 'ambient');
        this.updateEfficiencyElement('temp-heat-exchanger', temperatures.heat_exchanger_efficiency);
        
        // Update temperature tab details
        document.getElementById('temp-tank-detail').textContent = `${temperatures.tank?.toFixed(1) || '--'}°C`;
        document.getElementById('temp-collector-detail').textContent = `${temperatures.solar_collector?.toFixed(1) || '--'}°C`;
        document.getElementById('temp-ambient-detail').textContent = `${temperatures.ambient?.toFixed(1) || '--'}°C`;
        this.updateEfficiencyDetail('temp-heat-exchanger-detail', temperatures);
        
        // Update temperature status indicators
        this.updateTemperatureStatus('tank', temperatures.tank);
        this.updateTemperatureStatus('collector', temperatures.solar_collector);
        this.updateTemperatureStatus('ambient', temperatures.ambient);
        this.updateEfficiencyStatus('heat-exchanger', temperatures.heat_exchanger_efficiency);
    }
    
    // UX Fix #2: Temperature color coding helper function
    updateTempElement(elementId, temperature, sensorType) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const tempText = `${temperature?.toFixed(1) || '--'}°C`;
        element.textContent = tempText;
        
        // Remove all temp classes
        element.className = element.className.replace(/temp-\w+/g, '').trim() + ' temp-value';
        
        if (temperature === null || temperature === undefined) return;
        
        // Apply color class based on temperature ranges
        let tempClass = '';
        
        if (sensorType === 'tank') {
            if (temperature < 20) tempClass = 'temp-cold';
            else if (temperature < 40) tempClass = 'temp-cool';
            else if (temperature < 60) tempClass = 'temp-normal';
            else if (temperature < 75) tempClass = 'temp-warm';
            else if (temperature < 85) tempClass = 'temp-hot';
            else tempClass = 'temp-critical';
        } else if (sensorType === 'collector') {
            if (temperature < 30) tempClass = 'temp-cold';
            else if (temperature < 50) tempClass = 'temp-cool';
            else if (temperature < 70) tempClass = 'temp-normal';
            else if (temperature < 90) tempClass = 'temp-warm';
            else if (temperature < 110) tempClass = 'temp-hot';
            else tempClass = 'temp-critical';
        } else if (sensorType === 'ambient') {
            if (temperature < 0) tempClass = 'temp-cold';
            else if (temperature < 15) tempClass = 'temp-cool';
            else if (temperature < 25) tempClass = 'temp-normal';
            else if (temperature < 30) tempClass = 'temp-warm';
            else tempClass = 'temp-hot';
        } else {
            // Default for heat exchanger and others
            if (temperature < 20) tempClass = 'temp-cold';
            else if (temperature < 40) tempClass = 'temp-cool';
            else if (temperature < 60) tempClass = 'temp-normal';
            else if (temperature < 75) tempClass = 'temp-warm';
            else tempClass = 'temp-hot';
        }
        
        element.classList.add(tempClass);
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

    async controlHeater(action, optimisticState) {
        if (!this.heaterToggle) {
            return;
        }

        if (!this.manualControlEnabled) {
            this.showNotification('Switch to Manual mode to control the heater', 'warning');
            this.updateHeaterToggle();
            return;
        }

        if (this.heaterPending || this.isHeaterLockedOut()) {
            const waitSeconds = this.getHeaterLockoutRemaining();
            if (waitSeconds > 0) {
                this.showNotification(`Please wait ${waitSeconds}s before toggling the heater`, 'warning');
            }
            this.updateHeaterToggle();
            return;
        }

        const friendlyAction = action === 'heater_start' ? 'start' : 'stop';
        this.heaterPending = true;
        this.heaterState = optimisticState;
        this.updateHeaterToggle();

        try {
            const response = await this.apiRequest('POST', '/control', { action });

            if (response.success) {
                const message = action === 'heater_start' ? 'Cartridge heater started' : 'Cartridge heater stopped';
                this.showNotification(message, 'success');
                this.startHeaterLockout(5);
                setTimeout(() => this.loadSystemData(), 1000);
            } else if (response.error_code) {
                throw response;
            } else {
                throw new Error(response.error || 'Heater control failed');
            }
        } catch (error) {
            console.error('Error controlling heater:', error);
            this.heaterState = !optimisticState;

            let message = `Failed to ${friendlyAction} heater`;
            const errorCode = error?.error_code;
            if (errorCode === 'MANUAL_CONTROL_REQUIRED') {
                message = 'Switch to Manual mode to control the heater';
                this.manualControlEnabled = false;
            } else if (errorCode === 'HEATER_TEMP_LIMIT') {
                message = error.error;
            } else if (errorCode === 'HEATER_LOCKOUT') {
                message = error.error;
                const waitSeconds = this.extractSeconds(error.error) || 5;
                this.startHeaterLockout(waitSeconds);
            } else if (error?.error) {
                message = error.error;
            } else if (error instanceof Error) {
                message = error.message;
            }
            this.showNotification(message, errorCode ? 'warning' : 'error');
        } finally {
            this.heaterPending = false;
            this.updateHeaterToggle();
        }
    }

    updateHeaterToggle() {
        const toggle = this.heaterToggle;
        if (!toggle) {
            return;
        }

        toggle.checked = this.heaterState;
        const lockout = this.isHeaterLockedOut();
        toggle.disabled = !this.manualControlEnabled || this.heaterPending || lockout;

        const hintElement = document.getElementById('heater-toggle-hint');
        if (!hintElement) {
            return;
        }

        if (!this.manualControlEnabled) {
            hintElement.textContent = 'Switch to Manual mode to enable heater control.';
            hintElement.className = 'heater-toggle-hint disabled';
        } else if (this.heaterPending) {
            hintElement.textContent = 'Sending heater command...';
            hintElement.className = 'heater-toggle-hint info';
        } else if (lockout) {
            const seconds = this.getHeaterLockoutRemaining();
            hintElement.textContent = `Cooldown in effect. Please wait ${seconds}s.`;
            hintElement.className = 'heater-toggle-hint warning';
        } else {
            const stateText = toggle.checked ? 'Heater is ON. Toggle to stop heating.' : 'Heater is OFF. Toggle to start heating.';
            hintElement.textContent = stateText;
            hintElement.className = 'heater-toggle-hint active';
        }
    }

    startHeaterLockout(seconds = 5) {
        this.heaterLockoutUntil = Date.now() + seconds * 1000;
        if (this.heaterLockoutTimer) {
            clearInterval(this.heaterLockoutTimer);
        }

        this.heaterLockoutTimer = setInterval(() => {
            if (!this.isHeaterLockedOut()) {
                clearInterval(this.heaterLockoutTimer);
                this.heaterLockoutTimer = null;
                this.updateHeaterToggle();
            } else {
                this.updateHeaterToggle();
            }
        }, 1000);
        this.updateHeaterToggle();
    }

    isHeaterLockedOut() {
        return Date.now() < this.heaterLockoutUntil;
    }

    getHeaterLockoutRemaining() {
        if (!this.isHeaterLockedOut()) {
            return 0;
        }
        return Math.max(0, Math.ceil((this.heaterLockoutUntil - Date.now()) / 1000));
    }

    extractSeconds(message) {
        if (!message) return null;
        const match = message.match(/(\d+)/);
        return match ? Number(match[1]) : null;
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
    
    // UX Fix #3: Add status dots to status indicators
    updateStatusWithDot(elementId, statusText, dotClass) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        // Create status dot if it doesn't exist
        let dotSpan = element.querySelector('.status-dot');
        if (!dotSpan) {
            dotSpan = document.createElement('span');
            dotSpan.className = 'status-dot';
            element.textContent = ''; // Clear existing text
            element.appendChild(dotSpan);
            const textSpan = document.createElement('span');
            element.appendChild(textSpan);
        }
        
        // Update dot class
        dotSpan.className = `status-dot ${dotClass}`;
        
        // Update text
        const textSpan = element.querySelector('span:not(.status-dot)');
        if (textSpan) {
            textSpan.textContent = statusText;
        }
    }

    // Heat Exchanger Efficiency Display (replaces temperature)
    updateEfficiencyElement(elementId, efficiency) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const effText = efficiency !== null && efficiency !== undefined ? `${efficiency.toFixed(1)}%` : '--%';
        element.textContent = effText;
        
        // Remove all temp/efficiency classes
        element.className = element.className.replace(/temp-\w+|eff-\w+/g, '').trim() + ' temp-value';
        
        if (efficiency === null || efficiency === undefined) return;
        
        // Apply color class based on efficiency ranges
        let effClass = '';
        if (efficiency < 30) effClass = 'eff-poor';          // 🔴 Poor
        else if (efficiency < 60) effClass = 'eff-fair';     // 🟡 Fair
        else if (efficiency < 80) effClass = 'eff-good';     // 🟢 Good
        else effClass = 'eff-excellent';                     // 💚 Excellent
        
        element.classList.add(effClass);
    }

    // Heat Exchanger Efficiency Detail with tooltip
    updateEfficiencyDetail(elementId, temperatures) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const eff = temperatures.heat_exchanger_efficiency;
        const outdoor = temperatures.outdoor_air_temp;
        const exhaust = temperatures.exhaust_air_temp;
        const supply = temperatures.supply_air_temp;
        const returnAir = temperatures.return_air_temp;
        
        if (eff !== null && eff !== undefined) {
            let emoji = '';
            let status = '';
            if (eff < 30) { emoji = '🔴'; status = 'Poor'; }
            else if (eff < 60) { emoji = '🟡'; status = 'Fair'; }
            else if (eff < 80) { emoji = '🟢'; status = 'Good'; }
            else { emoji = '💚'; status = 'Excellent'; }
            
            element.textContent = `${eff.toFixed(1)}% ${emoji}`;
            
            // Add tooltip with air temperatures if available
            if (outdoor !== null && returnAir !== null) {
                const heatGain = supply !== null ? (supply - outdoor).toFixed(1) : '--';
                const heatLoss = returnAir !== null && exhaust !== null ? (returnAir - exhaust).toFixed(1) : '--';
                
                element.title = `Heat Exchanger Efficiency: ${status}\n` +
                               `━━━━━━━━━━━━━━━━━━━━━━━━\n` +
                               `Outdoor Air: ${outdoor.toFixed(1)}°C\n` +
                               `Supply Air: ${supply?.toFixed(1) || '--'}°C (+${heatGain}°C)\n` +
                               `Return Air: ${returnAir.toFixed(1)}°C\n` +
                               `Exhaust Air: ${exhaust?.toFixed(1) || '--'}°C (-${heatLoss}°C)`;
            }
        } else {
            element.textContent = '-- %';
            element.title = '';
        }
    }

    // Heat Exchanger Efficiency Status
    updateEfficiencyStatus(sensorId, efficiency) {
        const statusElement = document.getElementById(`${sensorId}-status`);
        if (!statusElement) return;
        
        if (efficiency === null || efficiency === undefined) {
            statusElement.textContent = 'Unknown';
            return;
        }
        
        if (efficiency < 30) {
            statusElement.textContent = '🔴 Poor - Low heat recovery';
        } else if (efficiency < 60) {
            statusElement.textContent = '🟡 Fair - Moderate efficiency';
        } else if (efficiency < 80) {
            statusElement.textContent = '🟢 Good - Efficient operation';
        } else {
            statusElement.textContent = '💚 Excellent - Maximum efficiency';
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
