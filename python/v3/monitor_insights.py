#!/usr/bin/env python3
"""
Continuous TaskMaster AI Insights Monitor
========================================

This script continuously monitors your system and displays
TaskMaster AI insights in real-time.
"""

import asyncio
import time
import logging
from datetime import datetime
from taskmaster_service import TaskMasterService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InsightsMonitor:
    """Continuous monitor for TaskMaster AI insights"""
    
    def __init__(self, update_interval=30):
        self.update_interval = update_interval
        self.service = None
        self.running = False
        
    async def start(self):
        """Start the monitoring service"""
        logger.info("🚀 Starting TaskMaster AI Insights Monitor...")
        
        try:
            # Initialize the service
            self.service = TaskMasterService()
            await self.service.initialize()
            
            logger.info("✅ TaskMaster AI service initialized")
            self.running = True
            
            # Start monitoring loop
            await self.monitor_loop()
            
        except Exception as e:
            logger.error(f"❌ Error starting monitor: {e}")
            
    async def monitor_loop(self):
        """Main monitoring loop"""
        iteration = 0
        
        while self.running:
            try:
                iteration += 1
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"\n{'='*80}")
                print(f"🧠 TASKMASTER AI INSIGHTS - {current_time} (Update #{iteration})")
                print(f"{'='*80}")
                
                # Get current insights
                insights = await self.service.get_system_insights()
                
                # Display key metrics
                self.display_insights(insights)
                
                # Get service status
                status = await self.service.get_service_status()
                self.display_status(status)
                
                print(f"\n⏰ Next update in {self.update_interval} seconds...")
                print("Press Ctrl+C to stop monitoring")
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    def display_insights(self, insights):
        """Display insights in a formatted way"""
        
        # System Health
        health_score = insights.get('health_score', 'N/A')
        print(f"\n🏥 SYSTEM HEALTH: {health_score}/100")
        print("-" * 50)
        
        if 'health_issues' in insights and insights['health_issues']:
            for issue in insights['health_issues']:
                print(f"  ⚠️  {issue}")
        else:
            print("  ✅ No health issues detected")
        
        # Energy Efficiency
        efficiency = insights.get('energy_efficiency', 'N/A')
        print(f"\n⚡ ENERGY EFFICIENCY: {efficiency}%")
        print("-" * 50)
        
        if 'efficiency_metrics' in insights:
            for metric, value in insights['efficiency_metrics'].items():
                print(f"  📊 {metric}: {value}")
        
        # Top Recommendations
        print(f"\n💡 TOP RECOMMENDATIONS")
        print("-" * 50)
        if 'recommendations' in insights and insights['recommendations']:
            for i, rec in enumerate(insights['recommendations'][:3], 1):
                print(f"  {i}. {rec}")
        else:
            print("  ✅ No recommendations at this time")
        
        # Critical Action Items
        print(f"\n🎯 CRITICAL ACTIONS")
        print("-" * 50)
        if 'action_items' in insights and insights['action_items']:
            critical_items = [item for item in insights['action_items'] 
                            if item.get('priority', '').upper() in ['CRITICAL', 'IMMEDIATE', 'HIGH']]
            if critical_items:
                for item in critical_items[:2]:
                    priority = item.get('priority', 'MEDIUM')
                    action = item.get('action', 'N/A')
                    effort = item.get('effort', 'N/A')
                    print(f"  🔥 [{priority}] {action} (Effort: {effort})")
            else:
                print("  ✅ No critical actions required")
        else:
            print("  ✅ No action items at this time")
    
    def display_status(self, status):
        """Display service status"""
        print(f"\n📊 SERVICE STATUS")
        print("-" * 50)
        print(f"  🔧 Initialized: {status.get('initialized', False)}")
        print(f"  📋 Active Tasks: {status.get('active_tasks', 0)}")
        print(f"  📈 Total Tasks Executed: {status.get('total_tasks_executed', 0)}")
        print(f"  🕒 Last Optimization: {status.get('last_optimization', 'N/A')}")
        
    async def stop(self):
        """Stop the monitoring service"""
        logger.info("🛑 Stopping TaskMaster AI Insights Monitor...")
        self.running = False
        
        if self.service:
            await self.service.cleanup()
            logger.info("✅ Service cleaned up")

async def main():
    """Main function"""
    print("🧠 TaskMaster AI Insights Monitor")
    print("=" * 50)
    print("This will continuously monitor your system and show AI insights")
    print("Updates every 30 seconds. Press Ctrl+C to stop.")
    print()
    
    monitor = InsightsMonitor(update_interval=30)
    
    try:
        await monitor.start()
    except KeyboardInterrupt:
        await monitor.stop()
        print("\n👋 Monitoring stopped. Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
