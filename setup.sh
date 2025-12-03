#!/bin/bash
# setup.sh - Environment setup script for Linux/macOS

set -e

echo "==============================================="
echo "Environment Setup Script for Python Project"
echo "==============================================="

# Detect Python version
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
echo "Using: $PYTHON_VERSION"

# Check for pip
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "ERROR: pip is not installed."
    exit 1
fi

PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "Using: $PIP_CMD"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
$PIP_CMD install --upgrade pip setuptools wheel
$PIP_CMD install -r requirements.txt

echo ""
echo "==============================================="
echo "Environment setup completed successfully!"
echo "==============================================="
echo ""
echo "Next steps:"
echo "1. Run tests: bash run_test.sh"
echo "2. Or use auto-test: python auto_test.py"
