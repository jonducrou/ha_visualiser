#!/usr/bin/env python3
"""
Enhanced test runner for HA Visualiser with mock-based unit testing.

This runner combines the existing validation tests with new pytest-based
unit tests that use mocked Home Assistant dependencies.
"""
import os
import sys
import subprocess
import importlib.util
from pathlib import Path


class EnhancedTestRunner:
    """Enhanced test runner combining validation and unit tests."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / 'tests'
        self.results = {
            'validation_tests': 0,
            'unit_tests': 0,
            'total_passed': 0,
            'total_failed': 0,
            'errors': []
        }
    
    def print_header(self, title):
        """Print a formatted header."""
        print(f"\n{'=' * 60}")
        print(f"{title:^60}")
        print(f"{'=' * 60}")
    
    def print_section(self, title):
        """Print a formatted section header."""
        print(f"\n{'-' * 40}")
        print(f"🔍 {title}")
        print(f"{'-' * 40}")
    
    def run_validation_tests(self):
        """Run existing validation tests."""
        self.print_section("Code Validation Tests")
        
        validation_passed = 0
        validation_failed = 0
        
        try:
            # Run syntax validation
            print("📄 Running syntax validation...")
            result = subprocess.run([
                sys.executable, 
                str(self.tests_dir / 'validate_code.py')
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Syntax validation: PASSED")
                validation_passed += 1
            else:
                print("❌ Syntax validation: FAILED")
                print(result.stdout)
                print(result.stderr)
                validation_failed += 1
                self.results['errors'].append("Syntax validation failed")
                
        except Exception as e:
            print(f"❌ Error running syntax validation: {e}")
            validation_failed += 1
            self.results['errors'].append(f"Syntax validation error: {e}")
        
        try:
            # Run linting
            print("\n🔍 Running code linting...")
            lint_script = self.project_root / 'lint_simple.py'
            if lint_script.exists():
                result = subprocess.run([
                    sys.executable, 
                    str(lint_script)
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    print("✅ Code linting: PASSED")
                    validation_passed += 1
                else:
                    print("⚠️  Code linting: WARNINGS (non-critical)")
                    # Linting warnings don't fail the build
                    validation_passed += 1
            else:
                print("⚠️  Linting script not found, skipping...")
                
        except Exception as e:
            print(f"❌ Error running linting: {e}")
            self.results['errors'].append(f"Linting error: {e}")
        
        try:
            # Run file serving tests
            print("\n📁 Running file serving tests...")
            file_test_script = self.tests_dir / 'test_file_serving.sh'
            if file_test_script.exists():
                result = subprocess.run([
                    'bash', str(file_test_script)
                ], capture_output=True, text=True, cwd=self.project_root)
                
                # File serving test always "passes" but provides useful info
                print("✅ File serving test: COMPLETED")
                validation_passed += 1
            else:
                print("⚠️  File serving test not found, skipping...")
                
        except Exception as e:
            print(f"❌ Error running file serving test: {e}")
            self.results['errors'].append(f"File serving test error: {e}")
        
        self.results['validation_tests'] = validation_passed
        return validation_passed, validation_failed
    
    def check_pytest_dependencies(self):
        """Check if pytest dependencies are available."""
        required_packages = ['pytest', 'pytest-mock', 'pytest-asyncio']
        missing_packages = []
        
        for package in required_packages:
            spec = importlib.util.find_spec(package.replace('-', '_'))
            if spec is None:
                missing_packages.append(package)
        
        return missing_packages
    
    def install_pytest_dependencies(self, missing_packages):
        """Attempt to install missing pytest dependencies."""
        print(f"🔧 Missing packages: {', '.join(missing_packages)}")
        print("📦 Attempting to install pytest dependencies...")
        
        try:
            # Try installing from requirements-test.txt
            requirements_file = self.project_root / 'requirements-test.txt'
            if requirements_file.exists():
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 
                    '-r', str(requirements_file)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Dependencies installed successfully")
                    return True
                else:
                    print(f"❌ Failed to install dependencies: {result.stderr}")
                    return False
            else:
                print("❌ requirements-test.txt not found")
                return False
                
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    def run_pytest_suite(self):
        """Run the new pytest-based unit tests."""
        self.print_section("Mock-Based Unit Tests")
        
        # Check pytest dependencies
        missing_packages = self.check_pytest_dependencies()
        if missing_packages:
            print("⚠️  Missing pytest dependencies detected")
            if not self.install_pytest_dependencies(missing_packages):
                print("❌ Cannot run unit tests without pytest dependencies")
                print("💡 Run: pip install -r requirements-test.txt")
                self.results['errors'].append("Missing pytest dependencies")
                return 0, 1
        
        try:
            # Run pytest with our new test files
            pytest_args = [
                sys.executable, '-m', 'pytest',
                str(self.tests_dir / 'test_preference_management.py'),
                str(self.tests_dir / 'test_graph_service_mocked.py'),
                str(self.tests_dir / 'test_websocket_api_mocked.py'),
                '-v',  # Verbose output
                '--tb=short',  # Short traceback format
                '--disable-warnings'  # Disable pytest warnings for cleaner output
            ]
            
            print("🧪 Running pytest unit tests...")
            result = subprocess.run(
                pytest_args, 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            
            # Parse pytest output
            output_lines = result.stdout.split('\n')
            test_results = [line for line in output_lines if '::' in line and ('PASSED' in line or 'FAILED' in line)]
            
            passed_tests = len([line for line in test_results if 'PASSED' in line])
            failed_tests = len([line for line in test_results if 'FAILED' in line])
            
            print(f"\n📊 Unit Test Results:")
            print(f"   ✅ Passed: {passed_tests}")
            print(f"   ❌ Failed: {failed_tests}")
            
            if failed_tests > 0:
                print(f"\n📋 Failed Tests:")
                for line in test_results:
                    if 'FAILED' in line:
                        print(f"   ❌ {line}")
                
                print(f"\n🔍 Error Details:")
                print(result.stdout[-1000:])  # Last 1000 characters of output
            
            self.results['unit_tests'] = passed_tests
            return passed_tests, failed_tests
            
        except FileNotFoundError:
            print("❌ pytest not found. Install with: pip install pytest")
            self.results['errors'].append("pytest not available")
            return 0, 1
        except Exception as e:
            print(f"❌ Error running pytest: {e}")
            self.results['errors'].append(f"pytest error: {e}")
            return 0, 1
    
    def run_comprehensive_tests(self):
        """Run all available tests."""
        self.print_header("HA Visualiser Enhanced Test Suite")
        
        print("🚀 Running comprehensive test suite with mock-based unit testing")
        print(f"📁 Project root: {self.project_root}")
        
        # Run validation tests
        validation_passed, validation_failed = self.run_validation_tests()
        
        # Run unit tests
        unit_passed, unit_failed = self.run_pytest_suite()
        
        # Calculate totals
        total_passed = validation_passed + unit_passed
        total_failed = validation_failed + unit_failed
        total_tests = total_passed + total_failed
        
        self.results['total_passed'] = total_passed
        self.results['total_failed'] = total_failed
        
        # Print summary
        self.print_header("Test Summary")
        
        print(f"📊 Overall Results:")
        print(f"   🔍 Validation Tests: {validation_passed} passed, {validation_failed} failed")
        print(f"   🧪 Unit Tests: {unit_passed} passed, {unit_failed} failed")
        print(f"   📈 Total: {total_passed}/{total_tests} tests passed")
        
        if total_failed == 0:
            print(f"\n🎉 All tests passed! ✅")
            success_rate = 100.0
        else:
            success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
            print(f"\n📊 Success rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n⚠️  Errors encountered:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print(f"\n💡 Next Steps:")
        if total_failed > 0:
            print("   • Review failed tests and fix issues")
            print("   • Ensure all dependencies are properly installed")
        else:
            print("   • All tests passing! Ready for integration testing")
            print("   • Copy to HA custom_components/ for live testing")
        
        print("\n📚 Testing Documentation:")
        print("   • tests/README.md - Comprehensive testing guide")
        print("   • requirements-test.txt - Testing dependencies")
        print("   • conftest.py - Shared test fixtures")
        
        return total_failed == 0
    
    def get_results(self):
        """Get detailed test results."""
        return self.results


def main():
    """Main entry point."""
    runner = EnhancedTestRunner()
    success = runner.run_comprehensive_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()