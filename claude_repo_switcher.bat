@echo off
echo Claude Code Repository Switcher
echo ================================
echo.
echo Available repositories:
echo 1. aceengineer-admin
echo 2. achantas-data
echo 3. client_projects
echo 4. doris
echo 5. ecs
echo 6. energy
echo 7. hobbies
echo 8. investments
echo 9. OGManufacturing
echo 10. predyct
echo 11. rock-oil-field
echo 12. saipem
echo 13. seanation
echo 14. spire_projects
echo.
set /p choice="Select repository (1-14): "

if "%choice%"=="1" set "repo=aceengineer-admin"
if "%choice%"=="2" set "repo=achantas-data"
if "%choice%"=="3" set "repo=client_projects"
if "%choice%"=="4" set "repo=doris"
if "%choice%"=="5" set "repo=ecs"
if "%choice%"=="6" set "repo=energy"
if "%choice%"=="7" set "repo=hobbies"
if "%choice%"=="8" set "repo=investments"
if "%choice%"=="9" set "repo=OGManufacturing"
if "%choice%"=="10" set "repo=predyct"
if "%choice%"=="11" set "repo=rock-oil-field"
if "%choice%"=="12" set "repo=saipem"
if "%choice%"=="13" set "repo=seanation"
if "%choice%"=="14" set "repo=spire_projects"

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