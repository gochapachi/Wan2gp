@echo off
setlocal enabledelayedexpansion

REM ============================================
REM Wan2GP + VPS Tunnel Startup Script
REM Starts Wan2GP and connects to your private VPS tunnel (FRP)
REM ============================================

REM Auto-detect ROOT_DIR and APP_DIR whether launched from root or Wan2GP subdirectory
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%Wan2GP\wgp.py" (
    set "ROOT_DIR=%SCRIPT_DIR%"
    set "APP_DIR=%SCRIPT_DIR%Wan2GP"
) else if exist "%SCRIPT_DIR%wgp.py" (
    set "ROOT_DIR=%SCRIPT_DIR%..\"
    set "APP_DIR=%SCRIPT_DIR%"
) else (
    set "ROOT_DIR=%SCRIPT_DIR%"
    set "APP_DIR=%SCRIPT_DIR%Wan2GP"
)

set "FRPC_EXE=%ROOT_DIR%wan2gp-tunnel.exe"
set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe"

echo ============================================
echo   Starting Wan2GP + VPS Tunnel
echo ============================================

REM Kill any existing process on port 7860 to prevent [Errno 10048] address in use
echo Checking for existing processes on port 7860...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7860 ^| findstr LISTENING') do (
    echo Killing existing process on port 7860 (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 3 >nul

REM Extract serverAddr from frpc.toml if it exists
set "serverAddr=wan.anagataitsolutions.in"
if exist "%ROOT_DIR%frpc.toml" (
    for /f "tokens=2 delims==" %%a in ('findstr "serverAddr" "%ROOT_DIR%frpc.toml"') do (
        set "val=%%a"
        set "val=!val: =!"
        set "val=!val:"=!"
        set "serverAddr=!val!"
    )
)

REM Check if venv exists
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python environment not found at:
    echo %PYTHON_EXE%
    echo Please ensure the .venv is correctly set up in %APP_DIR%
    pause
    exit /b 1
)

REM Check if frpc tunnel executable exists, download if missing
if not exist "%FRPC_EXE%" (
    echo FRP Client not found. Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/fatedier/frp/releases/download/v0.54.0/frp_0.54.0_windows_amd64.zip' -OutFile '%ROOT_DIR%frp.zip'"
    powershell -Command "Expand-Archive -Path '%ROOT_DIR%frp.zip' -DestinationPath '%ROOT_DIR%frp_temp' -Force"
    move "%ROOT_DIR%frp_temp\frp_0.54.0_windows_amd64\frpc.exe" "%FRPC_EXE%" >nul 2>&1
    rmdir /s /q "%ROOT_DIR%frp_temp" >nul 2>&1
    del "%ROOT_DIR%frp.zip" >nul 2>&1
    echo Download complete.
)

REM Set environment variables
set GRADIO_MCP_SERVER=True
set "N8N_OUTPUT_URL_BASE=https://!serverAddr!"

echo Starting Wan2GP with output base: https://!serverAddr!...
cd /d "%APP_DIR%"
start "Wan2GP App" cmd /k ""%PYTHON_EXE%" wgp.py"

echo Waiting for Wan2GP to start on port 7860...
echo (Initialization typically takes 15-30 seconds)

REM Poll port 7860 until it is listening (up to 90 seconds)
set /a ATTEMPTS=0
set /a MAX_ATTEMPTS=30
:WAIT_LOOP
timeout /t 3 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 4 >nul
set /a ATTEMPTS+=1
netstat -ano | findstr :7860 | findstr LISTENING >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [+] Wan2GP is ready and listening on port 7860!
    goto START_TUNNEL
)
if %ATTEMPTS% GEQ %MAX_ATTEMPTS% (
    echo.
    echo [!] WARNING: Wan2GP did not finish initializing within 90 seconds.
    echo Please check the "Wan2GP App" console window for any startup errors.
    echo Attempting to start tunnel anyway...
    goto START_TUNNEL
)
echo   Still initializing... (%ATTEMPTS%/%MAX_ATTEMPTS%)
goto WAIT_LOOP

:START_TUNNEL
echo.
echo -----------------------------------------------------------
echo Starting Tunnel to %serverAddr%...
echo Your site is live at: https://%serverAddr%
echo -----------------------------------------------------------
echo (Ensure you have deployed the Server component on your VPS!)
echo.

"%FRPC_EXE%" -c "%ROOT_DIR%frpc.toml"

pause
