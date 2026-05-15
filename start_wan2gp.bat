@echo off
REM Simple Wan2GP Startup Script
REM This script activates the venv and starts Wan2GP using setup.py

set "APP_DIR=%~dp0Wan2GP"
set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe"

echo ============================================
echo           Starting Wan2GP
echo ============================================

REM Kill any existing process on port 7860
echo Checking for existing processes on port 7860...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7860 ^| findstr LISTENING') do (
    echo Killing existing process on port 7860 (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 >nul

REM Check if venv exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Virtual environment not found at:
    echo %PYTHON_EXE%
    echo.
    echo Please make sure you have set up the venv correctly.
    pause
    exit /b 1
)

REM Navigate to the app directory
cd /d "%APP_DIR%"

REM MCP Server disabled (requires: pip install gradio[mcp])
set GRADIO_MCP_SERVER=True

echo Starting Wan2GP from: %APP_DIR%
echo.

REM Run the app via setup.py (uses envs.json to find the active environment)
"%PYTHON_EXE%" setup.py run

REM Keep window open on error
if errorlevel 1 (
    echo.
    echo ============================================
    echo ERROR: Wan2GP exited with an error.
    echo ============================================
    pause
)
