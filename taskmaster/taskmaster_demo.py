#!/usr/bin/env python3
"""
TaskMaster AI Demo Script
Demonstrates the integration of TaskMaster AI with the solar heating system
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from taskmaster_service import taskmaster_service
from taskmaster_config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_temperature_monitoring():
    """Demo temperature monitoring with TaskMaster AI"""
    logger.info("=== TaskMaster AI Temperature Monitoring Demo ===")
    
    # Initialize the service
    await taskmaster_service.initialize()
    
    # Simulate temperature data from different sensors
    temperature_scenarios = [
        {
            "solar_collector": 85.5,  # High temperature alert
            "storage_tank": 65.2,
            "heat_exchanger": 72.1
        },
        {
            "solar_collector": 45.3,
            "storage_tank": 18.7,  # Low temperature alert
            "heat_exchanger": 22.4
        },
        {
            "solar_collector": 68.9,
            "storage_tank": 55.6,
            "heat_exchanger": 58.2  # Normal temperatures
        }
    ]
    
    for i, temp_data in enumerate(temperature_scenarios, 1):
        logger.info(f"\n--- Scenario {i}: Processing temperature data ---")
        logger.info(f"Temperature readings: {temp_data}")
        
        # Process temperature data through TaskMaster AI
        await taskmaster_service.process_temperature_data(temp_data)
        
        # Get system status
        status = await taskmaster_service.get_system_status()
        logger.info(f"Active tasks: {status['active_tasks']}")
        
        # Wait a bit between scenarios
        await asyncio.sleep(2)
    
    logger.info("\n=== Temperature monitoring demo completed ===")

async def demo_ai_optimization():
    """Demo AI-powered system optimization"""
    logger.info("\n=== TaskMaster AI System Optimization Demo ===")
    
    # Simulate comprehensive system data
    system_data = {
        "temperatures": {
            "solar_collector": 75.2,
            "storage_tank": 62.8,
            "heat_exchanger": 58.9,
            "return_line": 45.3
        },
        "flow_rates": {
            "primary_pump": 12.5,
            "secondary_pump": 8.2
        },
        "valve_positions": {
            "collector_valve": 0.8,
            "storage_valve": 0.6,
            "bypass_valve": 0.2
        },
        "energy_consumption": {
            "pumps": 2.1,
            "total_system": 2.8
        },
        "efficiency_metrics": {
            "collector_efficiency": 0.72,
            "system_efficiency": 0.68
        }
    }
    
    # Update system state
    taskmaster_service.system_state.update(system_data)
    
    logger.info("Requesting AI optimization recommendations...")
    
    # Get AI recommendations
    recommendations = await taskmaster_service.taskmaster.optimize_system(system_data)
    
    if recommendations:
        logger.info(f"Received {len(recommendations)} AI recommendations:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"  {i}. {rec.get('type', 'Unknown')}: {rec.get('description', 'No description')}")
            logger.info(f"     Priority: {rec.get('priority', 'medium')}")
            logger.info(f"     Impact: {rec.get('impact', 'unknown')}")
    else:
        logger.info("No AI recommendations received (this is normal if API key is not set)")
    
    logger.info("=== AI optimization demo completed ===")

async def demo_task_management():
    """Demo task creation and management"""
    logger.info("\n=== TaskMaster AI Task Management Demo ===")
    
    # Create various types of tasks
    task_types = [
        ("pump_control", {"action": "increase_flow", "reason": "demo"}),
        ("valve_control", {"action": "optimize_distribution", "reason": "demo"}),
        ("data_logging", {"interval": "hourly", "reason": "demo"}),
        ("system_optimization", {"frequency": "daily", "reason": "demo"})
    ]
    
    created_tasks = []
    
    for task_name, parameters in task_types:
        logger.info(f"Creating task: {task_name}")
        task = await taskmaster_service.taskmaster.create_task(task_name, parameters)
        
        if task:
            created_tasks.append(task)
            logger.info(f"  ✓ Task created with ID: {task.id}")
        else:
            logger.info(f"  ✗ Failed to create task: {task_name}")
    
    # Simulate task execution
    for task in created_tasks:
        logger.info(f"Executing task: {task.name}")
        await taskmaster_service.execute_task_actions(task)
    
    logger.info("=== Task management demo completed ===")

async def main():
    """Main demo function"""
    logger.info("Starting TaskMaster AI Integration Demo")
    logger.info("=" * 50)
    
    try:
        # Check configuration
        if not config.validate():
            logger.warning("TaskMaster AI API key not configured. Some features may not work.")
            logger.info("Set TASKMASTER_API_KEY environment variable for full functionality.")
        
        # Run demos
        await demo_temperature_monitoring()
        await demo_ai_optimization()
        await demo_task_management()
        
        # Final status
        status = await taskmaster_service.get_system_status()
        logger.info("\n=== Final System Status ===")
        logger.info(f"Active tasks: {status['active_tasks']}")
        logger.info(f"Task history entries: {len(status['task_history'])}")
        logger.info(f"AI optimization enabled: {status['ai_enabled']}")
        
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")
    
    finally:
        # Cleanup
        await taskmaster_service.shutdown()
        logger.info("Demo completed. TaskMaster AI service shutdown.")

if __name__ == "__main__":
    asyncio.run(main())
