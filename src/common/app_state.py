"""
Small persisted app state that isn't user-editable config: the first-launch
disclaimer flag and the most recent runner build. Kept in its own file
(app_state.json), separate from config.json, since the Settings fields
fully overwrite config.json on every save.
"""

import json
import os
from datetime import datetime

from src.common import paths

STATE_FILENAME = "app_state.json"


def _state_path() -> str:
    return os.path.join(os.path.dirname(paths.resolve_config_path()), STATE_FILENAME)


def _load() -> dict:
    path = _state_path()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def _save(state: dict) -> None:
    path = _state_path()
    paths.ensure_parent_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def is_disclaimer_confirmed() -> bool:
    return bool(_load().get("disclaimer_confirmed", False))


def confirm_disclaimer() -> None:
    state = _load()
    state["disclaimer_confirmed"] = True
    _save(state)


def load_runner_build() -> dict:
    """The most recent runner executable build (see src/gui/runner_builder.py)."""
    return _load().get("runner_build") or {}


def record_runner_build(exe_path: str) -> None:
    state = _load()
    state["runner_build"] = {"path": exe_path, "timestamp": datetime.now().isoformat(timespec="seconds")}
    _save(state)
