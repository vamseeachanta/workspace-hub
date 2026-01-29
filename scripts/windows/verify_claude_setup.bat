@echo off
echo Claude Code Setup Verification
echo ==============================
echo.

REM Check if Claude CLI is installed
echo Checking Claude CLI installation...
where claude >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Claude CLI not found in PATH
    echo Please install Claude Code CLI first
    pause
    exit /b 1
) else (
    echo [OK] Claude CLI found
)

REM Check Claude version
echo.
echo Checking Claude CLI version...
claude --version
if %errorlevel% neq 0 (
    echo [WARNING] Could not get Claude version
) else (
    echo [OK] Claude CLI version check complete
)

REM Check VS Code integration
echo.
echo Checking VS Code installation...
where code >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] VS Code CLI not found in PATH
    echo VS Code may not be properly installed or configured
) else (
    echo [OK] VS Code CLI found
)

REM Check Git Bash
echo.
echo Checking Git Bash installation...
if exist "C:\Program Files\Git\bin\bash.exe" (
    echo [OK] Git Bash found at standard location
) else (
    echo [WARNING] Git Bash not found at expected location
)

REM Check repositories and CLAUDE.md files
echo.
echo Checking repositories and CLAUDE.md files...
set "repos=aceengineer-admin achantas-data client_projects doris ecs energy hobbies investments OGManufacturing predyct rock-oil-field saipem seanation spire_projects"

for %%r in (%repos%) do (
    if exist "C:\Users\vamseea\github\%%r\.git" (
        if exist "C:\Users\vamseea\github\%%r\CLAUDE.md" (
            echo [OK] %%r - Repository with CLAUDE.md
        ) else (
            echo [WARNING] %%r - Repository missing CLAUDE.md
        )
    ) else (
        echo [WARNING] %%r - Not a git repository
    )
)

echo.
echo Setup verification complete!
echo.
echo To use Claude Code:
echo 1. Open VS Code terminal (Git Bash is default)
echo 2. Navigate to any repository: cd /c/Users/vamseea/github/[repo-name]
echo 3. Run: claude
echo.
echo For easy repository switching, run: claude_repo_switcher.bat
echo.
pause