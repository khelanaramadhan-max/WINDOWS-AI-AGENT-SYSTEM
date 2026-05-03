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
echo Please select the mode you want to run:
echo [1] Terminal CLI (Original)
echo [2] Elegant GUI (CustomTkinter)
echo [3] Telegram Bot (Remote Control)
echo.

set /p mode="Enter your choice (1, 2, or 3): "

echo.
echo [INFO] Starting Agent...
echo.

if "%mode%"=="1" (
    python agent.py
) else if "%mode%"=="2" (
    python gui.py
) else if "%mode%"=="3" (
    python telegram_bot.py
) else (
    echo Invalid choice. Defaulting to GUI...
    python gui.py
)

echo.
pause
