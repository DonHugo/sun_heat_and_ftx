#!/usr/bin/env python3
"""
Test Runner for Solar Heating System v3
Automated test runner for continuous integration and validation

Usage:
    python3 run_tests.py [options]
    
Options:
    --category CATEGORY    Run specific test category (hardware, control, mqtt, state, modes, taskmaster, integration, all)
    --quick               Run quick tests only
    --comprehensive       Run comprehensive test suite
    --verbose             Enable verbose output
    --report              Generate test report
    --ci                  Run in CI mode (non-interactive)
    --help                Show this help message

Examples:
    python3 run_tests.py --quick                    # Run quick tests
    python3 run_tests.py --category hardware        # Run hardware tests only
    python3 run_tests.py --comprehensive --report   # Run all tests with report
    python3 run_tests.py --ci --category all        # Run all tests in CI mode
"""

import argparse
import sys
import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from test_config import TestConfig
    from comprehensive_test_suite import ComprehensiveTestSuite
    from quick_test_runner import QuickTestRunner
    from simulation_test_suite import SimulationTestSuite
    from hardware_test_suite import HardwareTestSuite
    from detect_environment import detect_environment
except ImportError as e:
    print(f"Error importing test modules: {e}")
    print("Make sure you're running from the v3 directory")
    sys.exit(1)

