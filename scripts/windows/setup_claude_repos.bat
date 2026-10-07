@echo off
echo Setting up Claude Code for all repositories...

REM Repo list is per-host (carried client repo names, #3098); read from a
REM gitignored file. Provision config\.windows-repos.local (one repo per line);
REM see config\.windows-repos.local.example.
set "REPO_LIST_FILE=%~dp0..\..\config\.windows-repos.local"
set "repos="
if exist "%REPO_LIST_FILE%" (
    for /f "usebackq eol=# delims=" %%r in ("%REPO_LIST_FILE%") do call set "repos=%%repos%% %%r"
)

for %%r in (%repos%) do (
    echo.
    echo Configuring repository: %%r
    
    REM Check if repository exists
    if exist "%USERPROFILE%\github\%%r\.git" (
        echo Repository %%r found
        
        REM Check if CLAUDE.md already exists
        if not exist "%USERPROFILE%\github\%%r\CLAUDE.md" (
            echo Creating CLAUDE.md for %%r
            
            REM Create basic CLAUDE.md
            echo # Claude Code Configuration for %%r > "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo. >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo ## Repository Overview >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo This repository contains project files and documentation for %%r. >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo. >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo ## Development Environment >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo - Use Git Bash terminal in VS Code >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo - Python environment managed via conda >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo - Follow existing code patterns and conventions >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo. >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo ## Project Structure >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo See README.md for detailed project structure and setup instructions. >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo. >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo ## Notes >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo - Always check existing patterns before making changes >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo - Use appropriate tools based on repository content >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            echo - Maintain consistent formatting and documentation >> "%USERPROFILE%\github\%%r\CLAUDE.md"
            
            echo CLAUDE.md created for %%r
        ) else (
            echo CLAUDE.md already exists for %%r
        )
    ) else (
        echo Warning: Repository %%r not found or not a git repository
    )
)

echo.
echo Claude Code setup complete for all repositories!
echo.
echo To use Claude Code in any repository:
echo 1. Open VS Code terminal (Git Bash is default)
echo 2. Navigate to the repository: cd /c/Users/vamseea/github/[repo-name]
echo 3. Run: claude
echo.
pause