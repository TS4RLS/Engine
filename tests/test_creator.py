"""
Unit tests for Sims4_RLS_Creator.py.

These exercise pure image-discovery, image-processing and binary
packaging logic using tmp_path fixtures and synthetic in-memory images.
Nothing here touches the user's real config.json, Mods folder, or the
actual Sims 4 game.
"""
import os
import struct
import sys
import zlib

import pytest
from PIL import Image

import Sims4_RLS_Creator as creator


# ─── find_images ──────────────────────────────────────────────────────────

def test_find_images_returns_supported_extensions_recursively(tmp_path):
    (tmp_path / "sub").mkdir()
    supported = ["a.png", "b.JPG", "c.jpeg", "d.bmp", "e.webp", "f.tiff"]
    for name in supported:
        (tmp_path / name).write_bytes(b"fake")
    (tmp_path / "sub" / "g.png").write_bytes(b"fake")
    (tmp_path / "notes.txt").write_bytes(b"not an image")
    (tmp_path / "archive.zip").write_bytes(b"not an image")

    found = creator.find_images(str(tmp_path))
    found_names = {os.path.basename(p) for p in found}

    assert found_names == {"a.png", "b.JPG", "c.jpeg", "d.bmp", "e.webp", "f.tiff", "g.png"}
    assert len(found) == 7


def test_find_images_empty_folder_returns_empty_list(tmp_path):
    assert creator.find_images(str(tmp_path)) == []


def test_find_images_ignores_unsupported_files_only(tmp_path):
    (tmp_path / "readme.md").write_bytes(b"x")
    (tmp_path / "data.json").write_bytes(b"{}")
    assert creator.find_images(str(tmp_path)) == []


# ─── _fit_and_crop ────────────────────────────────────────────────────────

def test_fit_and_crop_wide_image_to_square():
    img = Image.new("RGB", (200, 50), (1, 2, 3))
    result = creator._fit_and_crop(img, 40, 40)
    assert result.size == (40, 40)


def test_fit_and_crop_tall_image_to_square():
    img = Image.new("RGB", (50, 200), (1, 2, 3))
    result = creator._fit_and_crop(img, 40, 40)
    assert result.size == (40, 40)


def test_fit_and_crop_preserves_exact_target_dimensions_various_ratios():
    img = Image.new("RGB", (123, 77), (5, 6, 7))
    result = creator._fit_and_crop(img, 300, 100)
    assert result.size == (300, 100)


# ─── _to_argb_bytes ───────────────────────────────────────────────────────

def test_to_argb_bytes_pixel_order_is_argb_not_rgba():
    img = Image.new("RGB", (1, 1), (10, 20, 30))
    data = creator._to_argb_bytes(img)
    assert data == bytes([255, 10, 20, 30])  # A, R, G, B


def test_to_argb_bytes_length_matches_dimensions():
    img = Image.new("RGB", (5, 3), (0, 0, 0))
    data = creator._to_argb_bytes(img)
    assert len(data) == 5 * 3 * 4


# ─── prepare_single_image ─────────────────────────────────────────────────

def test_prepare_single_image_produces_target_size_bytes(tmp_path):
    src = tmp_path / "src.png"
    Image.new("RGB", (300, 120), (9, 9, 9)).save(src)
    data = creator.prepare_single_image(str(src), 64, 48)
    assert len(data) == 64 * 48 * 4


# ─── prepare_combined_image ───────────────────────────────────────────────

def _solid_portrait(path, color, size=(20, 100)):
    Image.new("RGB", size, color).save(path)


def test_prepare_combined_image_total_size(tmp_path):
    p1 = tmp_path / "1.png"
    p2 = tmp_path / "2.png"
    _solid_portrait(p1, (255, 0, 0))
    _solid_portrait(p2, (0, 255, 0))
    data = creator.prepare_combined_image([str(p1), str(p2)], 100, 50)
    assert len(data) == 100 * 50 * 4


def test_prepare_combined_image_distributes_remainder_to_middle_panel(tmp_path):
    # total_width=101, n=3 -> base widths [33,33,33] with the +2 remainder
    # added to the middle panel -> [33, 35, 33].
    paths = []
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    for i, color in enumerate(colors):
        p = tmp_path / f"{i}.png"
        _solid_portrait(p, color)
        paths.append(str(p))

    total_width, total_height = 101, 50
    data = creator.prepare_combined_image(paths, total_width, total_height)
    assert len(data) == total_width * total_height * 4

    def pixel_at(x, y=0):
        offset = (y * total_width + x) * 4
        a, r, g, b = data[offset:offset + 4]
        return (r, g, b)

    # Panel 1 (red): columns 0..32
    assert pixel_at(0) == (255, 0, 0)
    assert pixel_at(32) == (255, 0, 0)
    # Panel 2 (green): columns 33..67 (width 35, gets the +2 remainder)
    assert pixel_at(33) == (0, 255, 0)
    assert pixel_at(67) == (0, 255, 0)
    # Panel 3 (blue): columns 68..100
    assert pixel_at(68) == (0, 0, 255)
    assert pixel_at(100) == (0, 0, 255)


