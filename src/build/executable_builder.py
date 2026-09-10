"""
Build script — compiles src/app.py into standalone, self-contained
executables for the platform you run this on (bundled Python, Pillow,
tkinter, and the assets it needs — nothing else required on the target
machine). PyInstaller can't cross-compile, so run this on each platform
you want a native build for.

Run this whenever you want to create or refresh the executables:
    python src/build/executable_builder.py

Two executables are built from the exact same src/app.py, so there is only
one codepath to maintain:

  - Sims4RandomLoadingScreen(.exe) — double-click for the GUI; pass --cli
    for the interactive text menu; pass --generate [--force-launch] for a
    headless one-shot run (unattended use, other launchers, a Steam
    shortcut).
  - TS4_x64(.exe), built only if config.json has
    "create_curseforge_version": true — mirrors the filename of Sims 4's
    own game executable. app.py detects this filename and automatically
    behaves as --generate --force-launch with no arguments needed, for use
    as a CurseForge pre-launch script.
"""

import os
import sys
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(os.path.dirname(SCRIPT_DIR))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.common.config_format import parse_jsonc
from src.cli import cli_colors
APP_EXE_NAME       = "Sims4RandomLoadingScreen"
CURSEFORGE_EXE_NAME = "TS4_x64"

IS_WINDOWS = sys.platform.startswith("win")
IS_MACOS   = sys.platform == "darwin"

_DATA_SEP = ";" if IS_WINDOWS else ":"
_BUNDLED_DATA = [
    (os.path.join("assets", "template.package"), "assets"),
    (os.path.join("assets", "icon.png"), "assets"),
    (os.path.join("assets", "alt_icon.png"), "assets"),
    (os.path.join("assets", "steam"), os.path.join("assets", "steam")),
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


def _load_build_config() -> dict:
    config_path = os.path.join(ROOT_DIR, "config.json")
    if not os.path.isfile(config_path):
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return parse_jsonc(f.read())
    except Exception:
        return {}


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
    print(cli_colors.warning(f"{os.path.relpath(ico_path, ROOT_DIR)} not found — building without custom icon."))
    return []


def _build_exe(name: str, icon_base: str) -> str:
    build_dir = os.path.join(ROOT_DIR, f"_build_temp_{name}")
    entry = os.path.join(ROOT_DIR, "src", "app.py")

    try:
        print(f"\nRunning PyInstaller for '{name}'...")
        subprocess.check_call(
            [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--console",  # needed for --cli/--generate output; the GUI still opens fine
                f"--name={name}",
                f"--distpath={ROOT_DIR}",   # put the executable directly in the project root
                f"--workpath={build_dir}",
                f"--specpath={build_dir}",
                f"--paths={ROOT_DIR}",      # so PyInstaller can resolve `from src.x import y`
                *_data_args(),
                *_icon_args(icon_base),
                entry,
            ],
            cwd=ROOT_DIR,
        )
    finally:
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir, ignore_errors=True)

    exe_path = os.path.join(ROOT_DIR, name + _exe_suffix())
    if not os.path.isfile(exe_path):
        print("\n" + cli_colors.error(f"Build finished but executable was not found: {exe_path}"))
        sys.exit(1)

    if not IS_WINDOWS:
        os.chmod(exe_path, 0o755)

    return exe_path


def _should_build_curseforge(default: bool, interactive: bool, ask=input) -> bool:
    """Decide whether to build the CurseForge (TS4_x64) executable.

    Non-interactive runs (piped/redirected stdin, e.g. CI) always fall back
    to the `create_curseforge_version` config default. Interactive runs are
    asked each time, defaulting to whatever the config says, so config.json
    still lets you set a lasting preference without answering every build.
    """
    if not interactive:
        return default
    prompt = "Y/n" if default else "y/N"
    answer = ask(f"\nAlso build the CurseForge (TS4_x64) pre-launch executable? [{prompt}]: ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes")


def build():
    print(cli_colors.banner(
        "Sims 4 Random Loading Screen - Executable Builder",
        f"v{_get_version()}\nBuilt & Maintained by StuxieDev",
    ))

    ensure_pyinstaller()

    app_path = _build_exe(APP_EXE_NAME, "icon")
    print(f"\nDone!  App ready: {app_path}")
    print("Double-click for the GUI, or run with --cli / --generate [--force-launch].")

    cfg = _load_build_config()
    default_cf = cfg.get("create_curseforge_version", False)
    if _should_build_curseforge(default_cf, sys.stdin.isatty()):
        cf_path = _build_exe(CURSEFORGE_EXE_NAME, "alt_icon")
        print(f"\nCurseForge version ready: {cf_path}")
        print("This always launches the game — use it as your CurseForge pre-launch script.")


if __name__ == "__main__":
    build()
