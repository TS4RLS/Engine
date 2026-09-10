"""
Interactive text menu — the CLI side of the single app (src/app.py --cli).
Generate / Rename / Configure / Info / Exit, all in-process. "Build
executables" and "Run tests" are dev-only and stay in Launcher.bat/
Launcher.sh, not in this shipped menu.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.cli import cli_colors, config_editor, info_guide
from src.core.generator import GeneratorError, generate, load_config
from src.core.renamer import rename_images


def _get_version() -> str:
    try:
        with open(os.path.join(_ROOT, "VERSION.md"), "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "?"


def _do_generate():
    try:
        cfg = load_config()
        result = generate(cfg)
    except GeneratorError as e:
        print("\n" + cli_colors.error(str(e)))
        return
    if result.warning:
        print(cli_colors.warning(result.warning))
    print(cli_colors.success("\nDone!"))


def _do_rename():
    try:
        cfg = load_config()
    except GeneratorError as e:
        print("\n" + cli_colors.error(str(e)))
        return
    folder = cfg["images_folder"]
    if not os.path.isdir(folder):
        print(cli_colors.error(f"Images folder not found: {folder}"))
        return
    ok, failed = rename_images(folder)
    print(f"  Renamed {ok} file(s)" + (f", {failed} skipped." if failed else "."))


def run():
    from src.common import paths as _paths

    if not os.path.isfile(_paths.resolve_config_path()):
        config_editor.run()

    while True:
        print()
        print(cli_colors.banner(
            "Sims 4 Random Loading Screen - Interactive Menu",
            f"v{_get_version()}\nBuilt & Maintained by StuxieDev",
        ))
        print()
        print(f"      {cli_colors.green('1)')} Generate loading screen (and launch game if configured)")
        print(f"      {cli_colors.green('2)')} Rename images only")
        print(f"      {cli_colors.green('3)')} Configure settings")
        print(f"      {cli_colors.green('4)')} Info / about & support")
        print(f"      {cli_colors.green('5)')} Exit")
        print()
        choice = input("    Select an option [1-5]: ").strip()

        if choice == "1":
            _do_generate()
        elif choice == "2":
            _do_rename()
        elif choice == "3":
            config_editor.run()
        elif choice == "4":
            info_guide.run()
        elif choice == "5":
            return
        else:
            print(cli_colors.error("Invalid option. Please choose 1-5."))


if __name__ == "__main__":
    run()
