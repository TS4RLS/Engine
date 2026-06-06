@echo off
title Sims 4 Random Loading Screen

:: ─────────────────────────────────────────────────────────────────
:: Run this .bat file before launching The Sims 4.
:: It calls the Python script which picks a random image and
:: installs it as your loading screen mod.
::
:: Place this .bat file in the same folder as Sims4_RLS_Creator.py
:: ─────────────────────────────────────────────────────────────────

echo.
echo ---------------------------------------------------------------------
echo       Sims 4 Random Loading Screen Generator - Batch Launcher
echo ---------------------------------------------------------------------
echo.

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed or not on your PATH.
    echo  Download Python from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Check Pillow is installed; install if missing
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo  Pillow not found — installing...
    pip install Pillow --quiet
    echo  Pillow installed.
    echo.
)

:: Run the main script (located in the same folder as this .bat)
python "%~dp0Sims4_RLS_Creator.py"

if errorlevel 1 (
    echo.
    echo  [ERROR] Something went wrong. See message above.
    pause
    exit /b 1
)

echo.
echo  Press any key to close this window. 
echo  Make sure to launch The Sims 4 unless you enabled auto-launch in the script settings.
pause >nul
