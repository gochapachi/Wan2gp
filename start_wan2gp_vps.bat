@echo off
setlocal enabledelayedexpansion

REM Wan2GP + VPS Tunnel Startup Script
REM Starts Wan2GP and connects to your private VPS tunnel (FRP)

set "ROOT_DIR=%~dp0"
set "FRPC_EXE=%ROOT_DIR%wan2gp-tunnel.exe"
set "APP_DIR=%ROOT_DIR%Wan2GP"
set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe"

echo ============================================
echo   Starting Wan2GP + VPS Tunnel
echo ============================================

REM Extract serverAddr from frpc.toml if it exists
set "serverAddr=wan.gochapachi.com"
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
    echo [ERROR] Python environment not found at %PYTHON_EXE%
    echo Please ensure the .venv is correctly set up in %APP_DIR%
    pause
    exit /b 1
)

REM Check if frpc exists, download if not
if not exist "%FRPC_EXE%" (
    echo FRP Client not found. Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/fatedier/frp/releases/download/v0.54.0/frp_0.54.0_windows_amd64.zip' -OutFile '%ROOT_DIR%frp.zip'"
    powershell -Command "Expand-Archive -Path '%ROOT_DIR%frp.zip' -DestinationPath '%ROOT_DIR%frp_temp' -Force"
    move "%ROOT_DIR%frp_temp\frp_0.54.0_windows_amd64\frpc.exe" "%FRPC_EXE%"
    rmdir /s /q "%ROOT_DIR%frp_temp"
    del "%ROOT_DIR%frp.zip"
    echo Download complete.
)

REM Start Wan2GP
set GRADIO_MCP_SERVER=True
echo Starting Wan2GP...
cd /d "%APP_DIR%"
start "Wan2GP App" cmd /k ""%PYTHON_EXE%" wgp.py"

echo Waiting for Wan2GP to initialize...
timeout /t 15 >nul

echo.
echo -----------------------------------------------------------
echo Starting Tunnel to %serverAddr%...
echo Your site should be live at: http://%serverAddr%:9000
echo -----------------------------------------------------------
echo (Ensure you have deployed the Server component on your VPS!)
echo.

"%FRPC_EXE%" -c "%ROOT_DIR%frpc.toml"

pause
