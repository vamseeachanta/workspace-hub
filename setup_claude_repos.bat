@echo off
echo Setting up Claude Code for all repositories...

REM List of repositories to configure
set "repos=achantas-data client_projects doris ecs energy hobbies investments OGManufacturing predyct rock-oil-field saipem seanation spire_projects"

for %%r in (%repos%) do (
    echo.
    echo Configuring repository: %%r
    
    REM Check if repository exists
    if exist "C:\Users\vamseea\github\%%r\.git" (
        echo Repository %%r found
        
        REM Check if CLAUDE.md already exists
        if not exist "C:\Users\vamseea\github\%%r\CLAUDE.md" (
            echo Creating CLAUDE.md for %%r
            
            REM Create basic CLAUDE.md
            echo # Claude Code Configuration for %%r > "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo. >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo ## Repository Overview >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo This repository contains project files and documentation for %%r. >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo. >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo ## Development Environment >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo - Use Git Bash terminal in VS Code >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo - Python environment managed via conda >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo - Follow existing code patterns and conventions >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo. >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo ## Project Structure >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo See README.md for detailed project structure and setup instructions. >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo. >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo ## Notes >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo - Always check existing patterns before making changes >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo - Use appropriate tools based on repository content >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            echo - Maintain consistent formatting and documentation >> "C:\Users\vamseea\github\%%r\CLAUDE.md"
            
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