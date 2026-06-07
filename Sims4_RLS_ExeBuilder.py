"""
Build script — compiles Sims4_RLS_Launcher.bat into a standalone .exe.

Run this whenever you want to create or refresh the exe:
    python Sims4_RLS_ExeBuilder.py

The resulting Sims4_RLS_Launcher.exe will appear in this folder.
It simply calls the .bat file next to it, so you never need to rebuild
unless you want a fresh exe — editing the .bat is enough for day-to-day changes.

If config.json has "create_curseforge_version": true, a second exe named
TS4_x64.exe is also built. It behaves identically but never launches the game,
regardless of the launch_game setting in config.json.
"""

import json
import os
import sys
import shutil
import subprocess
import textwrap

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXE_NAME   = "Sims4_RLS_Launcher"

# Standard launcher: locates the .bat next to the .exe and runs it.
_LAUNCHER_CODE = textwrap.dedent("""\
    import os, sys, subprocess, ctypes

    base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False)
                           else os.path.abspath(__file__))
    bat  = os.path.join(base, 'Sims4_RLS_Launcher.bat')

    if not os.path.isfile(bat):
        ctypes.windll.user32.MessageBoxW(
            0,
            f'Cannot find the batch file:\\n{bat}\\n\\n'
            'Make sure the .exe is in the same folder as Sims4_RLS_Launcher.bat.',
            'Launcher Error',
            0x10,
        )
        sys.exit(1)

    subprocess.run(['cmd', '/c', bat], cwd=base)
""")

# CurseForge launcher: same but passes --force-launch so the game always starts,
# regardless of the launch_game setting in config.json.
_CURSEFORGE_LAUNCHER_CODE = textwrap.dedent("""\
    import os, sys, subprocess, ctypes

    base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False)
                           else os.path.abspath(__file__))
    bat  = os.path.join(base, 'Sims4_RLS_Launcher.bat')

    if not os.path.isfile(bat):
        ctypes.windll.user32.MessageBoxW(
            0,
            f'Cannot find the batch file:\\n{bat}\\n\\n'
            'Make sure the .exe is in the same folder as Sims4_RLS_Launcher.bat.',
            'Launcher Error',
            0x10,
        )
        sys.exit(1)

    subprocess.run(['cmd', '/c', bat, '--force-launch'], cwd=base)
""")


def ensure_pyinstaller():
    import importlib.util
    if importlib.util.find_spec("PyInstaller") is None:
        print("PyInstaller not found — installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"]
        )
        print("PyInstaller installed.\n")


def _load_build_config() -> dict:
    config_path = os.path.join(SCRIPT_DIR, "config.json")
    if not os.path.isfile(config_path):
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            text = f.read()
        _ph = "\x00"
        text = text.replace("\\\\", _ph).replace("\\", "\\\\").replace(_ph, "\\\\")
        return json.loads(text)
    except Exception:
        return {}


def _build_exe(name: str, launcher_code: str, icon_args: list) -> str:
    temp_py   = os.path.join(SCRIPT_DIR, f"_launcher_temp_{name}.py")
    build_dir = os.path.join(SCRIPT_DIR, f"_build_temp_{name}")

    print(f"\nWriting temporary launcher script for '{name}'...")
    with open(temp_py, "w") as f:
        f.write(launcher_code)

    try:
        print(f"Running PyInstaller for '{name}'...")
        subprocess.check_call(
            [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--console",                        # keep console so bat output is visible
                f"--name={name}",
                f"--distpath={SCRIPT_DIR}",         # put .exe directly in this folder
                f"--workpath={build_dir}",
                f"--specpath={build_dir}",
                *icon_args,
                temp_py,
            ],
            cwd=SCRIPT_DIR,
        )
    finally:
        if os.path.exists(temp_py):
            os.remove(temp_py)
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir, ignore_errors=True)

    exe_path = os.path.join(SCRIPT_DIR, name + ".exe")
    if not os.path.isfile(exe_path):
        print(f"\n[ERROR] Build finished but exe was not found: {exe_path}")
        sys.exit(1)

    return exe_path


def build():
    ensure_pyinstaller()

    ico_path = os.path.join(SCRIPT_DIR, ".DONOTRENAME_DONOTREMOVE", "ExeIcon_DONOTRENAME_DONOTREMOVE.ico")
    if os.path.isfile(ico_path):
        icon_args = [f"--icon={ico_path}"]
    else:
        print("[WARNING] ExeIcon_DONOTRENAME_DONOTREMOVE.ico not found — building without custom icon.")
        icon_args = []

    standard_path = _build_exe(EXE_NAME, _LAUNCHER_CODE, icon_args)
    print(f"\nDone!  Exe ready: {standard_path}")
    print("Add this exe to Steam as a non-Steam game.")

    cfg = _load_build_config()
    if cfg.get("create_curseforge_version", False):
        cf_path = _build_exe("TS4_x64", _CURSEFORGE_LAUNCHER_CODE, icon_args)
        print(f"\nCurseForge version ready: {cf_path}")
        print("This exe always launches the game — use it as your CurseForge pre-launch script.")


if __name__ == "__main__":
    build()
