"""TS4RLS's main window: Home / Build / About tabs.

Ports every feature of the old Tk build (see gui.py's git history for that
version) onto PySide6. A few things are genuinely simpler here rather than
just translated 1:1 -- see the module docstrings on theme.py, workers.py,
and disclaimer.py for what disappeared and why.
"""
from __future__ import annotations

import functools
import os
import re
import shutil
import zipfile
from html import escape

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFileDialog, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPlainTextEdit, QPushButton,
    QScrollArea, QSizePolicy, QTabWidget, QTextEdit, QVBoxLayout, QWidget,
)

from src.common import app_state, launcher, paths, update_checker
from src.cli import config_editor
from src.cli.config_editor import SETTINGS, format_value
from src.core.generator import GeneratorError, find_legacy_output, load_config as load_generator_config
from src.gui import theme
from src.gui.workers import GenerateWorker, RenameWorker, SubprocessWorker, UpdateCheckWorker

REPO_URL = "https://github.com/TS4RLS/Engine"
WEBSITE_URL = "https://ts4rls.stuxie.dev"
AUTHOR_NAME = "StuxieDev"
AUTHOR_URL = "https://stuxie.dev"
STUXIEDEV_PROJECTS_URL = "https://projects.stuxie.dev"

CHANGELOG_PATH = paths.resource_path("CHANGELOG.md")
FOLDER_KEYS = {"images_folder", "mods_folder", "game_folder"}
RUNNER_DEFAULT_NAME = "RLSRunner"
RUNNER_CURSEFORGE_NAME = "TS4_x64"

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_version() -> str:
    try:
        with open(paths.resource_path("VERSION.md"), "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "?"


def find_python() -> str:
    for candidate in ("python3", "python"):
        path = shutil.which(candidate)
        if path:
            return path
    return ""


def _styled_label(text: str, kind: str | None = None) -> QLabel:
    """kind: "hint"/"error"/"link" sets the matching QSS property selector
    from theme.py (QLabel[hint="true"] etc.) instead of a one-off inline
    color, so these stay correct across theme toggles automatically."""
    label = QLabel(text)
    if kind:
        label.setProperty(kind, "true")
    return label


def _render_changelog_html(md_text: str, theme_name: str, tokens: dict) -> str:
    """Converts CHANGELOG.md's actual subset of markdown (##/###
    headings, "- " bullets, **bold**, `code`) straight to HTML for
    QTextEdit.setHtml() -- far simpler than the old Tk version's
    manual per-line, per-run tag_configure()/insert() loop."""
    accent = tokens["accent"]
    text_dim = tokens["text_dim"]
    text_color = tokens["text"]
    code_color = "#ffbe6a" if theme_name == "dark" else "#a35e00"

    def inline(s: str) -> str:
        s = escape(s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"`([^`]+)`", rf'<code style="color:{code_color};">\1</code>', s)
        return s

    out = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in md_text.splitlines():
        if line.startswith("## "):
            close_list()
            out.append(f'<h2 style="color:{accent};">{inline(line[3:].strip())}</h2>')
        elif line.startswith("### "):
            close_list()
            out.append(f'<h3 style="color:{text_dim};">{inline(line[4:].strip())}</h3>')
        elif line.startswith("- ") or line.startswith("  - "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(line.lstrip('- ').lstrip())}</li>")
        elif line.startswith("# "):
            continue  # top-level title -- shown as a label above instead
        elif line.strip():
            close_list()
            out.append(f'<p style="color:{text_dim};">{inline(line.strip())}</p>')
        else:
            close_list()
    close_list()

    return f'<div style="color:{text_color}; font-family: \'Segoe UI\', sans-serif;">' + "".join(out) + "</div>"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"TS4RLS (The Sims 4 Random Loading Screen) — v{_get_version()}")
        self.setMinimumSize(760, 580)
        self.resize(960, 760)

        self.python_exe = find_python()
        self.field_vars: dict[str, tuple] = {}
        self.home_display_labels: dict[str, QLabel] = {}
        self.logs: dict[str, QPlainTextEdit] = {}
        self.status_labels: dict[str, QLabel] = {}
        self.buttons: dict[str, list[QPushButton]] = {}
        self._worker = None
        self._update_worker = None

        self.theme = theme.DEFAULT_THEME
        self._apply_theme()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.home_tab = QWidget()
        self.build_tab = QWidget()
        self.about_tab = QWidget()
        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.build_tab, "Build")
        self.tabs.addTab(self.about_tab, "About")
        self.tabs.currentChanged.connect(self._on_tab_changed)

        self._build_home_tab()
        self._build_build_tab()
        self._build_about_tab()

    def _on_tab_changed(self, index: int) -> None:
        if self.tabs.widget(index) is self.home_tab:
            self._refresh_home_display()

    # ── Theming ──────────────────────────────────────────────────────

    def _tokens(self) -> dict:
        return theme.tokens(self.theme)

    def _apply_theme(self) -> None:
        QApplication.instance().setStyleSheet(theme.stylesheet(self.theme))

    def _theme_toggle_label(self) -> str:
        return "Switch to light mode" if self.theme == "dark" else "Switch to dark mode"

    def _on_toggle_theme(self) -> None:
        self.theme = "light" if self.theme == "dark" else "dark"
        self._apply_theme()
        self.theme_toggle_btn.setText(self._theme_toggle_label())
        if hasattr(self, "changelog_text"):
            self._load_changelog()

    # ── First-launch disclaimer is a separate module: src/gui/disclaimer.py

    # ── Home tab (daily use: display current settings, run things) ────

    def _build_home_tab(self) -> None:
        outer = QVBoxLayout(self.home_tab)
        outer.setContentsMargins(12, 12, 12, 12)

        top_row = QHBoxLayout()
        top_row.addStretch(1)
        self.theme_toggle_btn = QPushButton(self._theme_toggle_label())
        self.theme_toggle_btn.clicked.connect(self._on_toggle_theme)
        top_row.addWidget(self.theme_toggle_btn)
        outer.addLayout(top_row)

        settings_box = QGroupBox("Current settings")
        grid = QGridLayout(settings_box)
        for row, (key, kind, desc, required, default) in enumerate(SETTINGS):
            grid.addWidget(_styled_label(key), row, 0)
            value_label = _styled_label("", "hint")
            grid.addWidget(value_label, row, 1)
            self.home_display_labels[key] = value_label
        grid.setColumnStretch(1, 1)
        outer.addWidget(settings_box)

        edit_btn = QPushButton("Edit settings in the Build tab...")
        edit_btn.clicked.connect(lambda: self.tabs.setCurrentWidget(self.build_tab))
        outer.addWidget(edit_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self.legacy_warning = QWidget()
        legacy_row = QHBoxLayout(self.legacy_warning)
        legacy_row.setContentsMargins(0, 0, 0, 0)
        legacy_row.addWidget(_styled_label(
            "Found an old loading screen mod from a previous version — delete it before generating a new one.",
            "error",
        ), 1)
        delete_legacy_btn = QPushButton("Delete legacy folder")
        delete_legacy_btn.clicked.connect(self._delete_legacy_folder)
        legacy_row.addWidget(delete_legacy_btn)
        self.legacy_warning.setVisible(False)
        outer.addWidget(self.legacy_warning)

        buttons = QHBoxLayout()
        self.buttons["home"] = []

        def add_button(label, command):
            btn = QPushButton(label)
            btn.clicked.connect(command)
            buttons.addWidget(btn)
            self.buttons["home"].append(btn)
            return btn

        self.generate_button = add_button("Generate loading screen", self._run_generate)
        add_button("Rename images only", self._run_rename)
        add_button("Build executable", self._run_build_from_home)
        add_button("Launch The Sims 4", self._launch_game)
        outer.addLayout(buttons)

        latest_build_box = QGroupBox("Latest build")
        latest_row = QHBoxLayout(latest_build_box)
        self.latest_build_label = _styled_label("No builds yet.", "hint")
        latest_row.addWidget(self.latest_build_label, 1)
        self.latest_build_copy_button = QPushButton("Copy path")
        self.latest_build_copy_button.clicked.connect(self._copy_latest_build_path)
        latest_row.addWidget(self.latest_build_copy_button)
        outer.addWidget(latest_build_box)

        runner_build_box = QGroupBox("Runner build")
        runner_row = QHBoxLayout(runner_build_box)
        self.runner_build_label = _styled_label("Not built yet.", "hint")
        runner_row.addWidget(self.runner_build_label, 1)
        self.runner_build_copy_exe_button = QPushButton("Copy path")
        self.runner_build_copy_exe_button.clicked.connect(self._copy_runner_build_path)
        runner_row.addWidget(self.runner_build_copy_exe_button)
        self.runner_build_copy_folder_button = QPushButton("Copy folder")
        self.runner_build_copy_folder_button.clicked.connect(self._copy_runner_build_folder)
        runner_row.addWidget(self.runner_build_copy_folder_button)
        outer.addWidget(runner_build_box)

        self.status_labels["home"] = QLabel("Ready.")
        outer.addWidget(self.status_labels["home"])

        self.logs["home"] = self._make_log_widget()
        outer.addWidget(self.logs["home"], 1)

        self._refresh_home_display()

    def _make_log_widget(self) -> QPlainTextEdit:
        log = QPlainTextEdit()
        log.setReadOnly(True)
        c = theme.LOG_TERMINAL
        log.setStyleSheet(f"QPlainTextEdit {{ background: {c['bg']}; color: {c['fg']}; }}")
        return log

    def _refresh_home_display(self) -> None:
        cfg = config_editor.load_config()
        for key, kind, desc, required, default in SETTINGS:
            current = cfg.get(key, None if required else default)
            if current is None and key == "mods_folder":
                current = paths.guess_mods_folder() or None
            self.home_display_labels[key].setText(format_value(current))

        mods_folder = cfg.get("mods_folder", "")
        legacy_found = bool(mods_folder and find_legacy_output(mods_folder))
        self.legacy_warning.setVisible(legacy_found)
        self.generate_button.setEnabled(not legacy_found)

        self._refresh_latest_build()
        self._refresh_runner_build()

    def _refresh_runner_build(self) -> None:
        entry = app_state.load_runner_build()
        if entry:
            self.runner_build_label.setText(f"{entry['path']}\nBuilt {entry['timestamp']}")
            self.runner_build_copy_exe_button.setEnabled(True)
            self.runner_build_copy_folder_button.setEnabled(True)
        else:
            self.runner_build_label.setText("Not built yet.")
            self.runner_build_copy_exe_button.setEnabled(False)
            self.runner_build_copy_folder_button.setEnabled(False)

    def _copy_runner_build_path(self) -> None:
        entry = app_state.load_runner_build()
        if entry:
            self._copy_to_clipboard(entry["path"])

    def _copy_runner_build_folder(self) -> None:
        entry = app_state.load_runner_build()
        if entry:
            self._copy_to_clipboard(os.path.dirname(entry["path"]))

    def _refresh_latest_build(self) -> None:
        history = app_state.load_build_history()
        if history:
            latest = history[0]
            self.latest_build_label.setText(f"{latest['path']}\nBuilt {latest['timestamp']}")
            self.latest_build_copy_button.setEnabled(True)
        else:
            self.latest_build_label.setText("No builds yet.")
            self.latest_build_copy_button.setEnabled(False)

    def _copy_latest_build_path(self) -> None:
        history = app_state.load_build_history()
        if history:
            self._copy_to_clipboard(history[0]["path"])

    def _copy_to_clipboard(self, text: str) -> None:
        QApplication.clipboard().setText(text)

    def _delete_legacy_folder(self) -> None:
        mods_folder = load_generator_config().get("mods_folder", "")
        legacy_folder = find_legacy_output(mods_folder) if mods_folder else ""
        if not legacy_folder:
            self._refresh_home_display()
            return
        answer = QMessageBox.question(
            self, "Delete legacy folder",
            f"Permanently delete this folder?\n\n{legacy_folder}",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            shutil.rmtree(legacy_folder)
            self._append_log("home", f"\nDeleted legacy folder: {legacy_folder}\n")
        except Exception as exc:
            QMessageBox.critical(self, "Failed", f"Couldn't delete the folder: {exc}")
        self._refresh_home_display()

    def _run_build_from_home(self) -> None:
        self.tabs.setCurrentWidget(self.build_tab)
        self._run_build_executables()

    # ── Build tab (configure settings, build the executable) ──────────

    def _build_build_tab(self) -> None:
        outer = QVBoxLayout(self.build_tab)
        outer.setContentsMargins(12, 12, 12, 12)

        settings_box = QGroupBox("Settings")
        grid = QGridLayout(settings_box)

        cfg = config_editor.load_config()
        for row, (key, kind, desc, required, default) in enumerate(SETTINGS):
            current = cfg.get(key, None if required else default)
            if current is None and key == "mods_folder":
                current = paths.guess_mods_folder() or None

            label_text = key + (" *" if required else "")
            grid.addWidget(_styled_label(label_text), row, 0, Qt.AlignmentFlag.AlignTop)

            if kind == "bool":
                widget = QCheckBox()
                widget.setChecked(bool(current))
                grid.addWidget(widget, row, 1, Qt.AlignmentFlag.AlignTop)
            else:
                widget = QLineEdit(format_value(current) if current is not None else "")
                widget.setMinimumWidth(260)
                grid.addWidget(widget, row, 1, Qt.AlignmentFlag.AlignTop)
                if key in FOLDER_KEYS:
                    browse_btn = QPushButton("Browse...")
                    browse_btn.clicked.connect(functools.partial(self._browse_folder, widget))
                    grid.addWidget(browse_btn, row, 2, Qt.AlignmentFlag.AlignTop)

            desc_label = _styled_label(desc, "hint")
            desc_label.setWordWrap(True)
            grid.addWidget(desc_label, row, 3, Qt.AlignmentFlag.AlignTop)

            self.field_vars[key] = (widget, kind, required)

        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 2)

        footer_row = len(SETTINGS)
        grid.addWidget(_styled_label("* required", "hint"), footer_row, 0)
        save_btn = QPushButton("Save settings")
        save_btn.clicked.connect(self._save_settings)
        grid.addWidget(save_btn, footer_row, 1)
        outer.addWidget(settings_box)

        build_box = QGroupBox("Build")
        build_row = QHBoxLayout(build_box)
        self.buttons["build"] = []

        def add_button(label, command):
            btn = QPushButton(label)
            btn.clicked.connect(command)
            build_row.addWidget(btn)
            self.buttons["build"].append(btn)
            return btn

        add_button("Build executable", self._run_build_executables)
        test_suite_btn = add_button("Run test suite", self._run_tests)
        outer.addWidget(build_box)

        if paths.is_frozen():
            # A shipped exe has no bundled pytest to test with, but it
            # can still build the runner executable (see
            # _run_build_executables) as long as a system Python capable
            # of running PyInstaller is available -- only the test-suite
            # action needs the actual source checkout.
            test_suite_btn.setEnabled(False)

        # "Build executable" above builds the runner (see
        # _run_build_executables), not the main app -- this shows *that*
        # build's result, same data as the Home tab's own "Runner build"
        # box (app_state.load_runner_build()), not the unrelated history
        # of `python scripts/build_release_files.py` runs (which this
        # tab's button hasn't triggered since the Qt migration).
        history_box = QGroupBox("Runner build")
        self.history_list_layout = QVBoxLayout(history_box)
        outer.addWidget(history_box)
        self._refresh_build_history()

        self.status_labels["build"] = QLabel("Ready.")
        outer.addWidget(self.status_labels["build"])

        self.logs["build"] = self._make_log_widget()
        outer.addWidget(self.logs["build"], 1)

    def _refresh_build_history(self) -> None:
        layout = self.history_list_layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        entry = app_state.load_runner_build()
        if not entry:
            layout.addWidget(_styled_label("Not built yet.", "hint"))
            return

        row = QHBoxLayout()
        row.addWidget(QLabel(f"{entry['path']}  ({entry['timestamp']})"), 1)
        copy_path_btn = QPushButton("Copy path")
        copy_path_btn.clicked.connect(self._copy_runner_build_path)
        row.addWidget(copy_path_btn)
        copy_folder_btn = QPushButton("Copy folder")
        copy_folder_btn.clicked.connect(self._copy_runner_build_folder)
        row.addWidget(copy_folder_btn)
        row_widget = QWidget()
        row_widget.setLayout(row)
        layout.addWidget(row_widget)

    def _browse_folder(self, line_edit: QLineEdit) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select folder", line_edit.text() or _ROOT)
        if path:
            line_edit.setText(path)

    def _save_settings(self) -> None:
        cfg = {}
        for key, (widget, kind, required) in self.field_vars.items():
            if kind == "bool":
                cfg[key] = widget.isChecked()
                continue
            raw = widget.text().strip()
            if not raw:
                if required:
                    QMessageBox.critical(self, "Missing value", f"'{key}' is required.")
                    return
                continue
            if kind == "int":
                try:
                    cfg[key] = int(raw)
                except ValueError:
                    QMessageBox.critical(self, "Invalid value", f"'{key}' must be a whole number.")
                    return
            else:
                cfg[key] = raw

        saved_to = config_editor.save_config(cfg)
        self._refresh_home_display()
        QMessageBox.information(self, "Saved", f"Saved to {saved_to}")

    # ── Shared worker/log plumbing ─────────────────────────────────────

    def _append_log(self, target: str, text: str) -> None:
        self.logs[target].appendPlainText(text.rstrip("\n"))

    def _set_buttons_enabled(self, target: str, enabled: bool) -> None:
        for btn in self.buttons[target]:
            btn.setEnabled(enabled)

    def _start_worker(self, target: str, worker) -> None:
        if self._worker is not None and self._worker.isRunning():
            QMessageBox.warning(self, "Busy", "Another action is already running.")
            return
        self.status_labels[target].setText("Running...")
        self._set_buttons_enabled(target, False)
        worker.line.connect(functools.partial(self._append_log, target))
        worker.done.connect(functools.partial(self._on_worker_done, target))
        self._worker = worker
        worker.start()

    def _on_worker_done(self, target: str, code: int) -> None:
        ok = code == 0
        self.status_labels[target].setText("Done." if ok else f"Failed (exit code {code}).")
        self._set_buttons_enabled(target, True)
        if target == "home":
            self._refresh_home_display()
        elif target == "build":
            self._refresh_build_history()
            self._refresh_home_display()

    # In-process actions (generate/rename): call the core logic directly.

    def _run_generate(self) -> None:
        self._append_log("home", "\n$ Generate loading screen\n")
        self._start_worker("home", GenerateWorker())

    def _run_rename(self) -> None:
        self._append_log("home", "\n$ Rename images\n")
        self._start_worker("home", RenameWorker())

    def _launch_game(self) -> None:
        # launcher.launch_game() just hands off and returns immediately
        # (webbrowser.open for the steam:// URI, Popen for a direct exe)
        # -- no worker thread needed, unlike generate/rename/build which
        # actually do work in-process or via subprocess and wait on it.
        self._append_log("home", "\n$ Launch The Sims 4\n")
        cfg = load_generator_config()
        try:
            message = launcher.launch_game(cfg)
            self._append_log("home", message)
        except launcher.LaunchError as e:
            self._append_log("home", f"[ERROR] {e}")
            QMessageBox.critical(self, "Couldn't launch", str(e))

    # "Build executable" builds the standalone *runner* (runner.py, not
    # gui.py) -- a separate, minimal, GUI-less exe meant to replace the
    # game's own launch target in Steam/CurseForge: running it just
    # regenerates the loading screen from the current config and launches
    # the game, no window or console of its own. Unlike the old
    # from-source-only "rebuild the whole app" action this replaced, this
    # works from a shipped exe too -- it only needs a system Python (same
    # find_python() the subprocess actions already used) capable of
    # running PyInstaller, not the app's own bundled runtime. Rebuilding
    # TS4RLS itself from source is still `python scripts/build_release_files.py`,
    # just without a GUI button for it.

    def _run_build_executables(self) -> None:
        cfg = load_generator_config()
        runner_name = RUNNER_CURSEFORGE_NAME if cfg.get("curseforge_mode") else RUNNER_DEFAULT_NAME
        self._run_subprocess_action("build", ["-m", "src.gui.runner_builder", f"--name={runner_name}"])

    def _run_tests(self) -> None:
        self._run_subprocess_action("build", ["-m", "pytest", "-v"])

    def _run_subprocess_action(self, target: str, args: list) -> None:
        if not self.python_exe:
            QMessageBox.critical(self, "Python not found", "Install Python and restart this app.")
            return
        cmd = [self.python_exe] + args
        self._append_log(target, f"\n$ {' '.join(cmd)}\n")
        self._start_worker(target, SubprocessWorker(cmd, _ROOT))

    # ── About tab ───────────────────────────────────────────────────

    def _link_label(self, text: str, url: str) -> QLabel:
        label = QLabel(f'<a href="{url}" style="color:{self._tokens()["accent"]};">{escape(text)}</a>')
        label.setOpenExternalLinks(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        return label

    def _build_about_tab(self) -> None:
        outer = QVBoxLayout(self.about_tab)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)

        body = QWidget()
        scroll.setWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        logo_path = paths.resource_path(os.path.join("assets", "logo.png"))
        if os.path.isfile(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaledToHeight(64, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(logo_label)

        version_label = QLabel(f"v{_get_version()}")
        font = version_label.font()
        font.setPointSize(font.pointSize() + 4)
        font.setBold(True)
        version_label.setFont(font)
        layout.addWidget(version_label)

        update_row = QHBoxLayout()
        self._update_url = update_checker.RELEASES_PAGE_URL
        self.update_status_label = _styled_label("Checking for updates...", "hint")
        update_row.addWidget(self.update_status_label)
        self.update_link = self._link_label("Download", self._update_url)
        self.update_link.setVisible(False)
        update_row.addWidget(self.update_link)
        self.update_check_btn = QPushButton("Check again")
        self.update_check_btn.clicked.connect(self._start_update_check)
        update_row.addWidget(self.update_check_btn)
        update_row.addStretch(1)
        layout.addLayout(update_row)

        description = QLabel(
            "Automatically picks a random image from a folder and installs it "
            "as your Sims 4 loading screen mod — run it, then launch the game "
            "yourself and get a fresh screen every time."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        layout.addWidget(self._link_label(WEBSITE_URL, WEBSITE_URL))
        layout.addWidget(self._link_label(REPO_URL, REPO_URL))
        layout.addWidget(self._link_label("Report a bug / get support", f"{REPO_URL}/issues"))

        author_row = QHBoxLayout()
        author_row.addWidget(QLabel("Written & Maintained by "))
        avatar_path = paths.resource_path(os.path.join("assets", "author.png"))
        if os.path.isfile(avatar_path):
            avatar_pixmap = QPixmap(avatar_path)
            if not avatar_pixmap.isNull():
                avatar_label = QLabel()
                avatar_label.setPixmap(avatar_pixmap.scaledToHeight(20, Qt.TransformationMode.SmoothTransformation))
                author_row.addWidget(avatar_label)
        author_row.addWidget(self._link_label(AUTHOR_NAME, AUTHOR_URL))
        author_row.addStretch(1)
        layout.addLayout(author_row)

        layout.addWidget(self._link_label("A StuxieDev Project", STUXIEDEV_PROJECTS_URL))

        save_zip_btn = QPushButton("Save Steam artwork (.zip)...")
        save_zip_btn.clicked.connect(self._save_steam_artwork_zip)
        layout.addWidget(save_zip_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(_styled_label(f"Config file: {paths.resolve_config_path()}", "hint"))

        changelog_header = QHBoxLayout()
        changelog_title = QLabel("Changelog")
        font = changelog_title.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        changelog_title.setFont(font)
        changelog_header.addWidget(changelog_title)
        changelog_header.addStretch(1)
        reload_btn = QPushButton("Reload")
        reload_btn.clicked.connect(self._load_changelog)
        changelog_header.addWidget(reload_btn)
        layout.addLayout(changelog_header)

        self.changelog_text = QTextEdit()
        self.changelog_text.setReadOnly(True)
        self.changelog_text.setMinimumHeight(320)
        self.changelog_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.changelog_text, 1)

        self._load_changelog()
        self._start_update_check()

    def _start_update_check(self) -> None:
        self.update_check_btn.setEnabled(False)
        self.update_status_label.setText("Checking for updates...")
        self.update_link.setVisible(False)

        self._update_worker = UpdateCheckWorker(_get_version())
        self._update_worker.result_ready.connect(self._on_update_check_result)
        self._update_worker.start()

    def _on_update_check_result(self, result) -> None:
        self.update_check_btn.setEnabled(True)
        self._update_url = result.url
        if result.error:
            self.update_status_label.setText("Couldn't check for updates.")
        elif result.update_available:
            self.update_status_label.setText(f"Update available: v{result.latest_version} —")
            self.update_link.setText(f'<a href="{result.url}" style="color:{self._tokens()["accent"]};">Download</a>')
            self.update_link.setVisible(True)
        else:
            self.update_status_label.setText("You're on the latest version.")

    def _load_changelog(self) -> None:
        try:
            with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
                md_text = f.read()
        except OSError as e:
            self.changelog_text.setPlainText(f"(Could not read CHANGELOG.md: {e})")
            return
        self.changelog_text.setHtml(_render_changelog_html(md_text, self.theme, self._tokens()))

    def _save_steam_artwork_zip(self) -> None:
        dest, _ = QFileDialog.getSaveFileName(
            self, "Save Steam artwork", "steam-artwork.zip", "Zip archive (*.zip)",
        )
        if not dest:
            return
        steam_dir = paths.resource_path(os.path.join("assets", "steam"))
        try:
            with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
                for name in sorted(os.listdir(steam_dir)):
                    zf.write(os.path.join(steam_dir, name), arcname=name)
            QMessageBox.information(self, "Saved", f"Steam artwork saved to {dest}")
        except Exception as exc:
            QMessageBox.critical(self, "Failed", f"Couldn't save the zip: {exc}")
