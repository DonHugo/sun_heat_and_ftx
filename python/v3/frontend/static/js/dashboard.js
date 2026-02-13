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
        this.pumpToggle = null;
        this.manualControlEnabled = false;
        this.heaterState = false;
        this.heaterPending = false;
        this.pumpState = false;
        this.heaterLockoutUntil = 0;
        this.heaterLockoutTimer = null;
        this.init();
    }
    
    async init() {
        try {
        console.log('🌞 Solar Heating Dashboard v3 - Initializing...');
        
        // Load configuration first
        await this.loadConfig();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup sidebar navigation (replaces tab navigation)
        this.setupTabNavigation();
        
        // Setup sidebar toggle for mobile
        this.setupSidebarToggle();
        
        // Initial data load
        await this.loadSystemData();
        
        // Start auto-update
        this.startAutoUpdate();
        
        console.log('✅ Dashboard initialized successfully');
        
        // Hide loading overlay after initial load
        } catch (error) {
            console.error("❌ Dashboard initialization failed:", error);
            this.showNotification("Failed to initialize dashboard. Please refresh the page.", "error");
        } finally {
        this.hideLoading();
        }
    }
    
    async loadConfig() {
        try {
            // Use relative API URL that works through nginx proxy
            // This allows the dashboard to work from any device on the network
            this.apiBaseUrl = '/api';
            this.updateInterval = 5000; // 5 seconds
            
            console.log('Configuration loaded (using nginx proxy)');
            console.log('API Base URL:', this.apiBaseUrl);
            
            this.configLoaded = true;
        } catch (error) {
            console.error('Failed to load configuration:', error);
            // Still use relative URL as fallback
            this.apiBaseUrl = '/api';
            this.configLoaded = true;
        }
    }
    
    setupEventListeners() {
        // Pump toggle control
        this.pumpToggle = document.getElementById('pump-toggle');
        if (this.pumpToggle) {
            this.pumpToggle.addEventListener('change', (e) => {
                const checked = e.target.checked;
                const action = checked ? 'start' : 'stop';
                this.controlPump(action, checked);
            });
        }
        
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
        // Updated to use .sidebar-link instead of .tab-button
        const sidebarLinks = document.querySelectorAll('.sidebar-link');
        const tabContents = document.querySelectorAll('.tab-content');
        
        sidebarLinks.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                
                // Remove active class from all buttons and contents
                sidebarLinks.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked button and corresponding content
                button.classList.add('active');
                document.getElementById(targetTab)?.classList.add('active');
                
                // Close sidebar on mobile after selecting a tab
                if (window.innerWidth <= 768) {
                    const sidebar = document.getElementById('sidebar');
                    if (sidebar) {
                        sidebar.classList.remove('open');
                    }
                }
            });
        });
    }
    
    setupSidebarToggle() {
        const sidebar = document.getElementById('sidebar');
        
        // Hamburger button click (via CSS body::before on mobile)
        // We detect clicks in the hamburger area when sidebar is closed
        document.body.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && sidebar) {
                // Hamburger is positioned at top-left (20px from edges)
                // CSS creates a 50x50px clickable area
                const rect = { left: 20, top: 20, right: 70, bottom: 70 };
                if (e.clientX >= rect.left && e.clientX <= rect.right &&
                    e.clientY >= rect.top && e.clientY <= rect.bottom &&
                    !sidebar.classList.contains('open')) {
                    sidebar.classList.add('open');
                    e.stopPropagation();
                }
            }
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && sidebar && sidebar.classList.contains('open')) {
                if (!sidebar.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            }
        });
    }
    
    async loadSystemData() {
        console.log("📊 loadSystemData() called - isLoading:", this.isLoading, "configLoaded:", this.configLoaded);
        if (this.isLoading || !this.configLoaded) return;
        
        this.isLoading = true;
        
        try {
            // Load system status
            console.log("🔄 Fetching /status...");
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
            console.error("❌ Error details:", error.message, error.stack);
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
        
        // Check if MockAPI is available (local development mode)
        if (window.MockAPI) {
            console.log(`[DEV MODE] Using Mock API for: ${method} ${endpoint}`);
            return window.MockAPI.mockFetch(endpoint, {
                method: method,
                body: data ? JSON.stringify(data) : null
            }).then(response => response.json());
        }
        
        // Production mode - use real API
        const url = `${this.apiBaseUrl}${endpoint}`;
        console.log(`📡 API Request: ${method} ${url}`);
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
        console.log(`📡 API Response: ${response.status} ${response.statusText}`);
        
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
        this.updateHeaterToggleWithTimer();
        
        // Update pump toggle state
        const actualPumpState = Boolean(data.system_state?.primary_pump);
        this.pumpState = actualPumpState;
        this.updatePumpToggle();
        
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
        
        // Update Status tab fields (pump runtime, heater runtime/energy, timestamps)
        const state = data.system_state || {};
        
        // Helper function to format numbers
        const fmt = (val, decimals = 1, unit = "") => {
            if (val === null || val === undefined || isNaN(val)) return "--";
            return `${Number(val).toFixed(decimals)}${unit}`;
        };
        
        // Helper function to format timestamps
        const formatTimestamp = (timestamp) => {
            if (!timestamp || timestamp === null) return "--";
            try {
                const date = new Date(timestamp * 1000); // Convert Unix timestamp to milliseconds
                return date.toLocaleString();
            } catch (e) {
                return "--";
            }
        };
        
        // Update pump runtime
        const pumpRuntime = state.pump_runtime_hours || 0;
        const pumpRuntimeEl = document.getElementById("pump-runtime");
        if (pumpRuntimeEl) {
            pumpRuntimeEl.textContent = fmt(pumpRuntime, 2, " hours");
        }
        
        // Update pump last change (use last_pump_start timestamp)
        const pumpLastChange = state.last_pump_start ? formatTimestamp(state.last_pump_start) : "Never";
        const pumpLastChangeEl = document.getElementById("pump-last-change");
        if (pumpLastChangeEl) {
            pumpLastChangeEl.textContent = pumpLastChange;
        }
        
        // Update pump control mode
        const pumpMode = state.primary_pump_manual ? "Manual" : "Automatic";
        const pumpModeEl = document.getElementById("control-pump-mode");
        if (pumpModeEl) {
            pumpModeEl.textContent = pumpMode;
        }
        
        // Update heater runtime
        const heaterRuntime = state.total_heating_time || 0;
        const heaterRuntimeEl = document.getElementById("heater-runtime");
        if (heaterRuntimeEl) {
            heaterRuntimeEl.textContent = fmt(heaterRuntime, 2, " hours");
        }
        
        // Update heater energy
        const heaterEnergy = state.cartridge_energy_today || 0;
        const heaterEnergyEl = document.getElementById("heater-energy");
        if (heaterEnergyEl) {
            heaterEnergyEl.textContent = fmt(heaterEnergy, 2, " kWh");
        }
        
        // Update heater last active (we don't have this timestamp in API yet, show "Never")
        const heaterLastActiveEl = document.getElementById("heater-last-active");
        if (heaterLastActiveEl) {
            heaterLastActiveEl.textContent = "Never";
        }
        
        // Update mode last change (we don't have this timestamp in API yet, show "Never")
        const modeLastChangeEl = document.getElementById("mode-last-change");
        if (modeLastChangeEl) {
            modeLastChangeEl.textContent = "Never";
        }
        
        // Update manual control status
        const manualStatus = state.manual_control ? "Enabled" : "Disabled";
        const manualStatusEl = document.getElementById("control-manual-status");
        if (manualStatusEl) {
            manualStatusEl.textContent = manualStatus;
        }
        
        // Update auto control active status
        const autoControlActive = !state.manual_control ? "Yes" : "No";
        const autoControlEl = document.getElementById("auto-control-active");
        if (autoControlEl) {
            autoControlEl.textContent = autoControlActive;
        }
        
        // Update hero card
        this.updateHeroCard(data);
        
        // Update energy card
        this.updateEnergyCard(data);
        
        // Update systems tab
        this.updateSystemsTab(data);
    }

    // Update Systems tab with subsystem details
    updateSystemsTab(data) {
        const temps = data.temperatures || {};
        const state = data.system_state || {};
        
        // Helper function to safely format numbers
        const fmt = (val, decimals = 1, unit = '°C') => {
            if (val === null || val === undefined || isNaN(val)) return '--';
            return `${Number(val).toFixed(decimals)}${unit}`;
        };
        
        // Helper function to update element text content
        const updateEl = (id, text) => {
            const el = document.getElementById(id);
            if (el) el.textContent = text;
        };
        
        // ==================================================================
        // SOLAR HEATING SYSTEM
        // ==================================================================
        const solarCollector = temps.solar_collector_temp || temps.solar_collector || 0;
        const solarTank = temps.storage_tank_temp || temps.tank || 0;
        const solarDt = solarCollector - solarTank;
        const solarPump = state.primary_pump || false;
        const solarEnergy = state.solar_energy_today || 0;
        
        updateEl('sys-solar-collector', fmt(solarCollector));
        updateEl('sys-solar-tank', fmt(solarTank));
        updateEl('sys-solar-dt', fmt(solarDt, 1, '°C'));
        
        const solarPumpBadge = document.getElementById('sys-solar-pump');
        if (solarPumpBadge) {
            solarPumpBadge.textContent = solarPump ? 'ON' : 'OFF';
            solarPumpBadge.className = `metric-value status-badge ${solarPump ? 'on' : 'off'}`;
        }
        
        updateEl('sys-solar-energy', fmt(solarEnergy, 2, ' kWh'));
        
        // Animate solar flow when pump is on and dT > 5
        const solarFlow = document.getElementById('sys-solar-flow');
        if (solarFlow) {
            if (solarPump && solarDt > 5) {
                solarFlow.classList.add('active');
            } else {
                solarFlow.classList.remove('active');
            }
        }
        
        // ==================================================================
        // CARTRIDGE HEATER
        // ==================================================================
        const heaterOn = state.cartridge_heater || false;
        const heaterPower = state.cartridge_energy_hour || 0; // kW rate
        const heaterEnergyToday = state.cartridge_energy_today || 0;
        const heaterRuntime = state.total_heating_time || 0; // hours
        
        const heaterStatusBadge = document.getElementById('sys-heater-status');
        if (heaterStatusBadge) {
            heaterStatusBadge.textContent = heaterOn ? 'ON' : 'OFF';
            heaterStatusBadge.className = `metric-value status-badge ${heaterOn ? 'on' : 'off'}`;
        }
        
        updateEl('sys-heater-power', fmt(heaterPower, 2, ' kW'));
        updateEl('sys-heater-energy-today', fmt(heaterEnergyToday, 2, ' kWh'));
        updateEl('sys-heater-runtime', fmt(heaterRuntime, 2, ' h'));
        
        // Update power bar (0-3kW scale)
        const heaterBar = document.getElementById('sys-heater-bar');
        if (heaterBar) {
            const percentage = Math.min(100, (heaterPower / 3.0) * 100);
            heaterBar.style.width = `${percentage}%`;
        }
        
        // ==================================================================
        // ==================================================================
        // WATER HEATER TANK (8 sensors)
        // ==================================================================
        const storedEnergy = temps.stored_energy_kwh || 0;
        updateEl('sys-tank-energy', fmt(storedEnergy, 2, ' kWh'));
        
        // Update all 8 tank temperature sensors
        const tankSensors = [
            { height: 140, key: 'water_heater_140cm' },
            { height: 120, key: 'water_heater_120cm' },
            { height: 100, key: 'water_heater_100cm' },
            { height: 80, key: 'water_heater_80cm' },
            { height: 60, key: 'water_heater_60cm' },
            { height: 40, key: 'water_heater_40cm' },
            { height: 20, key: 'water_heater_20cm' },
            { height: 0, key: 'water_heater_bottom' }
        ];
        
        const getColorClass = (temp) => {
            if (temp < 40) return 'cold';
            if (temp < 60) return 'warm';
            return 'hot';
        };
        
        tankSensors.forEach(sensor => {
            const temp = temps[sensor.key] || 0;
            const tempEl = document.getElementById(`sys-tank-${sensor.height}`);
            const levelEl = document.getElementById(`sys-tank-level-${sensor.height}`);
            
            if (tempEl) {
                updateEl(`sys-tank-${sensor.height}`, fmt(temp));
            }
            if (levelEl) {
                levelEl.className = `tank-level ${getColorClass(temp)}`;
            }
        });
        
        // FTX VENTILATION
        // ==================================================================
        const outdoorTemp = temps.outdoor_air_temp || 0;
        const supplyTemp = temps.supply_air_temp || 0;
        const exhaustTemp = temps.exhaust_air_temp || 0;
        const returnTemp = temps.return_air_temp || 0;
        
        updateEl('sys-ftx-outdoor', fmt(outdoorTemp));
        updateEl('sys-ftx-supply', fmt(supplyTemp));
        updateEl('sys-ftx-exhaust', fmt(exhaustTemp));
        updateEl('sys-ftx-return', fmt(returnTemp));
        
        // Calculate heat recovery as temperature delta (Return - Exhaust)
        // This shows actual heat extracted from return air
        let heatRecovery = 0;
        let recoveryIndicator = '';
        if (returnTemp !== null && exhaustTemp !== null) {
            heatRecovery = returnTemp - exhaustTemp;
            
            // Status indicator based on recovery amount
            if (heatRecovery < 5) { recoveryIndicator = '<span class="status-dot status-poor"></span>'; }
            else if (heatRecovery < 10) { recoveryIndicator = '<span class="status-dot status-fair"></span>'; }
            else if (heatRecovery < 15) { recoveryIndicator = '<span class="status-dot status-good"></span>'; }
            else { recoveryIndicator = '<span class="status-dot status-excellent"></span>'; }
        }
        
        // Display as temperature delta with status indicator
        const effElement = document.getElementById('sys-ftx-efficiency');
        if (effElement) {
            effElement.innerHTML = heatRecovery > 0 ? `${heatRecovery.toFixed(1)}°C ${recoveryIndicator}` : '-- °C';
        }
        updateEl('sys-ftx-efficiency-inline', heatRecovery > 0 ? `${heatRecovery.toFixed(1)}°C` : '--');
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
    
    // Update energy summary card
    updateEnergyCard(data) {
        // Extract energy data from API response
        const solarDaily = data.system_state?.solar_energy_today ?? 0;
        const heaterDaily = data.system_state?.cartridge_energy_today ?? 0;
        const pelletDaily = data.system_state?.pellet_energy_today ?? 0;
        
        const solarRate = data.system_state?.solar_energy_hour ?? 0;
        const heaterOn = data.system_state?.cartridge_heater ?? false;
        const heaterRate = heaterOn ? (data.system_state?.cartridge_energy_hour ?? 0) : 0;
        const pelletStoveOn = data.system_state?.pellet_stove_status ?? false;
        const pelletRate = pelletStoveOn ? (data.system_state?.pellet_energy_hour ?? 0) : 0;
        
        // Calculate total energy
        const totalEnergy = solarDaily + heaterDaily + pelletDaily;
        
        // Update total energy display
        const totalElement = document.getElementById('energy-total');
        if (totalElement) {
            totalElement.textContent = totalEnergy.toFixed(1);
        }
        
        // Update solar energy
        const solarDailyElement = document.getElementById('energy-solar-daily');
        const solarRateElement = document.getElementById('energy-solar-rate');
        if (solarDailyElement) solarDailyElement.textContent = solarDaily.toFixed(1);
        if (solarRateElement) solarRateElement.textContent = solarRate.toFixed(2);
        
        // Update heater energy
        const heaterDailyElement = document.getElementById('energy-heater-daily');
        const heaterRateElement = document.getElementById('energy-heater-rate');
        if (heaterDailyElement) heaterDailyElement.textContent = heaterDaily.toFixed(1);
        if (heaterRateElement) heaterRateElement.textContent = heaterRate.toFixed(2);
        
        // Update pellet energy
        const pelletDailyElement = document.getElementById('energy-pellet-daily');
        const pelletRateElement = document.getElementById('energy-pellet-rate');
        if (pelletDailyElement) pelletDailyElement.textContent = pelletDaily.toFixed(1);
        if (pelletRateElement) pelletRateElement.textContent = pelletRate.toFixed(2);
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
    
    async controlPump(action, optimisticState = null) {
        // Optimistically update toggle if state provided
        const pumpToggle = document.getElementById('pump-toggle');
        const prevToggleState = pumpToggle ? pumpToggle.checked : null;
        
        if (optimisticState !== null && pumpToggle) {
            pumpToggle.checked = optimisticState;
        }
        
        try {
            const apiAction = action === 'start' ? 'pump_start' : 'pump_stop';
            const response = await this.apiRequest('POST', '/control', {
                action: apiAction
            });
            
            if (response && response.success) {
                this.showNotification(response.message || `Pump ${action}ed successfully`, 'success');
                
                // Update toggle to match actual state
                if (pumpToggle && response.system_state) {
                    pumpToggle.checked = response.system_state.primary_pump || false;
                }
                
                // Refresh system state
                this.loadSystemData();
            } else {
                throw new Error(response?.error || 'Control failed');
            }
        } catch (error) {
            console.error(`Error controlling pump:`, error);
            this.showNotification(error.message || `Failed to ${action} pump`, 'error');
            
            // Revert toggle on error
            if (prevToggleState !== null && pumpToggle) {
                pumpToggle.checked = prevToggleState;
            }
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


        if (this.heaterPending || this.isHeaterLockedOut()) {
            const waitSeconds = this.getHeaterLockoutRemaining();
            if (waitSeconds > 0) {
                this.showNotification(`Please wait ${waitSeconds}s before toggling the heater`, 'warning');
            }
            this.updateHeaterToggleWithTimer();
            return;
        }

        const friendlyAction = action === 'heater_start' ? 'start' : 'stop';
        this.heaterPending = true;
        this.heaterState = optimisticState;
        this.updateHeaterToggleWithTimer();

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
            this.updateHeaterToggleWithTimer();
        }
    }

    updateHeaterToggle() {
        const toggle = this.heaterToggle;
        if (!toggle) {
            return;
        }

        toggle.checked = this.heaterState;
        const lockout = this.isHeaterLockedOut();
        toggle.disabled = this.heaterPending || lockout;

        const hintElement = document.getElementById('heater-toggle-hint');
        if (!hintElement) {
            return;
        }

        if (this.heaterPending) {
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

    updatePumpToggle() {
        const toggle = this.pumpToggle;
        if (!toggle) {
            return;
        }

        // Always update toggle to match actual pump state
        toggle.checked = this.pumpState;
        
        // Disable toggle in auto mode (not manual)
        toggle.disabled = !this.manualControlEnabled;
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
                this.updateHeaterToggleWithTimer();
            } else {
                this.updateHeaterToggleWithTimer();
            }
        }, 1000);
        this.updateHeaterToggleWithTimer();
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
        if (efficiency < 30) effClass = 'eff-poor';          // Poor
        else if (efficiency < 60) effClass = 'eff-fair';     // Fair
        else if (efficiency < 80) effClass = 'eff-good';     // Good
        else effClass = 'eff-excellent';                     // Excellent
        
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
            let statusIndicator = '';
            let status = '';
            if (eff < 30) { statusIndicator = '<span class="status-dot status-poor"></span>'; status = 'Poor'; }
            else if (eff < 60) { statusIndicator = '<span class="status-dot status-fair"></span>'; status = 'Fair'; }
            else if (eff < 80) { statusIndicator = '<span class="status-dot status-good"></span>'; status = 'Good'; }
            else { statusIndicator = '<span class="status-dot status-excellent"></span>'; status = 'Excellent'; }
            
            element.innerHTML = `${eff.toFixed(1)}% ${statusIndicator}`;
            
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
            statusElement.innerHTML = '<span class="status-dot status-poor"></span> Poor - Low heat recovery';
        } else if (efficiency < 60) {
            statusElement.innerHTML = '<span class="status-dot status-fair"></span> Fair - Moderate efficiency';
        } else if (efficiency < 80) {
            statusElement.innerHTML = '<span class="status-dot status-good"></span> Good - Efficient operation';
        } else {
            statusElement.innerHTML = '<span class="status-dot status-excellent"></span> Excellent - Maximum efficiency';
        }
    }
    updateHeaterToggleWithTimer() {
        const toggle = this.heaterToggle;
        if (!toggle) {
            return;
        }

        toggle.checked = this.heaterState;
        const lockout = this.isHeaterLockedOut();
        toggle.disabled = this.heaterPending || lockout;

        const hintElement = document.getElementById('heater-toggle-hint');
        const timerElement = document.getElementById('heater-lockout-timer');
        const countdownElement = document.getElementById('lockout-timer-countdown');
        
        if (!hintElement) {
            return;
        }

        // Show/hide lockout timer
        if (lockout && timerElement) {
            timerElement.classList.add('active');
            const seconds = this.getHeaterLockoutRemaining();
            if (countdownElement) {
                const mins = Math.floor(seconds / 60);
                const secs = seconds % 60;
                countdownElement.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
            }
        } else if (timerElement) {
            timerElement.classList.remove('active');
        }

        // Update hint text
        if (this.heaterPending) {
            hintElement.textContent = 'Sending heater command...';
            hintElement.className = 'heater-toggle-hint info';
        } else if (lockout) {
            const seconds = this.getHeaterLockoutRemaining();
            hintElement.textContent = `Please wait for cooldown to complete`;
            hintElement.className = 'heater-toggle-hint warning';
        } else {
            const stateText = toggle.checked ? 'Heater is ON. Toggle to stop heating.' : 'Heater is OFF. Toggle to start heating.';
            hintElement.textContent = stateText;
            hintElement.className = 'heater-toggle-hint active';
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
