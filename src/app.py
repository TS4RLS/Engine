"""
Single entry point for the app — this is what gets built into the
distributed executable(s). Run directly for development too:
    python src/app.py                     -> GUI
    python src/app.py --cli               -> interactive text menu
    python src/app.py --generate [--force-launch]  -> headless, one-shot

When the running executable's own filename matches the CurseForge disguise
name (TS4_x64[.exe]), it always behaves as --generate --force-launch with
no arguments needed, so the same build works as both the normal app and
the CurseForge pre-launch script.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

CURSEFORGE_NAME = "ts4_x64"


def _is_curseforge_build() -> bool:
    name = os.path.splitext(os.path.basename(sys.executable if getattr(sys, "frozen", False) else __file__))[0]
    return name.lower() == CURSEFORGE_NAME


def main():
    argv = sys.argv[1:]
    force_launch = "--force-launch" in argv or _is_curseforge_build()
    headless = "--generate" in argv or _is_curseforge_build()

    if headless:
        from src.cli import cli_colors
        from src.core.generator import GeneratorError, load_config, generate

        try:
            cfg = load_config()
            result = generate(cfg, force_launch=force_launch)
        except GeneratorError as e:
            print("\n" + cli_colors.error(str(e)))
            sys.exit(1)
        if result.warning:
            print(cli_colors.warning(result.warning))
        return

    if "--cli" in argv:
        from src.cli.menu import run as run_menu
        run_menu()
        return

    from src.gui import App
    App().mainloop()


if __name__ == "__main__":
    main()
