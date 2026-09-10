"""
TS4RLS — single entry point and desktop GUI. Requires tkinter (ships with
Python) and sv_ttk (a small pure-Tcl ttk theme, auto-installed below if
missing).

Run standalone:
    python gui.py              -> GUI
    python gui.py --generate   -> headless, one-shot

Use src/build/executable_builder.py to build the executable.
"""

import os
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
import zipfile
from tkinter import filedialog, messagebox, scrolledtext, ttk

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.common import app_state, paths


def _ensure_dependencies():
    if paths.is_frozen():
        return  # a frozen build must already bundle sv_ttk
    import importlib.util
    if importlib.util.find_spec("sv_ttk") is None:
        print("sv_ttk not found — installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "sv_ttk", "--quiet"],
            stdout=subprocess.DEVNULL,
        )
        print("sv_ttk installed.")


_ensure_dependencies()

# sv_ttk ("Sun Valley") is a third-party ttk theme that reskins every stock
# ttk widget with a real light/dark palette (flat buttons, modern look) --
# something the built-in ttk themes (vista/clam/etc.) can't do on their
# own. Matches the pattern used by TIGHC's own gui.py.
import sv_ttk
from src.cli import config_editor
from src.cli.config_editor import SETTINGS, format_value
from src.core.generator import (
    GeneratorError, find_legacy_output, generate,
    load_config as load_generator_config,
)

REPO_URL = "https://github.com/TS4RLS/Engine"
WEBSITE_URL = "https://ts4rls.stuxie.dev"
AUTHOR_NAME = "StuxieDev"
AUTHOR_URL = "https://stuxie.dev"
STUXIEDEV_PROJECTS_URL = "https://projects.stuxie.dev"

CHANGELOG_PATH = paths.resource_path("CHANGELOG.md")

FOLDER_KEYS = {"images_folder", "mods_folder"}

# Same green accent tokens as style.css's :root/[data-theme] blocks on the
# website (--accent for each theme) -- a brighter green for the dark
# theme, the deeper icon-face green for the light theme -- so the GUI's
# links/highlights match the site instead of using an unrelated color.
ACCENT_DARK = "#4fc264"
ACCENT_LIGHT = "#2e7d32"
DEFAULT_THEME = "dark"
# A mid-gray that stays legible against both sv_ttk's light background
# (near-white) and its dark background (near-black) -- avoids needing a
# separate hint color per theme, same reasoning as TIGHC's HINT_COLOR.
HINT_COLOR = "#8f8f8f"
# --error-fg tokens from style.css, for the legacy-folder warning text.
ERROR_DARK = "#d98c8c"
ERROR_LIGHT = "#b3312f"

