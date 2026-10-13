@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHON_CMD="
where py.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 set "PYTHON_CMD=py.exe -3"
if not defined PYTHON_CMD (
  where python.exe >nul 2>nul
  if %ERRORLEVEL% EQU 0 set "PYTHON_CMD=python.exe"
)
if not defined PYTHON_CMD (
  echo Python was not found on PATH.
  exit /b 2
)
%PYTHON_CMD% "%SCRIPT_DIR%campaign_runner.py" run-once
exit /b %ERRORLEVEL%
