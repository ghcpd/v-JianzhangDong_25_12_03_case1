#!/bin/bash

# Test runner script for Linux/macOS
# Runs all test cases in the tests/ directory

set -e

echo "====================================="
echo "Running Test Suite..."
echo "====================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Create logs directory if it doesn't exist
mkdir -p logs

# Get timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/test_run.log"

# Clear previous log or create new one
echo "Test Run - $TIMESTAMP" > "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Run each test case
TEST_PASSED=0
TEST_FAILED=0

for test_file in tests/case_*.py; do
    if [ -f "$test_file" ]; then
        TEST_NAME=$(basename "$test_file")
        echo "Running $TEST_NAME..." | tee -a "$LOG_FILE"
        
        if python "$test_file" >> "$LOG_FILE" 2>&1; then
            echo "✓ $TEST_NAME PASSED" | tee -a "$LOG_FILE"
            ((TEST_PASSED++))
        else
            echo "✗ $TEST_NAME FAILED" | tee -a "$LOG_FILE"
            ((TEST_FAILED++))
        fi
        echo "" >> "$LOG_FILE"
    fi
done

# Summary
echo "======================================" | tee -a "$LOG_FILE"
echo "Test Summary:" | tee -a "$LOG_FILE"
echo "  Passed: $TEST_PASSED" | tee -a "$LOG_FILE"
echo "  Failed: $TEST_FAILED" | tee -a "$LOG_FILE"
echo "======================================" | tee -a "$LOG_FILE"

echo ""
echo "Logs saved to: $LOG_FILE"
echo "====================================="

# Exit with error if any tests failed
if [ $TEST_FAILED -gt 0 ]; then
    exit 1
fi
