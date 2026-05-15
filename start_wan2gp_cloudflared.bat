@echo off
REM Wan2GP + Cloudflare Tunnel Startup Script
REM Starts Wan2GP directly and creates a public tunnel via Cloudflared

set "ROOT_DIR=%~dp0"
set "CLOUDFLARED_EXE=%ROOT_DIR%cloudflared.exe"
set "APP_DIR=%ROOT_DIR%Wan2GP"
set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe"

echo ============================================
echo   Starting Wan2GP + Cloudflare Tunnel
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

REM Check if cloudflared exists, download if not
if not exist "%CLOUDFLARED_EXE%" (
    echo Cloudflared not found. Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile '%CLOUDFLARED_EXE%'"
    if errorlevel 1 (
        echo Failed to download cloudflared. Please check your internet connection.
        pause
        exit /b 1
    )
    echo Download complete.
)

REM Enable Native Gradio MCP Server
set GRADIO_MCP_SERVER=True

REM Start Wan2GP directly in a separate window
echo Starting Wan2GP...
cd /d "%APP_DIR%"
start "Wan2GP App" cmd /k ""%PYTHON_EXE%" wgp.py"

echo Waiting for Wan2GP to start on port 7860...
echo (This may take 30-120 seconds depending on model loading)

REM Poll port 7860 until it's listening (up to 120 seconds)
set /a ATTEMPTS=0
set /a MAX_ATTEMPTS=24
:WAIT_LOOP
timeout /t 5 >nul
set /a ATTEMPTS+=1
netstat -ano | findstr :7860 | findstr LISTENING >nul 2>&1
if not errorlevel 1 (
    echo.
    echo Wan2GP is ready on port 7860!
    goto START_TUNNEL
)
if %ATTEMPTS% GEQ %MAX_ATTEMPTS% (
    echo.
    echo WARNING: Wan2GP did not start within 120 seconds.
    echo Check the Wan2GP window for errors.
    echo Attempting to start tunnel anyway...
    goto START_TUNNEL
)
echo   Still waiting... (%ATTEMPTS%/%MAX_ATTEMPTS%)
goto WAIT_LOOP

:START_TUNNEL
echo.
echo -----------------------------------------------------------
echo Starting Cloudflare Tunnel...
echo YOUR PUBLIC URL WILL APPEAR BELOW (Look for trycloudflare.com)
echo -----------------------------------------------------------
"%CLOUDFLARED_EXE%" tunnel --url http://127.0.0.1:7860

pause
