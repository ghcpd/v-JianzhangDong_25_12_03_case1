#!/bin/bash
# run_test.sh - Test runner script for Linux/macOS

set -e

echo "==============================================="
echo "Running Tests (Linux/macOS)"
echo "==============================================="
echo ""

# Detect Python version
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    exit 1
fi

echo "Python: $($PYTHON_CMD --version)"
echo ""

# Create logs directory
mkdir -p logs

# Run all test files
TEST_DIR="tests"
LOG_FILE="logs/test_run.log"

echo "Running tests from $TEST_DIR directory..."
echo "" | tee -a "$LOG_FILE"
echo "Test run started at $(date)" | tee -a "$LOG_FILE"
echo "======================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

FAILED=0
PASSED=0

for test_file in "$TEST_DIR"/*.py; do
    if [ -f "$test_file" ]; then
        test_name=$(basename "$test_file")
        echo "Running: $test_name" | tee -a "$LOG_FILE"
        if $PYTHON_CMD "$test_file" >> "$LOG_FILE" 2>&1; then
            echo "  ✓ PASSED" | tee -a "$LOG_FILE"
            ((PASSED++))
        else
            echo "  ✗ FAILED" | tee -a "$LOG_FILE"
            ((FAILED++))
        fi
        echo "" | tee -a "$LOG_FILE"
    fi
done

echo "======================================" | tee -a "$LOG_FILE"
echo "Test Results:" | tee -a "$LOG_FILE"
echo "  Passed: $PASSED" | tee -a "$LOG_FILE"
echo "  Failed: $FAILED" | tee -a "$LOG_FILE"
echo "Test run completed at $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

if [ $FAILED -eq 0 ]; then
    echo "✓ All tests passed!" | tee -a "$LOG_FILE"
    exit 0
else
    echo "✗ Some tests failed. See logs/test_run.log for details." | tee -a "$LOG_FILE"
    exit 1
fi
