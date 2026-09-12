"""Builds the files a GitHub Release needs: the standalone TS4RLS
executable, and TS4RLS_Steam_Assets.zip.

Run with: python src/build/create_release_files.py            (the exe)
          python src/build/create_release_files.py --steam-zip (the zip)
Installs its own dependencies (requirements.txt + PyInstaller) first, no
separate build.bat/build.sh wrapper or manual `pip install` needed.

PyInstaller can't cross-compile - run the exe build on each platform
(Windows, macOS, Linux) you want a native build for; that's also what the
Release GitHub Actions workflow does, once per OS runner. The Steam
assets zip has no platform dependency and only needs building once.

This is for release artifacts only -- NOT the per-user runner executable
(see src/gui/runner_builder.py for that), which is a completely separate,
GUI-less build only the app itself triggers, from its own Build tab.
"""
from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))  # so `from src.common import app_state` resolves below

VERSION = (REPO_ROOT / "VERSION.md").read_text(encoding="utf-8").strip()
DIST_DIR = REPO_ROOT / "dist"
BUILD_DIR = REPO_ROOT / "build"
STEAM_ZIP_NAME = "TS4RLS_Steam_Assets.zip"

_DATA_SEP = ";" if IS_WINDOWS else ":"


def _add_data(src: Path, dest: str) -> str:
    return f"--add-data={src}{_DATA_SEP}{dest}"


def _icon_args() -> list[str]:
    if IS_WINDOWS:
        icon = REPO_ROOT / "assets" / "icon.ico"
    elif IS_MACOS:
        icon = REPO_ROOT / "assets" / "icon.icns"
    else:
        # PyInstaller doesn't support icon embedding for plain Linux/ELF
        # binaries - nothing useful to pass here.
        return []
    return [f"--icon={icon}"] if icon.is_file() else []


COMMON_ARGS = [
    "--onefile",
    "--noconfirm",
    f"--distpath={DIST_DIR}",
    f"--workpath={BUILD_DIR}",
    f"--specpath={BUILD_DIR}",
    f"--paths={REPO_ROOT}",
]


def ensure_dependencies() -> None:
    # No build.bat/build.sh wrapper to install these first - this script
    # is run directly (`python src/build/create_release_files.py`), so it
    # installs its own runtime + build dependencies before importing
    # PyInstaller.
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", str(REPO_ROOT / "requirements.txt"), "-q"]
    )
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])


def build_gui() -> None:
    import PyInstaller.__main__

    # The About tab and disclaimer dialog read assets/logo.png,
    # CHANGELOG.md, and VERSION.md at runtime via src.common.paths
    # (which resolves to sys._MEIPASS in a frozen build) - bundle them as
    # data so those lookups succeed instead of silently no-op'ing
    # (missing icon/logo/blank changelog) in the packaged exe.
    PyInstaller.__main__.run([
        str(REPO_ROOT / "gui.py"),
        "--name=TS4RLS",
        "--windowed",
        # --generate still attaches to the launching terminal's own
        # console at runtime (see gui.py's _attach_parent_console) rather
        # than needing --console here, which would otherwise flash a
        # console window open on every plain GUI launch too.
        *_icon_args(),
        _add_data(REPO_ROOT / "assets", "assets"),
        _add_data(REPO_ROOT / "CHANGELOG.md", "."),
        _add_data(REPO_ROOT / "VERSION.md", "."),
        *COMMON_ARGS,
    ])

    exe_path = DIST_DIR / ("TS4RLS.exe" if IS_WINDOWS else "TS4RLS")
    if exe_path.is_file():
        # So the running app's own Home tab ("Latest build") can show
        # this -- it's a separate developer/dev-tooling script, but the
        # GUI still reads the same per-user app_state.json.
        from src.common import app_state
        app_state.record_build(str(exe_path))


def build_steam_zip() -> Path:
    """Zips assets/steam/ into dist/TS4RLS_Steam_Assets.zip -- the same
    file the website's /assets/steam redirect and every GitHub Release
    point at. No PyInstaller/platform dependency, unlike build_gui()
    above, but it's still a release artifact, so it lives here rather
    than in its own script."""
    steam_dir = REPO_ROOT / "assets" / "steam"
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DIST_DIR / STEAM_ZIP_NAME

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in sorted(steam_dir.iterdir()):
            zf.write(item, arcname=item.name)

    print(f"Done. Steam assets zip: {zip_path}")
    return zip_path


def main() -> None:
    if "--steam-zip" in sys.argv[1:]:
        build_steam_zip()
        return

    print(f"Building TS4RLS v{VERSION} standalone executable for {sys.platform}...")
    print("Installing build dependencies...")
    ensure_dependencies()
    build_gui()
    print(f"\nDone. Output in {DIST_DIR}:")
    print("  - TS4RLS  (double-click to run - .exe on Windows, .app on macOS)")


if __name__ == "__main__":
    main()
