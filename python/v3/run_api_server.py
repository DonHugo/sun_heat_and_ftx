#!/usr/bin/env python3
"""
Standalone API Server for Solar Heating System v3
Issue #43: API Input Validation

This script runs the API server as a separate service that connects to
the main system via shared system state file or MQTT.

For now, it provides a mock interface for testing validation.
Full integration with main_system.py can be done later.
"""

import json
import logging
import sys
import time
from datetime import datetime
from flask import Flask
from api_server import create_api_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class MockSolarSystem:
    """
    Mock solar system for API testing
    This provides a minimal interface for the API server to work
    """
    def __init__(self):
        self.system_state = {
            'mode': 'manual',
            'primary_pump': False,
            'cartridge_heater': False,
            'test_mode': False,
            'manual_control': True,
            'last_update': time.time()
        }
        
        self.sensors = {
            'collector_out': 45.5,
            'collector_in': 42.0,
            'tank_top': 55.0,
            'tank_middle': 50.0,
            'tank_bottom': 45.0,
            'ambient': 20.0
        }
        
        logger.info("Mock solar system initialized")
    
    def get_sensor_value(self, sensor_name):
        """Get sensor value"""
        return self.sensors.get(sensor_name, 0.0)
    
    def set_pump_state(self, state):
        """Set pump state"""
        self.system_state['primary_pump'] = state
        logger.info(f"Pump state changed to: {state}")
        return True
    
    def set_system_mode(self, mode):
        """Set system mode"""
        valid_modes = ['auto', 'manual', 'eco']
        if mode in valid_modes:
            self.system_state['mode'] = mode
            self.system_state['manual_control'] = (mode == 'manual')
            logger.info(f"System mode changed to: {mode}")
            return True
        return False

def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info("Solar Heating API Server v3 - Standalone Mode")
    logger.info("Issue #43: API Input Validation Active")
    logger.info("="*60)
    
    # Create mock system
    mock_system = MockSolarSystem()
    
    # Create API server
    api_server = create_api_server(mock_system, host='0.0.0.0', port=5001)
    
    logger.info("Starting API server on http://0.0.0.0:5001")
    logger.info("API endpoints:")
    logger.info("  GET  /api/status")
    logger.info("  POST /api/control  (body: {\"action\": \"pump_start|pump_stop|emergency_stop\"})")
    logger.info("  POST /api/mode     (body: {\"mode\": \"auto|manual|eco\"})")
    logger.info("  GET  /api/temperatures")
    logger.info("  GET  /api/mqtt")
    logger.info("")
    logger.info("Pydantic validation is ACTIVE - Try these tests:")
    logger.info("  curl -X POST http://localhost:5001/api/control -H 'Content-Type: application/json' -d '{\"action\": \"pump_start\"}'")
    logger.info("  curl -X POST http://localhost:5001/api/control -H 'Content-Type: application/json' -d '{\"action\": \"invalid\"}'")
    logger.info("="*60)
    
    try:
        # Run the Flask app
        api_server.app.run(host='0.0.0.0', port=5001, debug=False)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"API server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

