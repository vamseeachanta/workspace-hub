@echo off
setlocal
set "TASK_NAME=solver-campaign-runner"
set "ROOT=%~1"
if not defined ROOT set "ROOT=%SOLVER_CAMPAIGN_ROOT%"
if not defined ROOT set "ROOT=%CD%"
schtasks /Delete /TN "%TASK_NAME%" /F
set "RC=%ERRORLEVEL%"
if "%RC%"=="0" (
  if exist "%ROOT%\task-mode.txt" del "%ROOT%\task-mode.txt"
  echo Unregistered solver campaign runner scheduled task.
) else (
  echo Scheduled task was not removed or was not present.
)
exit /b %RC%
