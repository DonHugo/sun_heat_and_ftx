#!/usr/bin/env python3
"""
Web Server for Solar Heating System v3 GUI
Serves the frontend dashboard and provides API endpoints
This runs as a standalone service that can operate even if MQTT/HA are down
"""

import os
import sys
import logging
import threading
import time
from flask import Flask, send_from_directory, jsonify
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent
FRONTEND_DIR = SCRIPT_DIR / 'frontend'
STATIC_DIR = FRONTEND_DIR / 'static'

# Check if running on Raspberry Pi (production) or development
def is_raspberry_pi():
    """Check if running on Raspberry Pi"""
    try:
        # Check /proc/device-tree/model first (most reliable)
        try:
            with open('/proc/device-tree/model', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            pass
        
        # Fallback to /proc/cpuinfo (older method)
        with open('/proc/cpuinfo', 'r') as f:
            content = f.read()
            return 'BCM' in content or 'Raspberry Pi' in content
    except:
        return False


IS_PRODUCTION = is_raspberry_pi()

class SolarHeatingWebServer:
    """Web server for Solar Heating System GUI"""
    
    def __init__(self, host='0.0.0.0', port=8080, api_port=5001):
        """
        Initialize web server
        
        Args:
            host: Server host (default: 0.0.0.0 for all interfaces)
            port: Web server port (default: 8080)
            api_port: API server port (default: 5001)
        """
        self.host = host
        self.port = port
        self.api_port = api_port
        self.app = Flask(__name__, 
                        static_folder=str(STATIC_DIR),
                        template_folder=str(FRONTEND_DIR))
        
        # Check if frontend files exist
        if not FRONTEND_DIR.exists():
            logger.error(f"Frontend directory not found: {FRONTEND_DIR}")
            logger.error("Please make sure the frontend files are in the correct location")
            sys.exit(1)
        
        logger.info(f"Frontend directory: {FRONTEND_DIR}")
        logger.info(f"Static directory: {STATIC_DIR}")
        
        # Setup routes
        self._setup_routes()
        
        # CORS support
        self._setup_cors()
    
    def _setup_routes(self):
        """Setup web server routes"""
        
        # Serve the main dashboard
        @self.app.route('/')
        def index():
            return send_from_directory(str(FRONTEND_DIR), 'index.html')
        
        # Serve static files
        @self.app.route('/static/<path:path>')
        def serve_static(path):
            return send_from_directory(str(STATIC_DIR), path)
        
        # Health check endpoint
        @self.app.route('/health')
        def health():
            return jsonify({
                'status': 'ok',
                'service': 'solar_heating_web_gui',
                'api_port': self.api_port,
                'production': IS_PRODUCTION
            })
        
        # System info endpoint (for frontend configuration)
        @self.app.route('/api/config')
        def api_config():
            """Provide configuration to frontend"""
            # In production (Raspberry Pi), use the local hostname
            # In development, use localhost
            if IS_PRODUCTION:
                api_base_url = f"http://{os.uname().nodename}:{self.api_port}/api"
            else:
                api_base_url = f"http://localhost:{self.api_port}/api"
            
            return jsonify({
                'api_base_url': api_base_url,
                'api_port': self.api_port,
                'update_interval': 5000,  # 5 seconds
                'production': IS_PRODUCTION
            })
    
    def _setup_cors(self):
        """Setup CORS for API access"""
        @self.app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
    
    def start(self):
        """Start the web server"""
        logger.info("="*70)
        logger.info("☀️  Solar Heating System v3 - Web Dashboard")
        logger.info("="*70)
        logger.info(f"Environment: {'PRODUCTION (Raspberry Pi)' if IS_PRODUCTION else 'DEVELOPMENT'}")
        logger.info(f"Frontend directory: {FRONTEND_DIR}")
        logger.info(f"Web GUI: http://{self.host if self.host != '0.0.0.0' else 'localhost'}:{self.port}")
        logger.info(f"API Server: http://localhost:{self.api_port}")
        logger.info("")
        logger.info("Available URLs:")
        logger.info(f"  • Dashboard: http://localhost:{self.port}/")
        logger.info(f"  • Health Check: http://localhost:{self.port}/health")
        logger.info(f"  • API Config: http://localhost:{self.port}/api/config")
        logger.info("")
        logger.info("Note: Make sure the API server is running on port " + str(self.api_port))
        logger.info("      Run: python3 run_api_server.py")
        logger.info("="*70)
        
        try:
            self.app.run(host=self.host, port=self.port, debug=False, threaded=True)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Web server error: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Solar Heating Web GUI Server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--api-port', type=int, default=5001, help='API server port (default: 5001)')
    
    args = parser.parse_args()
    
    # Create and start web server
    web_server = SolarHeatingWebServer(
        host=args.host,
        port=args.port,
        api_port=args.api_port
    )
    
    web_server.start()

if __name__ == "__main__":
    main()
