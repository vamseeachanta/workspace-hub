@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "ROOT=%~1"
if not defined ROOT set "ROOT=%SOLVER_CAMPAIGN_ROOT%"
if not defined ROOT set "ROOT=%CD%"
set "POLICY=%ROOT%\policy.json"
if exist "%POLICY%" (
  echo Policy already exists: "%POLICY%"
  exit /b 0
)
copy "%SCRIPT_DIR%policy.example.json" "%POLICY%" >nul
if not "%ERRORLEVEL%"=="0" (
  echo Policy file was not written.
  exit /b 1
)
echo Wrote "%POLICY%".
echo The workstation administrator edits repositories and limits before use.
exit /b 0
