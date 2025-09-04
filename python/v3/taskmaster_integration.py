"""
TaskMaster AI Integration for Solar Heating System v3
Implements FR-008: TaskMaster AI Integration
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import httpx

from config import config

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """Task model for TaskMaster AI"""
    id: str
    name: str
    description: str
    status: str = "pending"
    priority: str = "medium"
    created_at: datetime = None
    updated_at: datetime = None
    parameters: Dict[str, Any] = None
    result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.parameters is None:
            self.parameters = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

class TaskMasterAI:
    """TaskMaster AI integration class implementing FR-008"""
    
    def __init__(self):
        self.api_key = config.taskmaster_api_key
        self.base_url = config.taskmaster_base_url
        self.enabled = config.taskmaster_enabled
        self.client = None
        self.active_tasks: Dict[str, Task] = {}
        self.task_history: List[Dict[str, Any]] = []
        self.last_optimization = datetime.now()
        
        if self.enabled and self.api_key:
            self.client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0
            )
            logger.info("TaskMaster AI client initialized")
        else:
            logger.warning("TaskMaster AI disabled or no API key provided")
    
    async def create_task(self, task_name: str, parameters: Dict[str, Any] = None) -> Optional[Task]:
        """Create a new task in TaskMaster AI (FR-008 requirement)"""
        if not self.enabled or not self.client:
            logger.debug(f"TaskMaster AI disabled, creating local task: {task_name}")
            return self._create_local_task(task_name, parameters)
        
        try:
            task_data = {
                "name": task_name,
                "description": self._get_task_description(task_name),
                "priority": self._get_task_priority(task_name),
                "parameters": parameters or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/tasks",
                json=task_data
            )
            
            if response.status_code == 201:
                task = Task(**response.json())
                self.active_tasks[task.id] = task
                self._log_task_creation(task)
                logger.info(f"Created TaskMaster AI task: {task_name} with ID: {task.id}")
                return task
            else:
                logger.error(f"Failed to create task: {response.status_code} - {response.text}")
                return self._create_local_task(task_name, parameters)
                
        except httpx.ConnectError as e:
            logger.warning(f"TaskMaster AI connection failed for {task_name}: {str(e)} - using local task")
            return self._create_local_task(task_name, parameters)
        except httpx.TimeoutException as e:
            logger.warning(f"TaskMaster AI timeout for {task_name}: {str(e)} - using local task")
            return self._create_local_task(task_name, parameters)
        except Exception as e:
            logger.error(f"Error creating TaskMaster AI task {task_name}: {str(e)}")
            return self._create_local_task(task_name, parameters)
    
    def _create_local_task(self, task_name: str, parameters: Dict[str, Any] = None) -> Task:
        """Create a local task when TaskMaster AI is not available"""
        task_id = f"local_{task_name}_{int(datetime.now().timestamp())}"
        task = Task(
            id=task_id,
            name=task_name,
            description=self._get_task_description(task_name),
            priority=self._get_task_priority(task_name),
            parameters=parameters or {}
        )
        self.active_tasks[task.id] = task
        self._log_task_creation(task)
        logger.info(f"Created local task: {task_name} with ID: {task.id}")
        return task
    
    def _get_task_description(self, task_name: str) -> str:
        """Get task description based on task name"""
        descriptions = {
            "temperature_monitoring": "Monitor temperature sensors and trigger alerts",
            "pump_control": "Control water circulation pumps based on temperature",
            "valve_control": "Control valves for optimal heat distribution",
            "data_logging": "Log system data for analysis and optimization",
            "system_optimization": "AI-powered system optimization recommendations",
            "stratification_monitoring": "Monitor water heater stratification quality",
            "operational_efficiency": "Monitor pump runtime and efficiency",
            "safety_monitoring": "Monitor overheating and freeze protection",
            "energy_optimization": "Monitor solar collector and heat exchanger efficiency",
            "predictive_maintenance": "Predict maintenance needs and optimize schedules"
        }
        return descriptions.get(task_name, f"Task: {task_name}")
    
    def _get_task_priority(self, task_name: str) -> str:
        """Get task priority based on task name"""
        priorities = {
            "temperature_monitoring": "high",
            "safety_monitoring": "high",
            "pump_control": "medium",
            "valve_control": "medium",
            "stratification_monitoring": "medium",
            "operational_efficiency": "medium",
            "energy_optimization": "medium",
            "predictive_maintenance": "medium",
            "system_optimization": "low",
            "data_logging": "low"
        }
        return priorities.get(task_name, "medium")
    
    def _log_task_creation(self, task: Task):
        """Log task creation for history tracking"""
        self.task_history.append({
            "task_id": task.id,
            "name": task.name,
            "created_at": task.created_at.isoformat(),
            "parameters": task.parameters,
            "priority": task.priority
        })
        
        # Keep only last 100 tasks in history
        if len(self.task_history) > 100:
            self.task_history = self.task_history[-100:]
    
    async def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the status of a task"""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].status
        
        if not self.enabled or not self.client:
            return None
        
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
        """Update task result (FR-008 requirement)"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.result = result
            task.status = "completed"
            task.updated_at = datetime.now()
            logger.info(f"Updated local task result for {task_id}")
            return True
        
        if not self.enabled or not self.client:
            return False
        
        try:
            response = await self.client.patch(
                f"{self.base_url}/tasks/{task_id}",
                json={"result": result, "status": "completed"}
            )
            
            if response.status_code == 200:
                logger.info(f"Updated TaskMaster AI task result for {task_id}")
                return True
            else:
                logger.error(f"Failed to update task result: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating task result: {str(e)}")
            return False
    
    async def get_active_tasks(self) -> List[Task]:
        """Get list of active tasks (FR-008 requirement)"""
        return list(self.active_tasks.values())
    
    async def get_task_history(self) -> List[Dict[str, Any]]:
        """Get task execution history (FR-008 requirement)"""
        return self.task_history.copy()
    
    async def cleanup_completed_tasks(self):
        """Clean up completed tasks from active tasks list"""
        completed_tasks = [
            task_id for task_id, task in self.active_tasks.items()
            if task.status == "completed"
        ]
        
        for task_id in completed_tasks:
            del self.active_tasks[task_id]
        
        if completed_tasks:
            logger.info(f"Cleaned up {len(completed_tasks)} completed tasks")
    
    async def close(self):
        """Close the TaskMaster AI client"""
        if self.client:
            await self.client.aclose()
            logger.info("TaskMaster AI client closed")

# Global TaskMaster AI instance
taskmaster = TaskMasterAI()
