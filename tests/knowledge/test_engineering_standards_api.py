"""W1-A bounded summary contract — API engineering standards (#2586).

Per the approved plan
``docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md``,
this test enforces:

- Each of the ten priority API code wiki pages exists at the prescribed
  path under ``knowledge/wikis/engineering-standards/wiki/standards/``.
- Frontmatter triple ``code_id`` / ``publisher`` / ``revision`` is present
  per the calc-citation-contract rule 2 (publisher pinned to ``API``).
- ``extraction_policy: metadata-only`` and ``raw_copy_allowed: false``
  are present (bounds enforcement against #2482 deny-list).
- The body word count stays inside ``100 < N < 500`` (W1-A MINOR-5
  tightening; bare-minimum scope/why/where/cross-refs fits well below 500).
- The body's top-level ``##`` headings are a subset of the four allowed
  structural sections — no ``Clauses``, ``Formulas``, ``Tables``,
  ``Excerpt``, etc.
- A narrowly-scoped denylist of API publication front-matter / cover-page
  phrases does not appear in the body (no raw-PDF text bleed-through).
- The wiki index lists every one of the ten new pages.
- For pages whose ``revision`` is pinned to a real edition (not the
  ``public-metadata-required-before-citation-use`` placeholder), a
  ``Citation`` constructor and a ``validate_citation`` resolver call both
  succeed against the live page.

The test parametrizes over the ten ``EXPECTED_PAGES``.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
STANDARDS_DIR = (
    REPO_ROOT / "knowledge" / "wikis" / "engineering-standards" / "wiki" / "standards"
)
INDEX_PATH = (
    REPO_ROOT / "knowledge" / "wikis" / "engineering-standards" / "wiki" / "index.md"
)


# (code_id, filename) — code_id MUST equal filename stem (kebab-case).
EXPECTED_PAGES: tuple[tuple[str, str], ...] = (
    ("api-rp-2a-wsd", "api-rp-2a-wsd.md"),
    ("api-std-2rd", "api-std-2rd.md"),
    ("api-rp-2sk", "api-rp-2sk.md"),
    ("api-rp-2geo", "api-rp-2geo.md"),
    ("api-rp-2met", "api-rp-2met.md"),
    ("api-rp-16q", "api-rp-16q.md"),
    ("api-rp-17b", "api-rp-17b.md"),
    ("api-spec-17j", "api-spec-17j.md"),
    ("api-spec-5l", "api-spec-5l.md"),
    ("api-rp-1111", "api-rp-1111.md"),
)


# Allowed body section headings (positive-shape constraint, plan TDD row 8).
ALLOWED_SECTIONS = frozenset(
    {
        "Scope",
        "Why this page exists",
        "Where to find the full text",
        "Cross-references",
    }
)


# Narrow API-publication cover/copyright telltales. These would only appear
# in a wiki page if a raw cover-page or copyright-page block was pasted
# verbatim. The standard's title and code identifier are deliberately
# excluded (the title is allowed; the identifier is required).
RAW_TELLTALE_PHRASES: tuple[str, ...] = (
    "American Petroleum Institute",
    "1220 L Street, NW",
    "Washington, DC 20005",
    "Reproduction or translation of any part",
    "All rights reserved.",
    "API publications are reviewed",
    "API does not represent",
    "Information concerning safety and health risks",
    "this material set forth herein",
    "API standards committee",
)


# Sentinel for stub-only pages whose revision can't be pinned yet.
STUB_REVISION = "public-metadata-required-before-citation-use"


def _load_page(filename: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_text) for a standards page."""
    path = STANDARDS_DIR / filename
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{filename}: must begin with YAML frontmatter"
    parts = text.split("---\n", 2)
    assert len(parts) == 3, f"{filename}: frontmatter must be closed with '---'"
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    return fm, body


def _top_level_headings(body: str) -> list[str]:
    out = []
    for line in body.splitlines():
        if line.startswith("## "):
            out.append(line[3:].strip())
    return out


@pytest.mark.parametrize(("code_id", "filename"), EXPECTED_PAGES)
def test_page_exists(code_id: str, filename: str) -> None:
    path = STANDARDS_DIR / filename
    assert path.is_file(), f"missing standards page: {path.relative_to(REPO_ROOT)}"


@pytest.mark.parametrize(("code_id", "filename"), EXPECTED_PAGES)
def test_frontmatter_has_code_id(code_id: str, filename: str) -> None:
    fm, _ = _load_page(filename)
    actual = fm.get("code_id")
    assert actual == code_id, (
        f"{filename}: code_id must equal filename stem; got {actual!r}, expected {code_id!r}"
    )
    # kebab-case
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", actual or ""), (
        f"{filename}: code_id must be kebab-case; got {actual!r}"
    )


