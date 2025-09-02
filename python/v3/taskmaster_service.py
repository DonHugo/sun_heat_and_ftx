"""
TaskMaster AI Service Layer for Solar Heating System v3
Integrates TaskMaster AI with the main system to implement FR-008 requirements
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from taskmaster_integration import taskmaster, Task

logger = logging.getLogger(__name__)

class TaskMasterService:
    """Service layer for TaskMaster AI integration implementing FR-008"""
    
    def __init__(self):
        self.last_optimization = datetime.now()
        self.system_state: Dict[str, Any] = {}
        self.task_execution_count = 0
        self.initialized = False
        
    async def initialize(self):
        """Initialize the TaskMaster AI service (FR-008 requirement)"""
        logger.info("Initializing TaskMaster AI service...")
        
        try:
            # Create initial system optimization task
            await self.create_system_optimization_task()
            
            # Create continuous monitoring tasks
            await self.create_continuous_monitoring_tasks()
            
            self.initialized = True
            logger.info("TaskMaster AI service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TaskMaster AI service: {str(e)}")
            return False
    
    async def create_continuous_monitoring_tasks(self):
        """Create continuous monitoring tasks (FR-008 requirement)"""
        # Temperature monitoring task (continuous)
        await taskmaster.create_task("temperature_monitoring", {
            "type": "continuous",
            "description": "Continuous temperature sensor monitoring",
            "interval": "30_seconds"
        })
        
        # Safety monitoring task (continuous)
        await taskmaster.create_task("safety_monitoring", {
            "type": "continuous",
            "description": "Continuous safety monitoring",
            "interval": "10_seconds"
        })
        
        logger.info("Created continuous monitoring tasks")
    
    async def create_system_optimization_task(self):
        """Create system optimization task (FR-008 requirement)"""
        await taskmaster.create_task("system_optimization", {
            "type": "daily",
            "description": "Daily system optimization analysis",
            "last_run": self.last_optimization.isoformat()
        })
        logger.info("Created system optimization task")
    
    async def process_temperature_data(self, temperature_data: Dict[str, float]):
        """Process temperature data and create tasks as needed (FR-008 requirement)"""
        if not self.initialized:
            return
        
        # Update system state
        self.system_state.update({
            "temperatures": temperature_data,
            "last_update": datetime.now().isoformat()
        })
        
        # Check for temperature alerts and create tasks
        await self._check_temperature_alerts(temperature_data)
        
        # Check for safety conditions
        await self._check_safety_conditions(temperature_data)
        
        # Update temperature monitoring task
        await self._update_temperature_monitoring_task(temperature_data)
    
    async def _check_temperature_alerts(self, temperature_data: Dict[str, float]):
        """Check for temperature alerts and create tasks"""
        from config import config
        
        for sensor_name, temperature in temperature_data.items():
            if temperature > config.temperature_threshold_high:
                # High temperature alert
                await taskmaster.create_task("temperature_monitoring", {
                    "action": "high_temperature_alert",
                    "sensor": sensor_name,
                    "temperature": temperature,
                    "threshold": config.temperature_threshold_high,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Create pump control task to increase circulation
                await taskmaster.create_task("pump_control", {
                    "action": "increase_flow",
                    "reason": "high_temperature",
                    "sensor": sensor_name,
                    "temperature": temperature
                })
                
                logger.warning(f"High temperature alert: {sensor_name} at {temperature}°C")
                
            elif temperature < config.temperature_threshold_low:
                # Low temperature alert
                await taskmaster.create_task("temperature_monitoring", {
                    "action": "low_temperature_alert",
                    "sensor": sensor_name,
                    "temperature": temperature,
                    "threshold": config.temperature_threshold_low,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.warning(f"Low temperature alert: {sensor_name} at {temperature}°C")
    
    async def _check_safety_conditions(self, temperature_data: Dict[str, float]):
        """Check for safety conditions and create tasks"""
        from config import config
        
        # Check for overheating (boiling temperature)
        for sensor_name, temperature in temperature_data.items():
            if temperature > config.temp_kok:
                await taskmaster.create_task("safety_monitoring", {
                    "action": "overheating_alert",
                    "sensor": sensor_name,
                    "temperature": temperature,
                    "threshold": config.temp_kok,
                    "severity": "critical",
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.critical(f"CRITICAL: Overheating detected on {sensor_name} at {temperature}°C")
    
    async def _update_temperature_monitoring_task(self, temperature_data: Dict[str, float]):
        """Update temperature monitoring task with current data"""
        # Find active temperature monitoring task
        active_tasks = await taskmaster.get_active_tasks()
        temp_task = None
        
        for task in active_tasks:
            if task.name == "temperature_monitoring" and task.parameters.get("type") == "continuous":
                temp_task = task
                break
        
        if temp_task:
            # Update task with current temperature data
            await taskmaster.update_task_result(temp_task.id, {
                "current_temperatures": temperature_data,
                "sensor_count": len(temperature_data),
                "update_timestamp": datetime.now().isoformat()
            })
    
    async def process_pump_control(self, pump_action: str, parameters: Dict[str, Any]):
        """Process pump control actions and create tasks (FR-008 requirement)"""
        if not self.initialized:
            return
        
        # Create pump control task
        task = await taskmaster.create_task("pump_control", {
            "action": pump_action,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat(),
            "system_state": self.system_state
        })
        
        if task:
            logger.info(f"Created pump control task: {pump_action}")
            self.task_execution_count += 1
    
    async def process_system_status(self, system_status: Dict[str, Any]):
        """Process system status and create optimization tasks (FR-008 requirement)"""
        if not self.initialized:
            return
        
        # Update system state
        self.system_state.update(system_status)
        
        # Check if it's time for daily optimization
        now = datetime.now()
        if (now - self.last_optimization).total_seconds() > 86400:  # 24 hours
            await self._run_daily_optimization()
    
    async def _run_daily_optimization(self):
        """Run daily system optimization (FR-008 requirement)"""
        logger.info("Running daily system optimization...")
        
        # Create optimization analysis task
        optimization_task = await taskmaster.create_task("system_optimization", {
            "type": "daily_analysis",
            "description": "Daily system performance analysis",
            "system_state": self.system_state,
            "timestamp": datetime.now().isoformat()
        })
        
        if optimization_task:
            # Analyze system performance
            analysis_result = await self._analyze_system_performance()
            
            # Update task with results
            await taskmaster.update_task_result(optimization_task.id, {
                "analysis_result": analysis_result,
                "completed_at": datetime.now().isoformat()
            })
            
            self.last_optimization = datetime.now()
            logger.info("Daily optimization completed")
    
    async def _analyze_system_performance(self) -> Dict[str, Any]:
        """Analyze system performance for optimization and provide improvement insights"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "system_uptime": self.system_state.get("uptime", 0),
            "task_execution_count": self.task_execution_count,
            "temperature_alerts": 0,
            "safety_alerts": 0,
            "pump_operations": 0,
            "energy_efficiency": {},
            "operational_metrics": {},
            "recommendations": [],
            "improvement_opportunities": [],
            "maintenance_suggestions": [],
            "performance_trends": {}
        }
        
        # Count different types of tasks
        active_tasks = await taskmaster.get_active_tasks()
        for task in active_tasks:
            if "temperature" in task.name:
                analysis["temperature_alerts"] += 1
            elif "safety" in task.name:
                analysis["safety_alerts"] += 1
            elif "pump" in task.name:
                analysis["pump_operations"] += 1
        
        # Analyze energy efficiency
        analysis["energy_efficiency"] = await self._analyze_energy_efficiency()
        
        # Analyze operational metrics
        analysis["operational_metrics"] = await self._analyze_operational_metrics()
        
        # Generate comprehensive recommendations
        analysis["recommendations"] = await self._generate_recommendations(analysis)
        
        # Identify improvement opportunities
        analysis["improvement_opportunities"] = await self._identify_improvement_opportunities(analysis)
        
        # Suggest maintenance actions
        analysis["maintenance_suggestions"] = await self._suggest_maintenance_actions(analysis)
        
        # Analyze performance trends
        analysis["performance_trends"] = await self._analyze_performance_trends()
        
        return analysis
    
    async def _analyze_energy_efficiency(self) -> Dict[str, Any]:
        """Analyze energy efficiency metrics"""
        temperatures = self.system_state.get("temperatures", {})
        
        efficiency_metrics = {
            "solar_collector_efficiency": 0.0,
            "heat_exchanger_efficiency": 0.0,
            "stratification_quality": 0.0,
            "overall_system_efficiency": 0.0
        }
        
        # Calculate solar collector efficiency
        solar_temp = temperatures.get("solar_collector", 0)
        outdoor_temp = temperatures.get("outdoor_air", 0)
        if solar_temp > 0 and outdoor_temp > 0:
            # Basic efficiency calculation (can be enhanced with solar radiation data)
            efficiency_metrics["solar_collector_efficiency"] = round(
                (solar_temp - outdoor_temp) / max(solar_temp, 1), 2
            )
        
        # Get heat exchanger efficiency from temperatures
        efficiency_metrics["heat_exchanger_efficiency"] = temperatures.get("heat_exchanger_efficiency", 0)
        
        # Calculate stratification quality
        top_temp = temperatures.get("water_heater_top", 0)
        bottom_temp = temperatures.get("water_heater_bottom", 0)
        if top_temp > 0 and bottom_temp > 0:
            efficiency_metrics["stratification_quality"] = round(
                (top_temp - bottom_temp) / 140, 3  # 140cm height
            )
        
        # Overall system efficiency (weighted average)
        if efficiency_metrics["solar_collector_efficiency"] > 0:
            efficiency_metrics["overall_system_efficiency"] = round(
                (efficiency_metrics["solar_collector_efficiency"] + 
                 efficiency_metrics["heat_exchanger_efficiency"] / 100) / 2, 2
            )
        
        return efficiency_metrics
    
    async def _analyze_operational_metrics(self) -> Dict[str, Any]:
        """Analyze operational performance metrics"""
        operational_metrics = {
            "pump_efficiency": 0.0,
            "heating_cycle_efficiency": 0.0,
            "system_reliability": 0.0,
            "maintenance_needs": []
        }
        
        # Calculate pump efficiency based on runtime vs heating cycles
        pump_runtime = self.system_state.get("pump_runtime_hours", 0)
        heating_cycles = self.system_state.get("heating_cycles_count", 0)
        
        if heating_cycles > 0:
            operational_metrics["pump_efficiency"] = round(
                heating_cycles / max(pump_runtime, 1), 2
            )
        
        # Calculate heating cycle efficiency
        if pump_runtime > 0:
            operational_metrics["heating_cycle_efficiency"] = round(
                heating_cycles / max(pump_runtime, 1), 2
            )
        
        # System reliability (based on uptime and error rates)
        uptime = self.system_state.get("uptime", 0)
        if uptime > 0:
            operational_metrics["system_reliability"] = round(
                min(99.9, 100 - (self.task_execution_count / max(uptime / 3600, 1))), 1
            )
        
        # Identify maintenance needs
        if pump_runtime > 100:  # 100 hours of operation
            operational_metrics["maintenance_needs"].append("Pump maintenance due - exceeded 100 hours runtime")
        
        if heating_cycles > 50:  # 50 heating cycles
            operational_metrics["maintenance_needs"].append("System inspection due - exceeded 50 heating cycles")
        
        return operational_metrics
    
    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate intelligent recommendations for system improvement"""
        recommendations = []
        
        # Temperature-related recommendations
        if analysis["temperature_alerts"] > 5:
            recommendations.append("High number of temperature alerts - check sensor calibration and positioning")
        
        if analysis["temperature_alerts"] > 10:
            recommendations.append("Excessive temperature alerts - consider adjusting temperature thresholds")
        
        # Safety-related recommendations
        if analysis["safety_alerts"] > 0:
            recommendations.append("Safety alerts detected - review system safety parameters and sensor placement")
        
        # Pump operation recommendations
        if analysis["pump_operations"] > 20:
            recommendations.append("High pump usage detected - consider optimizing temperature thresholds for better efficiency")
        
        if analysis["pump_operations"] > 30:
            recommendations.append("Excessive pump cycling - investigate system design or adjust control parameters")
        
        # Energy efficiency recommendations
        energy_efficiency = analysis.get("energy_efficiency", {})
        if energy_efficiency.get("solar_collector_efficiency", 0) < 0.3:
            recommendations.append("Low solar collector efficiency - check collector cleanliness and positioning")
        
        if energy_efficiency.get("stratification_quality", 0) < 0.1:
            recommendations.append("Poor water stratification - consider tank insulation or flow rate optimization")
        
        # Operational recommendations
        operational_metrics = analysis.get("operational_metrics", {})
        if operational_metrics.get("pump_efficiency", 0) < 0.5:
            recommendations.append("Low pump efficiency - investigate pump sizing or system resistance")
        
        if operational_metrics.get("system_reliability", 0) < 95:
            recommendations.append("System reliability below target - review maintenance schedule and component health")
        
        return recommendations
    
    async def _identify_improvement_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific opportunities for system improvement"""
        opportunities = []
        
        # Energy efficiency opportunities
        energy_efficiency = analysis.get("energy_efficiency", {})
        if energy_efficiency.get("solar_collector_efficiency", 0) < 0.4:
            opportunities.append({
                "category": "energy_efficiency",
                "priority": "high",
                "description": "Solar collector efficiency improvement",
                "potential_savings": "15-25% energy gain",
                "actions": [
                    "Clean solar collector surface",
                    "Check collector angle and positioning",
                    "Verify insulation around collector",
                    "Consider collector upgrade if efficiency remains low"
                ]
            })
        
        if energy_efficiency.get("stratification_quality", 0) < 0.15:
            opportunities.append({
                "category": "energy_efficiency",
                "priority": "medium",
                "description": "Water heater stratification improvement",
                "potential_savings": "10-20% heat retention",
                "actions": [
                    "Add tank insulation",
                    "Optimize flow rates",
                    "Check for internal mixing",
                    "Consider stratification baffles"
                ]
            })
        
        # Operational efficiency opportunities
        operational_metrics = analysis.get("operational_metrics", {})
        if operational_metrics.get("pump_efficiency", 0) < 0.6:
            opportunities.append({
                "category": "operational_efficiency",
                "priority": "medium",
                "description": "Pump operation optimization",
                "potential_savings": "5-15% operational cost",
                "actions": [
                    "Review pump sizing",
                    "Check for system resistance",
                    "Optimize control parameters",
                    "Consider variable speed pump"
                ]
            })
        
        # Maintenance opportunities
        maintenance_needs = operational_metrics.get("maintenance_needs", [])
        if maintenance_needs:
            opportunities.append({
                "category": "maintenance",
                "priority": "high",
                "description": "Preventive maintenance scheduling",
                "potential_savings": "Avoid costly repairs",
                "actions": [
                    "Schedule pump maintenance",
                    "Inspect system components",
                    "Clean sensors and collectors",
                    "Update maintenance records"
                ]
            })
        
        return opportunities
    
    async def _suggest_maintenance_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest specific maintenance actions based on system analysis"""
        maintenance_actions = []
        
        # Time-based maintenance
        pump_runtime = self.system_state.get("pump_runtime_hours", 0)
        if pump_runtime > 100:
            maintenance_actions.append({
                "type": "pump_maintenance",
                "priority": "high",
                "description": "Pump maintenance due",
                "runtime_hours": pump_runtime,
                "recommended_actions": [
                    "Inspect pump bearings and seals",
                    "Check pump efficiency",
                    "Clean pump internals",
                    "Verify electrical connections"
                ],
                "estimated_duration": "2-4 hours"
            })
        
        # Performance-based maintenance
        energy_efficiency = analysis.get("energy_efficiency", {})
        if energy_efficiency.get("solar_collector_efficiency", 0) < 0.3:
            maintenance_actions.append({
                "type": "collector_maintenance",
                "priority": "medium",
                "description": "Solar collector efficiency low",
                "current_efficiency": energy_efficiency.get("solar_collector_efficiency", 0),
                "recommended_actions": [
                    "Clean collector surface",
                    "Check for damage or wear",
                    "Verify proper positioning",
                    "Inspect insulation"
                ],
                "estimated_duration": "1-2 hours"
            })
        
        # Safety-based maintenance
        if analysis.get("safety_alerts", 0) > 0:
            maintenance_actions.append({
                "type": "safety_inspection",
                "priority": "critical",
                "description": "Safety system inspection required",
                "alert_count": analysis.get("safety_alerts", 0),
                "recommended_actions": [
                    "Review all safety sensors",
                    "Check emergency shutdown systems",
                    "Verify temperature limits",
                    "Test safety interlocks"
                ],
                "estimated_duration": "3-5 hours"
            })
        
        return maintenance_actions
    
    async def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        # This would typically analyze historical data
        # For now, we'll provide a framework for future implementation
        trends = {
            "efficiency_trend": "stable",  # improving, declining, stable
            "performance_indicators": [],
            "seasonal_patterns": [],
            "optimization_impact": []
        }
        
        # Basic trend analysis based on current metrics
        if self.task_execution_count > 50:
            trends["efficiency_trend"] = "improving"
            trends["performance_indicators"].append("High task execution indicates active optimization")
        elif self.task_execution_count < 10:
            trends["efficiency_trend"] = "stable"
            trends["performance_indicators"].append("Low task execution indicates stable operation")
        
        return trends
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get TaskMaster service status (FR-008 requirement)"""
        active_tasks = await taskmaster.get_active_tasks()
        task_history = await taskmaster.get_task_history()
        
        return {
            "initialized": self.initialized,
            "active_tasks_count": len(active_tasks),
            "total_tasks_executed": len(task_history),
            "last_optimization": self.last_optimization.isoformat(),
            "system_state": self.system_state,
            "active_tasks": [task.to_dict() for task in active_tasks],
            "recent_task_history": task_history[-10:]  # Last 10 tasks
        }
    
    async def get_system_insights(self) -> Dict[str, Any]:
        """Get comprehensive system insights for improvement (FR-008 requirement)"""
        if not self.initialized:
            return {"error": "Service not initialized"}
        
        # Get current analysis
        analysis = await self._analyze_system_performance()
        
        # Format insights for easy consumption
        insights = {
            "summary": {
                "overall_health": self._calculate_overall_health(analysis),
                "priority_issues": self._identify_priority_issues(analysis),
                "optimization_potential": self._calculate_optimization_potential(analysis)
            },
            "energy_analysis": analysis.get("energy_efficiency", {}),
            "operational_analysis": analysis.get("operational_metrics", {}),
            "recommendations": analysis.get("recommendations", []),
            "improvement_opportunities": analysis.get("improvement_opportunities", []),
            "maintenance_suggestions": analysis.get("maintenance_suggestions", []),
            "performance_trends": analysis.get("performance_trends", {}),
            "action_items": self._generate_action_items(analysis)
        }
        
        return insights
    
    def _calculate_overall_health(self, analysis: Dict[str, Any]) -> str:
        """Calculate overall system health score"""
        score = 100
        
        # Deduct points for issues
        if analysis.get("safety_alerts", 0) > 0:
            score -= 30  # Safety issues are critical
        
        if analysis.get("temperature_alerts", 0) > 10:
            score -= 20  # Excessive temperature alerts
        
        if analysis.get("pump_operations", 0) > 30:
            score -= 15  # Excessive pump cycling
        
        # Energy efficiency impact
        energy_efficiency = analysis.get("energy_efficiency", {})
        if energy_efficiency.get("solar_collector_efficiency", 0) < 0.3:
            score -= 15
        
        if energy_efficiency.get("stratification_quality", 0) < 0.1:
            score -= 10
        
        # Operational efficiency impact
        operational_metrics = analysis.get("operational_metrics", {})
        if operational_metrics.get("system_reliability", 0) < 95:
            score -= 10
        
        return max(0, score)
    
    def _identify_priority_issues(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify high-priority issues that need immediate attention"""
        priority_issues = []
        
        if analysis.get("safety_alerts", 0) > 0:
            priority_issues.append("CRITICAL: Safety alerts detected - immediate attention required")
        
        if analysis.get("temperature_alerts", 0) > 15:
            priority_issues.append("HIGH: Excessive temperature alerts - system calibration needed")
        
        energy_efficiency = analysis.get("energy_efficiency", {})
        if energy_efficiency.get("solar_collector_efficiency", 0) < 0.2:
            priority_issues.append("HIGH: Very low solar collector efficiency - maintenance required")
        
        return priority_issues
    
    def _calculate_optimization_potential(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate potential optimization improvements"""
        potential = {
            "energy_savings": "0%",
            "operational_improvements": "0%",
            "maintenance_optimization": "0%"
        }
        
        # Energy savings potential
        energy_efficiency = analysis.get("energy_efficiency", {})
        if energy_efficiency.get("solar_collector_efficiency", 0) < 0.4:
            potential["energy_savings"] = "15-25%"
        
        if energy_efficiency.get("stratification_quality", 0) < 0.15:
            potential["energy_savings"] = "10-20%"
        
        # Operational improvements
        if analysis.get("pump_operations", 0) > 20:
            potential["operational_improvements"] = "10-20%"
        
        # Maintenance optimization
        if analysis.get("safety_alerts", 0) > 0:
            potential["maintenance_optimization"] = "20-30%"
        
        return potential
    
    def _generate_action_items(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific action items for system improvement"""
        action_items = []
        
        # Immediate actions (next 24 hours)
        if analysis.get("safety_alerts", 0) > 0:
            action_items.append({
                "priority": "immediate",
                "description": "Safety system inspection",
                "estimated_effort": "2-4 hours",
                "impact": "critical"
            })
        
        # Short-term actions (next week)
        if analysis.get("temperature_alerts", 0) > 10:
            action_items.append({
                "priority": "high",
                "description": "Sensor calibration and system review",
                "estimated_effort": "4-8 hours",
                "impact": "high"
            })
        
        # Medium-term actions (next month)
        energy_efficiency = analysis.get("energy_efficiency", {})
        if energy_efficiency.get("solar_collector_efficiency", 0) < 0.3:
            action_items.append({
                "priority": "medium",
                "description": "Solar collector maintenance and optimization",
                "estimated_effort": "8-16 hours",
                "impact": "medium"
            })
        
        # Long-term actions (next quarter)
        if analysis.get("pump_operations", 0) > 30:
            action_items.append({
                "priority": "low",
                "description": "System design review and optimization",
                "estimated_effort": "16-32 hours",
                "impact": "high"
            })
        
        return action_items
    
    async def cleanup(self):
        """Cleanup completed tasks and close service"""
        if self.initialized:
            await taskmaster.cleanup_completed_tasks()
            await taskmaster.close()
            logger.info("TaskMaster AI service cleaned up")

# Global TaskMaster service instance
taskmaster_service = TaskMasterService()
