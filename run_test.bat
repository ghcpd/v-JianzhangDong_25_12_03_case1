@echo off
REM run_test.bat - Test runner script for Windows

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo Running Tests (Windows)
echo ===============================================
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo %PYTHON_VERSION%
echo.

REM Create logs directory
if not exist logs mkdir logs

REM Initialize counters
set PASSED=0
set FAILED=0

REM Run all test files
echo Running tests from tests directory...
echo. >> logs\test_run.log
echo Test run started at %date% %time% >> logs\test_run.log
echo ====================================== >> logs\test_run.log
echo. >> logs\test_run.log

for %%F in (tests\*.py) do (
    set TEST_FILE=%%F
    set TEST_NAME=%%~nF
    
    echo Running: !TEST_NAME!
    echo Running: !TEST_NAME! >> logs\test_run.log
    
    python "!TEST_FILE!" >> logs\test_run.log 2>&1
    if !errorlevel! equ 0 (
        echo   [OK] PASSED
        echo   [OK] PASSED >> logs\test_run.log
        set /a PASSED=!PASSED!+1
    ) else (
        echo   [FAILED]
        echo   [FAILED] >> logs\test_run.log
        set /a FAILED=!FAILED!+1
    )
    echo. >> logs\test_run.log
)

REM Print summary
echo.
echo ======================================
echo Test Results:
echo   Passed: %PASSED%
echo   Failed: %FAILED%
echo Test run completed at %date% %time%
echo.

echo. >> logs\test_run.log
echo ====================================== >> logs\test_run.log
echo Test Results: >> logs\test_run.log
echo   Passed: %PASSED% >> logs\test_run.log
echo   Failed: %FAILED% >> logs\test_run.log
echo Test run completed at %date% %time% >> logs\test_run.log
echo. >> logs\test_run.log

if %FAILED% equ 0 (
    echo [SUCCESS] All tests passed!
    echo [SUCCESS] All tests passed! >> logs\test_run.log
    exit /b 0
) else (
    echo [ERROR] Some tests failed. See logs\test_run.log for details.
    echo [ERROR] Some tests failed. See logs\test_run.log for details. >> logs\test_run.log
    exit /b 1
)
