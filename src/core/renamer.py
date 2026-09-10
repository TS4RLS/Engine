"""
Renames every image in a folder to a random 32-character alphanumeric
filename and converts it to JPEG format.

Callable API: rename_images(folder). Called automatically by
core/generator.py's generate() when rename_files is true in config.json,
or standalone via the CLI menu / this script's __main__.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import random
import string
import subprocess
from pathlib import Path

from src.common import paths
from src.cli import cli_colors


def _ensure_dependencies():
    if paths.is_frozen():
        return
    import importlib.util
    if importlib.util.find_spec("PIL") is None:
        print(" Pillow not found — installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "Pillow", "--quiet"],
            stdout=subprocess.DEVNULL,
        )
        print(" Pillow installed.")
        print()


_ensure_dependencies()

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"}


def _import_pil():
    try:
        from PIL import Image
        return Image
    except ImportError:
        from src.core.generator import GeneratorError
        raise GeneratorError("Pillow is not installed.\n  Run:  pip install Pillow")


def _random_name() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=32))


def _unique_jpg_path(folder: str) -> str:
    while True:
        path = os.path.join(folder, _random_name() + ".jpg")
        if not os.path.exists(path):
            return path


def rename_images(images_folder: str, log=print) -> tuple:
    """Rename all images in images_folder to random 32-char names and
    convert them to JPEG. Returns (ok_count, failed_count)."""
    Image = _import_pil()

    # Collect all paths upfront so in-progress renames don't affect the walk.
    sources = []
    for root, _, files in os.walk(images_folder):
        for name in files:
            if Path(name).suffix.lower() in SUPPORTED_EXTENSIONS:
                sources.append(os.path.join(root, name))

    if not sources:
        log(f"  No images found in: {images_folder}")
        return 0, 0

    log(f"  Renaming {len(sources)} image(s)...")
    ok = 0
    failed = 0
    for src in sources:
        dst = _unique_jpg_path(os.path.dirname(src))
        try:
            with Image.open(src) as img:
                img.convert("RGB").save(dst, "JPEG", quality=95)
            os.remove(src)
            ok += 1
        except Exception as exc:
            log("  " + cli_colors.warning(f"Could not process {os.path.basename(src)}: {exc}"))
            failed += 1

    return ok, failed


def _get_version() -> str:
    try:
        with open(os.path.join(_ROOT, "VERSION.md"), "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "?"


if __name__ == "__main__":
    from src.core.generator import GeneratorError, load_config

    print(cli_colors.banner(
        "TS4RLS - The Sims 4 Random Loading Screen - Images Renamer",
        f"v{_get_version()}\nBuilt & Maintained by StuxieDev",
    ))

    try:
        cfg = load_config()
    except GeneratorError as e:
        print(cli_colors.error(str(e)))
        sys.exit(1)

    folder = cfg["images_folder"]
    if not os.path.isdir(folder):
        print(cli_colors.error(f"Images folder not found: {folder}"))
        sys.exit(1)

    print(f"Images folder: {folder}")
    ok, failed = rename_images(folder)
    print(f"  Renamed {ok} file(s)" + (f", {failed} skipped." if failed else "."))
    print("Done.")
