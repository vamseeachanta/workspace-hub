"""W2-C maritime-law topical-expansion tests (#2592).

Covers the 10 new pages under ``knowledge/wikis/maritime-law/wiki/concepts/``
created by the W2-C expansion:

  - 6 doctrine-concept pages: general-average, salvage,
    limitation-of-liability, port-state-control, flag-state-jurisdiction,
    charterparties.
  - 4 IMO/ILO standards-tier pages (routed under ``concepts/`` per
    project memory ``project_wiki_standards_path_decision.md`` —
    maritime-law is OUT OF the ``wiki/standards/`` routing principle):
    marpol-73-78, solas-1974, mlc-2006, ism-code.

The standards-tier pages carry additive ``code_id`` / ``publisher`` /
``consolidated_edition`` frontmatter (NOT ``revision``: IMO/ILO instruments
are versioned by consolidated edition / amendment cutoff, not by publisher
revision; this is a maritime-law-specific schema convention NOT bound by
the #2471 calc-citation contract).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI_ROOT = REPO_ROOT / "knowledge" / "wikis" / "maritime-law" / "wiki"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"

DOCTRINE_PAGES = (
    "general-average",
    "salvage",
    "limitation-of-liability",
    "port-state-control",
    "flag-state-jurisdiction",
    "charterparties",
)

STANDARDS_TIER_PAGES = (
    "marpol-73-78",
    "solas-1974",
    "mlc-2006",
    "ism-code",
)

ALL_NEW_PAGES = DOCTRINE_PAGES + STANDARDS_TIER_PAGES

CODE_ID_RE = re.compile(r"^[a-z][a-z0-9-]+$")
INLINE_CASE_CITATION_RE = re.compile(r"\b\(\d{4}\)")  # e.g. (2002), (1997)
PUBLISHERS = {"IMO", "ILO"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(slug: str) -> str:
    p = CONCEPTS_DIR / f"{slug}.md"
    assert p.exists(), f"missing page: {p}"
    return p.read_text(encoding="utf-8")


def _split_frontmatter(text: str) -> tuple[str, str]:
    assert text.startswith("---\n"), "page must begin with YAML frontmatter delimiter"
    end = text.find("\n---\n", 4)
    assert end != -1, "frontmatter not terminated"
    return text[4:end], text[end + 5 :]


def _parse_frontmatter(text: str) -> dict[str, object]:
    """Minimal YAML-frontmatter parser sufficient for our flat schema.

    Supports scalar ``key: value`` lines and ``key:`` followed by
    ``  - item`` block-style lists. We do not depend on PyYAML to keep
    test surface tight.
    """
    fm_text, _ = _split_frontmatter(text)
    out: dict[str, object] = {}
    current_key: str | None = None
    for raw in fm_text.splitlines():
        line = raw.rstrip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("  - "):
            assert current_key is not None, "list item without preceding key"
            existing = out.setdefault(current_key, [])
            assert isinstance(existing, list)
            existing.append(line[4:].strip().strip('"').strip("'"))
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "":
            out[key] = []
            current_key = key
            continue
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            items = [v.strip().strip('"').strip("'") for v in inner.split(",") if v.strip()]
            out[key] = items
        else:
            out[key] = value.strip('"').strip("'")
        current_key = None
    return out


def _word_count(text: str) -> int:
    _, body = _split_frontmatter(text)
    # Strip code fences and markdown link syntax for a fair word count.
    body_no_code = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    return len(body_no_code.split())


# ---------------------------------------------------------------------------
# Existence + routing
# ---------------------------------------------------------------------------


def test_all_ten_pages_exist():
    for slug in ALL_NEW_PAGES:
        p = CONCEPTS_DIR / f"{slug}.md"
        assert p.exists(), f"expected page: {p}"


def test_no_standards_directory_created():
    """maritime-law is OUT OF the wiki/standards/ routing principle.

    Per project memory ``project_wiki_standards_path_decision.md`` and
    umbrella sanction #2615, the routing principle was extended only to
    {marine-engineering, engineering, naval-architecture,
    engineering-standards, asset-management}. maritime-law remains an
    Open Question — this test fails closed if any page is routed under
    ``wiki/standards/``.
    """
    standards_dir = WIKI_ROOT / "standards"
    if standards_dir.exists():
        offenders = sorted(p.name for p in standards_dir.glob("*.md"))
        pytest.fail(
            "wiki/standards/ directory must not exist for maritime-law "
            f"(routing-principle out-of-scope); found pages: {offenders}"
        )


def test_all_standards_tier_pages_under_concepts():
    """Belt-and-braces: every standards-tier page is under concepts/."""
    for slug in STANDARDS_TIER_PAGES:
        assert (CONCEPTS_DIR / f"{slug}.md").exists(), (
            f"standards-tier page {slug}.md must live under wiki/concepts/"
        )


# ---------------------------------------------------------------------------
# Frontmatter — required fields per CLAUDE.md schema
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("slug", ALL_NEW_PAGES)
def test_frontmatter_required_fields(slug: str):
    fm = _parse_frontmatter(_read(slug))
    for required in ("title", "tags", "added", "last_updated"):
        assert required in fm, f"{slug}: missing required field {required}"
        assert fm[required], f"{slug}: required field {required} is empty"
    assert fm["added"] == "2026-05-02", f"{slug}: added must be 2026-05-02"
    assert fm["last_updated"] == "2026-05-02", (
        f"{slug}: last_updated must be 2026-05-02"
    )


# ---------------------------------------------------------------------------
# Standards-tier additive frontmatter (code_id / publisher /
# consolidated_edition — NOT revision)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("slug", STANDARDS_TIER_PAGES)
def test_standards_tier_frontmatter_fields(slug: str):
    fm = _parse_frontmatter(_read(slug))
    for required in ("code_id", "publisher", "consolidated_edition"):
        assert required in fm, f"{slug}: missing standards-tier field {required}"
        assert fm[required], f"{slug}: standards-tier field {required} is empty"
    assert "revision" not in fm, (
        f"{slug}: must use consolidated_edition (NOT revision) per "
        "maritime-law schema convention"
    )


@pytest.mark.parametrize("slug", STANDARDS_TIER_PAGES)
def test_code_id_canonical_lowercase(slug: str):
    fm = _parse_frontmatter(_read(slug))
    code_id = fm["code_id"]
    assert isinstance(code_id, str)
    assert CODE_ID_RE.match(code_id), (
        f"{slug}: code_id {code_id!r} must match ^[a-z][a-z0-9-]+$"
    )
    assert code_id == slug, (
        f"{slug}: code_id ({code_id}) must match the page slug for canonical addressability"
    )


@pytest.mark.parametrize("slug", STANDARDS_TIER_PAGES)
def test_publisher_is_imo_or_ilo(slug: str):
    fm = _parse_frontmatter(_read(slug))
    assert fm["publisher"] in PUBLISHERS, (
        f"{slug}: publisher must be one of {PUBLISHERS}"
    )


def test_mlc_publisher_is_ilo():
    """MLC 2006 is ILO (not IMO) — distinct cadence via Special Tripartite Committee."""
    fm = _parse_frontmatter(_read("mlc-2006"))
    assert fm["publisher"] == "ILO"


def test_ism_embedded_in_solas():
    """ISM Code rides on the SOLAS Ch. IX amendment chain."""
    fm = _parse_frontmatter(_read("ism-code"))
    assert fm.get("embedded_in") == "solas-1974", (
        "ism-code must declare embedded_in: solas-1974"
    )


# ---------------------------------------------------------------------------
# see_also resolves
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("slug", ALL_NEW_PAGES)
def test_frontmatter_see_also_min_two(slug: str):
    fm = _parse_frontmatter(_read(slug))
    see_also = fm.get("see_also") or []
    assert isinstance(see_also, list)
    assert len(see_also) >= 2, (
        f"{slug}: see_also must list at least 2 entries (got {len(see_also)})"
    )


@pytest.mark.parametrize("slug", ALL_NEW_PAGES)
def test_see_also_paths_resolve(slug: str):
    fm = _parse_frontmatter(_read(slug))
    see_also = fm.get("see_also") or []
    assert isinstance(see_also, list)
    page_dir = CONCEPTS_DIR
    for entry in see_also:
        target = (page_dir / entry).resolve()
        assert target.exists(), (
            f"{slug}: see_also entry {entry!r} does not resolve to an existing file ({target})"
        )


# ---------------------------------------------------------------------------
# Doctrine pages: ≥1 case-link or convention-link or inline (YYYY) citation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("slug", DOCTRINE_PAGES)
def test_doctrine_page_has_case_or_convention_ref(slug: str):
    text = _read(slug)
    _, body = _split_frontmatter(text)
    has_entity_link = "../entities/" in body
    has_convention_link = bool(re.search(r"\./(?:clc-1992|opa-90|llmc-1996|bunker-convention-2001|hns-convention-2010|athens-convention-2002)\.md", body))
    has_inline_citation = bool(INLINE_CASE_CITATION_RE.search(body))
    assert has_entity_link or has_convention_link or has_inline_citation, (
        f"{slug}: must contain at least one entity link, convention link, or inline (YYYY) citation"
    )


# ---------------------------------------------------------------------------
# Word-count discipline (≤400 per page)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("slug", ALL_NEW_PAGES)
def test_word_count_under_400(slug: str):
    wc = _word_count(_read(slug))
    assert wc <= 400, f"{slug}: word count {wc} exceeds 400-word ceiling"


# ---------------------------------------------------------------------------
# Citation-form lint: no quoted convention prose >=10 words without nearby citation
# ---------------------------------------------------------------------------


_CITATION_TOKENS = (
    "http://",
    "https://",
    "Article ",
    "Art. ",
    "Chapter ",
    "Ch. ",
    "Annex ",
    "Rule ",
    "Resolution ",
    "Regulation ",
    "Reg. ",
    "MEPC ",
    "MSC ",
    "STC ",
    "U.S.C.",
    "Lloyd's Rep",
    "AC ",
    "imo.org",
    "ilo.org",
    "comitemaritime.org",
    "parismou.org",
    "tokyo-mou.org",
    "bimco.org",
    "(20",
    "(19",
)


def _citation_within(lines: list[str], idx: int, window: int = 2) -> bool:
    start = max(0, idx - window)
    end = min(len(lines), idx + window + 1)
    chunk = "\n".join(lines[start:end])
    return any(tok in chunk for tok in _CITATION_TOKENS)


@pytest.mark.parametrize("slug", STANDARDS_TIER_PAGES)
def test_no_quoted_convention_prose_without_citation(slug: str):
    text = _read(slug)
    _, body = _split_frontmatter(text)
    lines = body.splitlines()
    failures: list[str] = []
    for i, line in enumerate(lines):
        # blockquote ≥10 words
        if line.lstrip().startswith(">"):
            content = line.lstrip()[1:].strip()
            if len(content.split()) >= 10 and not _citation_within(lines, i):
                failures.append(f"line {i+1}: blockquote with no nearby citation: {content[:80]!r}")
        # straight-double-quoted span ≥10 words on the same line
        for m in re.finditer(r'"([^"\n]{40,})"', line):
            inner = m.group(1)
            if len(inner.split()) >= 10 and not _citation_within(lines, i):
                failures.append(f"line {i+1}: quoted span with no nearby citation: {inner[:80]!r}")
    if failures:
        pytest.fail(f"{slug}: {len(failures)} unmatched quoted prose entries:\n" + "\n".join(failures))


# ---------------------------------------------------------------------------
# Index + log
# ---------------------------------------------------------------------------


def test_index_links_resolve():
    index_path = WIKI_ROOT / "index.md"
    text = index_path.read_text(encoding="utf-8")
    # Match standard markdown links: [text](path) — but skip [[wikilink]] markers.
    # Strip out [[...]](path) wikilink-style which we DO want to resolve to the path part.
    link_re = re.compile(r"\]\(([^)]+\.md)\)")
    failures: list[str] = []
    for m in link_re.finditer(text):
        rel = m.group(1)
        target = (index_path.parent / rel).resolve()
        if not target.exists():
            failures.append(f"broken link: {rel} -> {target}")
    assert not failures, "\n".join(failures)


def test_index_page_count_matches_on_disk():
    index_path = WIKI_ROOT / "index.md"
    fm = _parse_frontmatter(index_path.read_text(encoding="utf-8"))
    on_disk = sorted(p for p in WIKI_ROOT.rglob("*.md"))
    expected = len(on_disk)
    actual = int(str(fm["page_count"]))
    assert actual == expected, (
        f"index.md page_count={actual} but on-disk markdown count={expected}; pages={[p.name for p in on_disk]}"
    )


def test_index_has_standards_tier_section():
    index_path = WIKI_ROOT / "index.md"
    text = index_path.read_text(encoding="utf-8")
    assert "## Standards-tier" in text, (
        "index.md must contain a '## Standards-tier' section listing the IMO/ILO pages"
    )
    for slug in STANDARDS_TIER_PAGES:
        assert f"concepts/{slug}.md" in text, (
            f"index.md Standards-tier section is missing concepts/{slug}.md"
        )


def test_log_entry_appended():
    log_path = WIKI_ROOT / "log.md"
    text = log_path.read_text(encoding="utf-8")
    assert "[2026-05-02] expand | maritime-law W2-C" in text, (
        "log.md must contain the W2-C expansion entry"
    )


# ---------------------------------------------------------------------------
# No PDF-extraction artifacts
# ---------------------------------------------------------------------------


_PDF_ARTIFACT_PATTERNS = (
    re.compile(r"Page \d+ of \d+", re.IGNORECASE),
    re.compile(r"\bcid:\d+\b"),  # PDF unmapped-glyph artifact
)


@pytest.mark.parametrize("slug", ALL_NEW_PAGES)
def test_no_pdf_extraction_markers(slug: str):
    text = _read(slug)
    for pat in _PDF_ARTIFACT_PATTERNS:
        assert not pat.search(text), (
            f"{slug}: PDF-extraction marker {pat.pattern!r} present (forbidden per #2482)"
        )
