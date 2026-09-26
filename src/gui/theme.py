"""Light/dark theme for the GUI, matching ts4rls.stuxie.dev's palette (same
tokens as style.css's :root/[data-theme] blocks, translated from CSS custom
properties to QSS).

Unlike TWRAR's theme.py (which only auto-detects the OS color scheme),
TS4RLS keeps a manual toggle -- see main_window.py's theme button -- so
tokens()/stylesheet() take the active theme name explicitly rather than
reading it from the OS. The toggle isn't persisted across restarts
(matches the old Tk build's behavior): every launch starts at
DEFAULT_THEME.
"""
from __future__ import annotations

import re

import os

from src.common import paths

DEFAULT_THEME = "dark"

# QSS's url() needs forward slashes even on Windows -- backslashes get
# parsed as escape characters and silently break the rule.
_CHECK_ICON = paths.resource_path(os.path.join("assets", "checkbox_check.png")).replace(os.sep, "/")

LIGHT = dict(
    bg="#f6faf5", bg_alt="#eef5ec", panel="#ffffff", border="#d9e5d6",
    text="#16241a", text_dim="#4c5f49", muted="#7c8c78",
    accent="#2e7d32", accent_hover="#256428", accent_contrast="#ffffff",
    error="#b3312f",
)

DARK = dict(
    bg="#10160f", bg_alt="#151d14", panel="#1a2419", border="#2a3728",
    text="#e7f0e5", text_dim="#a8b8a4", muted="#6d7d6a",
    accent="#4fc264", accent_hover="#6fd082", accent_contrast="#ffffff",
    error="#d98c8c",
)

_THEMES = {"light": LIGHT, "dark": DARK}

# Always-dark terminal-style log boxes (Home/Build action logs) -- these
# stay dark regardless of the active app theme, same as the old Tk build.
LOG_TERMINAL = {"bg": "#0d0d0d", "fg": "#d4d4d4"}

_QSS_TEMPLATE = """
QWidget {{
    background-color: {bg};
    color: {text};
    selection-background-color: {accent};
    selection-color: {accent_contrast};
    font-size: 9pt;
}}
QMainWindow, QDialog {{
    background-color: {bg};
}}
QTabWidget::pane {{
    border: 1px solid {border};
    background: {bg};
    top: -1px;
}}
QTabBar::tab {{
    background: {bg_alt};
    color: {text_dim};
    padding: 6px 16px;
    border: 1px solid {border};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{
    background: {bg};
    color: {text};
    border: 1px solid {accent};
    border-bottom: none;
}}
QTabBar::tab:hover:!selected {{
    color: {text};
}}
QPushButton {{
    background: {panel};
    color: {text};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 6px 14px;
}}
QPushButton:hover {{
    /* Qt's QSS engine doesn't reliably apply a pseudo-state rule that
       only overrides one sub-property (border-color) of a shorthand
       (border) set in the base rule -- redeclaring the full "border"
       shorthand here, not just its color, is what actually takes
       effect on hover. */
    border: 1px solid {accent};
}}
QPushButton:pressed {{
    background: {bg_alt};
    border: 1px solid {accent};
}}
QPushButton:disabled {{
    color: {muted};
    border: 1px solid {border};
    background: {bg_alt};
}}
QLineEdit, QPlainTextEdit, QTextEdit {{
    background: {panel};
    color: {text};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 3px 5px;
}}
QLineEdit:focus {{
    border: 1px solid {accent};
}}
QCheckBox {{
    color: {text};
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 17px;
    height: 17px;
    border: 1px solid {border};
    border-radius: 3px;
    background: {panel};
}}
QCheckBox::indicator:checked {{
    background: {accent};
    border: 1px solid {accent};
    image: url({check_icon});
}}
QCheckBox::indicator:hover {{
    border: 1px solid {accent};
}}
QGroupBox {{
    border: 1px solid {border};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
}}
QGroupBox::title {{
    color: {text};
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}}
QScrollArea {{
    border: none;
    background: {bg};
}}
QScrollArea > QWidget > QWidget {{
    background: {bg};
}}
QScrollBar:vertical {{
    background: {bg_alt};
    width: 13px;
    border-radius: 6px;
}}
QScrollBar:horizontal {{
    background: {bg_alt};
    height: 13px;
    border-radius: 6px;
}}
QScrollBar::handle {{
    background: {border};
    border-radius: 5px;
    min-height: 24px;
    min-width: 24px;
}}
QScrollBar::handle:hover {{
    background: {muted};
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0;
    width: 0;
}}
QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
}}
QLabel[hint="true"] {{
    color: {text_dim};
}}
QLabel[error="true"] {{
    color: {error};
}}
QLabel[link="true"] {{
    color: {accent};
}}
QMessageBox QLabel {{
    color: {text};
}}
"""


def tokens(theme_name: str) -> dict[str, str]:
    return _THEMES.get(theme_name, DARK)


def stylesheet(theme_name: str) -> str:
    return _QSS_TEMPLATE.format(check_icon=_CHECK_ICON, **tokens(theme_name))


def accent_color(theme_name: str) -> str:
    return tokens(theme_name)["accent"]


# Changelog section-type colours -- fixed across every project and matching
# the website's changelog badges: Added green, Changed blue, Fixed orange,
# Removed red, Security purple, Deprecated grey. Light-theme foregrounds are
# darker shades of the same hues so they keep contrast on light panels.
CHANGELOG_SECTION_ORDER = ("added", "changed", "fixed", "removed", "security", "deprecated")
_CHANGELOG_COLORS_DARK = {
    "added": "#2ecc71",
    "changed": "#3ba7ff",
    "fixed": "#ffa64d",
    "removed": "#ff4d4d",
    "security": "#b06bff",
    "deprecated": "#8a8a94",
}
_CHANGELOG_COLORS_LIGHT = {
    "added": "#17804a",
    "changed": "#1a6fc2",
    "fixed": "#a85400",
    "removed": "#c62828",
    "security": "#7a3fc7",
    "deprecated": "#5c5c66",
}


def changelog_section_color(section: str, dark: bool) -> str | None:
    """Colour for a changelog "### <Type>" heading, or None for unknown types."""
    colors = _CHANGELOG_COLORS_DARK if dark else _CHANGELOG_COLORS_LIGHT
    return colors.get(section.strip().lower())


def sort_changelog_sections(md_text: str) -> str:
    """Reorder the "### " sections inside each "## " release into
    CHANGELOG_SECTION_ORDER at render time (unknown types keep their relative
    order and go last). Text before a release's first "### " stays put; each
    section moves as a whole, heading plus body."""
    rank = {name: i for i, name in enumerate(CHANGELOG_SECTION_ORDER)}
    out: list[str] = []
    sections: list[tuple[str, list[str]]] | None = None

    def flush() -> None:
        nonlocal sections
        if not sections:
            sections = None
            return
        ordered = sorted(
            enumerate(sections),
            key=lambda item: (rank.get(item[1][0].strip().lower(), len(rank)), item[0]),
        )
        for _, (_, body) in ordered:
            if out and out[-1].strip() and not re.match(r"#{1,2} ", out[-1]):
                out.append("")
            out.extend(body)
        sections = None

    for line in md_text.splitlines():
        if re.match(r"#{1,2} ", line):
            flush()
            out.append(line)
        elif line.startswith("### "):
            if sections is None:
                sections = []
            sections.append((line[4:], [line]))
        elif sections is not None:
            sections[-1][1].append(line)
        else:
            out.append(line)
    flush()
    return "\n".join(out)
