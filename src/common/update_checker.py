"""
Checks GitHub Releases for a newer version of TS4RLS than the one
currently running. Pure stdlib (urllib), no extra dependency, and fails
quietly (never raises) since this is a background, best-effort check —
being offline or GitHub being unreachable shouldn't be an error the user
has to deal with.
"""

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

LATEST_RELEASE_URL = "https://api.github.com/repos/TS4RLS/Engine/releases/latest"
RELEASES_PAGE_URL = "https://github.com/TS4RLS/Engine/releases/latest"
REQUEST_TIMEOUT = 5


@dataclass
class UpdateCheckResult:
    update_available: bool
    current_version: str
    latest_version: Optional[str] = None
    url: str = RELEASES_PAGE_URL
    error: Optional[str] = None


def _parse_version(version: str) -> tuple:
    """'v4.3.1' / '4.3.1' -> (4, 3, 1). Non-numeric parts sort as 0 so a
    malformed version doesn't crash the comparison, just compares low."""
    cleaned = version.strip().lstrip("vV")
    parts = []
    for part in cleaned.split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def is_newer(latest: str, current: str) -> bool:
    return _parse_version(latest) > _parse_version(current)


def check_for_update(current_version: str, timeout: int = REQUEST_TIMEOUT) -> UpdateCheckResult:
    try:
        request = urllib.request.Request(
            LATEST_RELEASE_URL,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "TS4RLS-update-checker"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
        return UpdateCheckResult(update_available=False, current_version=current_version, error=str(e))

    tag_name = data.get("tag_name", "")
    html_url = data.get("html_url") or RELEASES_PAGE_URL
    if not tag_name:
        return UpdateCheckResult(update_available=False, current_version=current_version, error="No tag_name in response")

    return UpdateCheckResult(
        update_available=is_newer(tag_name, current_version),
        current_version=current_version,
        latest_version=tag_name.lstrip("vV"),
        url=html_url,
    )
