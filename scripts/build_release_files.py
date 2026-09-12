"""
Build script — compiles gui.py (repo root) into a standalone, self-contained
executable for the platform you run this on (bundled Python, Pillow,
tkinter, and the assets they need — nothing else required on the target
machine). PyInstaller can't cross-compile, so run this on each platform
you want a native build for.

Run this whenever you want to create or refresh the executable:
    python scripts/build_release_files.py

The built executable lands in dist/, not the repo root. Double-click it
for the GUI, or run it with --generate for a headless one-shot run
(unattended use, other launchers, a Steam shortcut).
"""

import os
import sys
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(SCRIPT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.cli import cli_colors
from src.common import app_state

APP_EXE_NAME = "TS4RLS"
DIST_DIR     = os.path.join(ROOT_DIR, "dist")

IS_WINDOWS = sys.platform.startswith("win")
IS_MACOS   = sys.platform == "darwin"

_DATA_SEP = ";" if IS_WINDOWS else ":"
_BUNDLED_DATA = [
    (os.path.join("assets", "template.package"), "assets"),
    (os.path.join("assets", "icon.png"), "assets"),
    (os.path.join("assets", "logo.png"), "assets"),
    (os.path.join("assets", "author.png"), "assets"),
    (os.path.join("assets", "steam"), os.path.join("assets", "steam")),
    ("VERSION.md", "."),
    ("CHANGELOG.md", "."),
]


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


def _exe_suffix() -> str:
    # PyInstaller only appends .exe when building on Windows; macOS/Linux
    # binaries come out with no extension.
    return ".exe" if IS_WINDOWS else ""


def _data_args() -> list:
    args = []
    for src, dest in _BUNDLED_DATA:
        src_path = os.path.join(ROOT_DIR, src)
        if os.path.exists(src_path):
            args.append(f"--add-data={src_path}{_DATA_SEP}{dest}")
        else:
            print(cli_colors.warning(f"{src} not found — skipping from the bundle."))
    return args


def _icon_args() -> list:
    if IS_WINDOWS:
        ico_path = os.path.join(ROOT_DIR, "assets", "icon.ico")
    elif IS_MACOS:
        ico_path = os.path.join(ROOT_DIR, "assets", "icon.icns")
    else:
        # PyInstaller doesn't support icon embedding for plain Linux/ELF
        # binaries, so there's nothing useful to pass here.
        return []

    if os.path.isfile(ico_path):
        return [f"--icon={ico_path}"]
    print(cli_colors.warning(f"{os.path.relpath(ico_path, ROOT_DIR)} not found — building without custom icon."))
    return []


def build():
    print(cli_colors.banner(
        "TS4RLS - The Sims 4 Random Loading Screen - Executable Builder",
        f"v{_get_version()}\nBuilt & Maintained by StuxieDev",
    ))

    ensure_pyinstaller()
    os.makedirs(DIST_DIR, exist_ok=True)

    build_dir = os.path.join(ROOT_DIR, f"_build_temp_{APP_EXE_NAME}")
    entry = os.path.join(ROOT_DIR, "gui.py")

    try:
        print(f"\nRunning PyInstaller for '{APP_EXE_NAME}'...")
        subprocess.check_call(
            [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                # --windowed (no console subsystem): a --console build
                # allocates a console for every launch, including a plain
                # GUI one, which briefly flashes a command-prompt window
                # before gui.py's own startup code can hide it. --generate
                # instead attaches to the LAUNCHING terminal's own console
                # (AttachConsole) at runtime when one exists -- see
                # gui.py's main().
                "--windowed",
                f"--name={APP_EXE_NAME}",
                f"--distpath={DIST_DIR}",
                f"--workpath={build_dir}",
                f"--specpath={build_dir}",
                f"--paths={ROOT_DIR}",      # so PyInstaller can resolve `from src.x import y`
                *_data_args(),
                *_icon_args(),
                entry,
            ],
            cwd=ROOT_DIR,
        )
    finally:
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir, ignore_errors=True)

    exe_path = os.path.join(DIST_DIR, APP_EXE_NAME + _exe_suffix())
    if not os.path.isfile(exe_path):
        print("\n" + cli_colors.error(f"Build finished but executable was not found: {exe_path}"))
        sys.exit(1)

    if not IS_WINDOWS:
        os.chmod(exe_path, 0o755)

    app_state.record_build(exe_path)

    print(f"\nDone!  App ready: {exe_path}")
    print("Double-click for the GUI, or run with --generate.")


if __name__ == "__main__":
    build()
