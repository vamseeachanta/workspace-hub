@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "MODE=batch"
set "MODE_SET="
set "ROOT="
set "DRY_RUN="
rem BEGIN_ARGUMENT_PARSE
:parse_args
if "%~1"=="" goto args_done
set "ARG=%~1"
if /I "%ARG%"=="--dry-run" (
  set "DRY_RUN=1"
  shift
  goto parse_args
)
if "%ARG:~0,1%"=="-" goto arg_error
if "%ARG:~0,1%"=="/" goto arg_error
if /I "%ARG%"=="batch" (
  if defined MODE_SET goto arg_error
  set "MODE=batch"
  set "MODE_SET=1"
  shift
  goto parse_args
)
if /I "%ARG%"=="batch-password" (
  if defined MODE_SET goto arg_error
  set "MODE=batch-password"
  set "MODE_SET=1"
  shift
  goto parse_args
)
if /I "%ARG%"=="desktop" (
  if defined MODE_SET goto arg_error
  set "MODE=desktop"
  set "MODE_SET=1"
  shift
  goto parse_args
)
if not defined ROOT (
  set "ROOT=%ARG%"
  shift
  goto parse_args
)
goto arg_error
:args_done
if not defined ROOT goto missing_root
set ROOT | "%SystemRoot%\System32\find.exe" "(" >nul && goto unsafe_root
set ROOT | "%SystemRoot%\System32\find.exe" ")" >nul && goto unsafe_root
set ROOT | "%SystemRoot%\System32\find.exe" "&" >nul && goto unsafe_root
set ROOT | "%SystemRoot%\System32\find.exe" "^^" >nul && goto unsafe_root
set ROOT | "%SystemRoot%\System32\find.exe" "%%" >nul && goto unsafe_root
set ROOT | "%SystemRoot%\System32\find.exe" "!" >nul && goto unsafe_root
if not exist "%ROOT%\" goto missing_root
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
rem END_ARGUMENT_PARSE
goto mode_ok
:missing_root
echo Campaign root must be an existing folder.
exit /b 2
:unsafe_root
echo Campaign root contains unsupported characters: ( ) ^& ^^ %% !
exit /b 2
:arg_error
echo Usage: register-solver-campaign-task.bat [batch^|batch-password^|desktop] root [--dry-run]
exit /b 2
:mode_ok
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
  echo Resolved campaign root: "%ROOT%"
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
  echo Earlier task of the same name was replaced and then removed after readback failed.
  call :cleanup_registration
  del "%TASK_XML%" >nul 2>nul
  del "%TASK_XML%.readback" >nul 2>nul
  exit /b 1
)
%PYTHON_CMD% "%SCRIPT_DIR%campaign_runner.py" task-readback "%TASK_XML%.readback" --expected-logon "%EXPECTED_LOGON%" --account "%ACCOUNT%"
if not "%ERRORLEVEL%"=="0" (
  echo Earlier task of the same name was replaced and then removed after readback mismatch.
  call :cleanup_registration
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

:cleanup_registration
schtasks /Delete /TN "%TASK_NAME%" /F
set "DELETE_RC=%ERRORLEVEL%"
if "%DELETE_RC%"=="0" echo Cleanup deletion completed.
if not "%DELETE_RC%"=="0" echo Cleanup deletion failed with exit code %DELETE_RC%.
exit /b %DELETE_RC%
:after_cleanup_registration
