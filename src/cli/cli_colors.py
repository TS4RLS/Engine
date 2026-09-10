"""
Shared ANSI color helpers for the CLI scripts. No-ops (plain text) when
stdout isn't a terminal or the NO_COLOR environment variable is set, so
piping output or redirecting to a file never leaves stray escape codes.
"""

import os
import sys

ENABLED = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

if ENABLED and os.name == "nt":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        ENABLED = False


def _wrap(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if ENABLED else text


def bold(text: str) -> str:
    return _wrap(text, "1")


def red(text: str) -> str:
    return _wrap(text, "91")


def green(text: str) -> str:
    return _wrap(text, "92")


def yellow(text: str) -> str:
    return _wrap(text, "93")


def cyan(text: str) -> str:
    return _wrap(text, "96")


def magenta(text: str) -> str:
    return _wrap(text, "95")


def error(text: str) -> str:
    return red(f"[ERROR] {text}")


def warning(text: str) -> str:
    return yellow(f"[WARNING] {text}")


def success(text: str) -> str:
    return green(text)


def banner(title: str, subtitle: str = "", width: int = 69) -> str:
    lines = [cyan("=" * width), bold(title.center(width))]
    for line in subtitle.splitlines():
        lines.append(line.center(width))
    lines.append(cyan("=" * width))
    return "\n".join(lines)
