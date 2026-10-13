@echo off
setlocal
set "TASK_MINUTE=solver-campaign-runner"
set "TASK_LOGON=solver-campaign-runner-logon"
schtasks /Delete /TN "%TASK_MINUTE%" /F
set "RC1=%ERRORLEVEL%"
schtasks /Delete /TN "%TASK_LOGON%" /F
set "RC2=%ERRORLEVEL%"
echo Unregistered solver campaign runner scheduled tasks where present.
if not "%RC1%"=="0" if not "%RC2%"=="0" exit /b 1
exit /b 0
