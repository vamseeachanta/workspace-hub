"""
Conversion-quality test module for the llm-wiki html_to_markdown() surface.

Structural tests (#1-16) + parametrized tests (120 = 6 dims × 20 topics).
Floor-occupancy gate is enforced by pytest_sessionfinish in conftest.py, not here.

v6 notes:
- No __init__.py in markdown_qa/ — bare sibling imports resolve via pytest rootdir.
- Oracle .md files use HTML-comment provenance metadata; test #14 proves no
  metadata line matches the heading regex.
- test #15 lives physically in test_session_hook_regression.py but is counted
  here as a structural assertion of the conftest contract.
- test #16 cross-validates manifest fields against HTML-comment metadata.
"""

import hashlib
import importlib.util
import re
import socket
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import jsonschema
import pytest
import yaml

# ── Sibling imports (bare — no __init__.py) ───────────────────────────────────

from fixtures_sampling import (  # noqa: E402
    validate_manifest,
    write_per_topic_artifact,
    PRODUCT_QUOTAS,
    CATEGORY_QUOTAS,
    COMPLEXITY_QUOTAS,
    HARD_ENCODING_STRESS_MIN,
    TOTAL_ENTRIES,
)
from rubric_scorers import SCORERS, RUBRIC_DIMENSIONS  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────

_THIS_DIR = Path(__file__).parent
_REPO_ROOT = _THIS_DIR.resolve().parents[4]  # workspace-hub/
_ORACLE_DIR = _REPO_ROOT / "tests" / "fixtures" / "llm-wiki" / "conversion-oracle"
MANIFEST_PATH = _ORACLE_DIR / "sample-manifest.yaml"
SCHEMA_PATH = _ORACLE_DIR / "sample-manifest.schema.json"

# ── ingest_orcina hyphen-path shim ────────────────────────────────────────────

_SCRIPT_DIR = _THIS_DIR.parents[1]  # scripts/data/llm-wiki/
_INGEST_PATH = _SCRIPT_DIR / "ingest-orcina.py"

_spec = importlib.util.spec_from_file_location("ingest_orcina", _INGEST_PATH)
ingest_orcina = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("ingest_orcina", ingest_orcina)
try:
    _spec.loader.exec_module(ingest_orcina)
except Exception:
    pass  # structural tests will surface import failure via test #9

# ── Collection-safe manifest loader ──────────────────────────────────────────

def load_sample_manifest() -> list[dict]:
    """Returns [] on ANY failure so pytest collection never aborts."""
    try:
        entries = yaml.safe_load(MANIFEST_PATH.read_text())
        return entries if isinstance(entries, list) else []
    except Exception:
        return []


_MANIFEST = load_sample_manifest()

# ── Metadata keys in oracle .md HTML comments ─────────────────────────────────

_ORACLE_META_KEYS = [
    "oracle_authored_by",
    "oracle_review_method",
    "oracle_authored_at",
    "oracle_second_reviewer",
    "oracle_reviewed_at",
    "single_reviewer_timelag",
]
_META_COMMENT_RE = re.compile(r"^<!--\s+(\w+):\s+(.*?)\s+-->$")


def _parse_oracle_meta(md_text: str) -> dict[str, str]:
    """Parse HTML-comment metadata lines from the top of an oracle .md file."""
    meta: dict[str, str] = {}
    for line in md_text.splitlines():
        m = _META_COMMENT_RE.match(line)
        if m:
            meta[m.group(1)] = m.group(2)
    return meta


# ── Structural tests (#1-16) ──────────────────────────────────────────────────

def test_sample_manifest_loads():
    """#1: Manifest file parses and has exactly 20 entries."""
    entries = yaml.safe_load(MANIFEST_PATH.read_text())
    assert isinstance(entries, list), "manifest must be a YAML list"
    assert len(entries) == TOTAL_ENTRIES, (
        f"expected {TOTAL_ENTRIES} entries, got {len(entries)}"
    )


def test_sample_manifest_schema_valid():
    """#2: Every entry conforms to sample-manifest.schema.json."""
    import json
    schema = json.loads(SCHEMA_PATH.read_text())
    entries = yaml.safe_load(MANIFEST_PATH.read_text())
    jsonschema.validate(entries, schema)


def test_sample_manifest_marginal_axes():
    """#3: Product/category/complexity marginals match declared quotas."""
    errors = validate_manifest(_MANIFEST)
    axis_errors = [e for e in errors if any(
        e.startswith(k) for k in ("product[", "category[", "complexity[")
    )]
    assert not axis_errors, "\n".join(axis_errors)


def test_sample_manifest_hard_tier_encoding_stress():
    """#4: At least 2 Hard-tier entries have encoding_stress=True."""
    hard_stress = sum(
        1 for e in _MANIFEST
        if e.get("complexity") == "Hard" and e.get("encoding_stress") is True
    )
    assert hard_stress >= HARD_ENCODING_STRESS_MIN, (
        f"Hard encoding_stress count {hard_stress} < {HARD_ENCODING_STRESS_MIN}"
    )


