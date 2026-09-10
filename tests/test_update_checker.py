"""
Unit tests for src/common/update_checker.py. No real network calls -
urllib.request.urlopen is monkeypatched with a fake response.
"""
import json
import urllib.error

import pytest

from src.common import update_checker


# ─── _parse_version / is_newer ────────────────────────────────────────────

def test_parse_version_strips_v_prefix():
    assert update_checker._parse_version("v4.3.1") == (4, 3, 1)


def test_parse_version_without_prefix():
    assert update_checker._parse_version("4.3.1") == (4, 3, 1)


def test_parse_version_pads_missing_parts():
    assert update_checker._parse_version("4") == (4, 0, 0)
    assert update_checker._parse_version("4.3") == (4, 3, 0)


def test_parse_version_non_numeric_part_sorts_as_zero():
    assert update_checker._parse_version("4.x.1") == (4, 0, 1)


def test_is_newer_true_when_latest_is_greater():
    assert update_checker.is_newer("v4.4.0", "4.3.1") is True


def test_is_newer_false_when_equal():
    assert update_checker.is_newer("v4.3.1", "4.3.1") is False


def test_is_newer_false_when_current_is_greater():
    assert update_checker.is_newer("v4.0.0", "4.3.1") is False


# ─── check_for_update ─────────────────────────────────────────────────────

class _FakeResponse:
    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_check_for_update_reports_update_available(monkeypatch):
    payload = {"tag_name": "v4.4.0", "html_url": "https://github.com/TS4RLS/Engine/releases/tag/v4.4.0"}
    monkeypatch.setattr(update_checker.urllib.request, "urlopen", lambda *a, **k: _FakeResponse(payload))

    result = update_checker.check_for_update("4.3.1")

    assert result.update_available is True
    assert result.latest_version == "4.4.0"
    assert result.url == payload["html_url"]
    assert result.error is None


def test_check_for_update_reports_up_to_date(monkeypatch):
    payload = {"tag_name": "v4.3.1", "html_url": "https://github.com/TS4RLS/Engine/releases/tag/v4.3.1"}
    monkeypatch.setattr(update_checker.urllib.request, "urlopen", lambda *a, **k: _FakeResponse(payload))

    result = update_checker.check_for_update("4.3.1")

    assert result.update_available is False
    assert result.latest_version == "4.3.1"
    assert result.error is None


def test_check_for_update_handles_network_error(monkeypatch):
    def raise_error(*a, **k):
        raise urllib.error.URLError("no connection")
    monkeypatch.setattr(update_checker.urllib.request, "urlopen", raise_error)

    result = update_checker.check_for_update("4.3.1")

    assert result.update_available is False
    assert result.error is not None


def test_check_for_update_handles_missing_tag_name(monkeypatch):
    monkeypatch.setattr(update_checker.urllib.request, "urlopen", lambda *a, **k: _FakeResponse({}))

    result = update_checker.check_for_update("4.3.1")

    assert result.update_available is False
    assert result.error is not None
