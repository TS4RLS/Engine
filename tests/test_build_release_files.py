"""
Unit tests for scripts/build_release_files.py.

Only the pure, platform-dependent helper logic is tested here. Actually
invoking ensure_dependencies()/build_gui() would shell out to pip/
PyInstaller and produce real executable artifacts -- that's a packaging/
build concern, not unit-testable logic, so it is intentionally left
uncovered (see report). build_steam_zip() is covered directly since it's
pure Python with no subprocess/PyInstaller involved.
"""
from scripts import build_release_files as builder


def _patch_repo_root(monkeypatch, tmp_path):
    monkeypatch.setattr(builder, "REPO_ROOT", tmp_path)


def test_icon_args_windows_looks_for_ico(tmp_path, monkeypatch):
    _patch_repo_root(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "IS_WINDOWS", True)
    monkeypatch.setattr(builder, "IS_MACOS", False)
    (tmp_path / "assets").mkdir()
    ico = tmp_path / "assets" / "icon.ico"
    ico.write_bytes(b"fake")
    assert builder._icon_args() == [f"--icon={ico}"]


def test_icon_args_macos_looks_for_icns(tmp_path, monkeypatch):
    _patch_repo_root(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "IS_WINDOWS", False)
    monkeypatch.setattr(builder, "IS_MACOS", True)
    (tmp_path / "assets").mkdir()
    icns = tmp_path / "assets" / "icon.icns"
    icns.write_bytes(b"fake")
    assert builder._icon_args() == [f"--icon={icns}"]


def test_icon_args_linux_returns_empty(tmp_path, monkeypatch):
    _patch_repo_root(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "IS_WINDOWS", False)
    monkeypatch.setattr(builder, "IS_MACOS", False)
    assert builder._icon_args() == []


def test_icon_args_missing_file_returns_empty(tmp_path, monkeypatch):
    _patch_repo_root(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "IS_WINDOWS", True)
    monkeypatch.setattr(builder, "IS_MACOS", False)
    assert builder._icon_args() == []


def test_build_steam_zip_zips_every_file_in_assets_steam(tmp_path, monkeypatch):
    _patch_repo_root(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "DIST_DIR", tmp_path / "dist")
    steam_dir = tmp_path / "assets" / "steam"
    steam_dir.mkdir(parents=True)
    (steam_dir / "cover.png").write_bytes(b"fake-cover")
    (steam_dir / "logo.png").write_bytes(b"fake-logo")

    zip_path = builder.build_steam_zip()

    assert zip_path == tmp_path / "dist" / builder.STEAM_ZIP_NAME
    assert zip_path.is_file()
    import zipfile
    with zipfile.ZipFile(zip_path) as zf:
        assert sorted(zf.namelist()) == ["cover.png", "logo.png"]
