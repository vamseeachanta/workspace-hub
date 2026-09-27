@echo off
REM Deploy #481 + sync for the FPSO OrcaWave unblock. STEP 0 status, STEP 1 ff-only
REM pulls, #481 confirmation, STEP 2 input hash. Non-destructive (ff-only; only
REM resolves the leftover .gitattributes to its committed version so the scope pull
REM isn't blocked). Logs to runtime\ow_sync.log. Does NOT touch the agent/queue.
setlocal
set "DECK=C:\ws\deckhand"
set "DM=C:\ws\digitalmodel"
if not defined LICENSED_RUN_SCOPE_REPO (echo ERROR: LICENSED_RUN_SCOPE_REPO is not set - see licensed-run\README.md & exit /b 2)
set "SCOPE_REPO=%LICENSED_RUN_SCOPE_REPO%"
set "QUEUE=C:\ws\deckhand-licensed-runs-queue"
set "OUT=C:\ws\workspace-hub\licensed-run\runtime\ow_sync.log"
echo === ow_sync %date% %time% === > "%OUT%"

echo ===== STEP 0: status (remote / branch / dirty) ===== >> "%OUT%"
echo --- deckhand --- >> "%OUT%"
git -C "%DECK%" remote get-url origin >> "%OUT%" 2>&1
git -C "%DECK%" rev-parse --abbrev-ref HEAD >> "%OUT%" 2>&1
git -C "%DECK%" status --porcelain >> "%OUT%" 2>&1
echo --- digitalmodel --- >> "%OUT%"
git -C "%DM%" remote get-url origin >> "%OUT%" 2>&1
git -C "%DM%" rev-parse --abbrev-ref HEAD >> "%OUT%" 2>&1
git -C "%DM%" status --porcelain >> "%OUT%" 2>&1
echo --- the scope repo --- >> "%OUT%"
git -C "%SCOPE_REPO%" remote get-url origin >> "%OUT%" 2>&1
git -C "%SCOPE_REPO%" rev-parse --abbrev-ref HEAD >> "%OUT%" 2>&1
git -C "%SCOPE_REPO%" status --porcelain >> "%OUT%" 2>&1
echo --- queue --- >> "%OUT%"
git -C "%QUEUE%" remote get-url origin >> "%OUT%" 2>&1
git -C "%QUEUE%" rev-parse --abbrev-ref HEAD >> "%OUT%" 2>&1
git -C "%QUEUE%" status --porcelain >> "%OUT%" 2>&1

echo ===== STEP 1: ff-only sync ===== >> "%OUT%"
echo --- deckhand --- >> "%OUT%"
git -C "%DECK%" pull --ff-only >> "%OUT%" 2>&1
echo --- digitalmodel --- >> "%OUT%"
git -C "%DM%" pull --ff-only >> "%OUT%" 2>&1
echo --- scope (resolve leftover .gitattributes first, non-destructive) --- >> "%OUT%"
git -C "%SCOPE_REPO%" checkout HEAD -- .gitattributes >> "%OUT%" 2>&1
git -C "%SCOPE_REPO%" pull --ff-only >> "%OUT%" 2>&1

echo ===== #481 deploy confirmation ===== >> "%OUT%"
echo --- _sync_scope_repo in licensed_run_agent.py? --- >> "%OUT%"
findstr /C:"_sync_scope_repo" "%DECK%\src\deckhand\licensed_run_agent.py" >> "%OUT%" 2>&1
echo --- scope_autopull in policy.yml? --- >> "%OUT%"
findstr /C:"scope_autopull" "%DECK%\config\deckhand\policy.yml" >> "%OUT%" 2>&1
echo --- deckhand recent log (481/477) --- >> "%OUT%"
git -C "%DECK%" log --oneline -30 | findstr /C:"481" /C:"477" >> "%OUT%" 2>&1

echo ===== scope HEAD + FPSO input + STEP 2 hash ===== >> "%OUT%"
echo scope HEAD (expect 87df574): >> "%OUT%"
git -C "%SCOPE_REPO%" rev-parse --short HEAD >> "%OUT%" 2>&1
echo --- force-renormalize input.yml to LF (autocrlf already false) --- >> "%OUT%"
del "%SCOPE_REPO%\cases\orcawave-diffraction-fpso\input.yml" 2>nul
git -C "%SCOPE_REPO%" checkout -- "cases/orcawave-diffraction-fpso/input.yml" >> "%OUT%" 2>&1
if exist "%SCOPE_REPO%\cases\orcawave-diffraction-fpso\input.yml" (echo FPSO input.yml: YES>> "%OUT%") else (echo FPSO input.yml: NO>> "%OUT%")
echo SHA256 (expect c511e0e7dab266bf989c2a03ce022982448bf56bb2a03c28d1df45104197218a): >> "%OUT%"
CertUtil -hashfile "%SCOPE_REPO%\cases\orcawave-diffraction-fpso\input.yml" SHA256 >> "%OUT%" 2>&1
echo --- ls-files --eol --- >> "%OUT%"
git -C "%SCOPE_REPO%" ls-files --eol cases/orcawave-diffraction-fpso/ >> "%OUT%" 2>&1
echo === done === >> "%OUT%"
endlocal
