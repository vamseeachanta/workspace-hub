"""Orcina release-version parsing helpers for llm-wiki ingestion."""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

PRODUCT_LABELS = {
    "orcaflex": "OrcaFlex",
    "orcawave": "OrcaWave",
    "orcfxapi": "OrcFxAPI",
}

VERSION_RE = r"\d+(?:\.\d+)?[a-z]?(?:-beta)?"


def detect_current_version(releases_html: str) -> dict[str, str | None]:
    """Extract current Orcina product versions from releases-page HTML."""
    text = BeautifulSoup(releases_html or "", "html.parser").get_text(" ", strip=True)
    versions: dict[str, str | None] = {}
    for key, label in PRODUCT_LABELS.items():
        match = re.search(rf"\b{re.escape(label)}\b[^\d]{{0,80}}({VERSION_RE})", text, re.IGNORECASE)
        versions[key] = match.group(1) if match else None
    return versions


def load_stored_version(index_path: Path) -> str | None:
    """Return the upstream_version value from an index, tolerating old indexes."""
    if not index_path.exists():
        return None
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    version = data.get("upstream_version")
    return version if isinstance(version, str) else None


def diff_versions(stored: dict[str, str | None], current: dict[str, str | None]) -> dict[str, tuple[str | None, str | None]]:
    """Return product keys whose stored and current version values differ."""
    return {
        key: (stored.get(key), current.get(key))
        for key in current
        if stored.get(key) != current.get(key)
    }

