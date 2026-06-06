"""
Build script — compiles Launch_RandomLoadingScreen.bat into a standalone .exe.

Run this whenever you want to create or refresh the exe:
    python build_exe.py

The resulting Launch_RandomLoadingScreen.exe will appear in this folder.
It simply calls the .bat file next to it, so you never need to rebuild
unless you want a fresh exe — editing the .bat is enough for day-to-day changes.
"""

import os
import sys
import shutil
import subprocess
import textwrap

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
EXE_NAME    = "Launch_RandomLoadingScreen"
TEMP_PY     = os.path.join(SCRIPT_DIR, "_launcher_temp.py")
BUILD_DIR   = os.path.join(SCRIPT_DIR, "_build_temp")

# Tiny launcher: locates the .bat next to the .exe and runs it.
_LAUNCHER_CODE = textwrap.dedent("""\
    import os, sys, subprocess, ctypes

    base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False)
                           else os.path.abspath(__file__))
    bat  = os.path.join(base, 'Launch_RandomLoadingScreen.bat')

    if not os.path.isfile(bat):
        ctypes.windll.user32.MessageBoxW(
            0,
            f'Cannot find the batch file:\\n{bat}\\n\\n'
            'Make sure the .exe is in the same folder as Launch_RandomLoadingScreen.bat.',
            'Launcher Error',
            0x10,
        )
        sys.exit(1)

    subprocess.run(['cmd', '/c', bat], cwd=base)
""")


def ensure_pyinstaller():
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller not found — installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"]
        )
        print("PyInstaller installed.\n")


def build():
    ensure_pyinstaller()

    print(f"Writing temporary launcher script...")
    with open(TEMP_PY, "w") as f:
        f.write(_LAUNCHER_CODE)

    try:
        print(f"Running PyInstaller...")
        subprocess.check_call(
            [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--console",                        # keep console so bat output is visible
                f"--name={EXE_NAME}",
                f"--distpath={SCRIPT_DIR}",         # put .exe directly in this folder
                f"--workpath={BUILD_DIR}",
                f"--specpath={BUILD_DIR}",
                TEMP_PY,
            ],
            cwd=SCRIPT_DIR,
        )
    finally:
        if os.path.exists(TEMP_PY):
            os.remove(TEMP_PY)
        if os.path.isdir(BUILD_DIR):
            shutil.rmtree(BUILD_DIR, ignore_errors=True)

    exe_path = os.path.join(SCRIPT_DIR, EXE_NAME + ".exe")
    if os.path.isfile(exe_path):
        print(f"\nDone!  Exe ready: {exe_path}")
        print("Add this exe to Steam as a non-Steam game.")
    else:
        print("\n[ERROR] Build finished but exe was not found.")
        sys.exit(1)


if __name__ == "__main__":
    build()
