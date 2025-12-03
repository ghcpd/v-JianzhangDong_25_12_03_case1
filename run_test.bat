@echo off
setlocal

if "%PYTHON_BIN%"=="" set PYTHON_BIN=python

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

%PYTHON_BIN% "%ROOT%\auto_test.py" --skip-install

endlocal
