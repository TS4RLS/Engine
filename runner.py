"""
TS4RLS runner — a separate, minimal, GUI-less entry point, compiled to its
own executable by the Build tab's "Build executable" button (see
src/gui/runner_builder.py) for use OUTSIDE the main app: as a Steam
"non-Steam game" launch target, or a CurseForge/Overwolf custom launch
executable.

Running the built runner regenerates the loading screen from the current
config.json, then launches the game -- no window or console of its own,
and nothing baked in at build time, so it always reflects whatever
config.json says right now. Point Steam/CurseForge at it instead of (or
renamed to replace) the game's own executable, and starting the game
through your normal launcher gets a fresh loading screen every time with
no extra step.

Not meant to be run directly from source for everyday use -- `gui.py`'s
own Home tab already has "Generate loading screen" and "Launch The Sims 4"
buttons that do the same two things interactively.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.common import launcher
from src.core.generator import GeneratorError, generate, load_config as load_generator_config


def main():
    # Every step here is best-effort: this has no window or console to
    # show an error in, and is meant to run fully unattended (launched by
    # Steam/CurseForge, not a person watching it) -- nothing may ever
    # raise out of main(), or PyInstaller's own crash dialog pops up with
    # no way to dismiss it except Task Manager. A missing config.json (or
    # any other generate() failure) should still fall through to
    # attempting to launch the game, not abort before that.
    try:
        cfg = load_generator_config()
    except GeneratorError:
        cfg = {}

    try:
        generate(cfg)
    except GeneratorError:
        pass

    try:
        launcher.launch_game(cfg)
    except launcher.LaunchError:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Last-resort catch-all -- see the comment in main() for why
        # nothing may ever raise all the way out of this script.
        pass
