"""Audit-time tests for data/document-index/online-resource-registry.yaml.

Implements the W2-D acceptance-criterion test set per
``docs/plans/2026-05-02-issue-2593-llm-wiki-W2D-online-resource-registry-refresh.md``.

Tests in this file are split by polarity:

- **Default-run (no marker)**: schema, drift, and well-formedness checks that
  read static yaml only. Safe in default CI; no network.
- **``@pytest.mark.audit``-marked**: live-network URL spot-check. Excluded from
  default ``pytest`` runs (see ``-m "not audit"`` in plan AC). Runs only on
  explicit opt-in via ``pytest -m audit``.

Per W2-D MAJOR-2 review fix: the audit marker is registered in
``pyproject.toml`` so unknown-marker warnings don't surface.

Per W2-D MAJOR-1 review fix: this test reads the existing ``last_checked``
field; it does NOT introduce a new ``last_verified`` field.
"""

from __future__ import annotations

import re
import urllib.parse
from datetime import date
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "data" / "document-index" / "online-resource-registry.yaml"
PATCH_PATH = REPO_ROOT / "data" / "document-index" / "online-resource-registry-patch-2026-05-03.yaml"
AUDIT_REPORT_PATH = REPO_ROOT / "docs" / "audits" / "2026-05-03-online-resource-registry-refresh.md"

# Permissive revision-string grammar per W2-D risk note.
# Accepts: "YYYY-MM", "YYYY-MM-DD", "Nth Edition", "(R\d{4})", ":YYYY", or
# composite strings containing any of the above.
REVISION_PATTERNS = (
    re.compile(r"\b\d{4}-\d{2}(?:-\d{2})?\b"),         # 2021-08 or 2021-08-15
    re.compile(r"\b\d+(?:st|nd|rd|th)\s+Edition\b"),    # 22nd Edition
    re.compile(r"\(R\d{4}\)"),                          # (R2025)
    re.compile(r":\d{4}\b"),                            # :2013
    re.compile(r"\bMEPC[\s.]*\d+", re.IGNORECASE),      # MEPC 81 / MEPC.391(81)
    re.compile(r"\bAdopted\s+\d{4}-\d{2}", re.IGNORECASE),  # Adopted 2025-03
    re.compile(r"\bcatalog\b", re.IGNORECASE),          # 2024 catalog / 2025 catalog
    re.compile(r"\bcycle\b", re.IGNORECASE),            # 2024 conference cycle
    re.compile(r"\d{4}\s+announced", re.IGNORECASE),    # 2025 announced
    re.compile(r"\bentry-into-force\b", re.IGNORECASE), # 2026-03-01 entry-into-force
    re.compile(r"\baudit-recheck\b", re.IGNORECASE),    # 2026-04 audit-recheck
)

PATCH_REQUIRED_FIELDS = ("id", "url", "name", "type", "domain", "last_checked", "revision")
SNAPSHOT_DATE = date(2026, 5, 3)
LEGACY_THRESHOLD_YEARS = 5


# ---------------------------------------------------------------------------
# Loaders (memoized)
# ---------------------------------------------------------------------------


def _load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        pytest.skip(f"Registry not found: {REGISTRY_PATH}")
    with REGISTRY_PATH.open() as f:
        return yaml.safe_load(f)


def _load_patch() -> dict:
    if not PATCH_PATH.exists():
        pytest.skip(f"Patch sidecar not found: {PATCH_PATH}")
    with PATCH_PATH.open() as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Default-run tests (static yaml only — no network, no audit marker)
# ---------------------------------------------------------------------------


def test_registry_yaml_loads() -> None:
    """Registry parses as YAML and exposes the `entries` list."""
    registry = _load_registry()
    assert isinstance(registry, dict)
    assert "entries" in registry
    assert isinstance(registry["entries"], list)
    assert len(registry["entries"]) > 0


def test_revision_field_zero_count_today() -> None:
    """Documents the schema gap: zero `revision` fields on the live registry today.

    W2-D Section 1 finding. When the patch lands and the registry adopts the
    `revision` field, this test will start failing — at which point it should
    flip polarity to ``> 0``. The current assertion is the audit baseline.
    """
    registry = _load_registry()
    revision_count = sum(1 for e in registry["entries"] if "revision" in e)
    assert revision_count == 0, (
        f"Expected 0 revision fields per W2-D audit baseline; got {revision_count}. "
        "Patch may have landed; flip this assertion to ``> 0`` and update the audit baseline."
    )


def test_no_duplicate_ids() -> None:
    """Every registry entry id is unique."""
    registry = _load_registry()
    ids = [e.get("id") for e in registry["entries"]]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"Duplicate ids found: {sorted(duplicates)}"


def test_every_url_well_formed() -> None:
    """Every `url` parses with scheme in {http, https}."""
    registry = _load_registry()
    bad = []
    for entry in registry["entries"]:
        url = entry.get("url", "")
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            bad.append((entry.get("id"), url))
    assert not bad, f"Malformed URLs: {bad[:5]}{'...' if len(bad) > 5 else ''}"


def test_frontmatter_total_entries_drift_documented() -> None:
    """Audit-baseline assertion: frontmatter says 247, body has 248 (1-entry drift).

    Per W2-D plan §m3: this drift is recorded as an audit finding, not fixed by
    this plan. When `scripts/data/build-online-resource-registry.py` is re-run
    and regenerates the frontmatter, both numbers will equalize and this test
    should be promoted to ``==`` polarity.
    """
    registry = _load_registry()
    declared = registry.get("total_entries")
    actual = len(registry["entries"])
    assert (declared, actual) == (247, 248), (
        f"Expected baseline drift (247, 248); got ({declared}, {actual}). "
        "Either the registry was regenerated (good — flip this to ``==``) or a "
        "new entry landed (audit must be re-run)."
    )


