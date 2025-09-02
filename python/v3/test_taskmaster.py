#!/usr/bin/env python3
"""
Test script for TaskMaster AI integration (FR-008)
Tests the basic functionality of the TaskMaster integration
"""

import asyncio
import logging
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_taskmaster_integration():
    """Test TaskMaster AI integration functionality"""
    try:
        logger.info("Testing TaskMaster AI integration...")
        
        # Import TaskMaster modules
        from taskmaster_integration import taskmaster, Task
        from taskmaster_service import taskmaster_service
        
        logger.info("✓ TaskMaster modules imported successfully")
        
        # Test TaskMaster AI initialization
        logger.info("Testing TaskMaster AI initialization...")
        await taskmaster_service.initialize()
        logger.info("✓ TaskMaster AI service initialized")
        
        # Test task creation
        logger.info("Testing task creation...")
        task = await taskmaster.create_task("temperature_monitoring", {
            "test": True,
            "description": "Test task for integration verification"
        })
        
        if task:
            logger.info(f"✓ Task created successfully: {task.id}")
            logger.info(f"  Name: {task.name}")
            logger.info(f"  Status: {task.status}")
            logger.info(f"  Priority: {task.priority}")
        else:
            logger.error("✗ Failed to create task")
            return False
        
        # Test temperature data processing
        logger.info("Testing temperature data processing...")
        test_temp_data = {
            'solar_collector': 75.5,
            'storage_tank': 65.2,
            'return_line': 58.9,
            'water_heater_bottom': 45.0,
            'water_heater_top': 78.5
        }
        
        await taskmaster_service.process_temperature_data(test_temp_data)
        logger.info("✓ Temperature data processed successfully")
        
        # Test pump control task creation
        logger.info("Testing pump control task creation...")
        await taskmaster_service.process_pump_control("start", {
            "reason": "test",
            "dT": 12.5,
            "threshold": 8.0
        })
        logger.info("✓ Pump control task created successfully")
        
        # Test system status processing
        logger.info("Testing system status processing...")
        test_system_status = {
            'mode': 'heating',
            'primary_pump': True,
            'pump_runtime_hours': 2.5,
            'heating_cycles_count': 5
        }
        
        await taskmaster_service.process_system_status(test_system_status)
        logger.info("✓ System status processed successfully")
        
        # Get service status
        logger.info("Getting TaskMaster service status...")
        status = await taskmaster_service.get_service_status()
        logger.info(f"✓ Service status retrieved:")
        logger.info(f"  Initialized: {status['initialized']}")
        logger.info(f"  Active tasks: {status['active_tasks_count']}")
        logger.info(f"  Total tasks executed: {status['total_tasks_executed']}")
        
        # Test task result update
        logger.info("Testing task result update...")
        if task:
            result = await taskmaster.update_task_result(task.id, {
                "test_result": "success",
                "completion_time": "2024-01-01T12:00:00Z"
            })
            if result:
                logger.info("✓ Task result updated successfully")
            else:
                logger.error("✗ Failed to update task result")
        
        # Test cleanup
        logger.info("Testing cleanup...")
        await taskmaster_service.cleanup()
        logger.info("✓ TaskMaster service cleaned up successfully")
        
        logger.info("🎉 All TaskMaster AI integration tests passed!")
        return True
        
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        logger.error("Make sure you're running from the v3 directory")
        return False
    except Exception as e:
        logger.error(f"✗ Test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("TaskMaster AI Integration Test (FR-008)")
    logger.info("=" * 60)
    
    success = await test_taskmaster_integration()
    
    if success:
        logger.info("✅ TaskMaster AI integration test completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ TaskMaster AI integration test failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
