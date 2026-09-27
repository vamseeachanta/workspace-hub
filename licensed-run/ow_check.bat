@echo off
REM OrcaWave lane: worktree-hygiene check + confirm #902 present + STEP 3 license
REM gate (orcawave-doctor). Read-only except nothing is changed. Logs to
REM runtime\ow_check.log. Does NOT touch the agent.
setlocal
if not defined LICENSED_RUN_SCOPE_REPO (echo ERROR: LICENSED_RUN_SCOPE_REPO is not set - see licensed-run\README.md & exit /b 2)
set "SCOPE_REPO=%LICENSED_RUN_SCOPE_REPO%"
set "DM=C:\ws\digitalmodel"
set "VIRTUAL_ENV=C:\ws\digitalmodel\.venv"
set "OUT=C:\ws\workspace-hub\licensed-run\runtime\ow_check.log"
echo === ow_check %date% %time% === > "%OUT%"
echo --- scope git status --porcelain (tracked-file cleanliness) --- >> "%OUT%"
git -C "%SCOPE_REPO%" status --porcelain >> "%OUT%" 2>&1
echo --- scope stash list --- >> "%OUT%"
git -C "%SCOPE_REPO%" stash list >> "%OUT%" 2>&1
echo --- orcaflex input.yml SHA256 (expect 6fc6e7920344084f...) --- >> "%OUT%"
CertUtil -hashfile "%SCOPE_REPO%\cases\orcaflex-strength-post\input.yml" SHA256 >> "%OUT%" 2>&1
echo --- digitalmodel history grep for #902 / orcawave --- >> "%OUT%"
git -C "%DM%" log --oneline -40 | findstr /C:"#902" /C:"orcawave" /C:"run_orcawave" >> "%OUT%" 2>&1
echo --- STEP 3: orcawave-doctor (is the OrcaWave SOLVER licensed?) --- >> "%OUT%"
cd /d "%DM%"
uv run python -m digitalmodel diffraction orcawave-doctor >> "%OUT%" 2>&1
echo DOCTOR_EXIT=%ERRORLEVEL% >> "%OUT%"
echo --- done --- >> "%OUT%"
endlocal