def test_sample_manifest_fixture_files_exist():
    """#5: Every html_path and oracle_md_path resolves to a non-empty file."""
    for entry in _MANIFEST:
        slug = entry["slug"]
        for field in ("html_path", "oracle_md_path"):
            path = _REPO_ROOT / entry[field]
            assert path.exists(), f"slug={slug}: {field} not found at {path}"
            assert path.stat().st_size > 0, f"slug={slug}: {field} is empty"


def test_sample_manifest_html_sha256_matches():
    """#6: SHA-256 of each .html file equals the manifest value."""
    for entry in _MANIFEST:
        slug = entry["slug"]
        html_path = _REPO_ROOT / entry["html_path"]
        actual = hashlib.sha256(html_path.read_bytes()).hexdigest()
        assert actual == entry["html_sha256"], (
            f"slug={slug}: html_sha256 mismatch\n  expected: {entry['html_sha256']}\n  actual:   {actual}"
        )


def test_oracle_authorship_method_is_from_source():
    """#7: Every entry has oracle_review_method == 'from-source'."""
    bad = [e["slug"] for e in _MANIFEST if e.get("oracle_review_method") != "from-source"]
    assert not bad, f"entries with wrong review method: {bad}"


def test_oracle_has_second_reviewer():
    """#8: Every entry has a non-empty oracle_second_reviewer.
    Sentinel entries must have oracle_reviewed_at - oracle_authored_at >= 24h.
    """
    sentinel = "self-reviewed-with-24h-delay"
    for entry in _MANIFEST:
        slug = entry["slug"]
        reviewer = entry.get("oracle_second_reviewer", "")
        assert reviewer, f"slug={slug}: oracle_second_reviewer is empty"
        if reviewer == sentinel:
            assert entry.get("single_reviewer_timelag") is True, (
                f"slug={slug}: sentinel reviewer requires single_reviewer_timelag=true"
            )
            authored = datetime.fromisoformat(str(entry["oracle_authored_at"]).replace("Z", "+00:00"))
            reviewed = datetime.fromisoformat(str(entry["oracle_reviewed_at"]).replace("Z", "+00:00"))
            assert reviewed - authored >= timedelta(hours=24), (
                f"slug={slug}: oracle_reviewed_at - oracle_authored_at < 24h "
                f"({reviewed - authored})"
            )
        else:
            assert reviewer != entry.get("oracle_authored_by"), (
                f"slug={slug}: oracle_second_reviewer must differ from oracle_authored_by"
            )


def test_html_to_markdown_import():
    """#9: ingest_orcina.html_to_markdown importable via hyphenated-path shim."""
    assert hasattr(ingest_orcina, "html_to_markdown"), (
        "html_to_markdown not found on ingest_orcina module; check importlib shim"
    )
    assert callable(ingest_orcina.html_to_markdown)


def test_rubric_scorer_determinism():
    """#10: Every scorer returns identical float on two calls with same inputs."""
    actual = "# H1\n\nSome text. [link](https://example.com)\n\n| A | B |\n|---|---|\n| 1 | 2 |\n"
    oracle = actual
    html = "<h1>H1</h1><p>Some text. <a href='https://example.com'>link</a></p>"
    for dim, scorer in SCORERS.items():
        s1 = scorer(actual, oracle, html)
        s2 = scorer(actual, oracle, html)
        assert s1 == s2, f"scorer '{dim}' not deterministic: {s1} != {s2}"


def test_heading_preservation_detects_reordering():
    """#11: Reordering H1/H2/H3 produces a score in [0.85, 0.95] and < 1.0."""
    actual = "# H1\n\n## H2\n\n### H3\n"
    oracle = "# H1\n\n### H3\n\n## H2\n"
    score = SCORERS["heading"](actual, oracle, "")
    assert 0.85 <= score <= 0.95, f"score {score} not in [0.85, 0.95]"
    assert score < 1.0, f"score {score} should be < 1.0 (reordering penalty)"


