"""
Unit tests for src/common/paths.py's config path resolution.
"""
import os

from src.common import paths


def test_resolve_config_path_env_override_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("SIMS4_RLS_CONFIG_DIR", str(tmp_path))
    assert paths.resolve_config_path() == os.path.join(str(tmp_path), "config.json")


def test_resolve_config_path_portable_mode_when_local_file_exists(tmp_path, monkeypatch):
    monkeypatch.delenv("SIMS4_RLS_CONFIG_DIR", raising=False)
    local_config = tmp_path / "config.json"
    local_config.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(paths, "app_base_dir", lambda: str(tmp_path))

    assert paths.resolve_config_path() == str(local_config)


def test_resolve_config_path_falls_back_to_user_data_dir(tmp_path, monkeypatch):
    monkeypatch.delenv("SIMS4_RLS_CONFIG_DIR", raising=False)
    monkeypatch.setattr(paths, "app_base_dir", lambda: str(tmp_path))  # no config.json here

    result = paths.resolve_config_path()

    assert result != os.path.join(str(tmp_path), "config.json")
    assert result.endswith(os.path.join(paths.APP_NAME, "config.json"))


def test_is_frozen_false_under_pytest():
    assert paths.is_frozen() is False


def test_ensure_parent_dir_creates_missing_directories(tmp_path):
    target = tmp_path / "a" / "b" / "config.json"
    paths.ensure_parent_dir(str(target))
    assert os.path.isdir(tmp_path / "a" / "b")
