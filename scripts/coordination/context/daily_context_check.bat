@echo off
REM Compatibility entry point; scheduled tasks call the shell script directly.
setlocal
for %%I in ("%~dp0..\..\..") do set "WORKSPACE_ROOT=%%~fI"
cd /d "%WORKSPACE_ROOT%" || exit /b 1
set "BASH_EXE="
for /f "delims=" %%G in ('where git.exe 2^>nul') do if not defined BASH_EXE if exist "%%~dpG..\bin\bash.exe" set "BASH_EXE=%%~dpG..\bin\bash.exe"
if not defined BASH_EXE if exist "%ProgramFiles%\Git\bin\bash.exe" set "BASH_EXE=%ProgramFiles%\Git\bin\bash.exe"
if not defined BASH_EXE if exist "%LOCALAPPDATA%\Programs\Git\bin\bash.exe" set "BASH_EXE=%LOCALAPPDATA%\Programs\Git\bin\bash.exe"
if not defined BASH_EXE exit /b 1
"%BASH_EXE%" "%~dp0daily_context_check.sh"
exit /b %ERRORLEVEL%
