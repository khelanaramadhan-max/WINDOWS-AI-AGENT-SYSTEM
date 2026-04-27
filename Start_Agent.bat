@echo off
title Intelligent Windows Automation Agent
color 0A

echo ===================================================
echo     Intelligent Windows Automation Agent Loader
echo ===================================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Setting it up...
    python -m venv venv
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing/Verifying dependencies...
pip install -r requirements.txt --quiet

echo.
echo [INFO] Starting Agent...
echo.
python agent.py

echo.
pause
