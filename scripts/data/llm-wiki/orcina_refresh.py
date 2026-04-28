"""Refresh-mode helpers for Orcina llm-wiki ingestion."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import socket
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError

HEADERS = {"User-Agent": "workspace-hub-llm-wiki/1.0 (documentation indexing)"}
FETCH_TIMEOUT_S = 30
HEAD_TIMEOUT_S = 15

log = logging.getLogger(__name__)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_conditional(url: str, cached_meta: dict | None = None) -> tuple[str, dict, bytes | None]:
    """Fetch a URL with conditional headers, returning changed/unchanged state."""
    headers = dict(HEADERS)
    cached_meta = cached_meta or {}
    if cached_meta.get("last_modified"):
        headers["If-Modified-Since"] = cached_meta["last_modified"]
    if cached_meta.get("etag"):
        headers["If-None-Match"] = cached_meta["etag"]

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_S) as resp:
            body = resp.read()
            new_meta = {
                "last_modified": resp.headers.get("Last-Modified"),
                "etag": resp.headers.get("ETag"),
                "content_hash": sha256_hex(body),
            }
    except HTTPError as exc:
        if exc.code == 304:
            return "unchanged", dict(cached_meta), None
        raise

    if cached_meta and new_meta["content_hash"] == cached_meta.get("content_hash"):
        return "unchanged", new_meta, body
    return "changed", new_meta, body


def head_pdf(url: str) -> dict[str, str | None] | None:
    """Return PDF metadata from HEAD, or None on any expected network failure."""
    req = urllib.request.Request(url, headers=HEADERS, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=HEAD_TIMEOUT_S) as resp:
            return {
                "last_modified": resp.headers.get("Last-Modified"),
                "content_length": resp.headers.get("Content-Length"),
            }
    except (HTTPError, URLError, socket.timeout, OSError) as exc:
        log.warning("head_pdf failed for %s: %s; falling back to download", url, exc)
        return None


def atomic_write_text(path: Path, text: str) -> None:
    """Atomically write UTF-8 text using a same-directory temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
            tmp.write(text)
            tmp_name = tmp.name
        os.replace(tmp_name, path)
    finally:
        if tmp_name and os.path.exists(tmp_name):
            try:
                os.unlink(tmp_name)
            except OSError:
                pass


def atomic_write_json(path: Path, data: dict) -> None:
    atomic_write_text(path, json.dumps(data, indent=2))


def safe_get_papers_entry(stored_meta: dict, url: str) -> dict | None:
    val = stored_meta.get(url)
    if not isinstance(val, dict):
        return None
    entry = val.get("entry")
    if not isinstance(entry, dict) or not entry.get("file"):
        return None
    return entry


def changelog_path(wiki_root: Path, version_label: str, now: datetime | None = None) -> Path:
    now = now or datetime.now(timezone.utc)
    base = wiki_root / "changelog" / f"{now.date().isoformat()}-{version_label}.md"
    if not base.exists():
        return base
    return base.with_name(f"{base.stem}-{now.strftime('T%H%M%S')}.md")


def has_changes(diffs: dict) -> bool:
    if diffs.get("version_bump"):
        return True
    for surface in ("supplementary", "papers"):
        changes = diffs.get(surface, {})
        if any(changes.get(kind) for kind in ("added", "removed", "modified")):
            return True
    for changes in diffs.get("product_topics", {}).values():
        if any(changes.get(kind) for kind in ("added", "removed", "modified")):
            return True
    return False


def render_changelog(diffs: dict) -> str:
    lines = ["# Orcina llm-wiki refresh changelog", ""]
    if diffs.get("version_bump"):
        lines.extend(["## Version changes", ""])
        for product, (old, new) in sorted(diffs["version_bump"].items()):
            lines.append(f"- {product}: {old or 'unknown'} -> {new or 'unknown'}")
        lines.append("")

    labels = {"orcaflex": "OrcaFlex", "orcawave": "OrcaWave", "orcfxapi": "OrcFxAPI"}
    product_topics = diffs.get("product_topics", {})
    if product_topics:
        lines.extend(["## Product topics", ""])
        for product, changes in product_topics.items():
            if not any(changes.get(kind) for kind in ("added", "removed", "modified")):
                continue
            lines.append(f"### Product: {labels.get(product, product)}")
            _append_change_group(lines, changes)

    for surface, title in (("supplementary", "Supplementary pages"), ("papers", "Papers")):
        changes = diffs.get(surface, {})
        if any(changes.get(kind) for kind in ("added", "removed", "modified")):
            lines.extend([f"## {title}", ""])
            _append_change_group(lines, changes)

    return "\n".join(lines).rstrip() + "\n"


def _append_change_group(lines: list[str], changes: dict) -> None:
    for kind in ("added", "removed", "modified"):
        values = changes.get(kind, [])
        if not values:
            continue
        lines.append(f"- {kind.title()} ({len(values)}):")
        for value in values:
            lines.append(f"  - {value}")
    lines.append("")


def write_changelog(wiki_root: Path, version_label: str, diffs: dict, now: datetime | None = None) -> Path:
    path = changelog_path(wiki_root, version_label, now=now)
    atomic_write_text(path, render_changelog(diffs))
    return path

