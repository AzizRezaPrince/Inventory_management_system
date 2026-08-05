@echo off
title Electronics Shop IMS & Repair System (Python Flask)
cd /d "%~dp0"
echo =========================================================
echo   Starting Electronics Shop Inventory & Repair System
echo =========================================================
echo.

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python was not found on your system!
    echo Please install Python 3.8+ from https://www.python.org and add it to PATH.
    pause
    exit /b
)

echo Installing / Checking Python dependencies...
python -m pip install -r requirements.txt >nul 2>&1

echo.
echo Launching Flask Server on http://127.0.0.1:5000 ...
echo Press Ctrl+C in this window to stop the server.
echo.

start "" "http://127.0.0.1:5000"
python app.py

pause
