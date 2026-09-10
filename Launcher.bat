@echo off

:: ─────────────────────────────────────────────────────────────────
:: Interactive CLI for this project. Double-click to open the menu,
:: or pass --generate (used by Launcher.exe/TS4_x64.exe) to skip
:: straight to generating a loading screen, e.g.:
::   Launcher.bat --generate [--force-launch]
:: ─────────────────────────────────────────────────────────────────

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

set "VERSION="
set /p VERSION=<"%ROOT%\VERSION.md"
title Sims 4 Random Loading Screen v%VERSION%

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

if "%~1"=="--generate" (
    python "%ROOT%\src\package_generator.py" %*
    if errorlevel 1 (
        echo.
        echo  [ERROR] Something went wrong. See message above.
        pause
        exit /b 1
    )
    exit /b 0
)

:menu
echo.
echo ---------------------------------------------------------------------
echo           Sims 4 Random Loading Screen - Interactive Launcher
echo                                  v%VERSION%
echo                         Built ^& Maintained by StuxieDev
echo ---------------------------------------------------------------------
echo.
echo       1) Generate loading screen (and launch game if configured)
echo       2) Rename images only
echo       3) Build launcher .exe(s)
echo       4) Run test suite
echo       5) Exit
echo.
set "choice="
set /p choice="    Select an option [1-5]: "

if "%choice%"=="1" (
    python "%ROOT%\src\package_generator.py"
    echo.
    pause
    goto menu
)
if "%choice%"=="2" (
    python "%ROOT%\src\images_renamer.py"
    echo.
    pause
    goto menu
)
if "%choice%"=="3" (
    python "%ROOT%\src\executable_builder.py"
    echo.
    pause
    goto menu
)
if "%choice%"=="4" (
    pushd "%ROOT%"
    python -m pytest -v
    popd
    echo.
    pause
    goto menu
)
if "%choice%"=="5" (
    exit /b 0
)

echo.
echo  Invalid option. Please choose 1-5.
goto menu
