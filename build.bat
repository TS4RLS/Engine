@echo off
REM TS4RLS - build the executable (Windows)
REM Thin wrapper so `build.bat` matches the sibling `commit.bat`, rather
REM than needing to remember the full module path. Dependencies (Pillow,
REM sv_ttk, PyInstaller) are installed automatically by
REM executable_builder.py itself.
setlocal
set "DIR=%~dp0"

python "%DIR%src\build\executable_builder.py" %*

endlocal
