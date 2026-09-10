"""
Build script — compiles Launcher.bat (Windows) or Launcher.sh (macOS/Linux)
into a standalone executable for the platform you run this on. PyInstaller
can't cross-compile, so run this script on each platform you want a native
build for.

Run this whenever you want to create or refresh the executable:
    python src/executable_builder.py

The resulting executable — Launcher.exe on Windows, plain Launcher on
macOS/Linux — appears in the project root. It simply calls Launcher.bat/
Launcher.sh next to it (in "--generate" mode, skipping the interactive
menu), so you never need to rebuild unless you want a fresh executable —
editing Launcher.bat/Launcher.sh/src/package_generator.py is enough for day-to-day
changes.

If config.json has "create_curseforge_version": true, a second executable
named TS4_x64 (TS4_x64.exe on Windows) is also built — mirroring the
filename of Sims 4's own game executable on each platform. It behaves
identically but always launches the game, regardless of the launch_game
setting in config.json, for use as a CurseForge pre-launch script.
"""

import json
import os
import sys
import shutil
import subprocess
import textwrap

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(SCRIPT_DIR)
EXE_NAME   = "Launcher"

IS_WINDOWS = sys.platform.startswith("win")
IS_MACOS   = sys.platform == "darwin"

# Windows launcher: locates Launcher.bat next to the .exe and runs it in
# non-interactive "generate" mode.
_LAUNCHER_CODE_WINDOWS = textwrap.dedent("""\
    import os, sys, subprocess, ctypes

    base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False)
                           else os.path.abspath(__file__))
    bat  = os.path.join(base, 'Launcher.bat')

    if not os.path.isfile(bat):
        ctypes.windll.user32.MessageBoxW(
            0,
            f'Cannot find the batch file:\\n{bat}\\n\\n'
            'Make sure the .exe is in the same folder as Launcher.bat.',
            'Launcher Error',
            0x10,
        )
        sys.exit(1)

    subprocess.run(['cmd', '/c', bat, '--generate'], cwd=base)
""")

# CurseForge launcher: same but also passes --force-launch so the game always
# starts, regardless of the launch_game setting in config.json. Windows-only.
_CURSEFORGE_LAUNCHER_CODE_WINDOWS = textwrap.dedent("""\
    import os, sys, subprocess, ctypes

    base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False)
                           else os.path.abspath(__file__))
    bat  = os.path.join(base, 'Launcher.bat')

    if not os.path.isfile(bat):
        ctypes.windll.user32.MessageBoxW(
            0,
            f'Cannot find the batch file:\\n{bat}\\n\\n'
            'Make sure the .exe is in the same folder as Launcher.bat.',
            'Launcher Error',
            0x10,
        )
        sys.exit(1)

    subprocess.run(['cmd', '/c', bat, '--generate', '--force-launch'], cwd=base)
""")

# macOS/Linux launcher: locates Launcher.sh next to the binary and runs it in
# non-interactive "generate" mode.
_LAUNCHER_CODE_UNIX = textwrap.dedent("""\
    import os, sys, subprocess

    base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False)
                           else os.path.abspath(__file__))
    sh = os.path.join(base, 'Launcher.sh')

    if not os.path.isfile(sh):
        print(
            f"Cannot find Launcher.sh:\\n{sh}\\n\\n"
            "Make sure this executable is in the same folder as Launcher.sh.",
            file=sys.stderr,
        )
        sys.exit(1)

    subprocess.run(['bash', sh, '--generate'], cwd=base)
""")

# CurseForge launcher for macOS/Linux: same but also passes --force-launch so
# the game always starts, regardless of the launch_game setting in
# config.json.
_CURSEFORGE_LAUNCHER_CODE_UNIX = textwrap.dedent("""\
    import os, sys, subprocess

    base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False)
                           else os.path.abspath(__file__))
    sh = os.path.join(base, 'Launcher.sh')

    if not os.path.isfile(sh):
        print(
            f"Cannot find Launcher.sh:\\n{sh}\\n\\n"
            "Make sure this executable is in the same folder as Launcher.sh.",
            file=sys.stderr,
        )
        sys.exit(1)

    subprocess.run(['bash', sh, '--generate', '--force-launch'], cwd=base)
""")


