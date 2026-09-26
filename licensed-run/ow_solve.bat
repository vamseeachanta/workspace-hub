@echo off
REM OrcaWave STEP 4: real local solve, mirroring the agent EXACTLY (cwd = scope
REM root, absolute input path, `uv run` from a non-project dir so no sync). If this
REM produces a completed solve, the dispatched run will too. Engine fails closed on
REM dry-run fallback, so SOLVE_EXIT=0 means it really solved. Outputs stay LOCAL
REM under the case dir's results\. Logs to runtime\ow_solve.log. Agent untouched.
setlocal
if not defined LICENSED_RUN_SCOPE_REPO (echo ERROR: LICENSED_RUN_SCOPE_REPO is not set - see licensed-run\README.md & exit /b 2)
set "SCOPE_REPO=%LICENSED_RUN_SCOPE_REPO%"
set "VIRTUAL_ENV=C:\ws\digitalmodel\.venv"
set "INPUT=%LICENSED_RUN_SCOPE_REPO%\cases\orcawave-diffraction-solve\input.yml"
set "OUT=C:\ws\workspace-hub\licensed-run\runtime\ow_solve.log"
echo === ow_solve %date% %time% === > "%OUT%"
cd /d "%SCOPE_REPO%"
echo --- STEP 4: run_orcawave solve (cwd=%SCOPE_REPO%, abs input) --- >> "%OUT%"
uv run python -m digitalmodel "%INPUT%" >> "%OUT%" 2>&1
echo SOLVE_EXIT=%ERRORLEVEL% >> "%OUT%"
echo --- results listing --- >> "%OUT%"
dir /s /b "%SCOPE_REPO%\cases\orcawave-diffraction-solve\results" >> "%OUT%" 2>&1
echo --- done --- >> "%OUT%"
endlocal
