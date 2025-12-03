#!/usr/bin/env python
"""
auto_test.py - Automatic environment detection and test runner

This script automatically detects the active Python environment selected by VSCode
(or creates a new external environment if necessary), installs dependencies from
requirements.txt, and runs all test scripts in the tests/ folder.

All test results are written to logs/test_run.log.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# Handle Windows encoding issues
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "test_run.log"

# Custom logging handler for Windows compatibility
class WindowsCompatibleStreamHandler(logging.StreamHandler):
    """Stream handler that handles encoding errors gracefully."""
    def emit(self, record):
        try:
            msg = self.format(record)
            # Replace problematic unicode characters for Windows console
            if sys.platform == "win32":
                msg = msg.replace("✓", "[OK]").replace("✗", "[FAILED]")
            self.stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# Set up logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        WindowsCompatibleStreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def get_python_executable() -> str:
    """Get the current Python executable path."""
    return sys.executable


def get_python_version() -> str:
    """Get the current Python version string."""
    return f"Python {sys.version.split()[0]}"


def detect_environment() -> str:
    """
    Detect the current Python environment.
    Returns a description of the environment being used.
    """
    executable = get_python_executable()
    
    # Check if in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        env_name = os.path.basename(sys.prefix)
        env_type = "Virtual Environment"
    else:
        env_type = "System Python"
        env_name = "Default"
    
    return f"{env_type} ({env_name}): {executable}"


def check_pip_available() -> bool:
    """Check if pip is available."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def install_requirements() -> bool:
    """
    Install dependencies from requirements.txt using the current environment.
    
    Returns:
        True if installation was successful, False otherwise.
    """
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        logger.error(f"requirements.txt not found in {Path.cwd()}")
        return False
    
    logger.info("Installing dependencies from requirements.txt...")
    
    try:
        # Upgrade pip, setuptools, and wheel first
        logger.info("Upgrading pip, setuptools, and wheel...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", 
             "pip>=24.0", "setuptools>=68.0", "wheel"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        if result.returncode != 0:
            logger.warning(f"Pip upgrade had issues: {result.stderr}")
        
        # Install requirements with pre-built wheels only (avoids compilation)
        logger.info("Installing project dependencies...")
        
        # Set environment variables for binary-only installation
        env = os.environ.copy()
        env['PIP_ONLY_BINARY'] = ':all:'
        
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", 
             "-r", str(requirements_file),
             "--prefer-binary",
             "--no-build-isolation"],  # Use system python for building
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
        )
        
        if result.returncode == 0:
            logger.info("[OK] Dependencies installed successfully")
            return True
        else:
            logger.error(f"Failed to install dependencies: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Installation timed out")
        return False
    except Exception as e:
        logger.error(f"Error installing dependencies: {e}")
        return False


def get_test_files() -> List[Path]:
    """
    Get all test files from the tests/ directory.
    
    Returns:
        List of Path objects for test files.
    """
    tests_dir = Path("tests")
    
    if not tests_dir.exists():
        logger.error("tests/ directory not found")
        return []
    
    test_files = sorted(tests_dir.glob("*.py"))
    return test_files


def run_test_file(test_file: Path) -> Tuple[bool, str]:
    """
    Run a single test file and return the result.
    
    Args:
        test_file: Path to the test file.
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    try:
        # Add project root to Python path so tests can import app module
        env = os.environ.copy()
        project_root = str(Path.cwd())
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{project_root}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = project_root
        
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )
        
        output = result.stdout + result.stderr
        success = result.returncode == 0
        return success, output
        
    except subprocess.TimeoutExpired:
        return False, f"Test timed out: {test_file.name}"
    except Exception as e:
        return False, f"Error running test: {e}"


def run_all_tests(test_files: List[Path]) -> Tuple[int, int]:
    """
    Run all test files and log the results.
    
    Args:
        test_files: List of test file paths.
        
    Returns:
        Tuple of (passed_count, failed_count)
    """
    if not test_files:
        logger.warning("No test files found in tests/ directory")
        return 0, 0
    
    passed = 0
    failed = 0
    
    logger.info("=" * 60)
    logger.info("Running tests...")
    logger.info("=" * 60)
    
    for test_file in test_files:
        test_name = test_file.name
        logger.info(f"\nRunning: {test_name}")
        
        success, output = run_test_file(test_file)
        
        if success:
            logger.info(f"  [OK] PASSED")
            passed += 1
        else:
            logger.error(f"  [FAILED]")
            logger.error(f"Output: {output}")
            failed += 1
    
    logger.info("=" * 60)
    logger.info(f"Test Results Summary:")
    logger.info(f"  Passed: {passed}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Total:  {passed + failed}")
    logger.info("=" * 60)
    
    return passed, failed


def main():
    """Main entry point for the auto-test script."""
    logger.info("\n")
    logger.info("=" * 70)
    logger.info("Automatic Environment Detection and Test Runner")
    logger.info("=" * 70)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Step 1: Detect and display environment
    logger.info("Step 1: Detecting Python environment...")
    logger.info(get_python_version())
    logger.info(detect_environment())
    logger.info("")
    
    # Step 2: Check pip availability
    logger.info("Step 2: Checking pip availability...")
    if not check_pip_available():
        logger.error("pip is not available. Please install pip or check your Python setup.")
        return 1
    logger.info("[OK] pip is available")
    logger.info("")
    
    # Step 3: Install requirements
    logger.info("Step 3: Installing dependencies...")
    if not install_requirements():
        logger.error("Failed to install dependencies. Check logs above for details.")
        return 1
    logger.info("")
    
    # Step 4: Discover test files
    logger.info("Step 4: Discovering test files...")
    test_files = get_test_files()
    if test_files:
        logger.info(f"Found {len(test_files)} test file(s):")
        for test_file in test_files:
            logger.info(f"  - {test_file.name}")
    else:
        logger.warning("No test files found")
    logger.info("")
    
    # Step 5: Run tests
    logger.info("Step 5: Running tests...")
    passed, failed = run_all_tests(test_files)
    logger.info("")
    
    # Final summary
    logger.info("=" * 70)
    if failed == 0 and passed > 0:
        logger.info("[SUCCESS] ALL TESTS PASSED!")
        logger.info("=" * 70)
        logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Results saved to: {LOG_FILE.absolute()}")
        logger.info("")
        return 0
    else:
        logger.error(f"[ERROR] TEST EXECUTION FAILED: {failed} test(s) failed")
        logger.info("=" * 70)
        logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Results saved to: {LOG_FILE.absolute()}")
        logger.info("Check the log file for details.")
        logger.info("")
        return 1


if __name__ == "__main__":
    sys.exit(main())
