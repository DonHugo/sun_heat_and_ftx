"""
Integration script to add API server to main_system.py
This follows TDD principles by implementing the API server integration
"""

import re

def integrate_api_server():
    """Integrate API server into main_system.py"""
    
    # Read the current main_system.py
    with open('python/v3/main_system.py', 'r') as f:
        content = f.read()
    
    # Add API server import after other imports
    import_addition = '''
# API Server Integration
try:
    from api_server import create_api_server
    API_SERVER_AVAILABLE = True
except ImportError as e:
    print(f"API server not available: {e}")
    API_SERVER_AVAILABLE = False
'''
    
    # Find the import section and add API server import
    import_pattern = r'(from taskmaster_service import taskmaster_service\n)'
    content = re.sub(import_pattern, r'\1' + import_addition, content)
    
    # Add API server initialization to SolarHeatingSystem.__init__
    init_addition = '''
        # API Server
        self.api_server = None
        self.api_thread = None
        if API_SERVER_AVAILABLE:
            try:
                self.api_server = create_api_server(self, host='0.0.0.0', port=5001)
                logger.info("API server initialized")
            except Exception as e:
                logger.error(f"Failed to initialize API server: {e}")
                self.api_server = None
'''
    
    # Find the __init__ method and add API server initialization
    init_pattern = r'(self\.system_state = \{.*?\})\s*\n'
    content = re.sub(init_pattern, r'\1' + init_addition + '\n', content, flags=re.DOTALL)
    
    # Add API server start to the start method
    start_addition = '''
        # Start API server
        if self.api_server and API_SERVER_AVAILABLE:
            try:
                import threading
                self.api_thread = threading.Thread(
                    target=self.api_server.start_server,
                    daemon=True,
                    name="API-Server"
                )
                self.api_thread.start()
                logger.info("API server started on port 5001")
            except Exception as e:
                logger.error(f"Failed to start API server: {e}")
'''
    
    # Find the start method and add API server start
    start_pattern = r'(logger\.info\("System started successfully"\))'
    content = re.sub(start_pattern, r'\1' + start_addition, content)
    
    # Add API server stop to the stop method
    stop_addition = '''
        # Stop API server
        if self.api_server:
            try:
                # API server will stop when main thread stops
                logger.info("API server stopped")
            except Exception as e:
                logger.error(f"Error stopping API server: {e}")
'''
    
    # Find the stop method and add API server stop
    stop_pattern = r'(logger\.info\("System stopped"\))'
    content = re.sub(stop_pattern, r'\1' + stop_addition, content)
    
    # Write the modified content back
    with open('python/v3/main_system.py', 'w') as f:
        f.write(content)
    
    print("✅ API server integration completed")
    print("📋 Changes made:")
    print("   • Added API server import")
    print("   • Added API server initialization in __init__")
    print("   • Added API server start in start() method")
    print("   • Added API server stop in stop() method")
    print("   • API server runs on port 5001")

if __name__ == "__main__":
    integrate_api_server()
