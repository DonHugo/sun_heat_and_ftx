#!/usr/bin/env python3
"""
Fix Cartridge Heater Configuration Bug
This script fixes the config.cartridge_heater_relay reference error
"""

import sys
import os
sys.path.append('/home/pi/solar_heating/python/v3')

def fix_cartridge_heater_config():
    """Fix the cartridge heater relay configuration reference"""
    
    print("🔧 Fixing Cartridge Heater Configuration Bug")
    print("=" * 50)
    
    # Read the main_system.py file
    main_system_path = '/home/pi/solar_heating/python/v3/main_system.py'
    
    try:
        with open(main_system_path, 'r') as f:
            content = f.read()
        
        print("✅ Read main_system.py successfully")
        
        # Check if the bug exists
        if 'config.cartridge_heater_relay' not in content:
            print("⚠️  Bug not found - may already be fixed")
            return True
        
        # Fix the configuration reference
        fixed_content = content.replace(
            'config.cartridge_heater_relay',
            'config.pump_config.cartridge_heater_relay'
        )
        
        # Create backup
        backup_path = main_system_path + '.backup_cartridge_fix'
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Created backup: {backup_path}")
        
        # Write fixed content
        with open(main_system_path, 'w') as f:
            f.write(fixed_content)
        print("✅ Fixed cartridge heater configuration reference")
        
        print("\n🎯 Configuration Fix Applied:")
        print("  • Changed config.cartridge_heater_relay")
        print("  • To config.pump_config.cartridge_heater_relay")
        print("  • This should resolve the MQTT command errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing cartridge heater config: {e}")
        return False

if __name__ == "__main__":
    success = fix_cartridge_heater_config()
    if success:
        print("\n✅ Cartridge heater configuration fixed!")
        print("🔄 Restart the solar heating service to apply changes:")
        print("   sudo systemctl restart solar_heating_v3.service")
    else:
        print("\n❌ Failed to fix cartridge heater configuration")
