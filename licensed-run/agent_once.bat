@echo off
REM Single test poll of the licensed-run agent (no continuous loop).
setlocal
if not defined LICENSED_RUN_SCOPE (echo ERROR: LICENSED_RUN_SCOPE is not set - see licensed-run\README.md & exit /b 2)
if not defined LICENSED_RUN_SCOPE_REPO (echo ERROR: LICENSED_RUN_SCOPE_REPO is not set - see licensed-run\README.md & exit /b 2)
set "HUB=C:\ws\workspace-hub\licensed-run"
set "VIRTUAL_ENV=C:\ws\digitalmodel\.venv"
set "DECKHAND_LICENSED_RUN_VERIFY_MARKER=%HUB%\runtime\licensed-run.verified.json"
echo START agent --once
"C:\ws\digitalmodel\.venv\Scripts\python.exe" "C:\ws\deckhand\scripts\deckhand\licensed-run-agent\agent.py" --queue-dir "C:\ws\deckhand-licensed-runs-queue\queue" --scope-root "%LICENSED_RUN_SCOPE%=%LICENSED_RUN_SCOPE_REPO%" --policy "%HUB%\runtime\policy.host-local.yml" --once
echo ONCE_EXIT=%ERRORLEVEL%
endlocal
