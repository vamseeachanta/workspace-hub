@echo off
setlocal EnableExtensions

REM collect-machine-baseline.bat
REM Windows launcher for collect-machine-baseline.ps1.
REM Recommended: copy or run this from the workspace-hub repo root on the target machine.
REM Output is saved under docs\reports\machine-baseline when possible, else Desktop.

set "SCRIPT_DIR=%~dp0"
set "PS1=%SCRIPT_DIR%collect-machine-baseline.ps1"

if not exist "%PS1%" (
  echo ERROR: Missing PowerShell collector: %PS1%
  echo Run this .bat from scripts\operations\agent-execution\ or keep the .ps1 beside it.
  exit /b 1
)

echo Running machine baseline collector...
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo Collector exited with code %RC%.
  exit /b %RC%
)

echo.
echo Done. Send Hermes the printed TXT/JSON paths, or leave the files under workspace-hub\docs\reports\machine-baseline for collection.
endlocal
