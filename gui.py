"""
TS4RLS — single entry point and desktop GUI, built on PySide6/Qt.

Run standalone:
    python gui.py              -> GUI
    python gui.py --generate   -> headless, one-shot

Use src/build/create_release_files.py to build the executable.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.common import app_state, paths
from src.core.generator import GeneratorError, generate, load_config as load_generator_config

ICON_PATH = paths.resource_path(os.path.join("assets", "icon.ico"))


def _attach_parent_console():
    # The exe is built --windowed (see src/build/create_release_files.py),
    # so it has no console of its own -- print() below would otherwise go
    # nowhere. If this was launched from an existing terminal, attach to
    # it and rebind stdout/stderr so --generate's output actually shows up
    # there. Only relevant for a frozen Windows build -- `python gui.py`
    # from source already has a normal console, and if there's no parent
    # console to attach to (e.g. double-clicked from Explorer), this is a
    # no-op and --generate just stays silent, same as before.
    if not (paths.is_frozen() and sys.platform == "win32"):
        return
    try:
        import ctypes
        ATTACH_PARENT_PROCESS = -1
        if ctypes.windll.kernel32.AttachConsole(ATTACH_PARENT_PROCESS):
            sys.stdout = open("CONOUT$", "w")
            sys.stderr = open("CONOUT$", "w")
    except Exception:
        pass
    # No parent console (e.g. double-clicked from Explorer/a Steam
    # shortcut): a --windowed build's sys.stdout/stderr may be None,
    # which would crash the print() calls below. Give them somewhere
    # harmless to write instead.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")


def _run_headless():
    _attach_parent_console()
    from src.cli import cli_colors

    try:
        cfg = load_generator_config()
        result = generate(cfg)
    except GeneratorError as e:
        print("\n" + cli_colors.error(str(e)))
        sys.exit(1)
    print(f"Done! Written to: {result.output_path}")


def _run_gui():
    if sys.platform == "win32":
        # Without an explicit AppUserModelID, Windows groups this window's
        # taskbar button under the launching python.exe's own icon instead
        # of the one set below via setWindowIcon() -- this is what actually
        # controls the taskbar/Alt-Tab icon, setWindowIcon() alone does not.
        import ctypes
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("StuxieDev.TS4RLS")
        except OSError:
            pass

    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication, QDialog

    from src.gui import theme
    from src.gui.disclaimer import DisclaimerDialog
    from src.gui.main_window import MainWindow

    app = QApplication(sys.argv)
    # Applied here, before the disclaimer dialog (which may run and finish
    # before MainWindow is ever constructed) -- MainWindow re-applies its
    # own (possibly toggled) theme later, but the disclaimer needs this
    # done upfront or it renders with no styling (default OS/Fusion look:
    # no themed borders, no hover states) instead of matching the app.
    app.setStyleSheet(theme.stylesheet(theme.DEFAULT_THEME))
    if os.path.isfile(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    if not app_state.is_disclaimer_confirmed():
        if DisclaimerDialog().exec() != QDialog.DialogCode.Accepted:
            return
        app_state.confirm_disclaimer()

    window = MainWindow()
    if os.path.isfile(ICON_PATH):
        window.setWindowIcon(QIcon(ICON_PATH))
    window.show()

    sys.exit(app.exec())


def main():
    if "--generate" in sys.argv[1:]:
        _run_headless()
        return
    _run_gui()


if __name__ == "__main__":
    main()
