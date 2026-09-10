"""
Small persisted app state that isn't user-editable config: the first-launch
disclaimer flag and recent executable-build history. Kept in its own file
(app_state.json), separate from config.json, since the Settings fields
fully overwrite config.json on every save.
"""

import json
import os
from datetime import datetime

from src.common import paths

STATE_FILENAME = "app_state.json"
MAX_BUILD_HISTORY = 10


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


def load_build_history() -> list:
    return _load().get("recent_builds", [])


def record_build(exe_path: str) -> None:
    state = _load()
    history = [h for h in state.get("recent_builds", []) if h.get("path") != exe_path]
    history.insert(0, {"path": exe_path, "timestamp": datetime.now().isoformat(timespec="seconds")})
    state["recent_builds"] = history[:MAX_BUILD_HISTORY]
    _save(state)
