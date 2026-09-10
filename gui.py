"""
TS4RLS — single entry point and desktop GUI. This is what gets built into
the distributed executable(s); requires only the Python standard library
(tkinter ships with Python).

Run standalone:
    python gui.py                                   -> GUI
    python gui.py --generate [--force-launch]        -> headless, one-shot

When the running executable's own filename matches the CurseForge disguise
name (TS4_x64[.exe]), it always behaves as --generate --force-launch with
no arguments needed, so the same build works as both the normal app and
the CurseForge pre-launch script. Use src/build/executable_builder.py to
build the executable(s).
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

from src.common import paths
from src.cli import config_editor
from src.cli.config_editor import SETTINGS, format_value
from src.core.generator import GeneratorError, generate, load_config as load_generator_config

REPO_URL = "https://github.com/TS4RLS/Engine"
CURSEFORGE_NAME = "ts4_x64"

FOLDER_KEYS = {"images_folder", "mods_folder"}
FILE_KEYS = {"game_exe"}


def _get_version() -> str:
    try:
        with open(os.path.join(_ROOT, "VERSION.md"), "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "?"


def find_python() -> str:
    for candidate in ("python3", "python"):
        path = shutil.which(candidate)
        if path:
            return path
    return ""


def _is_curseforge_build() -> bool:
    name = os.path.splitext(os.path.basename(sys.executable if getattr(sys, "frozen", False) else __file__))[0]
    return name.lower() == CURSEFORGE_NAME


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(f"TS4RLS - The Sims 4 Random Loading Screen v{_get_version()}")
        self.geometry("760x600")
        self.minsize(640, 500)
        self._set_window_icon()

        self.python_exe = find_python()
        self.field_vars = {}
        self.worker = None
        self.log_queue = queue.Queue()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.settings_tab = ttk.Frame(notebook)
        self.actions_tab = ttk.Frame(notebook)
        self.about_tab = ttk.Frame(notebook)
        notebook.add(self.settings_tab, text="Settings")
        notebook.add(self.actions_tab, text="Actions")
        notebook.add(self.about_tab, text="About")

        self._build_settings_tab()
        self._build_actions_tab()
        self._build_about_tab()

        self.after(100, self._poll_log_queue)

    def _set_window_icon(self):
        icon_path = paths.resource_path(os.path.join("assets", "icon.png"))
        try:
            photo = tk.PhotoImage(file=icon_path)
            self.iconphoto(True, photo)
            self._icon_photo = photo  # keep a reference alive
        except Exception:
            pass

    # ── Settings tab ─────────────────────────────────────────────────

    def _build_settings_tab(self):
        cfg = config_editor.load_config()

        container = ttk.Frame(self.settings_tab)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        for row, (key, kind, desc, required, default) in enumerate(SETTINGS):
            current = cfg.get(key, None if required else default)

            label_text = key + (" *" if required else "")
            ttk.Label(container, text=label_text, font=("", 9, "bold")).grid(
                row=row, column=0, sticky="nw", pady=4, padx=(0, 8)
            )
            ttk.Label(container, text=desc, wraplength=260, foreground="#666").grid(
                row=row, column=3, sticky="nw", pady=4, padx=(8, 0)
            )

            if kind == "bool":
                var = tk.BooleanVar(value=bool(current))
                widget = ttk.Checkbutton(container, variable=var)
                widget.grid(row=row, column=1, sticky="w", pady=4)
            else:
                var = tk.StringVar(value=format_value(current) if current is not None else "")
                widget = ttk.Entry(container, textvariable=var, width=42)
                widget.grid(row=row, column=1, sticky="w", pady=4)

                if key in FOLDER_KEYS:
                    ttk.Button(
                        container, text="Browse...",
                        command=lambda v=var: self._browse_folder(v),
                    ).grid(row=row, column=2, padx=4)
                elif key in FILE_KEYS:
                    ttk.Button(
                        container, text="Browse...",
                        command=lambda v=var: self._browse_file(v),
                    ).grid(row=row, column=2, padx=4)

            self.field_vars[key] = (var, kind, required)

        container.columnconfigure(3, weight=1)

        ttk.Label(container, text="* required", foreground="#666").grid(
            row=len(SETTINGS), column=0, sticky="w", pady=(10, 0)
        )
        ttk.Button(container, text="Save settings", command=self._save_settings).grid(
            row=len(SETTINGS), column=1, sticky="w", pady=(10, 0)
        )

    def _browse_folder(self, var):
        path = filedialog.askdirectory(initialdir=var.get() or _ROOT)
        if path:
            var.set(path)

    def _browse_file(self, var):
        path = filedialog.askopenfilename(initialdir=os.path.dirname(var.get()) or _ROOT)
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
        messagebox.showinfo("Saved", f"Saved to {saved_to}")

    # ── Actions tab ──────────────────────────────────────────────────

    def _build_actions_tab(self):
        buttons = ttk.Frame(self.actions_tab)
        buttons.pack(fill="x", padx=12, pady=12)

        self.action_buttons = []

        col = 0

        def add_button(label, command):
            nonlocal col
            btn = ttk.Button(buttons, text=label, command=command)
            btn.grid(row=0, column=col, padx=4, sticky="ew")
            buttons.columnconfigure(col, weight=1)
            self.action_buttons.append(btn)
            col += 1

        add_button("Generate loading screen", self._run_generate)
        add_button("Rename images only", self._run_rename)

        # Dev-only actions: meaningless in a shipped single exe (no
        # PyInstaller/pytest bundled), so only show them running from source.
        if not paths.is_frozen():
            add_button("Build launcher executable(s)", self._run_build_executables)
            add_button("Run test suite", self._run_tests)

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(self.actions_tab, textvariable=self.status_var).pack(anchor="w", padx=12)

        self.log = scrolledtext.ScrolledText(self.actions_tab, state="disabled", height=20)
        self.log.pack(fill="both", expand=True, padx=12, pady=(4, 12))

    def _append_log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_buttons_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for btn in self.action_buttons:
            btn.configure(state=state)

    def _start_worker(self, target, *args):
        if self.worker and self.worker.is_alive():
            messagebox.showwarning("Busy", "Another action is already running.")
            return
        self.status_var.set("Running...")
        self._set_buttons_enabled(False)
        self.worker = threading.Thread(target=target, args=args, daemon=True)
        self.worker.start()

    def _queue_log(self, text: str):
        self.log_queue.put(("line", text.rstrip("\n") + "\n"))

    # In-process actions (generate/rename): call the core logic directly.

    def _run_generate(self):
        self._append_log("\n$ Generate loading screen\n")
        self._start_worker(self._worker_generate)

    def _worker_generate(self):
        try:
            cfg = load_generator_config()
            result = generate(cfg, log=self._queue_log)
            if result.warning:
                self._queue_log(f"[WARNING] {result.warning}")
            self._queue_log(f"Done! Written to: {result.output_path}")
            self.log_queue.put(("done", 0))
        except GeneratorError as e:
            self._queue_log(f"[ERROR] {e}")
            self.log_queue.put(("done", 1))
        except Exception as e:
            self._queue_log(f"[ERROR] {e}")
            self.log_queue.put(("done", 1))

    def _run_rename(self):
        self._append_log("\n$ Rename images\n")
        self._start_worker(self._worker_rename)

    def _worker_rename(self):
        try:
            from src.core.renamer import rename_images
            cfg = load_generator_config()
            folder = cfg["images_folder"]
            if not os.path.isdir(folder):
                self._queue_log(f"[ERROR] Images folder not found: {folder}")
                self.log_queue.put(("done", 1))
                return
            ok, failed = rename_images(folder, log=self._queue_log)
            self._queue_log(f"Renamed {ok} file(s)" + (f", {failed} skipped." if failed else "."))
            self.log_queue.put(("done", 0))
        except GeneratorError as e:
            self._queue_log(f"[ERROR] {e}")
            self.log_queue.put(("done", 1))
        except Exception as e:
            self._queue_log(f"[ERROR] {e}")
            self.log_queue.put(("done", 1))

    # Dev-only actions (subprocess: need PyInstaller/pytest from source).

    def _run_build_executables(self):
        script = os.path.join(_ROOT, "src", "build", "executable_builder.py")
        self._run_subprocess_action([script])

    def _run_tests(self):
        self._run_subprocess_action(["-m", "pytest", "-v"])

    def _run_subprocess_action(self, args: list):
        if not self.python_exe:
            messagebox.showerror("Python not found", "Install Python and restart this app.")
            return
        cmd = [self.python_exe] + args
        self._append_log(f"\n$ {' '.join(cmd)}\n")
        self._start_worker(self._worker_subprocess, cmd)

    def _worker_subprocess(self, cmd: list):
        try:
            proc = subprocess.Popen(
                cmd, cwd=_ROOT,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
            for line in proc.stdout:
                self.log_queue.put(("line", line))
            proc.wait()
            self.log_queue.put(("done", proc.returncode))
        except Exception as exc:
            self.log_queue.put(("line", f"[ERROR] {exc}\n"))
            self.log_queue.put(("done", 1))

    def _poll_log_queue(self):
        try:
            while True:
                kind, payload = self.log_queue.get_nowait()
                if kind == "line":
                    self._append_log(payload)
                elif kind == "done":
                    ok = payload == 0
                    self.status_var.set("Done." if ok else f"Failed (exit code {payload}).")
                    self._set_buttons_enabled(True)
        except queue.Empty:
            pass
        self.after(100, self._poll_log_queue)

    # ── About tab ────────────────────────────────────────────────────

    def _build_about_tab(self):
        frame = ttk.Frame(self.about_tab)
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        header = ttk.Frame(frame)
        header.pack(fill="x", anchor="w")

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
        ttk.Label(text_col, text=f"v{_get_version()}  ·  Built & Maintained by StuxieDev").pack(anchor="w")

        ttk.Label(
            frame,
            text=(
                "Automatically picks a random image from a folder and installs it\n"
                "as your Sims 4 loading screen mod — run it before launching the\n"
                "game and get a fresh screen every time."
            ),
            justify="left",
        ).pack(anchor="w", pady=(10, 10))

        link = ttk.Label(frame, text=REPO_URL, foreground="#0645ad", cursor="hand2")
        link.pack(anchor="w")
        link.bind("<Button-1>", lambda e: webbrowser.open(REPO_URL))

        issues = ttk.Label(frame, text="Report a bug / get support", foreground="#0645ad", cursor="hand2")
        issues.pack(anchor="w", pady=(4, 10))
        issues.bind("<Button-1>", lambda e: webbrowser.open(f"{REPO_URL}/issues"))

        ttk.Button(
            frame, text="Save Steam artwork (.zip)...",
            command=self._save_steam_artwork_zip,
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(
            frame,
            text="README.md and CHANGELOG.md in the project folder have full\n"
                 "setup and usage docs.",
            justify="left",
        ).pack(anchor="w")
        ttk.Label(
            frame, text=f"Config file: {paths.resolve_config_path()}",
            foreground="#666",
        ).pack(anchor="w", pady=(10, 0))

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
    force_launch = "--force-launch" in argv or _is_curseforge_build()
    headless = "--generate" in argv or _is_curseforge_build()

    if headless:
        from src.cli import cli_colors

        try:
            cfg = load_generator_config()
            result = generate(cfg, force_launch=force_launch)
        except GeneratorError as e:
            print("\n" + cli_colors.error(str(e)))
            sys.exit(1)
        if result.warning:
            print(cli_colors.warning(result.warning))
        return

    App().mainloop()


if __name__ == "__main__":
    main()
