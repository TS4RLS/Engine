"""
Sims 4 Random Loading Screen Generator
=======================================
Picks a random image from your chosen folder, packages it as a valid
Sims 4 loading screen mod (.package file), and drops it into your Mods folder.

Callable API: load_config() / generate(cfg). main() is the CLI wrapper used
when this script is run directly (dev convenience) — the GUI and cli/menu.py
call generate() directly instead.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import json
import random
import struct
import subprocess
import time
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.common import paths
from src.common.config_format import parse_jsonc
from src.cli import cli_colors


class GeneratorError(Exception):
    """Raised for any user-facing failure generate()/load_config() hits."""


def _ensure_dependencies():
    if paths.is_frozen():
        return  # a frozen build must already bundle Pillow
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

TEMPLATE_PACKAGE = paths.resource_path(os.path.join("assets", "template.package"))
OUTPUT_PACKAGE_NAME = "RandomLoadingScreen.package"
SIMS4_STEAM_APP_ID = "1222670"

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"}

# ─── Resource key (confirmed by reverse-engineering a working package) ─────────
# Type 0x62ECC59A is the TS4 UI composition format (GFX/RLE2).
# Instance 0x432D1D2ADDFFC6D8 is the loading screen composition resource.
_RESOURCE_TYPE     = 0x62ECC59A
_RESOURCE_GROUP    = 0x00000000
_RESOURCE_INSTANCE = 0x432D1D2ADDFFC6D8


def _get_version() -> str:
    try:
        with open(os.path.join(_ROOT, "VERSION.md"), "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "?"


# ── CONFIGURATION ─────────────────────────────────────────────────────────────

def load_config() -> dict:
    config_path = paths.resolve_config_path()

    if not os.path.isfile(config_path):
        raise GeneratorError(
            "config.json not found.\n"
            "  Run the quick setup wizard (Configure settings), or see config.example.json."
        )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = parse_jsonc(f.read())
    except json.JSONDecodeError as e:
        raise GeneratorError(f"config.json contains invalid JSON: {e}")

    for key in ("images_folder", "mods_folder"):
        if key not in cfg:
            raise GeneratorError(f"config.json is missing required key: '{key}'")

    return cfg


# ── END CONFIGURATION ──────────────────────────────────────────────────────────


# ─── Image helpers ────────────────────────────────────────────────────────────

def _import_pil():
    try:
        from PIL import Image
        return Image
    except ImportError:
        raise GeneratorError("Pillow is not installed.\n  Run:  pip install Pillow")


def find_images(folder: str) -> list:
    images = []
    for root, _, files in os.walk(folder):
        for f in files:
            if Path(f).suffix.lower() in SUPPORTED_EXTENSIONS:
                images.append(os.path.join(root, f))
    return images


def _fit_and_crop(img, width: int, height: int):
    """Resize preserving aspect ratio, then centre-crop to exactly width x height."""
    img_ratio    = img.width / img.height
    target_ratio = width / height
    if img_ratio > target_ratio:
        new_h = height
        new_w = int(img.width * height / img.height)
    else:
        new_w = width
        new_h = int(img.height * width / img.width)
    Image = _import_pil()
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - width)  // 2
    top  = (new_h - height) // 2
    return img.crop((left, top, left + width, top + height))


def _to_argb_bytes(img) -> bytes:
    """Convert a PIL Image to raw ARGB bytes (the format the GFX resource expects)."""
    Image = _import_pil()
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    # PIL stores RGBA in-order; merge as (a,r,g,b) so tobytes() yields ARGB.
    return Image.merge("RGBA", (a, r, g, b)).tobytes()


def prepare_single_image(image_path: str, width: int, height: int) -> bytes:
    Image = _import_pil()
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img = _fit_and_crop(img, width, height)
        return _to_argb_bytes(img)


def prepare_combined_image(image_paths: list, total_width: int, total_height: int) -> bytes:
    """Combine three portrait images side-by-side into one landscape image."""
    Image = _import_pil()
    n = len(image_paths)
    base_w = total_width // n
    # Distribute any remainder pixel(s) to the middle panel
    widths = [base_w] * n
    widths[n // 2] += total_width - base_w * n

    canvas = Image.new("RGB", (total_width, total_height))
    x = 0
    for path, w in zip(image_paths, widths):
        with Image.open(path) as img:
            img = img.convert("RGB")
            panel = _fit_and_crop(img, w, total_height)
        canvas.paste(panel, (x, 0))
        x += w
    return _to_argb_bytes(canvas)


# ─── GFX / DBPF package builder ──────────────────────────────────────────────

def _load_template_gfx(template_path: str) -> bytearray:
    """Load the template .package and return the decompressed GFX resource bytes."""
    with open(template_path, "rb") as f:
        pkg = f.read()
    idx_offset = struct.unpack_from("<I", pkg, 64)[0]
    comp_data  = pkg[96:idx_offset]
    return bytearray(zlib.decompress(comp_data))


def _find_image_block_offset(gfx: bytearray) -> int:
    """
    Locate the inner image block within decompressed GFX data.

    The block starts with a uint32 size field immediately before the
    byte sequence 0x77 0x00 0x05 <width uint16> <height uint16> 0x78 <zlib byte>.
    Returns the offset of the size field (i.e. 4 bytes before 0x77).
    """
    for i in range(8, len(gfx) - 12):
        if (gfx[i] == 0x77 and gfx[i+1] == 0x00 and gfx[i+2] == 0x05
                and gfx[i+7] == 0x78):
            return i - 4
    raise ValueError(
        "Cannot find image data block in template GFX resource.\n"
        "  Make sure TEMPLATE_PACKAGE points to a valid loading screen .package."
    )


def get_template_image_size() -> tuple:
    """Return (width, height) of the image stored in the template package."""
    if not os.path.isfile(TEMPLATE_PACKAGE):
        raise GeneratorError(
            f"Template package not found:\n  {TEMPLATE_PACKAGE}\n"
            "  Ensure template.package is inside the assets folder."
        )
    gfx     = _load_template_gfx(TEMPLATE_PACKAGE)
    img_off = _find_image_block_offset(gfx)
    # Bytes 7-8 = width, bytes 9-10 = height (relative to img_off)
    width  = struct.unpack_from("<H", gfx, img_off + 7)[0]
    height = struct.unpack_from("<H", gfx, img_off + 9)[0]
    return width, height


def build_package(argb_bytes: bytes, width: int, height: int) -> bytes:
    """
    Build a .package file by splicing our image into the template's GFX resource.

    The GFX data layout (decompressed):
      [GFX\\x0F magic + total-size field  (8 bytes)]
      [UI composition metadata            (fixed, same in every package)]
      [Image block                        (variable)]
      [UI layout tail                     (fixed, same in every package)]

    Image block layout:
      [block_size - 4  uint32 ]   ← size of everything that follows
      [0x77 0x00 0x05           ]   ← format / flags / mip-hint (keep from template)
      [width   uint16 LE       ]
      [height  uint16 LE       ]
      [zlib-compressed ARGB data]
    """
    if not os.path.isfile(TEMPLATE_PACKAGE):
        raise GeneratorError(
            f"Template package not found:\n  {TEMPLATE_PACKAGE}\n"
            "  Ensure template.package is inside the assets folder."
        )

    gfx = _load_template_gfx(TEMPLATE_PACKAGE)

    img_off  = _find_image_block_offset(gfx)
    blk_size = struct.unpack_from("<I", gfx, img_off)[0]
    img_end  = img_off + 4 + blk_size      # exclusive end of old image block

    gfx_prefix = bytes(gfx[:img_off])
    gfx_tail   = bytes(gfx[img_end:])
    fmt_bytes  = bytes(gfx[img_off + 4 : img_off + 7])  # 0x77, 0x00, 0x05

    # Build inner block
    inner_zlib  = zlib.compress(argb_bytes, level=9)
    inner_fixed = fmt_bytes + struct.pack("<HH", width, height)  # 3 + 4 = 7 bytes
    inner_size  = len(inner_fixed) + len(inner_zlib)
    inner_block = struct.pack("<I", inner_size) + inner_fixed + inner_zlib

    # Reassemble GFX data and update the total-size field at bytes 4-7
    new_gfx = bytearray(gfx_prefix + inner_block + gfx_tail)
    struct.pack_into("<I", new_gfx, 4, len(new_gfx))

    # Outer zlib compress
    outer_zlib = zlib.compress(bytes(new_gfx), level=9)

    # ── DBPF package ──
    inst_hi = (_RESOURCE_INSTANCE >> 32) & 0xFFFFFFFF
    inst_lo =  _RESOURCE_INSTANCE        & 0xFFFFFFFF

    res_offset      = 96
    res_comp_size   = len(outer_zlib)
    res_uncomp_size = len(new_gfx)
    index_offset    = res_offset + res_comp_size

    index_flags = struct.pack("<I", 0)
    index_entry = struct.pack(
        "<IIIIIIIHH",
        _RESOURCE_TYPE,
        _RESOURCE_GROUP,
        inst_hi,
        inst_lo,
        res_offset,
        res_comp_size | 0x80000000,  # bit 31 = zlib-compressed
        res_uncomp_size,
        0x5A42,   # zlib compression type
        0x0001,   # committed
    )
    index_block = index_flags + index_entry   # 36 bytes
    index_size  = len(index_block)

    # Header layout (verified against working packages):
    #   0-3:   "DBPF"
    #   4-7:   major = 2
    #   8-11:  minor = 1
    #   12-31: zero (20 bytes)
    #   32-35: index_version_minor = 0
    #   36-39: num_entries = 1
    #   40-43: zero
    #   44-47: index_size = 36
    #   48-59: zero (12 bytes)
    #   60-63: index_version_major = 3
    #   64-67: index_offset
    #   68-95: zero (28 bytes)
    header = struct.pack(
        "<4sII20xII4xI12xII28x",
        b"DBPF", 2, 1,
        0, 1,
        index_size,
        3,
        index_offset,
    )
    assert len(header) == 96

    return header + outer_zlib + index_block


# ─── Generate ─────────────────────────────────────────────────────────────────

@dataclass
class GenerateResult:
    output_path: str
    launched: bool
    warning: Optional[str] = None


def generate(cfg: dict, force_launch: bool = False, log=print) -> GenerateResult:
    """Generate a new random loading screen package per cfg and write it to
    the Mods folder. Raises GeneratorError on any user-facing failure."""
    images_folder    = cfg["images_folder"]
    mods_folder      = cfg["mods_folder"]
    is_vertical      = cfg.get("is_vertical", True)
    launch_game      = cfg.get("launch_game", True) or force_launch
    rename_files     = cfg.get("rename_files", False)
    game_exe         = cfg.get("game_exe", "")
    launch_via_steam = cfg.get("launch_via_steam", True)

    if not os.path.isdir(images_folder):
        raise GeneratorError(
            f"Images folder not found:\n  {images_folder}\n"
            "  Update 'images_folder' in config.json."
        )

    if rename_files:
        log("\nRenaming images...")
        from src.core.renamer import rename_images
        ok, failed = rename_images(images_folder, log=log)
        log(f"  Renamed {ok} file(s)" + (f", {failed} skipped." if failed else "."))

    if not os.path.isdir(mods_folder):
        raise GeneratorError(
            f"Mods folder not found:\n  {mods_folder}\n"
            "  Update 'mods_folder' in config.json."
        )

    output_folder = os.path.join(mods_folder, "RandomLoadingScreen")
    os.makedirs(output_folder, exist_ok=True)

    images = find_images(images_folder)
    if not images:
        raise GeneratorError(
            f"No images found in:\n  {images_folder}\n"
            f"  Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    log(f"\nFound {len(images)} image(s).")

    # Use the exact dimensions the template stores so the game renders correctly.
    img_w, img_h = get_template_image_size()
    log(f"Template image size: {img_w}x{img_h}")

    try:
        if is_vertical:
            n = 2
            if len(images) >= n:
                chosen = random.sample(images, n)
            else:
                chosen = [random.choice(images) for _ in range(n)]
            log(f"Selected (vertical mode, combining {n}):")
            for c in chosen:
                log(f"  {os.path.basename(c)}")
            log(f"Processing {n} images -> {img_w}x{img_h} combined...")
            argb_bytes = prepare_combined_image(chosen, img_w, img_h)
        else:
            chosen = random.choice(images)
            log(f"Selected: {os.path.basename(chosen)}")
            log(f"Processing image ({img_w}x{img_h})...")
            argb_bytes = prepare_single_image(chosen, img_w, img_h)
    except GeneratorError:
        raise
    except Exception as e:
        raise GeneratorError(f"Failed to process image(s): {e}")

    log("Building .package file...")
    try:
        package_bytes = build_package(argb_bytes, img_w, img_h)
    except Exception as e:
        raise GeneratorError(f"Failed to build package: {e}")

    output_path = os.path.join(output_folder, OUTPUT_PACKAGE_NAME)
    if os.path.exists(output_path):
        os.remove(output_path)

    with open(output_path, "wb") as f:
        f.write(package_bytes)

    log(f"Written to: {output_path}")
    log(f"Package size: {len(package_bytes) / 1024:.1f} KB")

    launched = False
    warning = None
    if launch_game:
        log("\nLaunching Sims 4...")
        if launch_via_steam:
            subprocess.Popen(["start", f"steam://rungameid/{SIMS4_STEAM_APP_ID}"], shell=True)
            launched = True
        elif os.path.isfile(game_exe):
            subprocess.Popen([game_exe])
            launched = True
        else:
            warning = f"Game executable not found: {game_exe}"

    return GenerateResult(output_path=output_path, launched=launched, warning=warning)


# ─── Main (CLI wrapper for direct/dev invocation) ────────────────────────────

def main():
    print(cli_colors.banner(
        "TS4RLS - The Sims 4 Random Loading Screen - Package Generator",
        f"v{_get_version()}\nBuilt & Maintained by StuxieDev",
    ))

    force_launch = "--force-launch" in sys.argv
    non_interactive_flag = "--generate" in sys.argv

    try:
        cfg = load_config()
        non_interactive = cfg.get("non_interactive", True) or non_interactive_flag
        result = generate(cfg, force_launch=force_launch)
    except GeneratorError as e:
        print("\n" + cli_colors.error(str(e)))
        sys.exit(1)

    if result.warning:
        print(cli_colors.warning(result.warning))
        print("  Set game_exe or launch_via_steam in config.json.")

    launch_game = cfg.get("launch_game", True) or force_launch
    launch_msg = (
        "The Sims 4 will now launch with your new random loading screen."
        if result.launched else
        "Random loading screen package created. Launch the game to see it in action."
    )

    print("\nDone!")
    print(launch_msg)
    print("=" * 69)

    if launch_game:
        for i in range(15, 0, -1):
            print(f"\r  Closing in {i}s...  ", end="", flush=True)
            time.sleep(1)
        print()
    elif not non_interactive:
        print("\n  Press any key to close...")
        try:
            import msvcrt
            msvcrt.getch()
        except ImportError:
            input()


if __name__ == "__main__":
    main()
