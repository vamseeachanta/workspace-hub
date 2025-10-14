@echo off
REM Open Git Bash in current working directory
REM Usage: open_gitbash_here.bat [optional_path]

if "%1"=="" (
    REM No argument provided, use current directory
    start "" "C:\Program Files\Git\git-bash.exe" --cd="%CD%"
) else (
    REM Path provided as argument
    if exist "%~1" (
        start "" "C:\Program Files\Git\git-bash.exe" --cd="%~1"
    ) else (
        echo Error: Path "%~1" does not exist!
        pause
        exit /b 1
    )
)