def ensure_pyinstaller():
    import importlib.util
    if importlib.util.find_spec("PyInstaller") is None:
        print("PyInstaller not found — installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"]
        )
        print("PyInstaller installed.\n")


def _get_version() -> str:
    try:
        with open(os.path.join(ROOT_DIR, "VERSION.md"), "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "?"


def _load_build_config() -> dict:
    config_path = os.path.join(ROOT_DIR, "config.json")
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


def _exe_suffix() -> str:
    # PyInstaller only appends .exe when building on Windows; macOS/Linux
    # binaries come out with no extension.
    return ".exe" if IS_WINDOWS else ""


def _build_exe(name: str, launcher_code: str, icon_args: list) -> str:
    temp_py   = os.path.join(ROOT_DIR, f"_launcher_temp_{name}.py")
    build_dir = os.path.join(ROOT_DIR, f"_build_temp_{name}")

    print(f"\nWriting temporary launcher script for '{name}'...")
    with open(temp_py, "w") as f:
        f.write(launcher_code)

    try:
        print(f"Running PyInstaller for '{name}'...")
        subprocess.check_call(
            [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--console",                        # keep console so output is visible
                f"--name={name}",
                f"--distpath={ROOT_DIR}",           # put the executable directly in the project root
                f"--workpath={build_dir}",
                f"--specpath={build_dir}",
                *icon_args,
                temp_py,
            ],
            cwd=ROOT_DIR,
        )
    finally:
        if os.path.exists(temp_py):
            os.remove(temp_py)
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir, ignore_errors=True)

    exe_path = os.path.join(ROOT_DIR, name + _exe_suffix())
    if not os.path.isfile(exe_path):
        print(f"\n[ERROR] Build finished but executable was not found: {exe_path}")
        sys.exit(1)

    if not IS_WINDOWS:
        os.chmod(exe_path, 0o755)

    return exe_path


def _icon_args(base_name: str) -> list:
    if IS_WINDOWS:
        ico_path = os.path.join(ROOT_DIR, "assets", base_name + ".ico")
    elif IS_MACOS:
        ico_path = os.path.join(ROOT_DIR, "assets", base_name + ".icns")
    else:
        # PyInstaller doesn't support icon embedding for plain Linux/ELF
        # binaries, so there's nothing useful to pass here.
        return []

    if os.path.isfile(ico_path):
        return [f"--icon={ico_path}"]
    print(f"[WARNING] {os.path.relpath(ico_path, ROOT_DIR)} not found — building without custom icon.")
    return []


def build():
    banner_width = 69
    print("=" * banner_width)
    print("Sims 4 Random Loading Screen - Executable Builder".center(banner_width))
    print(f"v{_get_version()}".center(banner_width))
    print("Built & Maintained by StuxieDev".center(banner_width))
    print("=" * banner_width)

    ensure_pyinstaller()

    launcher_code = _LAUNCHER_CODE_WINDOWS if IS_WINDOWS else _LAUNCHER_CODE_UNIX
    standard_path = _build_exe(EXE_NAME, launcher_code, _icon_args("icon"))
    print(f"\nDone!  Executable ready: {standard_path}")
    if IS_WINDOWS:
        print("Add this exe to Steam as a non-Steam game.")
    else:
        print("Add this to Steam as a non-Steam game, or run it directly.")

    cfg = _load_build_config()
    if cfg.get("create_curseforge_version", False):
        cf_code = _CURSEFORGE_LAUNCHER_CODE_WINDOWS if IS_WINDOWS else _CURSEFORGE_LAUNCHER_CODE_UNIX
        cf_path = _build_exe("TS4_x64", cf_code, _icon_args("alt_icon"))
        print(f"\nCurseForge version ready: {cf_path}")
        print("This always launches the game — use it as your CurseForge pre-launch script.")


if __name__ == "__main__":
    build()
