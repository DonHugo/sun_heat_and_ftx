#!/usr/bin/env python3
"""
Get TaskMaster AI Insights On Demand
====================================

This script allows you to get real-time insights and recommendations
from your TaskMaster AI integration whenever you want.
"""

import asyncio
import logging
from taskmaster_service import TaskMasterService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def get_insights():
    """Get comprehensive system insights from TaskMaster AI"""
    
    logger.info("🔍 Getting TaskMaster AI insights...")
    
    try:
        # Initialize the service
        service = TaskMasterService()
        await service.initialize()
        
        logger.info("✅ TaskMaster AI service initialized")
        
        # Get comprehensive insights
        logger.info("📊 Analyzing system performance...")
        insights = await service.get_system_insights()
        
        # Display insights in a nice format
        print("\n" + "="*80)
        print("🧠 TASKMASTER AI SYSTEM INSIGHTS")
        print("="*80)
        
        # System Health
        print(f"\n🏥 SYSTEM HEALTH: {insights.get('health_score', 'N/A')}/100")
        print("-" * 50)
        if 'health_issues' in insights:
            for issue in insights['health_issues']:
                print(f"  ⚠️  {issue}")
        
        # Energy Efficiency
        print(f"\n⚡ ENERGY EFFICIENCY: {insights.get('energy_efficiency', 'N/A')}%")
        print("-" * 50)
        if 'efficiency_metrics' in insights:
            for metric, value in insights['efficiency_metrics'].items():
                print(f"  📊 {metric}: {value}")
        
        # Recommendations
        print(f"\n💡 INTELLIGENT RECOMMENDATIONS")
        print("-" * 50)
        if 'recommendations' in insights:
            for i, rec in enumerate(insights['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # Action Items
        print(f"\n🎯 ACTION ITEMS")
        print("-" * 50)
        if 'action_items' in insights:
            for item in insights['action_items']:
                priority = item.get('priority', 'MEDIUM')
                action = item.get('action', 'N/A')
                effort = item.get('effort', 'N/A')
                print(f"  🔧 [{priority}] {action} (Effort: {effort})")
        
        # Performance Trends
        print(f"\n📈 PERFORMANCE TRENDS")
        print("-" * 50)
        if 'performance_trends' in insights:
            for trend, value in insights['performance_trends'].items():
                print(f"  📊 {trend}: {value}")
        
        print("\n" + "="*80)
        print("✅ Insights retrieved successfully!")
        print("="*80)
        
        # Cleanup
        await service.cleanup()
        
    except Exception as e:
        logger.error(f"❌ Error getting insights: {e}")
        print(f"\n❌ Error: {e}")

def main():
    """Main function"""
    print("🧠 TaskMaster AI Insights Tool")
    print("=" * 40)
    print("Getting real-time system insights...")
    
    # Run the async function
    asyncio.run(get_insights())

if __name__ == "__main__":
    main()
