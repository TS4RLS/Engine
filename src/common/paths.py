"""
Path resolution shared by every entry point (CLI, GUI, headless generate).

Handles three concerns that differ between running from source and running
as a frozen (PyInstaller) executable:
  - where config.json lives (resolve_config_path)
  - where bundled read-only assets live (resource_path)
  - what "the app's own directory" means (app_base_dir)
"""

import os
import sys

APP_NAME = "TS4RLS"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def app_base_dir() -> str:
    """Directory the running app lives in: the exe's folder when frozen,
    otherwise the project root (two levels up from src/common/paths.py)."""
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def resource_path(relative: str) -> str:
    """Path to a bundled, read-only asset (e.g. assets/template.package).

    When frozen, PyInstaller extracts --add-data files under sys._MEIPASS;
    from source, they live at their normal path under the project root.
    """
    if is_frozen():
        base = getattr(sys, "_MEIPASS", app_base_dir())
    else:
        base = app_base_dir()
    return os.path.join(base, relative)


def _user_data_dir(app_name: str) -> str:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, app_name)


def resolve_config_path() -> str:
    """Where config.json should be read from/written to, in priority order:

    1. SIMS4_RLS_CONFIG_DIR env var (tests, power users who want a fixed spot).
    2. Portable mode: a config.json already sitting next to the running
       app/script (keeps existing from-source checkouts working as-is).
    3. The OS-appropriate per-user config directory (created on save).
    """
    override = os.environ.get("SIMS4_RLS_CONFIG_DIR")
    if override:
        return os.path.join(override, "config.json")

    local = os.path.join(app_base_dir(), "config.json")
    if os.path.isfile(local):
        return local

    return os.path.join(_user_data_dir(APP_NAME), "config.json")


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
