@echo off
REM NON-DESTRUCTIVE scope worktree tidy after the autostash conflict. Resolves only
REM the repo-managed .gitattributes to its committed version; UNSTAGES (does not
REM discard) the README edits so you can review them; leaves the stash intact;
REM host-local-ignores heavy licensed outputs via .git/info/exclude (never commits
REM the tracked .gitignore). Re-verifies both input hashes. Logs to runtime\.
setlocal
if not defined LICENSED_RUN_SCOPE_REPO (echo ERROR: LICENSED_RUN_SCOPE_REPO is not set - see licensed-run\README.md & exit /b 2)
set "SCOPE_REPO=%LICENSED_RUN_SCOPE_REPO%"
set "EXCL=%SCOPE_REPO%\.git\info\exclude"
set "OUT=C:\ws\workspace-hub\licensed-run\runtime\ow_cleanup.log"
echo === ow_cleanup %date% %time% === > "%OUT%"
echo --- resolve .gitattributes conflict to committed (HEAD) version --- >> "%OUT%"
git -C "%SCOPE_REPO%" checkout HEAD -- .gitattributes >> "%OUT%" 2>&1
echo --- unstage README edits (kept in working tree for your review, NOT discarded) --- >> "%OUT%"
git -C "%SCOPE_REPO%" reset -q HEAD -- README.md projects/README.md >> "%OUT%" 2>&1
findstr /C:"licensed-run outputs" "%EXCL%" >nul 2>&1
if errorlevel 1 (
  echo.>> "%EXCL%"
  echo # licensed-run outputs - host-local, never committed>> "%EXCL%"
  echo cases/orcaflex-strength-post/results/>> "%EXCL%"
  echo cases/orcaflex-strength-post/logs/>> "%EXCL%"
  echo cases/orcaflex-strength-post/*.sim_error.log>> "%EXCL%"
  echo cases/orcawave-diffraction-solve/results/>> "%EXCL%"
  echo *.owr>> "%EXCL%"
  echo *.owd>> "%EXCL%"
)
echo --- status after cleanup (tracked-file cleanliness) --- >> "%OUT%"
git -C "%SCOPE_REPO%" status --porcelain >> "%OUT%" 2>&1
echo --- stash preserved for your review (NOT dropped) --- >> "%OUT%"
git -C "%SCOPE_REPO%" stash list >> "%OUT%" 2>&1
echo --- input hashes still intact --- >> "%OUT%"
CertUtil -hashfile "%SCOPE_REPO%\cases\orcaflex-strength-post\input.yml" SHA256 >> "%OUT%" 2>&1
CertUtil -hashfile "%SCOPE_REPO%\cases\orcawave-diffraction-solve\input.yml" SHA256 >> "%OUT%" 2>&1
echo --- done --- >> "%OUT%"
endlocal
