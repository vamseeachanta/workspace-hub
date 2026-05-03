"""Bounded-summary contract test for the W2-A DNV engineering-standards pages.

Issue trail:
- Plan: docs/plans/2026-05-02-issue-2590-llm-wiki-W2A-engineering-standards-dnv.md
- Citation contract: .claude/rules/calc-citation-contract.md
- Sibling pattern: tests/knowledge/test_ocimf_tandem_no_raw_pdf_text.py (#2227 closure)
- Vendor-derivative governance: #2482

Each of the 10 W2-A pages MUST:
1. Exist at the prescribed path under wiki/standards/.
2. Carry frontmatter with `code_id` (lowercase-kebab, equal to filename stem),
   `publisher: DNV`, populated `revision`, `extraction_policy: metadata-only`,
   `raw_copy_allowed: false`.
3. Carry only the four allowed top-level sections: Scope, Why this page exists,
   Where to find the full text, Cross-references.
4. Be word-bounded: 100 < N < 500 (matches W1-A strict bounds).
5. Avoid the DNV-specific raw-text denylist (cover/copyright phrases).
6. Carry a /mnt/ace/O&G-Standards/DNV/ pointer (links-only).

The legacy_code_id bridge test enforces that ONLY `dnv-st-f101.md` carries
`legacy_code_id: dnv-os-f101` (the OS->ST 2021 rebrand pair).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
STANDARDS_DIR = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/standards"

EXPECTED_PAGES = (
    "dnv-st-f101",
    "dnv-rp-c203",
    "dnv-rp-c205",
    "dnv-rp-b401",
    "dnv-os-e301",
    "dnv-os-f201",
    "dnv-rp-f101",
    "dnv-rp-f105",
    "dnv-rp-f109",
    "dnv-rp-h103",
)

# DNV cover/copyright phrases that would only appear if raw PDF text bled
# through. Narrowly scoped; does NOT overlap OCIMF or API denylists.
RAW_TELLTALE_PHRASES = (
    "Det Norske Veritas AS",
    "DNV-Veritasveien",
    "Veritasveien 1",
    "1322 Høvik, Norway",
    "1322 Hovik, Norway",
    "© Det Norske Veritas",
    "All rights reserved",
    "Reproduction or transmission of any part",
    "DNV GL AS",
    "Copyright DNV",
    "British Library Cataloguing",
    "ISBN 978",
)

ALLOWED_SECTIONS = frozenset(
    {
        "Scope",
        "Why this page exists",
        "Where to find the full text",
        "Cross-references",
    }
)

LOWERCASE_KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DNV_REVISION_RE = re.compile(
    r"^(\d{4}(-\d{2})?|public-metadata-required-before-citation-use)$"
)


def _page_path(stem: str) -> Path:
    return STANDARDS_DIR / f"{stem}.md"


def _split_frontmatter(text: str) -> tuple[dict, str]:
    assert text.startswith("---\n"), "page must begin with YAML frontmatter"
    parts = text.split("---\n", 2)
    assert len(parts) == 3, "frontmatter must be closed with '---'"
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


def _top_level_sections(body: str) -> list[str]:
    headings = []
    for line in body.splitlines():
        if line.startswith("## "):
            headings.append(line[3:].strip())
    return headings


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_page_exists(stem: str) -> None:
    p = _page_path(stem)
    assert p.is_file(), f"missing wiki page: {p.relative_to(REPO_ROOT)}"


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_code_id(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    code_id = fm.get("code_id")
    assert code_id, f"{stem}: code_id missing"
    assert isinstance(code_id, str)
    assert LOWERCASE_KEBAB_RE.match(code_id), (
        f"{stem}: code_id must be lowercase-kebab; got {code_id!r}"
    )
    assert code_id == stem, (
        f"{stem}: code_id must equal filename stem (got {code_id!r})"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_publisher_dnv(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert fm.get("publisher") == "DNV", (
        f"{stem}: publisher must be 'DNV'; got {fm.get('publisher')!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_revision(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    revision = fm.get("revision")
    assert revision, f"{stem}: revision missing"
    revision_str = str(revision)
    assert DNV_REVISION_RE.match(revision_str), (
        f"{stem}: revision {revision_str!r} does not match DNV pattern"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_extraction_policy_metadata_only(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert fm.get("extraction_policy") == "metadata-only", (
        f"{stem}: extraction_policy must be 'metadata-only'"
    )
    assert fm.get("raw_copy_allowed") is False, (
        f"{stem}: raw_copy_allowed must be False"
    )


def test_legacy_code_id_only_on_renamed_codes() -> None:
    """Only dnv-st-f101 carries legacy_code_id (OS->ST 2021 rebrand bridge)."""
    expected_holder = "dnv-st-f101"
    expected_legacy = "dnv-os-f101"
    for stem in EXPECTED_PAGES:
        fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
        legacy = fm.get("legacy_code_id")
        if stem == expected_holder:
            assert legacy == expected_legacy, (
                f"{stem}: legacy_code_id must be {expected_legacy!r}; got {legacy!r}"
            )
        else:
            assert legacy is None, (
                f"{stem}: must NOT carry legacy_code_id (got {legacy!r}); "
                "only the OS->ST rebrand pair carries it"
            )


def test_legacy_code_id_bridge_resolves() -> None:
    """The dnv-st-f101 page bridges callers using the legacy DNV-OS-F101 spelling.

    Per plan TDD: the OS->ST 2021 rebrand bridge MUST be discoverable from
    frontmatter. A future Citation resolver normalization pass can use the
    legacy_code_id field to map legacy callers to the canonical page WITHOUT
    needing to scan filenames or maintain a separate alias table.
    """
    page = _page_path("dnv-st-f101")
    fm, body = _split_frontmatter(page.read_text(encoding="utf-8"))

    # Forward direction: canonical code_id is current ST- spelling.
    assert fm["code_id"] == "dnv-st-f101"

    # Backward direction: legacy field carries the pre-2021 OS- spelling.
    assert fm["legacy_code_id"] == "dnv-os-f101"

    # Build a tiny bridge index from EVERY page's frontmatter, simulating
    # what a resolver would do at calc time. The index must accept both
    # the canonical and the legacy code_id and resolve to the same page.
    bridge: dict[str, Path] = {}
    for stem in EXPECTED_PAGES:
        page_fm, _ = _split_frontmatter(
            _page_path(stem).read_text(encoding="utf-8")
        )
        bridge[page_fm["code_id"]] = _page_path(stem)
        legacy = page_fm.get("legacy_code_id")
        if legacy:
            bridge[legacy] = _page_path(stem)

    assert bridge["dnv-st-f101"] == page
    assert bridge["dnv-os-f101"] == page, (
        "legacy_code_id bridge must resolve dnv-os-f101 to the dnv-st-f101 page"
    )

    # Body must mention the legacy identifier so human readers know the bridge.
    assert "DNV-OS-F101" in body or "dnv-os-f101" in body, (
        "page body should reference the legacy identifier for human discoverability"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_no_raw_pdf_text_bleed_through(stem: str) -> None:
    text = _page_path(stem).read_text(encoding="utf-8")
    leaks = [phrase for phrase in RAW_TELLTALE_PHRASES if phrase in text]
    assert leaks == [], (
        f"{stem}: page contains DNV cover/copyright denylist phrases: {leaks!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_body_word_count_bounded(stem: str) -> None:
    _, body = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    word_count = len(body.split())
    assert 100 < word_count < 500, (
        f"{stem}: body word count {word_count} outside bounded budget (100<N<500)"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_body_structure_is_whitelisted_only(stem: str) -> None:
    _, body = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    sections = _top_level_sections(body)
    extra = set(sections) - ALLOWED_SECTIONS
    assert not extra, (
        f"{stem}: page contains non-whitelisted sections: {sorted(extra)!r}"
    )
    # All four allowed sections must be present.
    missing = ALLOWED_SECTIONS - set(sections)
    assert not missing, (
        f"{stem}: page is missing required sections: {sorted(missing)!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_links_only_pointer_to_mnt_ace(stem: str) -> None:
    text = _page_path(stem).read_text(encoding="utf-8")
    assert "/mnt/ace/O&G-Standards/DNV/" in text, (
        f"{stem}: page must point to the raw PDF location under /mnt/ace/O&G-Standards/DNV/"
    )
    # Pointer must be inside the 'Where to find the full text' section.
    _, body = _split_frontmatter(text)
    where_section_marker = "## Where to find the full text"
    assert where_section_marker in body, (
        f"{stem}: missing the 'Where to find the full text' section"
    )
    where_idx = body.index(where_section_marker)
    where_block = body[where_idx:]
    assert "/mnt/ace/O&G-Standards/DNV/" in where_block, (
        f"{stem}: /mnt/ace pointer must live in the 'Where to find' section"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_index_lists_page(stem: str) -> None:
    index_path = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/index.md"
    text = index_path.read_text(encoding="utf-8")
    assert f"standards/{stem}.md" in text, (
        f"index.md is missing a link to standards/{stem}.md"
    )


def test_index_page_count_bumped() -> None:
    """Index page_count must reflect ALL standards-page additions, including
    parallel W1-A API pages landing in the same window. The DNV W2-A floor
    is 16 (5 sources + api-17e + 10 DNV); higher values are allowed when
    additional parallel pages have landed."""
    index_path = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/index.md"
    text = index_path.read_text(encoding="utf-8")
    fm, _ = _split_frontmatter(text)
    page_count = fm.get("page_count")
    assert isinstance(page_count, int) and page_count >= 16, (
        f"index.md page_count must be >= 16 (5 sources + api-17e + 10 DNV floor); got {page_count!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_citation_schema_resolvable(stem: str) -> None:
    """Exercise the resolver: file-read + frontmatter parse must round-trip a Citation.

    Per plan AC: resolver call must NOT raise CitationResolutionError when
    the wiki_path/code_id/publisher/revision are taken verbatim from the
    page's own frontmatter.
    """
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    revision = str(fm["revision"])
    if revision == "public-metadata-required-before-citation-use":
        pytest.skip(f"{stem}: stub-only revision pending publisher pin")

    # Import lazily; ensure digitalmodel sibling package is on sys.path.
    import sys

    digitalmodel_src = REPO_ROOT / "digitalmodel" / "src"
    if str(digitalmodel_src) not in sys.path:
        sys.path.insert(0, str(digitalmodel_src))
    try:
        from digitalmodel.citations.schema import Citation, validate_citation
    except ModuleNotFoundError as exc:
        pytest.skip(
            f"digitalmodel package not importable from {digitalmodel_src}: {exc}"
        )

    wiki_path = f"knowledge/wikis/engineering-standards/wiki/standards/{stem}.md"
    citation = Citation(
        code_id=fm["code_id"],
        publisher=fm["publisher"],
        revision=revision,
        section="bounded-summary",
        wiki_path=wiki_path,
    )
    validate_citation(citation, repo_root=REPO_ROOT)
