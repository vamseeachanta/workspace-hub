@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "WRAPPER=%SCRIPT_DIR%run-solver-campaigns.bat"
set "TASK_MINUTE=solver-campaign-runner"
set "TASK_LOGON=solver-campaign-runner-logon"
set "ACTION=powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \"%WRAPPER%\""
set "REGISTERED=0"

schtasks /Create /TN "%TASK_MINUTE%" /TR "%ACTION%" /SC MINUTE /MO 10 /IT /F
if %ERRORLEVEL% EQU 0 set "REGISTERED=1"
schtasks /Create /TN "%TASK_LOGON%" /TR "%ACTION%" /SC ONLOGON /IT /F
if %ERRORLEVEL% NEQ 0 echo Logon trigger registration failed; the 10-minute trigger may still be registered.
if "%REGISTERED%"=="0" exit /b 1
schtasks /Query /TN "%TASK_MINUTE%" /FO LIST /V
schtasks /Query /TN "%TASK_LOGON%" /FO LIST /V
echo Registered solver campaign runner scheduled tasks.
exit /b 0
