@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "MODE=batch"
set "MODE_SET="
set "ROOT="
:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--dry-run" (
  set "DRY_RUN=1"
  shift
  goto parse_args
)
if /I "%~1"=="batch" (
  if defined MODE_SET goto arg_error
  set "MODE=batch"
  set "MODE_SET=1"
  shift
  goto parse_args
)
if /I "%~1"=="batch-password" (
  if defined MODE_SET goto arg_error
  set "MODE=batch-password"
  set "MODE_SET=1"
  shift
  goto parse_args
)
if /I "%~1"=="desktop" (
  if defined MODE_SET goto arg_error
  set "MODE=desktop"
  set "MODE_SET=1"
  shift
  goto parse_args
)
if not defined ROOT (
  set "ROOT=%~1"
  shift
  goto parse_args
)
:arg_error
echo Usage: register-solver-campaign-task.bat [batch^|batch-password^|desktop] [root] [--dry-run]
exit /b 2
:args_done
if not defined MODE set "MODE=batch"
if /I "%MODE%"=="batch" goto mode_ok
if /I "%MODE%"=="batch-password" goto mode_ok
if /I "%MODE%"=="desktop" goto mode_ok
echo Modes: batch, batch-password, desktop.
exit /b 2
:mode_ok
if not defined ROOT set "ROOT=%SOLVER_CAMPAIGN_ROOT%"
if not defined ROOT set "ROOT=%CD%"
set "WRAPPER=%SCRIPT_DIR%run-solver-campaigns.bat"
set "TASK_NAME=solver-campaign-runner"
set "TASK_XML=%TEMP%\solver-campaign-runner-%RANDOM%.xml"
set "ACCOUNT=%USERDOMAIN%\%USERNAME%"
set "EXPECTED_LOGON=S4U"
if /I "%MODE%"=="batch-password" set "EXPECTED_LOGON=Password"
if /I "%MODE%"=="desktop" set "EXPECTED_LOGON=InteractiveToken"
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
%PYTHON_CMD% "%SCRIPT_DIR%campaign_runner.py" task-definition "%MODE%" --account "%ACCOUNT%" --wrapper "%WRAPPER%" --campaign-root "%ROOT%" --output "%TASK_XML%"
if not "%ERRORLEVEL%"=="0" (
  echo Task definition was not written.
  exit /b 1
)
type "%TASK_XML%"
if defined DRY_RUN (
  del "%TASK_XML%" >nul 2>nul
  exit /b 0
)
if /I "%MODE%"=="batch-password" (
  schtasks /Create /TN "%TASK_NAME%" /XML "%TASK_XML%" /RU "%ACCOUNT%" /RP * /F
) else (
  schtasks /Create /TN "%TASK_NAME%" /XML "%TASK_XML%" /F
)
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo Task registration failed. Check rights for the selected mode.
  del "%TASK_XML%" >nul 2>nul
  exit /b %RC%
)
schtasks /Query /TN "%TASK_NAME%" /XML > "%TASK_XML%.readback"
if not "%ERRORLEVEL%"=="0" (
  echo Task readback failed.
  schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>nul
  del "%TASK_XML%" >nul 2>nul
  del "%TASK_XML%.readback" >nul 2>nul
  exit /b 1
)
findstr /I /C:"<LogonType>" "%TASK_XML%.readback"
findstr /I /C:"<LogonType>%EXPECTED_LOGON%</LogonType>" "%TASK_XML%.readback" >nul
if not "%ERRORLEVEL%"=="0" (
  echo Registered task logon type did not match requested mode.
  schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>nul
  del "%TASK_XML%" >nul 2>nul
  del "%TASK_XML%.readback" >nul 2>nul
  exit /b 1
)
if not exist "%ROOT%\state" mkdir "%ROOT%\state"
echo %MODE%>"%ROOT%\task-mode.txt"
del "%TASK_XML%" >nul 2>nul
del "%TASK_XML%.readback" >nul 2>nul
echo Registered solver campaign runner scheduled task in %MODE% mode.
exit /b 0
