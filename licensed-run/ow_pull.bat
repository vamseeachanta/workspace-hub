@echo off
REM OrcaWave lane STEP 1+2: pull digitalmodel (#902) + the scope repo (#36),
REM confirm the env still imports, renormalize the new scope files to LF, and
REM hash input.yml for gate 9. Logs to runtime\ow_pull.log. Does NOT touch the
REM agent or the .sim. scope core.autocrlf is already false (set earlier).
setlocal
set "DM=C:\ws\digitalmodel"
if not defined LICENSED_RUN_SCOPE_REPO (echo ERROR: LICENSED_RUN_SCOPE_REPO is not set - see licensed-run\README.md & exit /b 2)
set "SCOPE_REPO=%LICENSED_RUN_SCOPE_REPO%"
set "VIRTUAL_ENV=C:\ws\digitalmodel\.venv"
set "OUT=C:\ws\workspace-hub\licensed-run\runtime\ow_pull.log"
echo === ow_pull %date% %time% === > "%OUT%"
echo --- digitalmodel pull (must include PR #902) --- >> "%OUT%"
git -C "%DM%" pull --rebase --autostash >> "%OUT%" 2>&1
echo dm HEAD: >> "%OUT%"
git -C "%DM%" log -1 --oneline >> "%OUT%" 2>&1
echo --- scope pull (PR #36) --- >> "%OUT%"
git -C "%SCOPE_REPO%" pull --rebase --autostash >> "%OUT%" 2>&1
echo scope HEAD: >> "%OUT%"
git -C "%SCOPE_REPO%" log -1 --oneline >> "%OUT%" 2>&1
cd /d "%SCOPE_REPO%"
echo --- files present in cases\orcawave-diffraction-solve --- >> "%OUT%"
dir /b cases\orcawave-diffraction-solve >> "%OUT%" 2>&1
echo --- renormalize new files to LF --- >> "%OUT%"
git config core.autocrlf false
del cases\orcawave-diffraction-solve\input.yml cases\orcawave-diffraction-solve\spec.yml cases\orcawave-diffraction-solve\unit_box.gdf 2>nul
git checkout -- cases/orcawave-diffraction-solve/
echo --- ls-files --eol (expect i/lf w/lf) --- >> "%OUT%"
git ls-files --eol cases/orcawave-diffraction-solve/ >> "%OUT%" 2>&1
echo --- CertUtil input.yml SHA256 (must = 0703eb9247b72e31f75a54bc4df68ef9a94fab77545978ef80e01522887fd359) --- >> "%OUT%"
CertUtil -hashfile cases\orcawave-diffraction-solve\input.yml SHA256 >> "%OUT%" 2>&1
echo --- digitalmodel --help (expect HELP_EXIT=0; confirms env imports new source) --- >> "%OUT%"
cd /d C:\ws
uv run python -m digitalmodel --help > nul 2>> "%OUT%"
echo HELP_EXIT=%ERRORLEVEL% >> "%OUT%"
echo --- done --- >> "%OUT%"
endlocal
