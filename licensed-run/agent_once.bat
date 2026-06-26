@echo off
REM Single test poll of the licensed-run agent (no continuous loop).
setlocal
set "HUB=C:\ws\workspace-hub\licensed-run"
set "VIRTUAL_ENV=C:\ws\digitalmodel\.venv"
set "DECKHAND_LICENSED_RUN_VERIFY_MARKER=%HUB%\runtime\licensed-run.verified.json"
echo START agent --once
"C:\ws\digitalmodel\.venv\Scripts\python.exe" "C:\ws\deckhand\scripts\deckhand\licensed-run-agent\agent.py" --queue-dir "C:\ws\deckhand-licensed-runs-queue\queue" --scope-root "acma=C:\ws\llm-wiki-acma" --policy "%HUB%\runtime\policy.host-local.yml" --once
echo ONCE_EXIT=%ERRORLEVEL%
endlocal
