@echo off
REM Continuous licensed-run poller for ace-win-2 (acma). Heartbeat loop: each cycle
REM is one agent --once poll (git-pull queue, run approved requests through the gates,
REM commit metadata-only result). Logs every cycle to runtime\agent_poll.log so it can
REM be watched without copy-paste. Leave this window OPEN. Ctrl+C to stop.
setlocal
set "HUB=C:\ws\workspace-hub\licensed-run"
set "VIRTUAL_ENV=C:\ws\digitalmodel\.venv"
set "DECKHAND_LICENSED_RUN_VERIFY_MARKER=%HUB%\runtime\licensed-run.verified.json"
if not exist "%HUB%\runtime" mkdir "%HUB%\runtime"
echo [poller started] %date% %time% > "%HUB%\runtime\agent_poll.log"
echo Polling every 15s -- logging to %HUB%\runtime\agent_poll.log -- leave this window open
:loop
echo [poll] %date% %time% >> "%HUB%\runtime\agent_poll.log"
"C:\ws\digitalmodel\.venv\Scripts\python.exe" "C:\ws\deckhand\scripts\deckhand\licensed-run-agent\agent.py" --queue-dir "C:\ws\deckhand-licensed-runs-queue\queue" --scope-root "acma=C:\ws\llm-wiki-acma" --policy "%HUB%\runtime\policy.host-local.yml" --once >> "%HUB%\runtime\agent_poll.log" 2>&1
timeout /t 15 /nobreak > nul
goto loop
