"""
HTTP Health Check Server for Solar Heating System v3
Provides a simple HTTP endpoint for uptime monitoring
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional
from aiohttp import web, ClientSession

logger = logging.getLogger(__name__)

class HealthCheckServer:
    """Simple HTTP server for health checks"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.system_callback = None
        
        # Setup routes
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_get("/status", self.status_check)
        self.app.router.add_get("/", self.root)
        
        # Health check data
        self.last_heartbeat = time.time()
        self.start_time = time.time()
        self.health_status = "healthy"
    
    def set_system_callback(self, callback):
        """Set callback to get system information"""
        self.system_callback = callback
    
    def update_heartbeat(self, system_info: Dict[str, Any] = None):
        """Update heartbeat timestamp and system info"""
        self.last_heartbeat = time.time()
        if system_info:
            self.health_status = "healthy" if system_info.get('status') == 'alive' else 'degraded'
    
    async def health_check(self, request):
        """Simple health check endpoint"""
        try:
            # Check if we've received a heartbeat recently
            time_since_heartbeat = time.time() - self.last_heartbeat
            
            if time_since_heartbeat > 120:  # 2 minutes
                status = "unhealthy"
                http_status = 503
            elif time_since_heartbeat > 60:  # 1 minute
                status = "degraded"
                http_status = 200
            else:
                status = "healthy"
                http_status = 200
            
            response_data = {
                "status": status,
                "timestamp": time.time(),
                "last_heartbeat": self.last_heartbeat,
                "time_since_heartbeat": time_since_heartbeat,
                "uptime": time.time() - self.start_time
            }
            
            return web.json_response(response_data, status=http_status)
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return web.json_response(
                {"status": "error", "error": str(e)}, 
                status=500
            )
    
    async def status_check(self, request):
        """Detailed status endpoint"""
        try:
            if not self.system_callback:
                return web.json_response(
                    {"error": "System callback not available"}, 
                    status=503
                )
            
            # Get system information
            system_info = await self.system_callback()
            
            response_data = {
                "status": "healthy",
                "timestamp": time.time(),
                "last_heartbeat": self.last_heartbeat,
                "uptime": time.time() - self.start_time,
                "system": system_info
            }
            
            return web.json_response(response_data)
            
        except Exception as e:
            logger.error(f"Error in status check: {e}")
            return web.json_response(
                {"status": "error", "error": str(e)}, 
                status=500
            )
    
    async def root(self, request):
        """Root endpoint with basic info"""
        response_data = {
            "service": "Solar Heating System v3 Health Check",
            "endpoints": {
                "/health": "Simple health check",
                "/status": "Detailed system status"
            },
            "timestamp": time.time()
        }
        return web.json_response(response_data)
    
    async def start(self):
        """Start the HTTP server"""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(
                self.runner, 
                self.host, 
                self.port
            )
            
            await self.site.start()
            logger.info(f"Health check server started on {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")
            raise
    
    async def stop(self):
        """Stop the HTTP server"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            logger.info("Health check server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping health check server: {e}")
    
    def is_running(self) -> bool:
        """Check if server is running"""
        return self.site is not None and self.site.is_running

# Example usage
async def main():
    """Example usage of health check server"""
    server = HealthCheckServer(port=8080)
    
    try:
        await server.start()
        
        # Keep server running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down health check server...")
    finally:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
