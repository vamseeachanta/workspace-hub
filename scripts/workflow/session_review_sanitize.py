# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Sanitization gate for published session-review pages (#3298).

workspace-hub GitHub Pages is PUBLIC. A session-review page must never carry
client identifiers, absolute host paths, IPs, or machine hostnames. This module
is the fail-closed gate: `sanitize_*` scrubs known-bad tokens, `assert_clean`
raises if any denied client pattern survives.

Design split (so the Pages builder stays stdlib-only): sanitization runs at
GENERATION time here (pyyaml available via `uv`); `scripts/build_pages.py` only
copies the already-sanitized committed HTML. The deny-list is read from the
repo-root `.legal-deny-list.yaml` (same source as `legal-sanity-scan.sh`).

The core scrub/verify functions take an explicit `patterns` list so they are
pure and yaml-free for testing; only `load_deny_patterns` touches yaml.
"""
from __future__ import annotations

import re
from pathlib import Path

REDACTION = "[redacted]"

# Absolute host paths (home, mnt, Users, tmp, root, var, opt prefixes, or a
# Windows drive root) collapse to [path].
_ABS_PATH_RE = re.compile(r"(?:/(?:home|mnt|Users|tmp|root|var|opt)/[\w./\-]+|[A-Za-z]:\\[\w\\.\-]+)")
# IPv4 → [ip] (skips version-like x.y.z by requiring 4 octets).
_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
# Known internal machine hostnames → [host].
_HOST_RE = re.compile(r"\b(?:ace-linux-\d+|ace-win-\d+|dev-primary|dev-secondary|licensed-win-\d+)\b")


class SanitizationError(RuntimeError):
    """Raised when a denied client pattern survives into public output."""


def load_deny_patterns(deny_list_path: str | Path) -> list[tuple[str, bool]]:
    """Return [(pattern, case_sensitive), ...] from the legal deny-list YAML.

    Reads the client-identifier sections. Tolerates missing/empty sections so a
    deny-list without client_references still loads (returns []).
    """
    import yaml  # local import keeps the pure functions yaml-free

    data = yaml.safe_load(Path(deny_list_path).read_text(encoding="utf-8")) or {}
    out: list[tuple[str, bool]] = []
    for section in ("client_references", "proprietary_tools", "client_infrastructure"):
        for entry in data.get(section) or []:
            pat = (entry or {}).get("pattern")
            if pat:
                out.append((str(pat), bool((entry or {}).get("case_sensitive", False))))
    return out


def _pattern_re(pattern: str, case_sensitive: bool) -> re.Pattern[str]:
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(re.escape(pattern), flags)


def sanitize_text(text: str, patterns: list[tuple[str, bool]]) -> str:
    """Redact denied client patterns and scrub abs paths / IPs / hostnames."""
    out = text
    for pattern, cs in patterns:
        out = _pattern_re(pattern, cs).sub(REDACTION, out)
    out = _ABS_PATH_RE.sub("[path]", out)
    out = _IPV4_RE.sub("[ip]", out)
    out = _HOST_RE.sub("[host]", out)
    return out


def find_violations(text: str, patterns: list[tuple[str, bool]]) -> list[str]:
    """Return denied client patterns still present in `text` (empty == clean).

    Only client patterns are violations (fail-closed surface). Abs paths / IPs /
    hostnames are best-effort scrubbed but not hard-blocked, matching the
    deny-list's `block` vs `warn` split.
    """
    hits: list[str] = []
    for pattern, cs in patterns:
        if _pattern_re(pattern, cs).search(text):
            hits.append(pattern)
    return hits


def assert_clean(text: str, patterns: list[tuple[str, bool]]) -> None:
    """Raise SanitizationError if any denied client pattern survives."""
    hits = find_violations(text, patterns)
    if hits:
        raise SanitizationError(
            "denied client pattern(s) present in public output: " + ", ".join(sorted(set(hits)))
        )


def sanitize_payload(payload, patterns: list[tuple[str, bool]]):
    """Deep-sanitize every string value in a dict/list/scalar structure."""
    if isinstance(payload, str):
        return sanitize_text(payload, patterns)
    if isinstance(payload, dict):
        return {k: sanitize_payload(v, patterns) for k, v in payload.items()}
    if isinstance(payload, (list, tuple)):
        return [sanitize_payload(v, patterns) for v in payload]
    return payload