# ─── _find_image_block_offset ─────────────────────────────────────────────

def test_find_image_block_offset_raises_on_garbage_data():
    garbage = bytearray(b"\x01" * 64)
    with pytest.raises(ValueError):
        creator._find_image_block_offset(garbage)


def test_find_image_block_offset_locates_marker():
    # Construct a minimal buffer containing the marker sequence at a known offset.
    prefix = b"\x00" * 10
    marker = bytes([0x77, 0x00, 0x05]) + struct.pack("<HH", 640, 480) + bytes([0x78, 0x9c])
    padding = b"\x00" * 20  # loop needs room to look 12 bytes past the match
    buf = bytearray(prefix + marker + padding)
    offset = creator._find_image_block_offset(buf)
    assert offset == len(prefix) - 4


# ─── Template package integration (real committed asset) ─────────────────

def test_get_template_image_size_returns_positive_dimensions():
    width, height = creator.get_template_image_size()
    assert isinstance(width, int) and isinstance(height, int)
    assert 0 < width <= 10000
    assert 0 < height <= 10000


def test_build_package_roundtrip_preserves_image_data():
    width, height = creator.get_template_image_size()
    # Deterministic, non-trivial ARGB payload (not all-zero) so a broken
    # splice can't accidentally "match".
    argb = bytes(((i * 37) % 256) for i in range(width * height * 4))

    package_bytes = creator.build_package(argb, width, height)

    assert package_bytes[:4] == b"DBPF"

    index_offset = struct.unpack_from("<I", package_bytes, 64)[0]
    comp_data = package_bytes[96:index_offset]
    gfx = bytearray(zlib.decompress(comp_data))

    img_off = creator._find_image_block_offset(gfx)
    out_width = struct.unpack_from("<H", gfx, img_off + 7)[0]
    out_height = struct.unpack_from("<H", gfx, img_off + 9)[0]
    assert (out_width, out_height) == (width, height)

    blk_size = struct.unpack_from("<I", gfx, img_off)[0]
    inner_zlib = bytes(gfx[img_off + 4 + 7: img_off + 4 + blk_size])
    recovered = zlib.decompress(inner_zlib)
    assert recovered == argb


# ─── _load_config ──────────────────────────────────────────────────────────

def _patch_script_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(creator, "__file__", str(tmp_path / "Sims4_RLS_Creator.py"))


def test_load_config_missing_file_exits(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    with pytest.raises(SystemExit):
        creator._load_config()


def test_load_config_invalid_json_exits(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    (tmp_path / "config.json").write_text("{not valid json", encoding="utf-8")
    with pytest.raises(SystemExit):
        creator._load_config()


def test_load_config_missing_required_key_exits(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    (tmp_path / "config.json").write_text('{"images_folder": "x"}', encoding="utf-8")
    with pytest.raises(SystemExit):
        creator._load_config()


def test_load_config_accepts_lazy_single_backslash_paths(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    raw = '{"images_folder": "C:\\Foo\\Bar", "mods_folder": "C:\\Mods"}'
    (tmp_path / "config.json").write_text(raw, encoding="utf-8")
    cfg = creator._load_config()
    assert cfg["images_folder"] == r"C:\Foo\Bar"
    assert cfg["mods_folder"] == r"C:\Mods"


def test_load_config_accepts_properly_escaped_backslash_paths(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    raw = '{"images_folder": "C:\\\\Foo\\\\Bar", "mods_folder": "C:\\\\Mods"}'
    (tmp_path / "config.json").write_text(raw, encoding="utf-8")
    cfg = creator._load_config()
    assert cfg["images_folder"] == r"C:\Foo\Bar"
    assert cfg["mods_folder"] == r"C:\Mods"


def test_load_config_defaults_are_applied(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    (tmp_path / "config.json").write_text(
        '{"images_folder": "imgs", "mods_folder": "mods"}', encoding="utf-8"
    )
    cfg = creator._load_config()
    assert cfg["images_folder"] == "imgs"
    assert cfg["mods_folder"] == "mods"
    # Defaults for optional keys are applied by the module, not _load_config
    # itself, but the raw dict must at least round-trip cleanly with no
    # extra required keys enforced beyond the two mandatory ones.
    assert "is_vertical" not in cfg
