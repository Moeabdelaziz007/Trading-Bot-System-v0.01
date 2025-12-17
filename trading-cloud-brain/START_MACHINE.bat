@echo off
REM ============================================
REM 💰 AXIOM MONEY MACHINE - WINDOWS LAUNCHER
REM ============================================
REM One-click startup for the Axiom Alpha system
REM
REM This script:
REM   1. Starts the background engine (24/7 trading)
REM   2. Launches the voice interface (optional)
REM
REM Usage: Double-click START_MACHINE.bat
REM ============================================

title Axiom Money Machine

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║     ██╗  ██╗██╗██╗ ██████╗ ███╗   ███╗                       ║
echo ║    ██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗ ████║                   ║
echo ║    ███████║ ╚███╔╝ ██║██║   ██║██╔████╔██║                   ║
echo ║    ██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╔╝██║                   ║
echo ║    ██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚═╝ ██║                   ║
echo ║    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝                   ║
echo ║                                                              ║
echo ║              💰  MONEY MACHINE LAUNCHER  💰                  ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo 🚀 Starting Axiom Alpha...
echo.

REM Ask for mode
echo Select Mode:
echo   1. Demo Mode (Recommended - No real trades)
echo   2. Live Trading (Real money!)
echo.
set /p mode="Enter choice (1 or 2): "

if "%mode%"=="1" (
    echo.
    echo 🎮 Starting in DEMO MODE...
    start /B pythonw main_engine.py --demo
) else if "%mode%"=="2" (
    echo.
    echo ⚠️ WARNING: LIVE TRADING MODE
    set /p confirm="Type 'yes' to confirm: "
    if "%confirm%"=="yes" (
        start /B pythonw main_engine.py
    ) else (
        echo Cancelled. Starting demo mode...
        start /B pythonw main_engine.py --demo
    )
) else (
    echo Invalid choice. Starting demo mode...
    start /B pythonw main_engine.py --demo
)

echo.
echo ✅ Background engine started!
echo.

REM Ask about voice interface
echo Start Voice Interface?
echo   1. Yes - Control with voice
echo   2. No - Engine only
echo.
set /p voice="Enter choice (1 or 2): "

if "%voice%"=="1" (
    echo.
    echo 🎙️ Starting Voice Cockpit...
    python axiom_cli.py
) else (
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo Engine running in background.
    echo.
    echo   • View logs:    type axiom_engine.log
    echo   • Voice mode:   python axiom_cli.py
    echo.
    echo Press any key to exit this window...
    echo (Engine will continue running in background)
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pause >nul
)

echo.
echo 👋 Launcher closed. Engine may still be running in background.
