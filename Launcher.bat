@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: ─────────────────────────────────────────────────────────────────
:: Dev launcher for running this project from source (contributors).
:: End users should use the built TS4RLS(.exe)/TS4_x64 executable instead
:: (see src/build/executable_builder.py, dist/ once built). Pass
:: --generate here to skip straight to generating a loading screen, e.g.:
::   Launcher.bat --generate
:: ─────────────────────────────────────────────────────────────────

:: ── Colors (ANSI, supported by cmd.exe on Windows 10+) ─────────────
for /F %%a in ('echo prompt $E^|cmd') do set "ESC=%%a"
set "C_RESET=%ESC%[0m"
set "C_RED=%ESC%[91m"
set "C_GREEN=%ESC%[92m"
set "C_YELLOW=%ESC%[93m"
set "C_CYAN=%ESC%[96m"
set "C_MAGENTA=%ESC%[95m"
set "C_BOLD=%ESC%[1m"

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

set "VERSION="
set /p VERSION=<"%ROOT%\VERSION.md"
title TS4RLS - The Sims 4 Random Loading Screen v%VERSION%

:: ── Locate Python ───────────────────────────────────────────────────
where python >nul 2>&1
if errorlevel 1 (
    echo %C_RED%[ERROR] Python is not installed or not on your PATH.%C_RESET%
    echo Download Python from: https://www.python.org/downloads/
    echo During install, tick "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
    echo %C_RED%[ERROR] Found a "python" command, but it failed to run.%C_RESET%
    echo Re-run the Python installer and repair/reinstall it.
    echo.
    pause
    exit /b 1
)

:: ── Ensure pip is available, bootstrapping it if needed ─────────────
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo %C_YELLOW%pip not found — bootstrapping it...%C_RESET%
    python -m ensurepip --upgrade >nul 2>&1
    if errorlevel 1 (
        echo %C_RED%[ERROR] Could not install pip automatically.%C_RESET%
        echo Reinstall Python from https://www.python.org/downloads/ with pip included.
        echo.
        pause
        exit /b 1
    )
    echo %C_GREEN%pip installed.%C_RESET%
    echo.
)

:: ── Ensure Pillow is available ──────────────────────────────────────
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo %C_YELLOW%Pillow not found — installing...%C_RESET%
    python -m pip install Pillow --quiet
    if errorlevel 1 (
        echo %C_RED%[ERROR] Failed to install Pillow. Check your internet connection and try:%C_RESET%
        echo   python -m pip install Pillow
        echo.
        pause
        exit /b 1
    )
    echo %C_GREEN%Pillow installed.%C_RESET%
    echo.
)

if "%~1"=="--generate" (
    python "%ROOT%\gui.py" %*
    if errorlevel 1 (
        echo.
        echo %C_RED%[ERROR] Something went wrong. See message above.%C_RESET%
        pause
        exit /b 1
    )
    exit /b 0
)

:menu
echo.
echo %C_CYAN%---------------------------------------------------------------------%C_RESET%
echo %C_BOLD%          TS4RLS - The Sims 4 Random Loading Screen - Dev Launcher%C_RESET%
echo                                  v%VERSION%
echo                         Built ^& Maintained by StuxieDev
echo %C_CYAN%---------------------------------------------------------------------%C_RESET%
echo.
echo       %C_GREEN%1)%C_RESET% Launch the GUI
echo       %C_GREEN%2)%C_RESET% Build launcher executable(s)
echo       %C_GREEN%3)%C_RESET% Run test suite
echo       %C_GREEN%4)%C_RESET% Exit
echo.
set "choice="
set /p choice="    Select an option [1-4]: "

if "%choice%"=="1" (
    python "%ROOT%\gui.py"
    if errorlevel 1 echo %C_RED%[ERROR] Something went wrong — see message above.%C_RESET%
    goto menu
)
if "%choice%"=="2" (
    python "%ROOT%\src\build\executable_builder.py"
    if errorlevel 1 echo %C_RED%[ERROR] Build failed — see message above.%C_RESET%
    echo.
    pause
    goto menu
)
if "%choice%"=="3" (
    python -c "import pytest" >nul 2>&1
    if errorlevel 1 (
        echo %C_YELLOW%pytest not found — installing...%C_RESET%
        python -m pip install -r "%ROOT%\requirements.txt" --quiet
        if errorlevel 1 (
            echo %C_RED%[ERROR] Failed to install test dependencies.%C_RESET%
            echo.
            pause
            goto menu
        )
    )
    pushd "%ROOT%"
    python -m pytest -v
    if errorlevel 1 echo %C_RED%[ERROR] Some tests failed — see output above.%C_RESET%
    popd
    echo.
    pause
    goto menu
)
if "%choice%"=="4" (
    exit /b 0
)

echo.
echo %C_RED%Invalid option. Please choose 1-4.%C_RESET%
goto menu
