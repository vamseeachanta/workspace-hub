@echo off
REM OrcaWave STEP 3 (license gate) the SAFE way: invoke the venv python DIRECTLY
REM (no `uv run`, so it can never trigger a project sync). Also confirms the venv
REM survived the earlier failed sync. Logs to runtime\ow_doctor.log. cwd is neutral
REM (C:\ws) so nothing project-related is touched. Does NOT touch the agent.
setlocal
set "VENV_PY=C:\ws\digitalmodel\.venv\Scripts\python.exe"
set "VIRTUAL_ENV=C:\ws\digitalmodel\.venv"
set "OUT=C:\ws\workspace-hub\licensed-run\runtime\ow_doctor.log"
cd /d C:\ws
echo === ow_doctor %date% %time% === > "%OUT%"
echo --- venv intact? import digitalmodel + OrcFxAPI (venv python, no uv) --- >> "%OUT%"
"%VENV_PY%" -c "import digitalmodel; print('digitalmodel ok'); import OrcFxAPI; print('OrcFxAPI ok', OrcFxAPI.DLLVersion())" >> "%OUT%" 2>&1
echo VENV_IMPORT_EXIT=%ERRORLEVEL% >> "%OUT%"
echo --- STEP 3: orcawave-doctor (is the OrcaWave SOLVER licensed?) --- >> "%OUT%"
"%VENV_PY%" -m digitalmodel diffraction orcawave-doctor >> "%OUT%" 2>&1
echo DOCTOR_EXIT=%ERRORLEVEL% >> "%OUT%"
echo --- done --- >> "%OUT%"
endlocal
