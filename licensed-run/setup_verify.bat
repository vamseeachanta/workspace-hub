@echo off
REM One-time host setup: regenerate the host-local policy override (execution_enabled
REM true) into runtime\, then run verify-first (writes the marker into runtime\ on
REM 9/9 PASS). Re-run any time prerequisites change. Output -> runtime\verify.log too.
setlocal
set "HUB=C:\ws\workspace-hub\licensed-run"
set "VIRTUAL_ENV=C:\ws\digitalmodel\.venv"
if not exist "%HUB%\runtime" mkdir "%HUB%\runtime"
echo Regenerating host-local policy override (execution_enabled: true) ...
powershell -NoProfile -Command "(Get-Content 'C:\ws\deckhand\config\deckhand\policy.yml') -replace 'execution_enabled: false','execution_enabled: true' | Set-Content '%HUB%\runtime\policy.host-local.yml'"
echo Running verify-ace-win-2 ...
"C:\ws\digitalmodel\.venv\Scripts\python.exe" "C:\ws\deckhand\scripts\deckhand\verify-ace-win-2.py" --scope-repo "C:\ws\llm-wiki-acma" --results-dir "C:\ws\deckhand-licensed-results" --queue-dir "C:\ws\deckhand-licensed-runs-queue\queue" --marker "%HUB%\runtime\licensed-run.verified.json"
echo VERIFY_EXIT=%ERRORLEVEL%
endlocal
