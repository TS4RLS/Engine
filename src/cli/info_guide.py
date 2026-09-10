"""
Prints project info, support, and issue-reporting links. Run via the CLI
menu (cli/menu.py) or directly:
    python src/cli/info_guide.py
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.cli import cli_colors
from src.common import paths

REPO_URL = "https://github.com/StuxieDev/Sims-4-Random-Loading-Screen"


def _get_version() -> str:
    try:
        with open(os.path.join(_ROOT, "VERSION.md"), "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "?"


def run():
    print(cli_colors.banner(
        "Sims 4 Random Loading Screen",
        f"v{_get_version()}\nBuilt & Maintained by StuxieDev",
    ))
    print()
    print("Automatically picks a random image from a folder and installs it")
    print("as your Sims 4 loading screen mod — run it before launching the")
    print("game and get a fresh screen every time.")
    print()
    print(cli_colors.bold("Repository"))
    print(f"  {REPO_URL}")
    print()
    print(cli_colors.bold("Documentation"))
    print("  README.md              Setup, configuration, and usage")
    print("  docs/STEAM_GUIDE.md    Adding this to Steam with custom artwork")
    print("  docs/CONTRIBUTING.md   How to contribute changes")
    print("  CHANGELOG.md           What changed in each version")
    print()
    print(cli_colors.bold("Your config file"))
    print(f"  {paths.resolve_config_path()}")
    print()
    print(cli_colors.bold("Support & bug reports"))
    print(f"  Open an issue: {REPO_URL}/issues")
    print(f"  Existing discussions: {REPO_URL}/issues?q=is%3Aissue")
    print()
    print("When reporting a problem, include your OS, the exact error")
    print("message, and (with personal paths redacted) your config.json.")


if __name__ == "__main__":
    run()