class TestRunner:
    """Main test runner for Solar Heating System v3"""
    
    def __init__(self, args):
        self.args = args
        self.start_time = time.time()
        self.test_results = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = logging.DEBUG if self.args.verbose else logging.INFO
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_quick_tests(self, category: str = "all") -> bool:
        """Run quick tests"""
        self.logger.info("🚀 Running Quick Tests")
        self.logger.info("=" * 50)
        
        runner = QuickTestRunner()
        success = runner.run_tests(category)
        
        # Store results
        self.test_results['quick_tests'] = {
            'success': success,
            'results': runner.test_results,
            'duration': time.time() - self.start_time
        }
        
        return success
    
    def run_comprehensive_tests(self) -> bool:
        """Run comprehensive test suite"""
        self.logger.info("🚀 Running Comprehensive Test Suite")
        self.logger.info("=" * 50)
        
        suite = ComprehensiveTestSuite()
        success = suite.run_all_tests()
        
        # Store results
        self.test_results['comprehensive_tests'] = {
            'success': success,
            'results': suite.results,
            'duration': time.time() - self.start_time
        }
        
        return success
    
    def run_simulation_tests(self) -> bool:
        """Run simulation test suite"""
        self.logger.info("🚀 Running Simulation Test Suite")
        self.logger.info("=" * 50)
        
        suite = SimulationTestSuite()
        success = suite.run_all_tests()
        
        # Store results
        self.test_results['simulation_tests'] = {
            'success': success,
            'results': suite.results,
            'duration': time.time() - self.start_time
        }
        
        return success
    
    def run_hardware_tests(self) -> bool:
        """Run hardware test suite"""
        self.logger.info("🚀 Running Hardware Test Suite")
        self.logger.info("=" * 50)
        
        suite = HardwareTestSuite()
        success = suite.run_all_tests()
        
        # Store results
        self.test_results['hardware_tests'] = {
            'success': success,
            'results': suite.results,
            'duration': time.time() - self.start_time
        }
        
        return success
    
    def run_auto_detect_tests(self) -> bool:
        """Run tests based on environment detection"""
        self.logger.info("🔍 Auto-detecting environment...")
        
        environment = detect_environment()
        recommended_suite = environment['recommended_test_suite']
        
        self.logger.info(f"Environment: {environment['platform']['system']} {environment['platform']['machine']}")
        self.logger.info(f"Hardware libraries: {'Available' if environment['hardware']['libraries_available'] else 'Not Available'}")
        self.logger.info(f"Recommended test suite: {recommended_suite.upper()}")
        
        if recommended_suite == 'hardware':
            return self.run_hardware_tests()
        else:
            return self.run_simulation_tests()
    
    def run_category_tests(self, category: str) -> bool:
        """Run tests for specific category"""
        if category not in TestConfig.TEST_CATEGORIES:
            self.logger.error(f"Invalid test category: {category}")
            self.logger.info(f"Valid categories: {', '.join(TestConfig.TEST_CATEGORIES.keys())}")
            return False
        
        self.logger.info(f"🚀 Running {TestConfig.TEST_CATEGORIES[category]['name']}")
        self.logger.info("=" * 50)
        
        # For now, use quick tests for category-specific testing
        # This can be extended to run specific comprehensive tests
        return self.run_quick_tests(category)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        total_duration = time.time() - self.start_time
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_run': {
                'duration': total_duration,
                'args': vars(self.args),
                'success': all(result.get('success', False) for result in self.test_results.values())
            },
            'results': self.test_results,
            'summary': self.generate_summary()
        }
        
        return report
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for test_type, result in self.test_results.items():
            if 'results' in result:
                if isinstance(result['results'], list):
                    # Comprehensive test results
                    for test_result in result['results']:
                        total_tests += 1
                        if test_result.passed:
                            passed_tests += 1
                        else:
                            failed_tests += 1
                elif isinstance(result['results'], dict):
                    # Quick test results
                    for test_name, test_result in result['results'].items():
                        total_tests += 1
                        if test_result['passed']:
                            passed_tests += 1
                        else:
                            failed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'overall_success': failed_tests == 0
        }
    
    def save_report(self, report: Dict[str, Any]):
        """Save test report to file"""
        if not self.args.report:
            return
        
        # Create reports directory
        reports_dir = TestConfig.OUTPUT_SETTINGS['log_directory']
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"solar_heating_test_report_{timestamp}.json"
        filepath = os.path.join(reports_dir, filename)
        
        # Save report
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📊 Test report saved to: {filepath}")
    
    def print_summary(self, report: Dict[str, Any]):
        """Print test summary"""
        summary = report['summary']
        
        self.logger.info("\n📊 TEST SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Total Tests: {summary['total_tests']}")
        self.logger.info(f"Passed: {summary['passed_tests']} ✅")
        self.logger.info(f"Failed: {summary['failed_tests']} ❌")
        self.logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        self.logger.info(f"Duration: {report['test_run']['duration']:.2f} seconds")
        
        if summary['overall_success']:
            self.logger.info("\n🎉 ALL TESTS PASSED! System is fully functional.")
        else:
            self.logger.info(f"\n⚠️  {summary['failed_tests']} TESTS FAILED. System needs attention.")
    
    def run(self) -> int:
        """Run tests based on arguments"""
        success = True
        
        try:
            if self.args.quick:
                success = self.run_quick_tests()
            elif self.args.comprehensive:
                success = self.run_comprehensive_tests()
            elif self.args.simulation:
                success = self.run_simulation_tests()
            elif self.args.hardware:
                success = self.run_hardware_tests()
            elif self.args.auto:
                success = self.run_auto_detect_tests()
            elif self.args.category:
                success = self.run_category_tests(self.args.category)
            else:
                # Default: auto-detect environment and run appropriate tests
                success = self.run_auto_detect_tests()
            
            # Generate and save report
            report = self.generate_report()
            self.save_report(report)
            self.print_summary(report)
            
            return 0 if success else 1
            
        except KeyboardInterrupt:
            self.logger.info("\n⏹️  Tests interrupted by user")
            return 1
        except Exception as e:
            self.logger.error(f"❌ Test runner error: {e}")
            return 1

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Test Runner for Solar Heating System v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_tests.py                            # Auto-detect environment and run appropriate tests
  python3 run_tests.py --simulation               # Run simulation tests (no hardware required)
  python3 run_tests.py --hardware                 # Run hardware tests (requires actual hardware)
  python3 run_tests.py --quick                    # Run quick tests
  python3 run_tests.py --comprehensive --report   # Run comprehensive tests with report
  python3 run_tests.py --ci --auto                # Auto-detect and run in CI mode
        """
    )
    
    # Test type options
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        '--quick',
        action='store_true',
        help='Run quick tests only'
    )
    test_group.add_argument(
        '--comprehensive',
        action='store_true',
        help='Run comprehensive test suite'
    )
    test_group.add_argument(
        '--simulation',
        action='store_true',
        help='Run simulation test suite (no hardware required)'
    )
    test_group.add_argument(
        '--hardware',
        action='store_true',
        help='Run hardware test suite (requires actual hardware)'
    )
    test_group.add_argument(
        '--auto',
        action='store_true',
        help='Auto-detect environment and run appropriate tests'
    )
    
    # Test category
    parser.add_argument(
        '--category',
        choices=list(TestConfig.TEST_CATEGORIES.keys()) + ['all'],
        help='Run specific test category'
    )
    
    # Output options
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate test report'
    )
    
    # CI mode
    parser.add_argument(
        '--ci',
        action='store_true',
        help='Run in CI mode (non-interactive)'
    )
    
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    # Validate arguments
    if args.category and args.category not in TestConfig.TEST_CATEGORIES and args.category != 'all':
        print(f"Invalid test category: {args.category}")
        print(f"Valid categories: {', '.join(TestConfig.TEST_CATEGORIES.keys())}, all")
        return 1
    
    # Run tests
    runner = TestRunner(args)
    return runner.run()

if __name__ == "__main__":
    exit(main())
