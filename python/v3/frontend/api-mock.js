/**
 * Mock API for local development
 * Simulates the Flask API responses for faster UI iteration
 * 
 * Usage:
 * 1. Start a local web server: python3 -m http.server 8000
 * 2. Open: http://localhost:8000/python/v3/frontend/
 * 3. Dashboard will use mock data instead of real API
 */

const MockAPI = {
    // Track mock state
    state: {
        mode: 'auto',
        pump_running: true,
        heater_on: false,
        tank_temp: 39.1,
        collector_temp: 44.6,
        manual_mode: false,
        mqtt_connected: true,
        ha_connected: false,
        night_cooling_enabled: false,
        night_cooling_active: false,
        night_cooling_tank_temp: 80.0,
    },
    
    // Mock delay to simulate network latency
    delay: 200, // ms
    
    // Simulate API call with delay
    async mockFetch(endpoint, options = {}) {
        await new Promise(resolve => setTimeout(resolve, this.delay));
        
        const method = options.method || 'GET';
        console.log(`[MOCK API] ${method} ${endpoint}`, options.body || '');
        
        // Parse endpoint
        const path = endpoint.replace('/api', '');
        
        // Route to appropriate handler
        if (path === '/status') {
            return this.getStatus();
        } else if (path === '/temperatures') {
            return this.getTemperatures();
        } else if (path === '/mqtt') {
            return this.getMqtt();
        } else if (path === '/mode' && method === 'POST') {
            return this.setMode(JSON.parse(options.body));
        } else if (path === '/control' && method === 'POST') {
            return this.control(JSON.parse(options.body));
        } else if (path === '/control/pump' && method === 'POST') {
            return this.controlPump(JSON.parse(options.body));
        } else if (path === '/control/heater' && method === 'POST') {
            return this.controlHeater(JSON.parse(options.body));
        }
        
        return {
            ok: false,
            status: 404,
            json: async () => ({ error: `Mock API endpoint not found: ${path}` })
        };
    },
    
    // API Endpoints
    getStatus() {
        return {
            ok: true,
            status: 200,
            json: async () => ({
                success: true,
                system_state: {
                    mode: this.state.mode,
                    primary_pump: this.state.pump_running,
                    primary_pump_manual: this.state.manual_mode,
                    cartridge_heater: this.state.heater_on,
                    night_cooling_enabled: this.state.night_cooling_enabled,
                    night_cooling_active: this.state.night_cooling_active,
                    night_cooling_tank_temp: this.state.night_cooling_tank_temp,
                },
                status: this.state.pump_running ? 'Operating Normally' : 'Idle',
                energy_status: this.state.pump_running ? 'Collecting' : 'Standby',
            })
        };
    },
    
    getTemperatures() {
        // Simulate slight temperature variations
        const variation = () => (Math.random() - 0.5) * 0.2;
        
        return {
            ok: true,
            status: 200,
            json: async () => ({
                success: true,
                temperatures: {
                    storage_tank: this.state.tank_temp + variation(),
                    solar_collector: this.state.collector_temp + variation(),
                    rtd_sensor_0: 35.2 + variation(),
                    rtd_sensor_1: 36.8 + variation(),
                    rtd_sensor_2: 38.1 + variation(),
                    rtd_sensor_3: this.state.tank_temp + variation(),
                    rtd_sensor_4: 42.3 + variation(),
                    rtd_sensor_5: this.state.collector_temp + variation(),
                    rtd_sensor_6: 15.8 + variation(),
                    rtd_sensor_7: 16.2 + variation(),
                }
            })
        };
    },
    
    getMqtt() {
        return {
            ok: true,
            status: 200,
            json: async () => ({
                success: true,
                mqtt_connected: this.state.mqtt_connected,
                home_assistant_connected: this.state.ha_connected,
            })
        };
    },
    
    setMode(data) {
        const validModes = ['auto', 'manual', 'heating'];
        if (!validModes.includes(data.mode)) {
            return {
                ok: false,
                status: 400,
                json: async () => ({
                    success: false,
                    error: `Invalid mode: ${data.mode}`
                })
            };
        }
        
        this.state.mode = data.mode;
        this.state.manual_mode = (data.mode === 'manual');
        
        console.log(`[MOCK] Mode changed to: ${data.mode}`);
        
        return {
            ok: true,
            status: 200,
            json: async () => ({
                success: true,
                message: `Mode set to ${data.mode}`,
                mode: data.mode
            })
        };
    },
    
    // Action-based /control endpoint (mirrors the real Flask API)
    control(data) {
        const action = data.action;

        if (action === 'night_cooling_on' || action === 'night_cooling_off') {
            const enable = action === 'night_cooling_on';
            this.state.night_cooling_enabled = enable;
            if (!enable) {
                this.state.night_cooling_active = false;
            }
            console.log(`[MOCK] Night cooling ${enable ? 'enabled' : 'disabled'}`);
            return {
                ok: true,
                status: 200,
                json: async () => ({
                    success: true,
                    message: `Night cooling ${enable ? 'enabled' : 'disabled'}`,
                    system_state: {
                        night_cooling_enabled: enable,
                        night_cooling_active: this.state.night_cooling_active,
                    }
                })
            };
        }

        if (action === 'night_cooling_set_temp') {
            const value = data.value;
            if (value === undefined || value === null || value < 50 || value > 95) {
                return {
                    ok: false,
                    status: 200,
                    json: async () => ({
                        success: false,
                        error: 'Tank threshold must be between 50 and 95°C',
                        error_code: 'VALUE_OUT_OF_RANGE'
                    })
                };
            }
            this.state.night_cooling_tank_temp = value;
            console.log(`[MOCK] Night cooling threshold set to ${value}°C`);
            return {
                ok: true,
                status: 200,
                json: async () => ({
                    success: true,
                    message: `Night cooling tank threshold set to ${value.toFixed(1)}°C`,
                    system_state: { night_cooling_tank_temp: value }
                })
            };
        }

        // Pump/heater actions delegate to existing handlers
        if (action === 'pump_start' || action === 'pump_stop') {
            return this.controlPump({ action: action.replace('pump_', '') });
        }
        if (action === 'heater_start' || action === 'heater_stop') {
            return this.controlHeater({ action });
        }

        return {
            ok: false,
            status: 200,
            json: async () => ({ success: false, error: `Unknown action: ${action}` })
        };
    },
    
    controlPump(data) {
        // In auto mode, reject pump control
        if (!this.state.manual_mode && this.state.mode !== 'manual') {
            return {
                ok: false,
                status: 400,
                json: async () => ({
                    success: false,
                    error: 'Pump control only available in manual mode'
                })
            };
        }
        
        if (data.action === 'start') {
            this.state.pump_running = true;
            console.log('[MOCK] Pump started');
        } else if (data.action === 'stop') {
            this.state.pump_running = false;
            console.log('[MOCK] Pump stopped');
        }
        
        return {
            ok: true,
            status: 200,
            json: async () => ({
                success: true,
                message: `Pump ${data.action}ed`,
                pump_running: this.state.pump_running
            })
        };
    },
    
    controlHeater(data) {
        // Heater works in both auto and manual modes
        if (data.action === 'heater_start') {
            // Simulate temperature check
            if (this.state.tank_temp >= 80) {
                return {
                    ok: false,
                    status: 400,
                    json: async () => ({
                        success: false,
                        error: 'Tank temperature too high (80°C limit)'
                    })
                };
            }
            
            this.state.heater_on = true;
            console.log('[MOCK] Heater started');
        } else if (data.action === 'heater_stop') {
            this.state.heater_on = false;
            console.log('[MOCK] Heater stopped');
        }
        
        return {
            ok: true,
            status: 200,
            json: async () => ({
                success: true,
                message: `Heater ${data.action === 'heater_start' ? 'started' : 'stopped'}`,
                heater_on: this.state.heater_on
            })
        };
    },
    
    // Simulate temperature changes over time
    startSimulation() {
        setInterval(() => {
            // If pump is running, slowly equalize temperatures
            if (this.state.pump_running) {
                const diff = this.state.collector_temp - this.state.tank_temp;
                if (diff > 0.5) {
                    this.state.tank_temp += 0.1;
                    this.state.collector_temp -= 0.05;
                }
            }
            
            // If heater is on, increase tank temp
            if (this.state.heater_on) {
                this.state.tank_temp += 0.2;
                if (this.state.tank_temp >= 80) {
                    this.state.heater_on = false; // Safety cutoff
                    console.log('[MOCK] Heater auto-stopped at 80°C');
                }
            }
            
            // Natural cooling
            if (!this.state.heater_on && !this.state.pump_running) {
                this.state.tank_temp -= 0.05;
            }
            
            // Collector temperature varies with "sunlight"
            this.state.collector_temp += (Math.random() - 0.5) * 0.3;
            
            // Keep temps in reasonable range
            this.state.tank_temp = Math.max(15, Math.min(85, this.state.tank_temp));
            this.state.collector_temp = Math.max(10, Math.min(95, this.state.collector_temp));

            // Simulate night cooling: active when enabled, tank >= threshold,
            // and collector is at least 5°C colder than the tank.
            if (this.state.night_cooling_enabled) {
                const dt = this.state.tank_temp - this.state.collector_temp;
                if (this.state.tank_temp >= this.state.night_cooling_tank_temp && dt >= 5) {
                    this.state.night_cooling_active = true;
                    this.state.pump_running = true;
                    // Cooling effect: tank slowly loses heat via the collector
                    this.state.tank_temp -= 0.15;
                } else if (this.state.night_cooling_active &&
                           (this.state.tank_temp < (this.state.night_cooling_tank_temp - 5) || dt < 5)) {
                    this.state.night_cooling_active = false;
                }
            } else {
                this.state.night_cooling_active = false;
            }
        }, 2000); // Update every 2 seconds
    }
};

// Start simulation
MockAPI.startSimulation();

// Export for use in dashboard
window.MockAPI = MockAPI;

console.log('🔧 Mock API loaded - Local development mode active');
console.log('📊 Initial state:', MockAPI.state);