def test_proposed_patch_loads() -> None:
    """Patch sidecar parses and has the expected metadata + entries."""
    patch = _load_patch()
    assert "patch_metadata" in patch
    assert "entries" in patch
    assert isinstance(patch["entries"], list)
    assert 0 < len(patch["entries"]) <= 20, (
        "Plan caps the patch at ≤20 entries; got " + str(len(patch["entries"]))
    )
    assert patch["patch_metadata"]["entry_count"] == len(patch["entries"]), (
        "Metadata entry_count must match len(entries)"
    )
    assert patch["patch_metadata"]["applied"] is False, (
        "Patch must declare applied=false; W2-D does not modify the live registry"
    )


def test_proposed_patch_required_fields() -> None:
    """Every patch entry has the required fields including `revision`."""
    patch = _load_patch()
    missing = []
    for entry in patch["entries"]:
        for field in PATCH_REQUIRED_FIELDS:
            if field not in entry or entry[field] in (None, ""):
                missing.append((entry.get("id"), field))
    assert not missing, f"Patch entries missing required fields: {missing}"


def test_proposed_patch_revision_parseable() -> None:
    """Every patch entry's `revision` matches one of the permissive patterns."""
    patch = _load_patch()
    bad = []
    for entry in patch["entries"]:
        revision = entry.get("revision", "")
        if not any(p.search(revision) for p in REVISION_PATTERNS):
            bad.append((entry.get("id"), revision))
    assert not bad, (
        f"Patch entries with unparseable revision strings: {bad}. "
        "Either fix the revision string or extend REVISION_PATTERNS."
    )


def test_proposed_patch_has_action_field() -> None:
    """Every patch entry declares `patch_action` ∈ {add, update}."""
    patch = _load_patch()
    bad = []
    for entry in patch["entries"]:
        action = entry.get("patch_action")
        if action not in {"add", "update"}:
            bad.append((entry.get("id"), action))
    assert not bad, f"Patch entries with bad patch_action: {bad}"


def test_proposed_patch_no_legacy_unflagged() -> None:
    """No patch entry has a revision >5 years before snapshot without `superseded_or_legacy: true`.

    Per W2-D Acceptance Criterion #5.
    """
    patch = _load_patch()
    bad = []
    year_pattern = re.compile(r"\b(\d{4})\b")
    for entry in patch["entries"]:
        revision = entry.get("revision", "")
        years = [int(y) for y in year_pattern.findall(revision)]
        if not years:
            continue
        oldest = min(years)
        # Allow strings like "MEPC 81" not to count — guarded by 4-digit year match
        if oldest < (SNAPSHOT_DATE.year - LEGACY_THRESHOLD_YEARS):
            if not entry.get("superseded_or_legacy"):
                bad.append((entry.get("id"), revision, oldest))
    assert not bad, (
        f"Legacy revisions (>{LEGACY_THRESHOLD_YEARS}yr) without superseded_or_legacy=true: {bad}"
    )


def test_audit_report_exists_and_cites_patch() -> None:
    """The audit report exists at the expected path and references the patch sidecar."""
    assert AUDIT_REPORT_PATH.exists(), f"Missing audit report: {AUDIT_REPORT_PATH}"
    text = AUDIT_REPORT_PATH.read_text()
    assert "online-resource-registry-patch-2026-05-03.yaml" in text, (
        "Audit report must reference the patch sidecar filename"
    )
    assert "#2593" in text, "Audit report must cite issue #2593"


# ---------------------------------------------------------------------------
# Audit-marked tests (opt-in via `pytest -m audit`)
# ---------------------------------------------------------------------------


@pytest.mark.audit
def test_url_resolves_sample() -> None:
    """Live-network sample of 10 entries.

    Semantics per W2-D MAJOR-2 fix:
    - 200/3xx              → pass (verified)
    - 503/timeout/DNS-fail → pytest.skip (flaky — annotate audit report)
    - 4xx                  → pytest.fail (genuinely missing)

    Sampling is deterministic (seeded by md5 of registry generated-at to keep
    runs stable across hosts). Ten URLs is enough to surface a dead one without
    being publisher-rude.
    """
    import hashlib
    import socket
    import urllib.error
    import urllib.request

    registry = _load_registry()
    seed = hashlib.md5(str(registry.get("generated", "")).encode()).hexdigest()
    seed_int = int(seed[:8], 16)

    entries = registry["entries"]
    indexed = [(i, e) for i, e in enumerate(entries) if e.get("url", "").startswith(("http://", "https://"))]
    # Deterministic stride sampling
    stride = max(1, len(indexed) // 10)
    sample_indices = [(seed_int + i * stride) % len(indexed) for i in range(10)]
    sample = [indexed[i][1] for i in sample_indices]

    failures = []
    skips = []
    socket.setdefaulttimeout(10)
    for entry in sample:
        url = entry["url"]
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (workspace-hub W2-D audit)"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                code = resp.getcode()
                if code >= 400 and code < 500:
                    failures.append((entry.get("id"), url, code))
        except urllib.error.HTTPError as exc:
            if 400 <= exc.code < 500:
                failures.append((entry.get("id"), url, exc.code))
            else:
                skips.append((entry.get("id"), url, f"HTTP {exc.code}"))
        except (urllib.error.URLError, socket.timeout, socket.gaierror, ConnectionError, OSError) as exc:
            skips.append((entry.get("id"), url, str(exc)))

    if failures:
        pytest.fail(f"4xx failures (genuine dead URLs): {failures}")
    if skips:
        pytest.skip(f"Flaky/network: {skips}")
