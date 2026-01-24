@echo off
REM run-reflection.bat - Windows wrapper for scheduled RAGS reflection
REM
REM Usage:
REM   1. Open Task Scheduler
REM   2. Create new task with trigger: Daily at 5:00 AM
REM   3. Action: Start a program
REM      Program: D:\workspace-hub\.claude\skills\workspace-hub\claude-reflect\scripts\run-reflection.bat
REM

SET WORKSPACE_HUB=D:\workspace-hub
SET GIT_BASH=C:\Program Files\Git\bin\bash.exe

REM Check if Git Bash exists
IF NOT EXIST "%GIT_BASH%" (
    echo ERROR: Git Bash not found at %GIT_BASH%
    exit /b 1
)

REM Run the bash script via Git Bash
"%GIT_BASH%" -c "cd /d/workspace-hub && /d/workspace-hub/.claude/skills/workspace-hub/claude-reflect/scripts/run-reflection.sh --days 30"

exit /b %ERRORLEVEL%
