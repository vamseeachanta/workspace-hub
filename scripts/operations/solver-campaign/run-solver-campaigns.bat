@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "ROOT=%~1"
if not defined ROOT set "ROOT=%SOLVER_CAMPAIGN_ROOT%"
set "PYTHON_CMD="
where py.exe >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py.exe -3"
if not defined PYTHON_CMD (
  where python.exe >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python.exe"
)
if not defined PYTHON_CMD (
  echo Python was not found on PATH.
  exit /b 2
)
if defined ROOT (
  if not exist "%ROOT%\state" mkdir "%ROOT%\state"
  %PYTHON_CMD% "%SCRIPT_DIR%campaign_runner.py" run-once --root "%ROOT%" >> "%ROOT%\state\task-runner.log" 2>&1
) else (
  %PYTHON_CMD% "%SCRIPT_DIR%campaign_runner.py" run-once
)
exit /b %ERRORLEVEL%
