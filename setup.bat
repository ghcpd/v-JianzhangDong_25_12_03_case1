@echo off
REM setup.bat - Environment setup script for Windows

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo Environment Setup Script for Python Project
echo ===============================================
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Using: %PYTHON_VERSION%
echo.

REM Check for pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not installed.
    exit /b 1
)

echo Installing dependencies from requirements.txt...
pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 (
    echo ERROR: Failed to install tools.
    exit /b 1
)

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    exit /b 1
)

echo.
echo ===============================================
echo Environment setup completed successfully!
echo ===============================================
echo.
echo Next steps:
echo 1. Run tests: run_test.bat
echo 2. Or use auto-test: python auto_test.py
echo.
