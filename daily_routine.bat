@echo off
REM Navigate to current directory in Git Bash before running git commands
set mydate=%date:~10,4%%date:~7,2%%date:~4,2%

REM Ensure we're in the correct directory
cd /d "%~dp0"

git pull
git add --all
git commit -m %mydate%
git push
