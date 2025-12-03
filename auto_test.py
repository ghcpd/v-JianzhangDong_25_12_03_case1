#!/usr/bin/env python3
"""
Automatic Test Runner for VSCode Python Environment
This script detects and uses the active Python environment from VSCode
instead of creating a virtual environment inside the project directory.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


class AutoTestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests"
        self.logs_dir = self.project_root / "logs"
        self.requirements_file = self.project_root / "requirements.txt"
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup log file
        self.log_file = self.logs_dir / "test_run.log"
        
    def log(self, message, to_console=True, to_file=True):
        """Log message to console and/or file."""
        if to_console:
            print(message)
        if to_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(message + "\n")
    
    def get_python_executable(self):
        """Get the current Python executable path."""
        return sys.executable
    
    def check_python_environment(self):
        """Check and display current Python environment information."""
        python_exe = self.get_python_executable()
        
        self.log("=" * 50)
        self.log("Python Environment Information")
        self.log("=" * 50)
        self.log(f"Python Executable: {python_exe}")
        self.log(f"Python Version: {sys.version}")
        self.log(f"Virtual Environment: {sys.prefix}")
        
        # Check if running in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        self.log(f"In Virtual Environment: {in_venv}")
        self.log("=" * 50)
        self.log("")
        
        return python_exe
    
    def check_dependencies(self, python_exe):
        """Check if all required dependencies are installed."""
        self.log("Checking dependencies...")
        
        if not self.requirements_file.exists():
            self.log("Warning: requirements.txt not found.")
            return True
        
        try:
            # Get list of installed packages
            result = subprocess.run(
                [python_exe, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            installed_packages = {
                pkg["name"].lower(): pkg["version"] 
                for pkg in json.loads(result.stdout)
            }
            
            # Read requirements
            missing_packages = []
            with open(self.requirements_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Parse package name (handle ==, >=, etc.)
                        pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                        if pkg_name.lower() not in installed_packages:
                            missing_packages.append(pkg_name)
            
            if missing_packages:
                self.log(f"Missing packages: {', '.join(missing_packages)}")
                return False
            
            self.log("✓ All dependencies are installed.")
            self.log("")
            return True
            
        except Exception as e:
            self.log(f"Warning: Could not verify dependencies: {e}")
            return True  # Continue anyway
    
    def install_dependencies(self, python_exe):
        """Install dependencies from requirements.txt."""
        self.log("Installing dependencies...")
        self.log("-" * 50)
        
        try:
            result = subprocess.run(
                [python_exe, "-m", "pip", "install", "-r", str(self.requirements_file)],
                capture_output=True,
                text=True,
                check=False
            )
            
            self.log(result.stdout)
            if result.returncode != 0:
                self.log(f"Error installing dependencies:\n{result.stderr}")
                return False
            
            self.log("✓ Dependencies installed successfully.")
            self.log("")
            return True
            
        except Exception as e:
            self.log(f"Error: Failed to install dependencies: {e}")
            return False
    
    def run_test_file(self, test_file, python_exe):
        """Run a single test file."""
        test_name = test_file.name
        self.log(f"Running {test_name}...")
        self.log("-" * 50)
        
        try:
            # Set up environment with project root in PYTHONPATH
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root) + os.pathsep + env.get('PYTHONPATH', '')
            
            result = subprocess.run(
                [python_exe, str(test_file)],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                env=env,
                timeout=60  # 60 second timeout per test
            )
            
            # Log output
            if result.stdout:
                self.log(result.stdout, to_console=False)
            if result.stderr:
                self.log(result.stderr, to_console=False)
            
            # Check result
            if result.returncode == 0:
                self.log(f"✓ {test_name} PASSED", to_file=True)
                return True
            else:
                self.log(f"✗ {test_name} FAILED (exit code: {result.returncode})", to_file=True)
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"✗ {test_name} FAILED (timeout)", to_file=True)
            return False
        except Exception as e:
            self.log(f"✗ {test_name} FAILED (error: {e})", to_file=True)
            return False
    
    def run_all_tests(self, python_exe):
        """Run all test files in the tests directory."""
        if not self.tests_dir.exists():
            self.log(f"Error: Tests directory not found: {self.tests_dir}")
            return 0, 0
        
        # Find all test files
        test_files = sorted(self.tests_dir.glob("case_*.py"))
        
        if not test_files:
            self.log("Warning: No test files found matching pattern 'case_*.py'")
            return 0, 0
        
        self.log(f"Found {len(test_files)} test file(s)")
        self.log("=" * 50)
        self.log("")
        
        # Run tests
        passed = 0
        failed = 0
        
        for test_file in test_files:
            if self.run_test_file(test_file, python_exe):
                passed += 1
            else:
                failed += 1
            self.log("")
        
        return passed, failed
    
    def print_summary(self, passed, failed):
        """Print test summary."""
        total = passed + failed
        
        self.log("=" * 50)
        self.log("Test Summary")
        self.log("=" * 50)
        self.log(f"Total Tests: {total}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        self.log("=" * 50)
        self.log("")
        self.log(f"Detailed logs saved to: {self.log_file}")
    
    def run(self):
        """Main execution method."""
        # Initialize log file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"Test Run - {timestamp}\n")
            f.write("=" * 50 + "\n\n")
        
        self.log(f"Auto Test Runner Started - {timestamp}")
        self.log("")
        
        # Get Python executable
        python_exe = self.check_python_environment()
        
        # Check dependencies
        if not self.check_dependencies(python_exe):
            self.log("Some dependencies are missing. Installing...")
            if not self.install_dependencies(python_exe):
                self.log("Failed to install dependencies. Exiting.")
                return 1
        
        # Run tests
        passed, failed = self.run_all_tests(python_exe)
        
        # Print summary
        self.print_summary(passed, failed)
        
        # Return exit code
        return 0 if failed == 0 else 1


if __name__ == "__main__":
    runner = AutoTestRunner()
    exit_code = runner.run()
    sys.exit(exit_code)
