"""
Unit tests for Sims4_RLS_ExeBuilder.py.

Only the pure config-loading logic is tested here. Actually invoking
ensure_pyinstaller()/_build_exe()/build() would shell out to PyInstaller,
require the real .ico assets to be discovered relative to cwd, and produce
real .exe artifacts -- that's a packaging/build concern, not unit-testable
logic, so it is intentionally left uncovered (see report).
"""
import pytest

import Sims4_RLS_ExeBuilder as builder


def _patch_script_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(builder, "SCRIPT_DIR", str(tmp_path))


def test_load_build_config_missing_file_returns_empty_dict(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    assert builder._load_build_config() == {}


def test_load_build_config_invalid_json_returns_empty_dict(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    (tmp_path / "config.json").write_text("{not valid", encoding="utf-8")
    assert builder._load_build_config() == {}


def test_load_build_config_parses_valid_json(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    (tmp_path / "config.json").write_text(
        '{"create_curseforge_version": true}', encoding="utf-8"
    )
    cfg = builder._load_build_config()
    assert cfg == {"create_curseforge_version": True}


def test_load_build_config_handles_lazy_backslash_paths(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    raw = '{"images_folder": "C:\\Foo\\Bar"}'
    (tmp_path / "config.json").write_text(raw, encoding="utf-8")
    cfg = builder._load_build_config()
    assert cfg["images_folder"] == r"C:\Foo\Bar"