DISCLAIMER_TITLE = "Before you continue"
DISCLAIMER_TEXT = (
    "TS4RLS is an unofficial, independent tool. It is not affiliated with, "
    "endorsed by, or sponsored by Electronic Arts or Maxis.\n\n"
    "It works by writing a single .package file into your Sims 4 Mods "
    "folder. Only one loading screen package can be active at a time, so "
    "remove any other loading screen mod first.\n\n"
    "This software is provided \"as is\", without warranty of any kind — "
    "use it at your own risk."
)


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


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Stay hidden until the first-launch disclaimer (if any) is
        # resolved -- see the end of __init__ -- so the main window never
        # flashes on screen before it.
        self.withdraw()

        self.title(f"TS4RLS - The Sims 4 Random Loading Screen v{_get_version()}")
        self.geometry("780x640")
        self.minsize(660, 540)
        self._set_window_icon()

        self.python_exe = find_python()
        self.field_vars = {}
        self.home_display_vars = {}
        self.worker = None
        self.log_queue = queue.Queue()
        self.logs = {}
        self.status_vars = {}
        self.buttons = {}
        self._link_labels = []  # accent-colored labels re-colored on theme toggle
        self._error_labels = []  # warning-colored labels re-colored on theme toggle
        self._scrollable_canvases = []  # plain Tk canvases (see _build_scrollable_body) re-themed alongside changelog_text

        self.theme = DEFAULT_THEME
        sv_ttk.set_theme(self.theme, self)
        self._apply_custom_style_layer()

        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=8, pady=(8, 0))
        self.theme_toggle_btn = ttk.Button(top_bar, text=self._theme_toggle_label(), command=self._on_toggle_theme)
        self.theme_toggle_btn.pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.home_tab = ttk.Frame(self.notebook)
        self.build_tab = ttk.Frame(self.notebook)
        self.about_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.build_tab, text="Build")
        self.notebook.add(self.about_tab, text="About")
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._build_home_tab()
        self._build_build_tab()
        self._build_about_tab()

        self._restyle_text_widgets()
        self.after(100, self._poll_log_queue)

        if not app_state.is_disclaimer_confirmed():
            self._show_disclaimer()
        self.deiconify()

    def _set_window_icon(self):
        icon_path = paths.resource_path(os.path.join("assets", "icon.png"))
        try:
            photo = tk.PhotoImage(file=icon_path)
            self.iconphoto(True, photo)
            self._icon_photo = photo  # keep a reference alive
        except Exception:
            pass

    def _on_tab_changed(self, _event):
        if self.notebook.select() == str(self.home_tab):
            self._refresh_home_display()

    # ── Theming (matches the website's dark/light green palette) ───────

    @staticmethod
    def _apply_custom_style_layer():
        """Style tweaks layered on top of whichever sv_ttk palette is active."""
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=(16, 8))
        style.configure("TLabelframe.Label", font=("", 9, "bold"))
        style.configure("Hint.TLabel", foreground=HINT_COLOR)

    def _accent_color(self) -> str:
        return ACCENT_DARK if self.theme == "dark" else ACCENT_LIGHT

    def _error_color(self) -> str:
        return ERROR_DARK if self.theme == "dark" else ERROR_LIGHT

    def _panel_bg(self) -> str:
        """sv_ttk's own background color for the active theme (from its
        theme/{dark,light}.tcl -- not queryable via ttk.Style().lookup(),
        which returns "" for sv_ttk's image-based flat theme)."""
        return "#1c1c1c" if self.theme == "dark" else "#fafafa"

    def _theme_toggle_label(self) -> str:
        return "Switch to light mode" if self.theme == "dark" else "Switch to dark mode"

    def _on_toggle_theme(self):
        sv_ttk.toggle_theme(self)
        self.theme = sv_ttk.get_theme(self)
        self._apply_custom_style_layer()
        self.theme_toggle_btn.config(text=self._theme_toggle_label())
        self._restyle_text_widgets()

    def _register_link(self, label: tk.Widget):
        self._link_labels.append(label)
        label.configure(foreground=self._accent_color())

    def _register_error_label(self, label: tk.Widget):
        self._error_labels.append(label)
        label.configure(foreground=self._error_color())

    _LOG_TERMINAL_COLORS = {"bg": "#0d0d0d", "fg": "#d4d4d4", "insertbackground": "#d4d4d4"}

    def _text_widget_colors(self) -> dict:
        """bg/fg/cursor-color for the changelog viewer, matched to sv_ttk's current palette."""
        if self.theme == "dark":
            return {"bg": "#1e1e1e", "fg": "#e6e6e6", "insertbackground": "#e6e6e6"}
        return {"bg": "#ffffff", "fg": "#16241a", "insertbackground": "#16241a"}

    def _restyle_text_widgets(self):
        """Re-theme everything sv_ttk itself doesn't touch: the accent color
        on link labels, the warning color on error labels, the always-dark
        terminal-style action logs, and the changelog viewer (which follows
        the app theme). Called once after all tabs are built, and again on
        every theme toggle."""
        accent = self._accent_color()
        for label in self._link_labels:
            label.configure(foreground=accent)

        error = self._error_color()
        for label in self._error_labels:
            label.configure(foreground=error)

        for log in self.logs.values():
            log.configure(**self._LOG_TERMINAL_COLORS)

        panel_bg = self._panel_bg()
        for canvas in self._scrollable_canvases:
            canvas.configure(bg=panel_bg)

        changelog_text = getattr(self, "changelog_text", None)
        if changelog_text is not None:
            colors = self._text_widget_colors()
            changelog_text.configure(**colors)
            if self.theme == "dark":
                changelog_text.tag_configure("h2", foreground="#7fdb90")
                changelog_text.tag_configure("h3", foreground=HINT_COLOR)
                changelog_text.tag_configure("bullet_dash", foreground="#7fdb90")
                changelog_text.tag_configure("prose", foreground=HINT_COLOR)
                changelog_text.tag_configure("code_span", foreground="#ffbe6a")
            else:
                changelog_text.tag_configure("h2", foreground=ACCENT_LIGHT)
                changelog_text.tag_configure("h3", foreground=HINT_COLOR)
                changelog_text.tag_configure("bullet_dash", foreground=ACCENT_LIGHT)
                changelog_text.tag_configure("prose", foreground=HINT_COLOR)
                changelog_text.tag_configure("code_span", foreground="#a35e00")

    # ── First-launch disclaimer ─────────────────────────────────────────

    def _show_disclaimer(self):
        """Modal first-launch gate, laid out like TWRAR's own disclaimer
        dialog: centered logo, title, body, and buttons, shown before the
        main window (which stays withdrawn until this resolves)."""
        dialog = tk.Toplevel(self)
        dialog.configure(bg=self._panel_bg())
        dialog.title(DISCLAIMER_TITLE)
        dialog.transient(self)
        dialog.resizable(False, False)
        dialog.protocol("WM_DELETE_WINDOW", lambda: self._exit_from_disclaimer(dialog))

        frame = ttk.Frame(dialog, padding=(24, 20))
        frame.pack(fill="both", expand=True)

        logo_path = paths.resource_path(os.path.join("assets", "logo.png"))
        try:
            logo = tk.PhotoImage(file=logo_path)
            factor = max(1, logo.height() // 96)
            logo = logo.subsample(factor, factor)
            logo_label = ttk.Label(frame, image=logo)
            logo_label.image = logo  # keep a reference alive
            logo_label.pack(pady=(0, 12))
        except Exception:
            pass

        ttk.Label(frame, text=DISCLAIMER_TITLE, font=("", 14, "bold"), justify="center").pack(pady=(0, 12))
        ttk.Label(frame, text=DISCLAIMER_TEXT, wraplength=420, justify="center").pack(pady=(0, 12))

        buttons = ttk.Frame(frame)
        buttons.pack()
        continue_btn = ttk.Button(
            buttons, text="I understand — Continue",
            command=lambda: self._confirm_disclaimer(dialog),
        )
        continue_btn.pack(side="right")
        ttk.Button(
            buttons, text="Exit",
            command=lambda: self._exit_from_disclaimer(dialog),
        ).pack(side="right", padx=(0, 8))
        continue_btn.focus_set()

        self.update_idletasks()
        dialog.update_idletasks()
        x = (self.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (self.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")

        dialog.grab_set()
        self.wait_window(dialog)

    def _confirm_disclaimer(self, dialog):
        app_state.confirm_disclaimer()
        dialog.destroy()

    def _exit_from_disclaimer(self, dialog):
        dialog.destroy()
        self.destroy()
        sys.exit(0)

    # ── Home tab (daily use: display current settings, run things) ─────

    def _build_home_tab(self):
        frame = ttk.Frame(self.home_tab)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        settings_box = ttk.LabelFrame(frame, text="Current settings")
        settings_box.pack(fill="x")

        for row, (key, kind, desc, required, default) in enumerate(SETTINGS):
            ttk.Label(settings_box, text=key, font=("", 9, "bold")).grid(
                row=row, column=0, sticky="w", padx=(8, 12), pady=2
            )
            var = tk.StringVar(value="")
            ttk.Label(settings_box, textvariable=var, style="Hint.TLabel").grid(
                row=row, column=1, sticky="w", pady=2
            )
            self.home_display_vars[key] = var
        settings_box.columnconfigure(1, weight=1)

        ttk.Button(
            frame, text="Edit settings in the Build tab...",
            command=lambda: self.notebook.select(self.build_tab),
        ).pack(anchor="w", pady=(6, 12))

        self.legacy_warning = ttk.Frame(frame)
        legacy_warning_label = ttk.Label(
            self.legacy_warning,
            text="Found an old loading screen mod from a previous version — delete it before generating a new one.",
            wraplength=520, justify="left",
        )
        legacy_warning_label.pack(side="left", padx=(0, 8), pady=8)
        self._register_error_label(legacy_warning_label)
        ttk.Button(
            self.legacy_warning, text="Delete legacy folder",
            command=self._delete_legacy_folder,
        ).pack(side="left")
        # Not packed until _refresh_home_display() finds something to show.

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(0, 8))
        self.buttons["home"] = []

        col = 0

        def add_button(label, command):
            nonlocal col
            btn = ttk.Button(buttons, text=label, command=command)
            btn.grid(row=0, column=col, padx=(0 if col == 0 else 4), sticky="ew")
            buttons.columnconfigure(col, weight=1)
            self.buttons["home"].append(btn)
            col += 1

        add_button("Generate loading screen", self._run_generate)
        self.generate_button = self.buttons["home"][-1]
        add_button("Rename images only", self._run_rename)
        add_button("Build executable", self._run_build_from_home)

        latest_build_box = ttk.LabelFrame(frame, text="Latest build")
        latest_build_box.pack(fill="x", pady=(0, 8))
        self.latest_build_var = tk.StringVar(value="No builds yet.")
        ttk.Label(latest_build_box, textvariable=self.latest_build_var, style="Hint.TLabel").pack(
            side="left", padx=8, pady=6
        )
        self.latest_build_copy_button = ttk.Button(
            latest_build_box, text="Copy path", command=self._copy_latest_build_path,
        )
        self.latest_build_copy_button.pack(side="right", padx=8, pady=6)

        self.status_vars["home"] = tk.StringVar(value="Ready.")
        ttk.Label(frame, textvariable=self.status_vars["home"]).pack(anchor="w")

        self.logs["home"] = scrolledtext.ScrolledText(frame, state="disabled", height=14)
        self.logs["home"].pack(fill="both", expand=True, pady=(4, 0))

        self._refresh_home_display()

    def _refresh_home_display(self):
        cfg = config_editor.load_config()
        for key, kind, desc, required, default in SETTINGS:
            current = cfg.get(key, None if required else default)
            if current is None and key == "mods_folder":
                current = paths.guess_mods_folder() or None
            self.home_display_vars[key].set(format_value(current))

        mods_folder = cfg.get("mods_folder", "")
        legacy_found = bool(mods_folder and find_legacy_output(mods_folder))
        if legacy_found:
            self.legacy_warning.pack(fill="x", before=self.generate_button.master, pady=(0, 8))
            self.generate_button.configure(state="disabled")
        else:
            self.legacy_warning.pack_forget()
            self.generate_button.configure(state="normal")

        self._refresh_latest_build()

    def _refresh_latest_build(self):
        history = app_state.load_build_history()
        if history:
            latest = history[0]
            self.latest_build_var.set(f"{latest['path']}\nBuilt {latest['timestamp']}")
            self.latest_build_copy_button.configure(state="normal")
        else:
            self.latest_build_var.set("No builds yet.")
            self.latest_build_copy_button.configure(state="disabled")

    def _copy_latest_build_path(self):
        history = app_state.load_build_history()
        if history:
            self._copy_to_clipboard(history[0]["path"])

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)

    def _delete_legacy_folder(self):
        mods_folder = load_generator_config().get("mods_folder", "")
        legacy_folder = find_legacy_output(mods_folder) if mods_folder else ""
        if not legacy_folder:
            self._refresh_home_display()
            return
        if not messagebox.askyesno(
            "Delete legacy folder",
            f"Permanently delete this folder?\n\n{legacy_folder}",
        ):
            return
        try:
            shutil.rmtree(legacy_folder)
            self._append_log("home", f"\nDeleted legacy folder: {legacy_folder}\n")
        except Exception as exc:
            messagebox.showerror("Failed", f"Couldn't delete the folder: {exc}")
        self._refresh_home_display()

    def _run_build_from_home(self):
        self.notebook.select(self.build_tab)
        self._run_build_executables()

    # ── Build tab (configure settings, build the executable) ───────────

    def _build_build_tab(self):
        container = ttk.Frame(self.build_tab)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        settings_box = ttk.LabelFrame(container, text="Settings")
        settings_box.pack(fill="x")

        cfg = config_editor.load_config()
        for row, (key, kind, desc, required, default) in enumerate(SETTINGS):
            current = cfg.get(key, None if required else default)
            if current is None and key == "mods_folder":
                current = paths.guess_mods_folder() or None

            label_text = key + (" *" if required else "")
            ttk.Label(settings_box, text=label_text, font=("", 9, "bold")).grid(
                row=row, column=0, sticky="nw", pady=4, padx=(8, 8)
            )
            ttk.Label(settings_box, text=desc, wraplength=260, style="Hint.TLabel").grid(
                row=row, column=3, sticky="nw", pady=4, padx=(8, 8)
            )

            if kind == "bool":
                var = tk.BooleanVar(value=bool(current))
                widget = ttk.Checkbutton(settings_box, variable=var)
                widget.grid(row=row, column=1, sticky="w", pady=4)
            else:
                var = tk.StringVar(value=format_value(current) if current is not None else "")
                widget = ttk.Entry(settings_box, textvariable=var, width=38)
                widget.grid(row=row, column=1, sticky="w", pady=4)

                if key in FOLDER_KEYS:
                    ttk.Button(
                        settings_box, text="Browse...",
                        command=lambda v=var: self._browse_folder(v),
                    ).grid(row=row, column=2, padx=4)

            self.field_vars[key] = (var, kind, required)

        settings_box.columnconfigure(3, weight=1)

        footer_row = len(SETTINGS)
        ttk.Label(settings_box, text="* required", style="Hint.TLabel").grid(
            row=footer_row, column=0, sticky="w", pady=(10, 8), padx=(8, 0)
        )
        ttk.Button(settings_box, text="Save settings", command=self._save_settings).grid(
            row=footer_row, column=1, sticky="w", pady=(10, 8)
        )

        build_box = ttk.LabelFrame(container, text="Build")
        build_box.pack(fill="x", pady=(12, 8))

        buttons = ttk.Frame(build_box)
        buttons.pack(fill="x", padx=8, pady=8)
        self.buttons["build"] = []

        col = 0

        def add_button(label, command):
            nonlocal col
            btn = ttk.Button(buttons, text=label, command=command)
            btn.grid(row=0, column=col, padx=(0 if col == 0 else 4), sticky="ew")
            buttons.columnconfigure(col, weight=1)
            self.buttons["build"].append(btn)
            col += 1

        add_button("Build executable", self._run_build_executables)
        add_button("Run test suite", self._run_tests)

        history_box = ttk.LabelFrame(container, text="Recent builds")
        history_box.pack(fill="x", pady=(0, 8))
        self.history_list_frame = ttk.Frame(history_box)
        self.history_list_frame.pack(fill="x", padx=8, pady=8)
        self._refresh_build_history()

        self.status_vars["build"] = tk.StringVar(value="Ready.")
        ttk.Label(container, textvariable=self.status_vars["build"]).pack(anchor="w")

        self.logs["build"] = scrolledtext.ScrolledText(container, state="disabled", height=10)
        self.logs["build"].pack(fill="both", expand=True, pady=(4, 0))

        if paths.is_frozen():
            # A shipped exe has no bundled PyInstaller/pytest to build or
            # test with -- only settings editing makes sense here.
            for btn in self.buttons["build"]:
                btn.configure(state="disabled")

    def _refresh_build_history(self):
        for child in self.history_list_frame.winfo_children():
            child.destroy()

        history = app_state.load_build_history()
        if not history:
            ttk.Label(self.history_list_frame, text="No builds yet.", style="Hint.TLabel").pack(anchor="w")
            return

        for entry in history:
            row = ttk.Frame(self.history_list_frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=f"{entry['path']}  ({entry['timestamp']})").pack(side="left")
            ttk.Button(
                row, text="Copy path",
                command=lambda p=entry["path"]: self._copy_to_clipboard(p),
            ).pack(side="right")

    def _browse_folder(self, var):
        path = filedialog.askdirectory(initialdir=var.get() or _ROOT)
        if path:
            var.set(path)

    def _save_settings(self):
        cfg = {}
        for key, (var, kind, required) in self.field_vars.items():
            if kind == "bool":
                cfg[key] = bool(var.get())
                continue
            raw = var.get().strip()
            if not raw:
                if required:
                    messagebox.showerror("Missing value", f"'{key}' is required.")
                    return
                continue
            if kind == "int":
                try:
                    cfg[key] = int(raw)
                except ValueError:
                    messagebox.showerror("Invalid value", f"'{key}' must be a whole number.")
                    return
            else:
                cfg[key] = raw

        saved_to = config_editor.save_config(cfg)
        self._refresh_home_display()
        messagebox.showinfo("Saved", f"Saved to {saved_to}")

    # ── Shared worker/log plumbing ──────────────────────────────────────

    def _append_log(self, target: str, text: str):
        log = self.logs[target]
        log.configure(state="normal")
        log.insert("end", text)
        log.see("end")
        log.configure(state="disabled")

    def _set_buttons_enabled(self, target: str, enabled: bool):
        state = "normal" if enabled else "disabled"
        for btn in self.buttons[target]:
            btn.configure(state=state)

    def _start_worker(self, target: str, worker_fn, *args):
        if self.worker and self.worker.is_alive():
            messagebox.showwarning("Busy", "Another action is already running.")
            return
        self.status_vars[target].set("Running...")
        self._set_buttons_enabled(target, False)
        self.worker = threading.Thread(target=worker_fn, args=args, daemon=True)
        self.worker.start()

    def _queue_log(self, target: str, text: str):
        self.log_queue.put((target, "line", text.rstrip("\n") + "\n"))

    # In-process actions (generate/rename): call the core logic directly.

    def _run_generate(self):
        self._append_log("home", "\n$ Generate loading screen\n")
        self._start_worker("home", self._worker_generate)

    def _worker_generate(self):
        try:
            cfg = load_generator_config()
            result = generate(cfg, log=lambda t: self._queue_log("home", t))
            self._queue_log("home", f"Done! Written to: {result.output_path}")
            self.log_queue.put(("home", "done", 0))
        except GeneratorError as e:
            self._queue_log("home", f"[ERROR] {e}")
            self.log_queue.put(("home", "done", 1))
        except Exception as e:
            self._queue_log("home", f"[ERROR] {e}")
            self.log_queue.put(("home", "done", 1))

    def _run_rename(self):
        self._append_log("home", "\n$ Rename images\n")
        self._start_worker("home", self._worker_rename)

    def _worker_rename(self):
        try:
            from src.core.renamer import rename_images
            cfg = load_generator_config()
            folder = cfg["images_folder"]
            if not os.path.isdir(folder):
                self._queue_log("home", f"[ERROR] Images folder not found: {folder}")
                self.log_queue.put(("home", "done", 1))
                return
            ok, failed = rename_images(folder, log=lambda t: self._queue_log("home", t))
            self._queue_log("home", f"Renamed {ok} file(s)" + (f", {failed} skipped." if failed else "."))
            self.log_queue.put(("home", "done", 0))
        except GeneratorError as e:
            self._queue_log("home", f"[ERROR] {e}")
            self.log_queue.put(("home", "done", 1))
        except Exception as e:
            self._queue_log("home", f"[ERROR] {e}")
            self.log_queue.put(("home", "done", 1))

    # Dev-only actions (subprocess: need PyInstaller/pytest from source).

    def _run_build_executables(self):
        script = os.path.join(_ROOT, "src", "build", "executable_builder.py")
        self._run_subprocess_action("build", [script])

    def _run_tests(self):
        self._run_subprocess_action("build", ["-m", "pytest", "-v"])

    def _run_subprocess_action(self, target: str, args: list):
        if not self.python_exe:
            messagebox.showerror("Python not found", "Install Python and restart this app.")
            return
        cmd = [self.python_exe] + args
        self._append_log(target, f"\n$ {' '.join(cmd)}\n")
        self._start_worker(target, self._worker_subprocess, target, cmd)

    def _worker_subprocess(self, target: str, cmd: list):
        try:
            proc = subprocess.Popen(
                cmd, cwd=_ROOT,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
            for line in proc.stdout:
                self.log_queue.put((target, "line", line))
            proc.wait()
            self.log_queue.put((target, "done", proc.returncode))
        except Exception as exc:
            self.log_queue.put((target, "line", f"[ERROR] {exc}\n"))
            self.log_queue.put((target, "done", 1))

    def _poll_log_queue(self):
        try:
            while True:
                target, kind, payload = self.log_queue.get_nowait()
                if kind == "line":
                    self._append_log(target, payload)
                elif kind == "done":
                    ok = payload == 0
                    self.status_vars[target].set("Done." if ok else f"Failed (exit code {payload}).")
                    self._set_buttons_enabled(target, True)
                    if target == "home":
                        self._refresh_home_display()
                    elif target == "build":
                        self._refresh_build_history()
                        self._refresh_home_display()
        except queue.Empty:
            pass
        self.after(100, self._poll_log_queue)

    # ── About tab ────────────────────────────────────────────────────

    def _build_scrollable_body(self, parent):
        canvas = tk.Canvas(parent, highlightthickness=0, bg=self._panel_bg())
        self._scrollable_canvases.append(canvas)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        return inner

    def _about_link_row(self, parent, label_text, url, image=None, **pack_opts):
        row = ttk.Frame(parent)
        row.pack(anchor="w", pady=pack_opts.pop("pady", (2, 0)), **pack_opts)
        if image is not None:
            ttk.Label(row, image=image).pack(side="left", padx=(0, 6))
        link = ttk.Label(row, text=label_text, cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: webbrowser.open(url))
        self._register_link(link)
        return row

    def _build_about_tab(self):
        outer = ttk.Frame(self.about_tab)
        outer.pack(fill="both", expand=True, padx=8, pady=8)

        header = ttk.Frame(outer)
        header.pack(fill="x", anchor="w", padx=8, pady=(4, 8))

        logo_path = paths.resource_path(os.path.join("assets", "icon.png"))
        try:
            logo = tk.PhotoImage(file=logo_path)
            logo = logo.subsample(max(1, logo.width() // 64), max(1, logo.height() // 64))
            logo_label = ttk.Label(header, image=logo)
            logo_label.image = logo  # keep a reference alive
            logo_label.pack(side="left", padx=(0, 10))
        except Exception:
            pass

        text_col = ttk.Frame(header)
        text_col.pack(side="left", anchor="w")
        ttk.Label(text_col, text="TS4RLS — The Sims 4 Random Loading Screen", font=("", 13, "bold")).pack(anchor="w")
        ttk.Label(text_col, text=f"v{_get_version()}").pack(anchor="w")

        body = self._build_scrollable_body(outer)

        ttk.Label(
            body,
            text=(
                "Automatically picks a random image from a folder and installs it\n"
                "as your Sims 4 loading screen mod — run it, then launch the game\n"
                "yourself and get a fresh screen every time."
            ),
            justify="left",
        ).pack(anchor="w", pady=(10, 10))

        self._about_link_row(body, WEBSITE_URL, WEBSITE_URL)
        self._about_link_row(body, REPO_URL, REPO_URL)
        self._about_link_row(body, "Report a bug / get support", f"{REPO_URL}/issues", pady=(2, 10))

        author_row = ttk.Frame(body)
        author_row.pack(anchor="w", pady=(2, 0))
        ttk.Label(author_row, text="Written & Maintained by ").pack(side="left")
        try:
            avatar_full = tk.PhotoImage(file=paths.resource_path(os.path.join("assets", "author.png")))
            factor = max(1, avatar_full.width() // 20)
            avatar_image = avatar_full.subsample(factor, factor)
            self._author_avatar_image = avatar_image  # keep a reference alive
            ttk.Label(author_row, image=avatar_image).pack(side="left", padx=(0, 4))
        except Exception:
            pass
        author_link = ttk.Label(author_row, text=AUTHOR_NAME, cursor="hand2")
        author_link.pack(side="left")
        author_link.bind("<Button-1>", lambda e: webbrowser.open(AUTHOR_URL))
        self._register_link(author_link)

        self._about_link_row(body, "A StuxieDev Project", STUXIEDEV_PROJECTS_URL, pady=(2, 10))

        ttk.Button(
            body, text="Save Steam artwork (.zip)...",
            command=self._save_steam_artwork_zip,
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(
            body, text=f"Config file: {paths.resolve_config_path()}",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        changelog_header = ttk.Frame(body)
        changelog_header.pack(fill="x", pady=(4, 4))
        ttk.Label(changelog_header, text="Changelog", font=("", 11, "bold")).pack(side="left")
        ttk.Button(changelog_header, text="Reload", command=self._load_changelog).pack(side="right")

        self.changelog_text = scrolledtext.ScrolledText(
            body, wrap="word", font=("Segoe UI", 9), padx=8, pady=6, height=16, state="disabled",
        )
        self.changelog_text.pack(fill="both", expand=True, pady=(0, 8))

        ct = self.changelog_text
        ct.tag_configure("h2", font=("Segoe UI", 12, "bold"), spacing1=14, spacing3=4)
        ct.tag_configure("h3", font=("Segoe UI", 9, "bold"), spacing1=8, spacing3=2)
        ct.tag_configure("bullet", lmargin1=10, lmargin2=22, spacing1=1)
        ct.tag_configure("bullet_dash")
        ct.tag_configure("prose", font=("Segoe UI", 9), spacing1=2, spacing3=4)
        ct.tag_configure("bold_span", font=("Segoe UI", 9, "bold"))
        ct.tag_configure("code_span", font=("Consolas", 9))
        self._load_changelog()

    def _load_changelog(self):
        """(Re)load CHANGELOG.md into the changelog viewer, rendering markdown
        headings, bullets, bold, and code spans with text tags instead of
        showing raw markdown."""
        import re

        ct = self.changelog_text
        ct.config(state="normal")
        ct.delete("1.0", "end")

        try:
            with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError as e:
            ct.insert("end", f"(Could not read CHANGELOG.md: {e})")
            ct.config(state="disabled")
            return

        def insert_inline(text):
            parts = re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    ct.insert("end", part[2:-2], "bold_span")
                elif part.startswith("`") and part.endswith("`"):
                    ct.insert("end", part[1:-1], "code_span")
                else:
                    ct.insert("end", part)

        in_list = False
        for line in lines:
            if line.startswith("## "):
                if in_list:
                    ct.insert("end", "\n")
                    in_list = False
                ct.insert("end", line[3:].strip() + "\n", "h2")
            elif line.startswith("### "):
                if in_list:
                    ct.insert("end", "\n")
                    in_list = False
                ct.insert("end", line[4:].strip() + "\n", "h3")
            elif line.startswith("- ") or line.startswith("  - "):
                in_list = True
                ct.insert("end", "  – ", "bullet_dash")
                insert_inline(line.lstrip("- ").lstrip())
                ct.insert("end", "\n", "bullet")
            elif line.startswith("# "):
                pass  # skip the top-level title -- shown as a label above
            elif line.strip():
                if in_list:
                    ct.insert("end", "\n")
                    in_list = False
                ct.insert("end", line.strip() + "\n", "prose")
            else:
                if in_list:
                    ct.insert("end", "\n")
                    in_list = False
                ct.insert("end", "\n")

        ct.config(state="disabled")

    def _save_steam_artwork_zip(self):
        dest = filedialog.asksaveasfilename(
            defaultextension=".zip",
            initialfile="steam-artwork.zip",
            filetypes=[("Zip archive", "*.zip")],
        )
        if not dest:
            return
        steam_dir = paths.resource_path(os.path.join("assets", "steam"))
        try:
            with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
                for name in sorted(os.listdir(steam_dir)):
                    zf.write(os.path.join(steam_dir, name), arcname=name)
            messagebox.showinfo("Saved", f"Steam artwork saved to {dest}")
        except Exception as exc:
            messagebox.showerror("Failed", f"Couldn't save the zip: {exc}")


def main():
    argv = sys.argv[1:]
    headless = "--generate" in argv

    if headless:
        from src.cli import cli_colors

        try:
            cfg = load_generator_config()
            result = generate(cfg)
        except GeneratorError as e:
            print("\n" + cli_colors.error(str(e)))
            sys.exit(1)
        print(f"Done! Written to: {result.output_path}")
        return

    App().mainloop()


if __name__ == "__main__":
    main()
