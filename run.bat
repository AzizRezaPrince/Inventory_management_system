@echo off
title Inventory Management System
cd /d "%~dp0"
echo Starting Inventory Management System...
java -jar "InventoryMangagementSystem.jar"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with code %ERRORLEVEL%.
    echo Please make sure Java is installed and MySQL is running if required.
    pause
)
