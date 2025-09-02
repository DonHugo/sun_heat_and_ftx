"""
TaskMaster AI Integration for Solar Heating System
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
from pydantic import BaseModel

from taskmaster_config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Task(BaseModel):
    """Task model for TaskMaster AI"""
    id: str
    name: str
    description: str
    status: str = "pending"
    priority: str = "medium"
    created_at: datetime
    updated_at: datetime
    parameters: Dict[str, Any] = {}
    result: Optional[Dict[str, Any]] = None

class TaskMasterAI:
    """TaskMaster AI integration class"""
    
    def __init__(self):
        self.api_key = config.taskmaster_api_key
        self.base_url = config.taskmaster_base_url
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0
        )
        self.active_tasks: Dict[str, Task] = {}
        
    async def create_task(self, task_name: str, parameters: Dict[str, Any] = None) -> Optional[Task]:
        """Create a new task in TaskMaster AI"""
        try:
            task_data = {
                "name": task_name,
                "description": config.system_tasks.get(task_name, {}).get("description", ""),
                "priority": config.system_tasks.get(task_name, {}).get("priority", "medium"),
                "parameters": parameters or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/tasks",
                json=task_data
            )
            
            if response.status_code == 201:
                task = Task(**response.json())
                self.active_tasks[task.id] = task
                logger.info(f"Created task: {task_name} with ID: {task.id}")
                return task
            else:
                logger.error(f"Failed to create task: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating task {task_name}: {str(e)}")
            return None
    
    async def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the status of a task"""
        try:
            response = await self.client.get(f"{self.base_url}/tasks/{task_id}")
            
            if response.status_code == 200:
                task_data = response.json()
                return task_data.get("status")
            else:
                logger.error(f"Failed to get task status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting task status: {str(e)}")
            return None
    
    async def update_task_result(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Update task result"""
        try:
            response = await self.client.patch(
                f"{self.base_url}/tasks/{task_id}",
                json={"result": result, "status": "completed"}
            )
            
            if response.status_code == 200:
                logger.info(f"Updated task result for {task_id}")
                return True
            else:
                logger.error(f"Failed to update task result: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating task result: {str(e)}")
            return False
    
    async def get_ai_recommendations(self, system_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get AI-powered recommendations for system optimization"""
        try:
            response = await self.client.post(
                f"{self.base_url}/ai/analyze",
                json={
                    "system_type": "solar_heating",
                    "data": system_data,
                    "analysis_type": "optimization"
                }
            )
            
            if response.status_code == 200:
                recommendations = response.json().get("recommendations", [])
                logger.info(f"Received {len(recommendations)} AI recommendations")
                return recommendations
            else:
                logger.error(f"Failed to get AI recommendations: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {str(e)}")
            return []
    
    async def monitor_temperature(self, temperature_data: Dict[str, float]) -> Optional[Task]:
        """Monitor temperature and create tasks if thresholds are exceeded"""
        for sensor, temp in temperature_data.items():
            if temp > config.temperature_threshold_high:
                return await self.create_task(
                    "temperature_monitoring",
                    {
                        "sensor": sensor,
                        "temperature": temp,
                        "threshold": config.temperature_threshold_high,
                        "action": "high_temperature_alert"
                    }
                )
            elif temp < config.temperature_threshold_low:
                return await self.create_task(
                    "temperature_monitoring",
                    {
                        "sensor": sensor,
                        "temperature": temp,
                        "threshold": config.temperature_threshold_low,
                        "action": "low_temperature_alert"
                    }
                )
        return None
    
    async def optimize_system(self, current_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get system optimization recommendations"""
        if not config.enable_ai_optimization:
            return []
            
        return await self.get_ai_recommendations(current_data)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global TaskMaster AI instance
taskmaster = TaskMasterAI()
