"""Builds the standalone TS4RLS runner executable -- a separate, GUI-less
exe (see runner.py, at the repo root) meant to replace the game's own
launch target in Steam/CurseForge: running it regenerates the loading
screen from the current config.json and launches the game, no window of
its own.

Only used by the GUI itself -- main_window.py's Build tab runs this as a
subprocess (via the same system Python find_python() already locates for
the test-suite action), not something a developer invokes directly or CI
ever runs. It works from a shipped exe too, unlike
src/build/create_release_files.py, since it only needs a system Python
capable of running PyInstaller, not the app's own bundled runtime.

Run with: python -m src.gui.runner_builder [--name=NAME]
Defaults to "RLSRunner" if --name isn't given; config.json's
curseforge_mode setting decides which name main_window.py passes --
"TS4_x64" for CurseForge/launcher integrations that expect that specific
filename.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from src.common import app_state, paths

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_NAME = "RLSRunner"

# Not dist/ -- that's a source-checkout/dev concept (gitignored, and not
# guaranteed to exist or be writable next to a shipped exe). Every user
# who builds a runner gets one, so it lands in the same always-writable
# per-user directory config.json/app_state.json already use.
OUTPUT_DIR = Path(paths.user_data_dir())
BUILD_DIR = OUTPUT_DIR / "_runner_build"

_DATA_SEP = ";" if IS_WINDOWS else ":"


def _add_data(src: Path, dest: str) -> str:
    return f"--add-data={src}{_DATA_SEP}{dest}"


def _icon_args() -> list[str]:
    if IS_WINDOWS:
        icon = REPO_ROOT / "assets" / "icon.ico"
    elif IS_MACOS:
        icon = REPO_ROOT / "assets" / "icon.icns"
    else:
        return []
    return [f"--icon={icon}"] if icon.is_file() else []


def ensure_pyinstaller() -> None:
    import importlib.util
    if importlib.util.find_spec("PyInstaller") is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])


def build(name: str = DEFAULT_NAME) -> Path:
    ensure_pyinstaller()
    import PyInstaller.__main__

    build_dir = BUILD_DIR / f"runner_{name}"

    PyInstaller.__main__.run([
        str(REPO_ROOT / "runner.py"),
        f"--name={name}",
        "--onefile",
        "--windowed",
        "--noconfirm",
        f"--distpath={OUTPUT_DIR}",
        f"--workpath={build_dir}",
        f"--specpath={build_dir}",
        f"--paths={REPO_ROOT}",
        *_icon_args(),
        _add_data(REPO_ROOT / "assets" / "template.package", "assets"),
    ])

    exe_path = OUTPUT_DIR / (name + (".exe" if IS_WINDOWS else ""))
    if not exe_path.is_file():
        raise SystemExit(f"Build finished but executable was not found: {exe_path}")

    shutil.rmtree(build_dir, ignore_errors=True)
    app_state.record_runner_build(str(exe_path))
    return exe_path


def main() -> None:
    name = DEFAULT_NAME
    for arg in sys.argv[1:]:
        if arg.startswith("--name="):
            name = arg.split("=", 1)[1]

    print(f"Building runner '{name}'...")
    exe_path = build(name)
    print(f"\nDone. Runner ready: {exe_path}")
    print("Place it wherever your launcher (Steam/CurseForge) expects the game's own executable.")


if __name__ == "__main__":
    main()
