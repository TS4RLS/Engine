"""
Unit tests for scripts/build_release_files.py.

Only the pure, platform-dependent helper logic is tested here. Actually
invoking ensure_pyinstaller()/build() would shell out to PyInstaller,
require the real .ico assets to be discovered relative to cwd, and produce
real .exe artifacts -- that's a packaging/build concern, not unit-testable
logic, so it is intentionally left uncovered (see report).
"""
import pytest

from scripts import build_release_files as builder


def _patch_script_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(builder, "ROOT_DIR", str(tmp_path))


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
    assert builder._icon_args() == [f"--icon={ico}"]


def test_icon_args_macos_looks_for_icns(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "IS_WINDOWS", False)
    monkeypatch.setattr(builder, "IS_MACOS", True)
    (tmp_path / "assets").mkdir()
    icns = tmp_path / "assets" / "icon.icns"
    icns.write_bytes(b"fake")
    assert builder._icon_args() == [f"--icon={icns}"]


def test_icon_args_linux_returns_empty(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "IS_WINDOWS", False)
    monkeypatch.setattr(builder, "IS_MACOS", False)
    assert builder._icon_args() == []


def test_icon_args_missing_file_returns_empty(tmp_path, monkeypatch):
    _patch_script_dir(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "IS_WINDOWS", True)
    monkeypatch.setattr(builder, "IS_MACOS", False)
    assert builder._icon_args() == []
