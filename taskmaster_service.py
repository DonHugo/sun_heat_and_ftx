"""
TaskMaster AI Service Integration
Integrates TaskMaster AI with the existing solar heating system
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from taskmaster_integration import taskmaster, Task
from taskmaster_config import config

logger = logging.getLogger(__name__)

class TaskMasterService:
    """Service layer for TaskMaster AI integration"""
    
    def __init__(self):
        self.last_optimization = datetime.now()
        self.system_state: Dict[str, Any] = {}
        self.task_history: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Initialize the TaskMaster AI service"""
        logger.info("Initializing TaskMaster AI service...")
        
        if not config.validate():
            logger.warning("TaskMaster AI configuration validation failed")
            return False
            
        # Create initial system optimization task
        await self.create_system_optimization_task()
        logger.info("TaskMaster AI service initialized successfully")
        return True
    
    async def process_temperature_data(self, temperature_data: Dict[str, float]):
        """Process temperature data and create tasks as needed"""
        logger.info(f"Processing temperature data: {temperature_data}")
        
        # Update system state
        self.system_state.update({
            "temperatures": temperature_data,
            "last_update": datetime.now().isoformat()
        })
        
        # Monitor temperatures and create tasks
        task = await taskmaster.monitor_temperature(temperature_data)
        
        if task:
            self.task_history.append({
                "task_id": task.id,
                "name": task.name,
                "created_at": task.created_at.isoformat(),
                "parameters": task.parameters
            })
            
            # Execute task-specific actions
            await self.execute_task_actions(task)
    
    async def execute_task_actions(self, task: Task):
        """Execute actions based on task type"""
        if task.name == "temperature_monitoring":
            await self.handle_temperature_alert(task)
        elif task.name == "pump_control":
            await self.handle_pump_control(task)
        elif task.name == "valve_control":
            await self.handle_valve_control(task)
        elif task.name == "system_optimization":
            await self.handle_system_optimization(task)
    
    async def handle_temperature_alert(self, task: Task):
        """Handle temperature monitoring alerts"""
        params = task.parameters
        sensor = params.get("sensor")
        temperature = params.get("temperature")
        action = params.get("action")
        
        logger.warning(f"Temperature alert: {action} for sensor {sensor} at {temperature}°C")
        
        # Create follow-up tasks based on alert type
        if action == "high_temperature_alert":
            # Create pump control task to increase circulation
            await taskmaster.create_task("pump_control", {
                "action": "increase_flow",
                "reason": "high_temperature",
                "sensor": sensor
            })
        elif action == "low_temperature_alert":
            # Create valve control task to optimize heat distribution
            await taskmaster.create_task("valve_control", {
                "action": "optimize_distribution",
                "reason": "low_temperature",
                "sensor": sensor
            })
    
    async def handle_pump_control(self, task: Task):
        """Handle pump control tasks"""
        params = task.parameters
        action = params.get("action")
        
        logger.info(f"Executing pump control: {action}")
        
        # Here you would integrate with your actual pump control hardware
        # For now, we'll just log the action
        result = {
            "action": action,
            "executed_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        await taskmaster.update_task_result(task.id, result)
    
    async def handle_valve_control(self, task: Task):
        """Handle valve control tasks"""
        params = task.parameters
        action = params.get("action")
        
        logger.info(f"Executing valve control: {action}")
        
        # Here you would integrate with your actual valve control hardware
        result = {
            "action": action,
            "executed_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        await taskmaster.update_task_result(task.id, result)
    
    async def handle_system_optimization(self, task: Task):
        """Handle system optimization tasks"""
        logger.info("Executing system optimization analysis")
        
        # Get AI recommendations
        recommendations = await taskmaster.optimize_system(self.system_state)
        
        result = {
            "recommendations": recommendations,
            "analysis_timestamp": datetime.now().isoformat(),
            "system_state": self.system_state
        }
        
        await taskmaster.update_task_result(task.id, result)
        
        # Process recommendations
        for rec in recommendations:
            await self.process_recommendation(rec)
    
    async def process_recommendation(self, recommendation: Dict[str, Any]):
        """Process AI recommendations"""
        rec_type = recommendation.get("type")
        priority = recommendation.get("priority", "medium")
        
        logger.info(f"Processing recommendation: {rec_type} (priority: {priority})")
        
        if rec_type == "pump_adjustment":
            await taskmaster.create_task("pump_control", {
                "action": recommendation.get("action"),
                "reason": "ai_optimization",
                "priority": priority
            })
        elif rec_type == "valve_adjustment":
            await taskmaster.create_task("valve_control", {
                "action": recommendation.get("action"),
                "reason": "ai_optimization",
                "priority": priority
            })
    
    async def create_system_optimization_task(self):
        """Create periodic system optimization task"""
        task = await taskmaster.create_task("system_optimization", {
            "frequency": "daily",
            "analysis_type": "comprehensive"
        })
        
        if task:
            logger.info("Created system optimization task")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "system_state": self.system_state,
            "active_tasks": len(taskmaster.active_tasks),
            "task_history": self.task_history[-10:],  # Last 10 tasks
            "last_optimization": self.last_optimization.isoformat(),
            "ai_enabled": config.enable_ai_optimization
        }
    
    async def run_periodic_optimization(self):
        """Run periodic system optimization"""
        while True:
            try:
                await asyncio.sleep(config.ai_analysis_interval)
                
                # Check if it's time for optimization
                if datetime.now() - self.last_optimization > timedelta(hours=24):
                    await self.create_system_optimization_task()
                    self.last_optimization = datetime.now()
                    
            except Exception as e:
                logger.error(f"Error in periodic optimization: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def shutdown(self):
        """Shutdown the service"""
        logger.info("Shutting down TaskMaster AI service...")
        await taskmaster.close()

# Global service instance
taskmaster_service = TaskMasterService()
