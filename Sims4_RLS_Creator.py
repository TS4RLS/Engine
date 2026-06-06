"""
Sims 4 Random Loading Screen Generator
=======================================
Picks a random image from your chosen folder, packages it as a valid
Sims 4 loading screen mod (.package file), and drops it into your Mods folder.

Run this script before launching the game. Each run picks a new random image.

Requirements:
  - Python 3.6+
  - Pillow  (pip install Pillow)

Configuration:
  Copy config.example.json to config.json and fill in your paths.
"""

import json
import os
import random
import struct
import zlib
import sys
import subprocess
from pathlib import Path

# ── CONFIGURATION ─────────────────────────────────────────────────────────────

def _load_config() -> dict:
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")

    if not os.path.isfile(config_path):
        example_path = os.path.join(script_dir, "config.example.json")
        print("[ERROR] config.json not found.")
        print("  Copy config.example.json to config.json and fill in your paths:")
        print(f'    copy "{example_path}" "{config_path}"')
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            text = f.read()
        # Allow single backslashes in paths — protect existing \\ pairs, then
        # double up any lone \, then restore the protected pairs.
        _ph = "\x00"
        text = text.replace("\\\\", _ph)
        text = text.replace("\\", "\\\\")
        text = text.replace(_ph, "\\\\")
        cfg = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[ERROR] config.json contains invalid JSON: {e}")
        sys.exit(1)

    for key in ("images_folder", "mods_folder"):
        if key not in cfg:
            print(f"[ERROR] config.json is missing required key: '{key}'")
            print("  See config.example.json for the full list of settings.")
            sys.exit(1)

    return cfg


_cfg = _load_config()

IMAGES_FOLDER       = _cfg["images_folder"]
MODS_FOLDER         = _cfg["mods_folder"]
IS_VERTICAL         = _cfg.get("is_vertical", True)
LAUNCH_GAME         = _cfg.get("launch_game", True)
GAME_EXE            = _cfg.get("game_exe", "")
LAUNCH_VIA_STEAM    = _cfg.get("launch_via_steam", True)
TARGET_WIDTH        = _cfg.get("target_width", 1920)
TARGET_HEIGHT       = _cfg.get("target_height", 1080)

# ── END CONFIGURATION ──────────────────────────────────────────────────────────

_SCRIPT_DIR         = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PACKAGE    = os.path.join(
    _SCRIPT_DIR, ".DONOTRENAME_DONOTREMOVE", "TemplateLoadingScreen_DONOTRENAMEORREMOVE.package"
)
OUTPUT_PACKAGE_NAME = "RandomLoadingScreen.package"
SIMS4_STEAM_APP_ID  = "1222670"

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"}

# ─── Resource key (confirmed by reverse-engineering a working package) ─────────
# Type 0x62ECC59A is the TS4 UI composition format (GFX/RLE2).
# Instance 0x432D1D2ADDFFC6D8 is the loading screen composition resource.
_RESOURCE_TYPE     = 0x62ECC59A
_RESOURCE_GROUP    = 0x00000000
_RESOURCE_INSTANCE = 0x432D1D2ADDFFC6D8


# ─── Image helpers ────────────────────────────────────────────────────────────

def _import_pil():
    try:
        from PIL import Image
        return Image
    except ImportError:
        print("\n[ERROR] Pillow is not installed.")
        print("  Run:  pip install Pillow")
        sys.exit(1)


def find_images(folder: str) -> list:
    images = []
    for root, _, files in os.walk(folder):
        for f in files:
            if Path(f).suffix.lower() in SUPPORTED_EXTENSIONS:
                images.append(os.path.join(root, f))
    return images


def _fit_and_crop(img, width: int, height: int):
    """Resize preserving aspect ratio, then centre-crop to exactly width×height."""
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
        print(f"\n[ERROR] Template package not found:\n  {TEMPLATE_PACKAGE}")
        print("  Ensure TemplateLoadingScreen_DONOTRENAMEORREMOVE.package is inside the .DONOTRENAME_DONOTREMOVE folder.")
        sys.exit(1)
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
        print(f"\n[ERROR] Template package not found:\n  {TEMPLATE_PACKAGE}")
        print("  Ensure TemplateLoadingScreen_DONOTRENAMEORREMOVE.package is inside the .DONOTRENAME_DONOTREMOVE folder.")
        sys.exit(1)

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


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 69)
    print("       Sims 4 Random Loading Screen Generator - Python Script")
    print("=" * 69)

    if not os.path.isdir(IMAGES_FOLDER):
        print(f"\n[ERROR] Images folder not found:\n  {IMAGES_FOLDER}")
        print("  Update 'images_folder' in config.json.")
        sys.exit(1)

    if not os.path.isdir(MODS_FOLDER):
        print(f"\n[ERROR] Mods folder not found:\n  {MODS_FOLDER}")
        print("  Update 'mods_folder' in config.json.")
        sys.exit(1)

    output_folder = os.path.join(MODS_FOLDER, "RandomLoadingScreen")
    os.makedirs(output_folder, exist_ok=True)

    images = find_images(IMAGES_FOLDER)
    if not images:
        print(f"\n[ERROR] No images found in:\n  {IMAGES_FOLDER}")
        print(f"  Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(1)

    print(f"\nFound {len(images)} image(s).")

    # Use the exact dimensions the template stores so the game renders correctly.
    img_w, img_h = get_template_image_size()
    print(f"Template image size: {img_w}×{img_h}")

    try:
        if IS_VERTICAL:
            n = 2
            if len(images) >= n:
                chosen = random.sample(images, n)
            else:
                chosen = [random.choice(images) for _ in range(n)]
            print(f"Selected (vertical mode, combining {n}):")
            for c in chosen:
                print(f"  {os.path.basename(c)}")
            print(f"Processing {n} images → {img_w}×{img_h} combined...")
            argb_bytes = prepare_combined_image(chosen, img_w, img_h)
        else:
            chosen = random.choice(images)
            print(f"Selected: {os.path.basename(chosen)}")
            print(f"Processing image ({img_w}×{img_h})...")
            argb_bytes = prepare_single_image(chosen, img_w, img_h)
    except Exception as e:
        print(f"\n[ERROR] Failed to process image(s): {e}")
        sys.exit(1)

    print("Building .package file...")
    try:
        package_bytes = build_package(argb_bytes, img_w, img_h)
    except Exception as e:
        print(f"\n[ERROR] Failed to build package: {e}")
        sys.exit(1)

    output_path = os.path.join(output_folder, OUTPUT_PACKAGE_NAME)
    if os.path.exists(output_path):
        os.remove(output_path)

    with open(output_path, "wb") as f:
        f.write(package_bytes)

    print(f"Written to: {output_path}")
    print(f"Package size: {len(package_bytes) / 1024:.1f} KB")

    if LAUNCH_GAME:
        print("\nLaunching Sims 4...")
        if LAUNCH_VIA_STEAM:
            subprocess.Popen(
                ["start", f"steam://rungameid/{SIMS4_STEAM_APP_ID}"],
                shell=True
            )
        elif os.path.isfile(GAME_EXE):
            subprocess.Popen([GAME_EXE])
        else:
            print(f"[WARNING] Game executable not found: {GAME_EXE}")
            print("  Set GAME_EXE or LAUNCH_VIA_STEAM in the script settings.")

    print("\nDone! Launch The Sims 4 to see your random loading screen.")
    print("=" * 69)


if __name__ == "__main__":
    main()
