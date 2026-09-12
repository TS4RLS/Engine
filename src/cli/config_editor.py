"""
config.json read/write helpers, shared by gui.py (Build tab) and
src/build/executable_builder.py. Not a CLI tool itself — the interactive
config wizard was removed along with the rest of the text-menu CLI; the
GUI's Build tab is the only editor now.
"""

import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.common import paths
from src.common.config_format import parse_jsonc, dump_commented
from src.cli.cli_colors import error

# (key, type, description, required, default-when-not-required)
SETTINGS = [
    ("images_folder", "str", "Folder containing your source images", True, ""),
    ("mods_folder", "str", "Your Sims 4 Mods folder", True, ""),
    ("is_vertical", "bool", "Combine 2 portrait images side-by-side into one loading screen", False, True),
    ("rename_files", "bool", "Rename every image to a random name (and convert to JPEG) before picking", False, False),
    ("non_interactive", "bool", 'Never block on the "press any key to close" prompt', False, True),
    ("target_width", "int", "Loading screen output width", False, 1920),
    ("target_height", "int", "Loading screen output height", False, 1080),
    ("launch_via_steam", "bool", "Launch The Sims 4 via Steam (steam://) instead of a direct .exe", False, True),
    ("game_folder", "str", "Sims 4 game install folder (only used when not launching via Steam)", False, ""),
]


def load_config() -> dict:
    config_path = paths.resolve_config_path()
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return parse_jsonc(f.read())
        except (OSError, json.JSONDecodeError):
            print(error("config.json is missing or contains invalid JSON — starting fresh."))
    return {}


def save_config(cfg: dict) -> str:
    config_path = paths.resolve_config_path()
    paths.ensure_parent_dir(config_path)
    dump_commented(cfg, SETTINGS, config_path)
    return config_path


def format_value(value) -> str:
    return "(not set)" if value is None or value == "" else str(value)
