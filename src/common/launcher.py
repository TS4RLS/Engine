"""Launches The Sims 4 via Steam or a direct executable, per the user's
config. Pure logic, no GUI framework dependency -- shared by the main
app's "Launch The Sims 4" button (src/gui/main_window.py) and the
standalone runner executable (runner.py), which has no GUI at all.
"""
import os
import subprocess
import webbrowser

# The Sims 4's own Steam App ID -- stable, public, same for everyone who
# owns it on Steam (unlike an install path, which varies per machine).
SIMS4_STEAM_APP_ID = "1222670"
SIMS4_STEAM_LAUNCH_URI = f"steam://rungameid/{SIMS4_STEAM_APP_ID}"
SIMS4_EXE_CANDIDATES = ("TS4_x64.exe", "TS4.exe")


class LaunchError(Exception):
    """Raised with a short, user-facing message describing what to fix."""


def launch_game(cfg: dict) -> str:
    """Launches the game per cfg's launch_via_steam/game_folder settings.
    Returns a short status string on success; raises LaunchError (with a
    message safe to show the user directly) on failure."""
    via_steam = cfg.get("launch_via_steam", True)

    if via_steam:
        try:
            opened = webbrowser.open(SIMS4_STEAM_LAUNCH_URI)
        except Exception as e:
            raise LaunchError(f"Couldn't hand off to Steam: {e}") from e
        if not opened:
            raise LaunchError(
                "Couldn't hand off to Steam. Make sure Steam is installed "
                "and you own The Sims 4 on it, or uncheck \"Launch via "
                "Steam\" in the Build tab and set a game folder instead."
            )
        return "Launch request sent to Steam."

    game_folder = cfg.get("game_folder") or ""
    exe_path = next(
        (os.path.join(game_folder, name) for name in SIMS4_EXE_CANDIDATES
         if os.path.isfile(os.path.join(game_folder, name))),
        None,
    )
    if not exe_path:
        raise LaunchError(
            "No Sims 4 executable (TS4_x64.exe/TS4.exe) found in the "
            "configured game folder. Set it in the Build tab to the "
            "folder that directly contains the game's .exe."
        )
    try:
        subprocess.Popen([exe_path], cwd=game_folder)
    except OSError as e:
        raise LaunchError(f"Couldn't launch {exe_path}: {e}") from e
    return f"Launched: {exe_path}"
