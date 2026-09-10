"""
Unit tests for src/executable_builder.py.

Only the pure config-loading logic is tested here. Actually invoking
ensure_pyinstaller()/_build_exe()/build() would shell out to PyInstaller,
require the real .ico assets to be discovered relative to cwd, and produce
real .exe artifacts -- that's a packaging/build concern, not unit-testable
logic, so it is intentionally left uncovered (see report).
"""
import pytest

import executable_builder as builder


def _patch_script_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(builder, "ROOT_DIR", str(tmp_path))


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


# ─── platform-dependent helpers ─────────────────────────────────────────────

def test_exe_suffix_is_dot_exe_on_windows(monkeypatch):
    monkeypatch.setattr(builder, "IS_WINDOWS", True)
    assert builder._exe_suffix() == ".exe"


def test_exe_suffix_is_empty_off_windows(monkeypatch):
    monkeypatch.setattr(builder, "IS_WINDOWS", False)
    assert builder._exe_suffix() == ""


def test_icon_args_windows_looks_for_ico(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "IS_WINDOWS", True)
    monkeypatch.setattr(builder, "IS_MACOS", False)
    (tmp_path / "assets").mkdir()
    ico = tmp_path / "assets" / "icon.ico"
    ico.write_bytes(b"fake")
    assert builder._icon_args("icon") == [f"--icon={ico}"]


def test_icon_args_macos_looks_for_icns(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "IS_WINDOWS", False)
    monkeypatch.setattr(builder, "IS_MACOS", True)
    (tmp_path / "assets").mkdir()
    icns = tmp_path / "assets" / "icon.icns"
    icns.write_bytes(b"fake")
    assert builder._icon_args("icon") == [f"--icon={icns}"]


def test_icon_args_linux_returns_empty(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "IS_WINDOWS", False)
    monkeypatch.setattr(builder, "IS_MACOS", False)
    assert builder._icon_args("icon") == []


def test_icon_args_missing_file_returns_empty(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "IS_WINDOWS", True)
    monkeypatch.setattr(builder, "IS_MACOS", False)
    assert builder._icon_args("icon") == []
