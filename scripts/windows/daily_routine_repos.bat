REM #TODO get current directory and then refer back to the daily_routine batch file relative to this directory.
REM Repo list is per-host (carried client repo names, #3098); read from a
REM gitignored file. Provision config\.windows-repos.local (one repo per line);
REM see config\.windows-repos.local.example.
set "REPO_LIST_FILE=%~dp0..\..\config\.windows-repos.local"
set "DAILY_ROUTINE=C:\Users\vamseea\github\assetutilities\src\assetutilities\tools\git\daily_routine.bat"

for /f "usebackq eol=# delims=" %%r in ("%REPO_LIST_FILE%") do (
    cd /d "C:\Users\vamseea\github\%%r"
    cmd /c "%DAILY_ROUTINE%"
)