def test_rubric_scorer_handles_empty_oracle_and_actual():
    """#12: All four quadrants on each of dims 2-5 (link/table/code/image).

    (a) both empty -> 1.0
    (b) oracle empty, actual non-empty -> 0.0 (spurious content)
    (c) oracle non-empty, actual empty -> 0.0 (missed all tokens)
    (d) both non-empty partial match -> expected ratio
    """
    for dim in ("link", "table", "code", "image"):
        scorer = SCORERS[dim]

        if dim == "link":
            both_empty = ("", "")
            actual_has = ("[a](https://x.com)", "")
            oracle_has = ("", "[a](https://x.com)")
            partial = ("[a](https://x.com) [b](https://y.com)", "[a](https://x.com) [c](https://z.com)")
            # 1 match out of 2 oracle hrefs = 0.5
            expected_partial = 0.5
        elif dim == "table":
            both_empty = ("", "")
            actual_has = ("| A |\n|---|\n| 1 |", "")
            oracle_has = ("", "| A |\n|---|\n| 1 |")
            partial = ("| A | B |\n|---|---|\n| 1 | 2 |", "| A | B |\n|---|---|\n| 1 | X |")
            # cells: A,B,---,---,1,2 vs A,B,---,---,1,X — 5 matches out of 6 oracle cells
            expected_partial = 5 / 6
        elif dim == "code":
            both_empty = ("", "")
            actual_has = ("```\ncode\n```", "")
            oracle_has = ("", "```\ncode\n```")
            partial = ("```\ncode1\n```\n\n```\ncode2\n```", "```\ncode1\n```\n\n```\ncodeX\n```")
            # 1 match out of 2 oracle blocks = 0.5
            expected_partial = 0.5
        else:  # image
            both_empty = ("", "")
            actual_has = ("![alt](img.png)", "")
            oracle_has = ("", "![alt](img.png)")
            partial = ("![alt](img.png) ![b](b.png)", "![alt](img.png) ![c](c.png)")
            # img.png matches, b.png not in oracle, c.png not in actual — 1 of 2 oracle srcs = 0.5
            expected_partial = 0.5

        assert scorer(both_empty[0], both_empty[1], "") == 1.0, (
            f"{dim}: both-empty should be 1.0"
        )
        assert scorer(actual_has[0], actual_has[1], "") == 0.0, (
            f"{dim}: oracle-empty/actual-non-empty should be 0.0"
        )
        assert scorer(oracle_has[0], oracle_has[1], "") == 0.0, (
            f"{dim}: oracle-non-empty/actual-empty should be 0.0"
        )
        actual_partial = scorer(partial[0], partial[1], "")
        assert abs(actual_partial - expected_partial) < 1e-9, (
            f"{dim}: partial match expected {expected_partial}, got {actual_partial}"
        )


def test_no_network_access():
    """#13: pytest-socket is active; live AF_INET connection raises SocketBlockedError."""
    from pytest_socket import SocketBlockedError
    with pytest.raises(SocketBlockedError):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("8.8.8.8", 53))


def test_oracle_md_files_lack_heading_regex_metadata():
    """#14 (v6 P1 #1 proof): No oracle .md heading match contains a metadata key.

    Runs the EXACT scorer heading regex over each oracle .md file's raw lines.
    For every matched heading, asserts the heading text does not contain any of
    the oracle metadata keys. Proves no oracle accidentally uses YAML-comment
    headers (# key: value) instead of HTML comments.
    """
    heading_re = re.compile(r"^(#{1,6})\s+(.*)$")
    meta_keys = set(_ORACLE_META_KEYS)

    for entry in _MANIFEST:
        path = _REPO_ROOT / entry["oracle_md_path"]
        text = path.read_text()
        for line in text.splitlines():
            m = heading_re.match(line)
            if m:
                heading_text = m.group(2)
                for key in meta_keys:
                    assert key not in heading_text, (
                        f"slug={entry['slug']}: oracle .md heading '{heading_text}' "
                        f"contains metadata key '{key}'. Use HTML-comment format instead."
                    )


def test_oracle_md_provenance_matches_manifest():
    """#16 (v6 Claude r5 P2): HTML-comment metadata in each oracle .md equals manifest fields."""
    for entry in _MANIFEST:
        slug = entry["slug"]
        path = _REPO_ROOT / entry["oracle_md_path"]
        meta = _parse_oracle_meta(path.read_text())

        for key in _ORACLE_META_KEYS:
            manifest_val = entry.get(key)
            if manifest_val is None:
                continue
            # Normalize: booleans in YAML become Python bool; compare as strings.
            if isinstance(manifest_val, bool):
                manifest_str = str(manifest_val).lower()
            elif isinstance(manifest_val, datetime):
                manifest_str = manifest_val.isoformat()
            else:
                manifest_str = str(manifest_val).strip()
            html_str = meta.get(key, "").strip()
            assert manifest_str == html_str, (
                f"slug={slug}: field '{key}' mismatch\n"
                f"  manifest: {manifest_str!r}\n"
                f"  html-comment: {html_str!r}"
            )


# ── Parametrized tests (6 dims × 20 topics = 120 cases) ──────────────────────

@pytest.mark.parametrize("dim", RUBRIC_DIMENSIONS)
@pytest.mark.parametrize("entry", _MANIFEST, ids=lambda e: e["slug"])
def test_per_topic_dimension(entry, dim):
    """120-case parametrized: score each oracle entry on each rubric dimension.

    Does NOT assert a per-topic floor here; the floor-occupancy gate is enforced
    by pytest_sessionfinish in conftest.py after ALL 120 cases complete.
    The per-topic artifact written here feeds that gate.
    """
    html = (_REPO_ROOT / entry["html_path"]).read_text()
    expected_md = (_REPO_ROOT / entry["oracle_md_path"]).read_text()
    _, actual_md = ingest_orcina.html_to_markdown(html, entry["source_url"])
    score = SCORERS[dim](actual_md, expected_md, html)
    write_per_topic_artifact(entry["slug"], dim, score)
