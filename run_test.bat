@echo off
REM Test runner script for Windows
REM Runs all test cases in the tests/ directory

echo =====================================
echo Running Test Suite...
echo =====================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo Error: Virtual environment not found. Please run setup first.
    echo Run: python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Create logs directory if it doesn't exist
if not exist "logs\" mkdir logs

REM Get timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set LOG_FILE=logs\test_run.log

REM Clear previous log or create new one
echo Test Run - %TIMESTAMP% > "%LOG_FILE%"
echo ====================================== >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Run each test case
set TEST_PASSED=0
set TEST_FAILED=0

for %%f in (tests\case_*.py) do (
    echo Running %%~nxf... | tee -a "%LOG_FILE%"
    
    python "%%f" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo X %%~nxf FAILED | tee -a "%LOG_FILE%"
        set /a TEST_FAILED+=1
    ) else (
        echo √ %%~nxf PASSED | tee -a "%LOG_FILE%"
        set /a TEST_PASSED+=1
    )
    echo. >> "%LOG_FILE%"
)

REM Summary
echo ====================================== | tee -a "%LOG_FILE%"
echo Test Summary: | tee -a "%LOG_FILE%"
echo   Passed: %TEST_PASSED% | tee -a "%LOG_FILE%"
echo   Failed: %TEST_FAILED% | tee -a "%LOG_FILE%"
echo ====================================== | tee -a "%LOG_FILE%"

echo.
echo Logs saved to: %LOG_FILE%
echo =====================================

REM Exit with error if any tests failed
if %TEST_FAILED% gtr 0 exit /b 1
