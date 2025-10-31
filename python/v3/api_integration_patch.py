#!/usr/bin/env python3
"""
Patch script to integrate API server into main_system.py
Issue #43: API Input Validation
"""

import re

def integrate_api_server(main_system_content):
    """Integrate API server into main_system.py"""
    
    # 1. Add API server import after other imports
    import_pattern = r"(from taskmaster_service import taskmaster_service)"
    import_replacement = r"""\1
    from api_server import create_api_server
    API_SERVER_AVAILABLE = True
    logger.info("API server module imported successfully")
except ImportError as api_err:
    logger.warning(f"API server not available: {api_err}")
    API_SERVER_AVAILABLE = False
    create_api_server = None
try:
    pass  # Continue with normal imports"""
    
    content = re.sub(import_pattern, import_replacement, main_system_content)
    
    # 2. Add API server initialization in __init__
    init_pattern = r"(self\.mqtt = None)"
    init_replacement = r"""\1
        self.api_server = None
        self.api_thread = None"""
    
    content = re.sub(init_pattern, init_replacement, content)
    
    # 3. Add API server start in start() method
    # Find the end of hardware/mqtt initialization
    start_pattern = r"(# Initialize system state\s+self\.system_state = {)"
    start_replacement = r"""# Initialize API server (Issue #43)
        if API_SERVER_AVAILABLE and create_api_server:
            try:
                import threading
                self.api_server = create_api_server(self, host='0.0.0.0', port=5001)
                
                # Start API server in background thread
                def run_api():
                    try:
                        logger.info("Starting API server on port 5001...")
                        self.api_server.run()
                    except Exception as e:
                        logger.error(f"API server error: {e}")
                
                self.api_thread = threading.Thread(target=run_api, daemon=True)
                self.api_thread.start()
                logger.info("API server started successfully")
            except Exception as e:
                logger.error(f"Failed to start API server: {e}")
                self.api_server = None
        else:
            logger.info("API server not available - skipping")
        
        \1"""
    
    content = re.sub(start_pattern, start_replacement, content)
    
    # 4. Add API server stop in stop() method
    stop_pattern = r"(async def stop\(self\):.*?\"\"\".*?\n\s+)(logger\.info)"
    stop_replacement = r"""\1# Stop API server (Issue #43)
        if self.api_server:
            try:
                logger.info("Stopping API server...")
                # Flask server will stop when daemon thread ends
                self.api_server = None
            except Exception as e:
                logger.error(f"Error stopping API server: {e}")
        
        \2"""
    
    content = re.sub(stop_pattern, stop_replacement, content, flags=re.DOTALL)
    
    return content

if __name__ == "__main__":
    print("API Integration Patch Script")
    print("This script is for reference - apply changes manually")

