"""
Unit tests for Sims4_RLS_ImagesRenamer.py.

All file operations run against tmp_path fixtures; nothing touches the
user's real images_folder or config.json.
"""
import os
import string

import pytest
from PIL import Image

import Sims4_RLS_ImagesRenamer as renamer


# ─── _random_name ──────────────────────────────────────────────────────────

def test_random_name_length_and_charset():
    name = renamer._random_name()
    assert len(name) == 32
    allowed = set(string.ascii_lowercase + string.digits)
    assert set(name) <= allowed


def test_random_name_is_not_constant_across_calls():
    names = {renamer._random_name() for _ in range(20)}
    assert len(names) > 1  # astronomically unlikely to collide 20 times


# ─── _unique_jpg_path ──────────────────────────────────────────────────────

def test_unique_jpg_path_retries_on_collision(tmp_path, monkeypatch):
    (tmp_path / "aaaa.jpg").write_bytes(b"taken")

    names = iter(["aaaa", "bbbb"])
    monkeypatch.setattr(renamer, "_random_name", lambda: next(names))

    result = renamer._unique_jpg_path(str(tmp_path))
    assert os.path.basename(result) == "bbbb.jpg"


def test_unique_jpg_path_returns_free_name_first_try(tmp_path, monkeypatch):
    monkeypatch.setattr(renamer, "_random_name", lambda: "onlyoption")
    result = renamer._unique_jpg_path(str(tmp_path))
    assert result == os.path.join(str(tmp_path), "onlyoption.jpg")


# ─── rename_and_convert ────────────────────────────────────────────────────

def test_rename_and_convert_empty_folder_does_nothing(tmp_path, capsys):
    renamer.rename_and_convert(str(tmp_path))
    out = capsys.readouterr().out
    assert "No images found" in out
    assert list(tmp_path.iterdir()) == []


def test_rename_and_convert_renames_and_converts_to_jpeg(tmp_path):
    Image.new("RGB", (10, 10), (255, 0, 0)).save(tmp_path / "one.png")
    Image.new("RGB", (10, 10), (0, 255, 0)).save(tmp_path / "two.bmp")
    (tmp_path / "notes.txt").write_text("keep me")

    renamer.rename_and_convert(str(tmp_path))

    remaining = list(tmp_path.iterdir())
    names = [p.name for p in remaining]

    # Originals gone, non-image untouched.
    assert "one.png" not in names
    assert "two.bmp" not in names
    assert "notes.txt" in names

    jpgs = [p for p in remaining if p.suffix == ".jpg"]
    assert len(jpgs) == 2
    for p in jpgs:
        stem = p.stem
        assert len(stem) == 32
        assert set(stem) <= set(string.ascii_lowercase + string.digits)
        with Image.open(p) as img:
            assert img.format == "JPEG"


def test_rename_and_convert_skips_corrupt_file_and_leaves_it_in_place(tmp_path, capsys):
    bad = tmp_path / "corrupt.png"
    bad.write_bytes(b"this is not a real image")

    renamer.rename_and_convert(str(tmp_path))

    out = capsys.readouterr().out
    assert "skipped" in out
    assert bad.exists()  # left untouched since conversion failed
    jpgs = [p for p in tmp_path.iterdir() if p.suffix == ".jpg"]
    assert jpgs == []


def test_rename_and_convert_recurses_into_subfolders(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    Image.new("RGB", (5, 5), (1, 2, 3)).save(sub / "nested.png")

    renamer.rename_and_convert(str(tmp_path))

    remaining = list(sub.iterdir())
    assert len(remaining) == 1
    assert remaining[0].suffix == ".jpg"


# ─── _load_images_folder ───────────────────────────────────────────────────

def _patch_script_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(renamer, "__file__", str(tmp_path / "Sims4_RLS_ImagesRenamer.py"))


def test_load_images_folder_missing_config_exits(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    with pytest.raises(SystemExit):
        renamer._load_images_folder()


def test_load_images_folder_missing_key_exits(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    (tmp_path / "config.json").write_text('{"mods_folder": "x"}', encoding="utf-8")
    with pytest.raises(SystemExit):
        renamer._load_images_folder()


def test_load_images_folder_returns_value(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    (tmp_path / "config.json").write_text(
        '{"images_folder": "/some/path"}', encoding="utf-8"
    )
    assert renamer._load_images_folder() == "/some/path"
