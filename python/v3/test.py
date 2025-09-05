#!/usr/bin/env python3
"""
Simple Test Runner for Solar Heating System v3
Easy-to-use test runner that automatically detects environment and runs appropriate tests

Usage:
    python3 test.py                    # Auto-detect and run appropriate tests
    python3 test.py --simulation       # Force simulation tests
    python3 test.py --hardware         # Force hardware tests
    python3 test.py --quick            # Run quick tests only
    python3 test.py --verify           # Run system verification only
"""

import sys
import os
import subprocess
import argparse

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print(f"⏹️  {description} interrupted by user")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Simple Test Runner for Solar Heating System v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 test.py                    # Auto-detect and run appropriate tests
  python3 test.py --simulation       # Force simulation tests
  python3 test.py --hardware         # Force hardware tests
  python3 test.py --quick            # Run quick tests only
  python3 test.py --verify           # Run system verification only
        """
    )
    
    parser.add_argument('--simulation', action='store_true', help='Run simulation tests')
    parser.add_argument('--hardware', action='store_true', help='Run hardware tests')
    parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    parser.add_argument('--verify', action='store_true', help='Run system verification only')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Determine which tests to run
    if args.verify:
        cmd = ['python3', 'verify_system.py']
        description = "System Verification"
    elif args.quick:
        cmd = ['python3', 'quick_test_runner.py']
        description = "Quick Tests"
    elif args.simulation:
        cmd = ['python3', 'run_tests.py', '--simulation']
        description = "Simulation Tests"
    elif args.hardware:
        cmd = ['python3', 'run_tests.py', '--hardware']
        description = "Hardware Tests"
    else:
        # Auto-detect environment
        cmd = ['python3', 'run_tests.py']
        description = "Auto-detected Tests"
    
    if args.verbose:
        cmd.append('--verbose')
    
    # Run the tests
    success = run_command(cmd, description)
    
    if success:
        print("\n🎉 Tests completed successfully!")
        return 0
    else:
        print("\n⚠️  Tests failed or were interrupted.")
        return 1

if __name__ == "__main__":
    exit(main())
