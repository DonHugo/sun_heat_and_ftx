#!/usr/bin/env python3
"""
Fix Cartridge Heater Control Logic
This script implements automatic cartridge heater control based on temperature conditions
"""

import sys
import os
sys.path.append('/home/pi/solar_heating/python/v3')

def implement_cartridge_heater_control():
    """Implement automatic cartridge heater control logic"""
    
    print("🔧 Implementing Cartridge Heater Control Logic")
    print("=" * 50)
    
    # Read the main_system.py file
    main_system_path = '/home/pi/solar_heating/python/v3/main_system.py'
    
    try:
        with open(main_system_path, 'r') as f:
            content = f.read()
        
        print("✅ Read main_system.py successfully")
        
        # Check if cartridge heater control already exists
        if 'def _control_cartridge_heater' in content:
            print("⚠️  Cartridge heater control already exists")
            return
        
        # Find the process_control_logic method
        if 'def process_control_logic' not in content:
            print("❌ process_control_logic method not found")
            return
        
        # Find where to insert the cartridge heater control
        # Look for the end of the process_control_logic method
        lines = content.split('\n')
        insert_index = -1
        
        for i, line in enumerate(lines):
            if 'def process_control_logic' in line:
                # Find the end of this method (look for next def or class)
                for j in range(i+1, len(lines)):
                    if lines[j].strip().startswith('def ') or lines[j].strip().startswith('class '):
                        insert_index = j
                        break
                break
        
        if insert_index == -1:
            print("❌ Could not find insertion point")
            return
        
        # Create the cartridge heater control method
        cartridge_control_method = '''
    def _control_cartridge_heater(self):
        """
        Automatic cartridge heater control based on temperature conditions
        """
        try:
            # Get current temperatures
            outdoor_temp = self.temperatures.get('outdoor_air_temp', 25)
            heat_exchanger_temp = self.temperatures.get('heat_exchanger_in', 25)
            water_heater_bottom = self.temperatures.get('water_heater_bottom', 25)
            
            # Temperature thresholds for cartridge heater activation
            outdoor_threshold = 15.0  # Activate if outdoor temp < 15°C
            heat_exchanger_threshold = 15.0  # Activate if heat exchanger < 15°C
            water_heater_threshold = 40.0  # Activate if water heater < 40°C
            
            # Check if cartridge heater should be ON
            should_activate = (
                outdoor_temp < outdoor_threshold or
                heat_exchanger_temp < heat_exchanger_threshold or
                water_heater_bottom < water_heater_threshold
            )
            
            # Get current heater state
            current_state = self.system_state.get('cartridge_heater', False)
            
            # Control logic
            if should_activate and not current_state:
                # Turn ON cartridge heater
                self.system_state['cartridge_heater'] = True
                self.hardware.set_relay_state(config.cartridge_heater_relay, True)
                logger.info(f"Cartridge heater activated: outdoor={outdoor_temp:.1f}°C, heat_exchanger={heat_exchanger_temp:.1f}°C, water_heater={water_heater_bottom:.1f}°C")
                
            elif not should_activate and current_state:
                # Turn OFF cartridge heater
                self.system_state['cartridge_heater'] = False
                self.hardware.set_relay_state(config.cartridge_heater_relay, False)
                logger.info(f"Cartridge heater deactivated: outdoor={outdoor_temp:.1f}°C, heat_exchanger={heat_exchanger_temp:.1f}°C, water_heater={water_heater_bottom:.1f}°C")
            
            # Log current status
            if current_state:
                logger.debug(f"Cartridge heater ON: outdoor={outdoor_temp:.1f}°C, heat_exchanger={heat_exchanger_temp:.1f}°C, water_heater={water_heater_bottom:.1f}°C")
            
        except Exception as e:
            logger.error(f"Error in cartridge heater control: {e}")
'''
        
        # Insert the method before the next method/class
        lines.insert(insert_index, cartridge_control_method)
        
        # Now add the call to this method in process_control_logic
        # Find the process_control_logic method and add the call
        for i, line in enumerate(lines):
            if 'def process_control_logic' in line:
                # Find a good place to insert the call (after temperature processing)
                for j in range(i+1, len(lines)):
                    if 'self._update_system_mode()' in lines[j]:
                        lines.insert(j, '        # Control cartridge heater based on temperature conditions\n        self._control_cartridge_heater()\n')
                        break
                break
        
        # Write the modified content back
        modified_content = '\n'.join(lines)
        
        # Create backup
        backup_path = main_system_path + '.backup'
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Created backup: {backup_path}")
        
        # Write modified content
        with open(main_system_path, 'w') as f:
            f.write(modified_content)
        print("✅ Modified main_system.py with cartridge heater control")
        
        print("\n🎯 Cartridge Heater Control Logic Added:")
        print("  • Automatic activation when outdoor temp < 15°C")
        print("  • Automatic activation when heat exchanger temp < 15°C") 
        print("  • Automatic activation when water heater temp < 40°C")
        print("  • Automatic deactivation when conditions improve")
        print("  • Proper logging of heater status changes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error implementing cartridge heater control: {e}")
        return False

if __name__ == "__main__":
    success = implement_cartridge_heater_control()
    if success:
        print("\n✅ Cartridge heater control logic implemented successfully!")
        print("🔄 Restart the solar heating service to apply changes:")
        print("   sudo systemctl restart solar_heating_v3.service")
    else:
        print("\n❌ Failed to implement cartridge heater control logic")
