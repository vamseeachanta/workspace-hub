@echo off
setlocal enabledelayedexpansion
echo Claude Code Repository Switcher
echo ================================
echo.

REM Repo list is per-host (carried client repo names, #3098); read from a
REM gitignored file. Provision config\.windows-repos.local (one repo per line);
REM see config\.windows-repos.local.example. The numbered menu and the
REM choice->repo mapping are generated from that list.
set "REPO_LIST_FILE=%~dp0..\..\config\.windows-repos.local"
if not exist "%REPO_LIST_FILE%" (
    echo Error: repo list not found: %REPO_LIST_FILE%
    echo Provision it from config\.windows-repos.local.example
    pause
    exit /b 1
)

echo Available repositories:
set /a count=0
for /f "usebackq eol=# delims=" %%r in ("%REPO_LIST_FILE%") do (
    set /a count+=1
    set "repo[!count!]=%%r"
    echo !count!. %%r
)
echo.
set /p choice="Select repository (1-!count!): "

set "repo=!repo[%choice%]!"

if "%repo%"=="" (
    echo Invalid selection!
    pause
    exit /b 1
)

echo.
echo Opening VS Code in repository: %repo%
echo Repository path: C:\Users\vamseea\github\%repo%
echo.

REM Check if repository exists
if not exist "C:\Users\vamseea\github\%repo%" (
    echo Error: Repository %repo% not found!
    pause
    exit /b 1
)

REM Open VS Code in the repository
code "C:\Users\vamseea\github\%repo%"

REM Open Git Bash in the repository directory
start "" "C:\Program Files\Git\git-bash.exe" --cd="C:\Users\vamseea\github\%repo%"

echo.
echo To use Claude Code in this repository:
echo 1. Git Bash terminal opened in repository directory
echo 2. Verify you're in the repository: pwd
echo 3. Run: claude
echo.
echo Repository %repo% is now ready for Claude Code!
pause
