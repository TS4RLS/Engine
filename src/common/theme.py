"""
Best-effort OS dark-mode detection, used by the GUI to pick which icon set
(main "dark" branding vs. green plumbob "alt"/"light" branding) to show.
Defaults to dark (the main brand) whenever detection is inconclusive.
"""

import subprocess
import sys


def detect_dark_mode() -> bool:
    try:
        if sys.platform == "win32":
            return _windows_dark_mode()
        if sys.platform == "darwin":
            return _macos_dark_mode()
        return _linux_dark_mode()
    except Exception:
        return True


def _windows_dark_mode() -> bool:
    import winreg
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
    )
    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
    return value == 0


def _macos_dark_mode() -> bool:
    result = subprocess.run(
        ["defaults", "read", "-g", "AppleInterfaceStyle"],
        capture_output=True, text=True, timeout=2,
    )
    return result.returncode == 0 and "dark" in result.stdout.lower()


def _linux_dark_mode() -> bool:
    result = subprocess.run(
        ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
        capture_output=True, text=True, timeout=2,
    )
    if result.returncode == 0:
        return "dark" in result.stdout.lower()
    return True
