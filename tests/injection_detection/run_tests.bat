@echo off
REM Prompt Injection Detection Test Suite Runner
REM Run from tests\injection_detection\ directory

setlocal enabledelayedexpansion

echo.
echo =====================================================================
echo Prompt Injection Detection Test Suite
echo =====================================================================
echo.

REM Get the script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..\..\

echo Project Root: %PROJECT_ROOT%
echo Test Dir:     %SCRIPT_DIR%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

echo Python:
python --version
echo.

REM Change to test directory
cd /d "%SCRIPT_DIR%"

REM Run the test runner
echo Running tests...
echo.
python test_runner.py

exit /b %ERRORLEVEL%
