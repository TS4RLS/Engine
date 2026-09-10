"""
Interactive config.json editor — review every setting and change it from
the CLI instead of hand-editing JSON. Run via the CLI menu (cli/menu.py) or
directly:
    python src/cli/config_editor.py

When config.json doesn't exist yet, this automatically runs a quick-setup
wizard that walks through every setting in order (Enter accepts the
default/current value, or type a custom one) instead of dropping you into
the pick-one-to-edit menu with everything unset.
"""

import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.common import paths
from src.common.config_format import parse_jsonc, dump_commented
from src.cli.cli_colors import banner, bold, cyan, error, success

# (key, type, description, required, default-when-not-required)
SETTINGS = [
    ("images_folder", "str", "Folder containing your source images", True, ""),
    ("mods_folder", "str", "Your Sims 4 Mods folder", True, ""),
    ("is_vertical", "bool", "Combine 2 portrait images side-by-side into one loading screen", False, True),
    ("rename_files", "bool", "Rename every image to a random name (and convert to JPEG) before picking", False, False),
    ("launch_game", "bool", "Automatically launch Sims 4 after generating the mod", False, True),
    ("non_interactive", "bool", 'Never block on the "press any key to close" prompt', False, True),
    ("launch_via_steam", "bool", "Launch via Steam (steam://rungameid/...) instead of game_exe", False, True),
    ("game_exe", "str", "Direct path to TS4_x64.exe — only used when launch_via_steam is false", False, ""),
    ("target_width", "int", "Loading screen output width", False, 1920),
    ("target_height", "int", "Loading screen output height", False, 1080),
    ("create_curseforge_version", "bool", "Also build the TS4_x64 CurseForge pre-launch executable", False, False),
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


def parse_value(kind: str, raw: str, current):
    if kind == "bool":
        return raw.lower() in ("y", "yes", "true", "1")
    if kind == "int":
        try:
            return int(raw)
        except ValueError:
            print(error("Not a whole number — keeping the previous value."))
            return current
    return raw


def prompt_new_value(key: str, kind: str, current, ask=input):
    raw = ask(f"  New value for '{key}' [{format_value(current)}]: ").strip()
    if not raw:
        return current
    return parse_value(kind, raw, current)


def run_wizard(cfg: dict, ask=input) -> dict:
    print()
    print(banner("Quick Setup", "Press Enter to accept the default/current value, or type your own."))
    for key, kind, desc, required, default in SETTINGS:
        current = cfg.get(key, None if required else default)
        while True:
            label = "REQUIRED, no default" if required and current in (None, "") else format_value(current)
            print(f"\n{bold(key)} — {desc}")
            raw = ask(f"  [{label}]: ").strip()
            if not raw:
                if required and current in (None, ""):
                    print(error("This setting is required — please enter a value."))
                    continue
                value = current
            else:
                value = parse_value(kind, raw, current)
            cfg[key] = value
            break
    return cfg


def run():
    config_path = paths.resolve_config_path()
    is_new = not os.path.isfile(config_path)
    cfg = load_config()

    if is_new:
        print(error("config.json not found."))
        print("Let's set it up now — you can change any of this again later.")
        cfg = run_wizard(cfg)
        saved_to = save_config(cfg)
        print(success(f"\nSaved to {saved_to}"))

    while True:
        print()
        print(banner("Config Settings"))
        for i, (key, _kind, _desc, required, default) in enumerate(SETTINGS, start=1):
            value = cfg.get(key, None if required else default)
            marker = "*" if required else " "
            print(f"  {i:>2}){marker} {key:<26} = {format_value(value)}")
        print()
        print("   * required   w) Quick setup wizard   0) Save and exit   q) Quit without saving")
        choice = input("\nSelect a setting to change: ").strip().lower()

        if choice == "0":
            for key, _kind, _desc, required, default in SETTINGS:
                if key not in cfg and not required:
                    cfg[key] = default
            saved_to = save_config(cfg)
            print(success(f"\nSaved to {saved_to}"))
            return

        if choice in ("q", "quit", "exit"):
            print(cyan("\nDiscarded changes."))
            return

        if choice == "w":
            cfg = run_wizard(cfg)
            continue

        try:
            key, kind, desc, _required, default = SETTINGS[int(choice) - 1]
        except (ValueError, IndexError):
            print(error("Invalid selection."))
            continue

        print(f"\n{bold(key)} — {desc}")
        cfg[key] = prompt_new_value(key, kind, cfg.get(key, default))


if __name__ == "__main__":
    run()
