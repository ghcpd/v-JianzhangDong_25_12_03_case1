@echo off
setlocal
set "ROOT=%~dp0"
set "PY=python"

set "MPLBACKEND=Agg"
cd /d "%ROOT%"
"%PY%" auto_test.py %*
endlocal
