"""Background-thread workers for the Home/Build tabs' long-running actions.

Each is a QThread that emits `line` for log text and `done` with an exit
code when finished. Signals emitted from a QThread's run() are delivered
to slots on the main thread automatically (Qt marshals cross-thread signal
delivery via a queued connection whenever emitter and receiver live in
different threads) -- unlike the old Tk build, there's no manual
queue.Queue + polling loop needed to get worker output back to the UI
safely.
"""
from __future__ import annotations

import os
import subprocess

from PySide6.QtCore import QThread, Signal

from src.core.generator import GeneratorError, generate, load_config as load_generator_config


class GenerateWorker(QThread):
    line = Signal(str)
    done = Signal(int)

    def run(self) -> None:
        try:
            cfg = load_generator_config()
            result = generate(cfg, log=lambda t: self.line.emit(t))
            self.line.emit(f"Done! Written to: {result.output_path}")
            self.done.emit(0)
        except GeneratorError as e:
            self.line.emit(f"[ERROR] {e}")
            self.done.emit(1)
        except Exception as e:
            self.line.emit(f"[ERROR] {e}")
            self.done.emit(1)


class RenameWorker(QThread):
    line = Signal(str)
    done = Signal(int)

    def run(self) -> None:
        try:
            from src.core.renamer import rename_images
            cfg = load_generator_config()
            folder = cfg["images_folder"]
            if not os.path.isdir(folder):
                self.line.emit(f"[ERROR] Images folder not found: {folder}")
                self.done.emit(1)
                return
            ok, failed = rename_images(folder, log=lambda t: self.line.emit(t))
            self.line.emit(f"Renamed {ok} file(s)" + (f", {failed} skipped." if failed else "."))
            self.done.emit(0)
        except GeneratorError as e:
            self.line.emit(f"[ERROR] {e}")
            self.done.emit(1)
        except Exception as e:
            self.line.emit(f"[ERROR] {e}")
            self.done.emit(1)


class SubprocessWorker(QThread):
    line = Signal(str)
    done = Signal(int)

    def __init__(self, cmd: list, cwd: str) -> None:
        super().__init__()
        self._cmd = cmd
        self._cwd = cwd

    def run(self) -> None:
        try:
            proc = subprocess.Popen(
                self._cmd, cwd=self._cwd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
            for line in proc.stdout:
                self.line.emit(line)
            proc.wait()
            self.done.emit(proc.returncode)
        except Exception as exc:
            self.line.emit(f"[ERROR] {exc}\n")
            self.done.emit(1)


class UpdateCheckWorker(QThread):
    result_ready = Signal(object)

    def __init__(self, current_version: str) -> None:
        super().__init__()
        self._current_version = current_version

    def run(self) -> None:
        from src.common import update_checker
        self.result_ready.emit(update_checker.check_for_update(self._current_version))
