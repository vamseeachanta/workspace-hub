@echo off
REM Daily RAG Aggregation Task
REM Extracts session transcripts and aggregates learnings

set WORKSPACE_HUB=D:\workspace-hub
set LOG_DIR=%WORKSPACE_HUB%\.claude\skills\session-logs

echo [%date% %time%] Starting daily RAG aggregation >> "%LOG_DIR%\scheduler.log"

REM Use Git Bash explicitly (not WSL)
set GIT_BASH="C:\Program Files\Git\bin\bash.exe"

REM Run extraction script
%GIT_BASH% "%WORKSPACE_HUB%\.claude\hooks\extract-session-for-rag.sh" --today >> "%LOG_DIR%\scheduler.log" 2>&1

REM Run aggregation script
%GIT_BASH% "%WORKSPACE_HUB%\.claude\hooks\aggregate-learnings.sh" >> "%LOG_DIR%\scheduler.log" 2>&1

echo [%date% %time%] Completed daily RAG aggregation >> "%LOG_DIR%\scheduler.log"
