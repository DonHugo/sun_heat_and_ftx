#!/usr/bin/env python3
"""
Solar Heating System Switch Script
Easily switch between v1 and v3 systems on Raspberry Pi
"""

import subprocess
import sys
import time
import os

def run_command(command, check=True):
    """Run a shell command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_service_status(service_name):
    """Check if a systemd service is active"""
    success, stdout, stderr = run_command(f"systemctl is-active {service_name}", check=False)
    return success and stdout.strip() == "active"

def stop_service(service_name):
    """Stop a systemd service"""
    print(f"🛑 Stopping {service_name}...")
    success, stdout, stderr = run_command(f"sudo systemctl stop {service_name}")
    if success:
        print(f"✅ {service_name} stopped successfully")
    else:
        print(f"⚠️  Warning: {service_name} may not have been running")
    return success

def start_service(service_name):
    """Start a systemd service"""
    print(f"🚀 Starting {service_name}...")
    success, stdout, stderr = run_command(f"sudo systemctl start {service_name}")
    if success:
        print(f"✅ {service_name} started successfully")
    else:
        print(f"❌ Failed to start {service_name}")
        print(f"Error: {stderr}")
    return success

def get_service_status(service_name):
    """Get detailed status of a service"""
    success, stdout, stderr = run_command(f"systemctl status {service_name}", check=False)
    return stdout

def switch_to_v1():
    """Switch to v1 system"""
    print("🔄 Switching to v1 (Original) System")
    print("=" * 50)
    
    # Stop v3 if running
    if check_service_status("solar_heating_v3.service"):
        stop_service("solar_heating_v3.service")
        time.sleep(2)
    
    # Start v1
    if start_service("temperature_monitoring.service"):
        print("\n✅ Successfully switched to v1 system")
        print("📊 System status:")
        print(get_service_status("temperature_monitoring.service"))
        return True
    else:
        print("\n❌ Failed to switch to v1 system")
        return False

def switch_to_v3():
    """Switch to v3 system"""
    print("🔄 Switching to v3 (New) System")
    print("=" * 50)
    
    # Stop v1 if running
    if check_service_status("temperature_monitoring.service"):
        stop_service("temperature_monitoring.service")
        time.sleep(2)
    
    # Start v3
    if start_service("solar_heating_v3.service"):
        print("\n✅ Successfully switched to v3 system")
        print("📊 System status:")
        print(get_service_status("solar_heating_v3.service"))
        return True
    else:
        print("\n❌ Failed to switch to v3 system")
        return False

def show_status():
    """Show status of both systems"""
    print("📊 System Status")
    print("=" * 30)
    
    v1_status = check_service_status("temperature_monitoring.service")
    v3_status = check_service_status("solar_heating_v3.service")
    
    print(f"v1 (Original): {'🟢 RUNNING' if v1_status else '🔴 STOPPED'}")
    print(f"v3 (New):      {'🟢 RUNNING' if v3_status else '🔴 STOPPED'}")
    
    if v1_status and v3_status:
        print("\n⚠️  WARNING: Both systems are running!")
        print("   This may cause conflicts. Consider stopping one system.")
    elif not v1_status and not v3_status:
        print("\nℹ️  No system is currently running")
    else:
        active_system = "v1" if v1_status else "v3"
        print(f"\n✅ {active_system} system is active")

def show_logs(service_name, lines=20):
    """Show recent logs for a service"""
    print(f"📋 Recent logs for {service_name}")
    print("=" * 40)
    
    success, stdout, stderr = run_command(f"journalctl -u {service_name} -n {lines} --no-pager")
    if success:
        print(stdout)
    else:
        print(f"❌ Failed to get logs: {stderr}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🔧 Solar Heating System Switch Script")
        print("=" * 40)
        print("Usage:")
        print("  python3 system_switch.py v1     - Switch to v1 system")
        print("  python3 system_switch.py v3     - Switch to v3 system")
        print("  python3 system_switch.py status - Show system status")
        print("  python3 system_switch.py logs   - Show logs for active system")
        print("  python3 system_switch.py logs-v1 - Show v1 logs")
        print("  python3 system_switch.py logs-v3 - Show v3 logs")
        return
    
    command = sys.argv[1].lower()
    
    if command == "v1":
        switch_to_v1()
    elif command == "v3":
        switch_to_v3()
    elif command == "status":
        show_status()
    elif command == "logs":
        # Show logs for whichever system is running
        if check_service_status("temperature_monitoring.service"):
            show_logs("temperature_monitoring.service")
        elif check_service_status("solar_heating_v3.service"):
            show_logs("solar_heating_v3.service")
        else:
            print("ℹ️  No system is currently running")
    elif command == "logs-v1":
        show_logs("temperature_monitoring.service")
    elif command == "logs-v3":
        show_logs("solar_heating_v3.service")
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python3 system_switch.py' for help")

if __name__ == "__main__":
    main()