@pytest.mark.parametrize(("code_id", "filename"), EXPECTED_PAGES)
def test_frontmatter_has_publisher_api(code_id: str, filename: str) -> None:
    fm, _ = _load_page(filename)
    assert fm.get("publisher") == "API", (
        f"{filename}: publisher must be exactly 'API'; got {fm.get('publisher')!r}"
    )


@pytest.mark.parametrize(("code_id", "filename"), EXPECTED_PAGES)
def test_frontmatter_has_revision(code_id: str, filename: str) -> None:
    fm, _ = _load_page(filename)
    revision = fm.get("revision")
    assert isinstance(revision, str) and revision.strip(), (
        f"{filename}: revision must be a non-empty string per calc-citation-contract"
    )


@pytest.mark.parametrize(("code_id", "filename"), EXPECTED_PAGES)
def test_frontmatter_has_extraction_policy_metadata_only(
    code_id: str, filename: str
) -> None:
    fm, _ = _load_page(filename)
    assert fm.get("extraction_policy") == "metadata-only", (
        f"{filename}: extraction_policy must be 'metadata-only'"
    )
    assert fm.get("raw_copy_allowed") is False, (
        f"{filename}: raw_copy_allowed must be False"
    )


@pytest.mark.parametrize(("code_id", "filename"), EXPECTED_PAGES)
def test_no_raw_pdf_text_bleed_through(code_id: str, filename: str) -> None:
    _, body = _load_page(filename)
    leaks = [phrase for phrase in RAW_TELLTALE_PHRASES if phrase in body]
    assert leaks == [], (
        f"{filename}: contains verbatim API publication front-matter phrases that would "
        f"breach the bounded-preview boundary: {leaks!r}"
    )


@pytest.mark.parametrize(("code_id", "filename"), EXPECTED_PAGES)
def test_body_word_count_bounded(code_id: str, filename: str) -> None:
    _, body = _load_page(filename)
    word_count = len(body.split())
    assert 100 < word_count < 500, (
        f"{filename}: body has {word_count} words; bounded-preview budget is "
        "100 < N < 500 (W1-A MINOR-5 tightening)"
    )


@pytest.mark.parametrize(("code_id", "filename"), EXPECTED_PAGES)
def test_body_structure_is_whitelisted_only(code_id: str, filename: str) -> None:
    _, body = _load_page(filename)
    headings = set(_top_level_headings(body))
    extra = headings - ALLOWED_SECTIONS
    assert not extra, (
        f"{filename}: body contains disallowed top-level sections {sorted(extra)!r}; "
        f"allowed set is {sorted(ALLOWED_SECTIONS)!r}"
    )


@pytest.mark.parametrize(("code_id", "filename"), EXPECTED_PAGES)
def test_links_only_pointer_to_mnt_ace(code_id: str, filename: str) -> None:
    _, body = _load_page(filename)
    assert "/mnt/ace/O&G-Standards/API/" in body, (
        f"{filename}: body must include a /mnt/ace/O&G-Standards/API/ pointer in "
        "the 'Where to find' section"
    )


@pytest.mark.parametrize(("code_id", "filename"), EXPECTED_PAGES)
def test_citation_schema_resolvable(code_id: str, filename: str) -> None:
    """Downstream-resolution check: pinned-revision pages only.

    Pages whose revision is the stub sentinel are skipped per plan
    Acceptance Criteria.
    """
    fm, _ = _load_page(filename)
    revision = fm.get("revision", "")
    if revision == STUB_REVISION:
        pytest.skip(f"{filename}: stub-only revision pending publisher confirmation")

    # Import here so the test file remains importable even if the
    # digitalmodel package layout shifts; the resolver target is verified
    # at acceptance time per the plan.
    import sys

    digitalmodel_src = REPO_ROOT / "digitalmodel" / "src"
    if str(digitalmodel_src) not in sys.path:
        sys.path.insert(0, str(digitalmodel_src))

    from digitalmodel.citations.schema import (  # type: ignore[import-not-found]
        Citation,
        validate_citation,
    )

    wiki_path = (
        f"knowledge/wikis/engineering-standards/wiki/standards/{filename}"
    )
    citation = Citation(
        code_id=code_id,
        publisher="API",
        revision=revision,
        section="placeholder",
        wiki_path=wiki_path,
    )
    # Should not raise.
    validate_citation(citation, repo_root=REPO_ROOT)


@pytest.mark.parametrize(("code_id", "filename"), EXPECTED_PAGES)
def test_index_lists_all_ten(code_id: str, filename: str) -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")
    expected_link = f"standards/{filename}"
    assert expected_link in text, (
        f"index.md: missing link to {expected_link} (page {code_id})"
    )
