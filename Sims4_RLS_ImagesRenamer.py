"""
Renames every image in the images folder to a random 32-character alphanumeric
filename and converts it to JPEG format.

Run standalone:
    python Sims4_RLS_ImagesRenamer.py

Or called automatically by Sims4_RLS_Creator.py when rename_files is true in config.json.
"""

import json
import os
import random
import string
import subprocess
import sys
from pathlib import Path


def _ensure_dependencies():
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
        print("\n[ERROR] Pillow is not installed.")
        print("  Run:  pip install Pillow")
        sys.exit(1)


def _random_name() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=32))


def _unique_jpg_path(folder: str) -> str:
    while True:
        path = os.path.join(folder, _random_name() + ".jpg")
        if not os.path.exists(path):
            return path


def rename_and_convert(images_folder: str) -> None:
    """Rename all images in images_folder to random 32-char names and convert to JPEG."""
    Image = _import_pil()

    # Collect all paths upfront so in-progress renames don't affect the walk.
    sources = []
    for root, _, files in os.walk(images_folder):
        for name in files:
            if Path(name).suffix.lower() in SUPPORTED_EXTENSIONS:
                sources.append(os.path.join(root, name))

    if not sources:
        print(f"  No images found in: {images_folder}")
        return

    print(f"  Renaming {len(sources)} image(s)...")
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
            print(f"  [WARNING] Could not process {os.path.basename(src)}: {exc}")
            failed += 1

    print(f"  Renamed {ok} file(s)" + (f", {failed} skipped." if failed else "."))


def _load_images_folder() -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    if not os.path.isfile(config_path):
        print("[ERROR] config.json not found.")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if "images_folder" not in cfg:
        print("[ERROR] config.json is missing 'images_folder'.")
        sys.exit(1)
    return cfg["images_folder"]


if __name__ == "__main__":
    folder = _load_images_folder()
    if not os.path.isdir(folder):
        print(f"[ERROR] Images folder not found: {folder}")
        sys.exit(1)
    print(f"Images folder: {folder}")
    rename_and_convert(folder)
    print("Done.")
