"""Bounded-summary contract test for the W4-A NACE/AMPP engineering-standards pages.

Issue trail:
- Plan: docs/plans/2026-05-03-issue-2599-llm-wiki-W4A-engineering-standards-nace.md
- Issue: #2599
- Citation contract: .claude/rules/calc-citation-contract.md
- Sibling pattern: tests/knowledge/test_engineering_standards_dnv.py (W2-A precedent)
- Vendor-derivative governance: #2482

Each of the 5 W4-A pages MUST:
1. Exist at the prescribed path under wiki/standards/.
2. Carry frontmatter with `code_id` (lowercase-kebab, equal to filename stem,
   `ampp-` prefix), `publisher: AMPP`, `legacy_publisher: "NACE International"`,
   `legacy_code_id` (NACE-prefixed bridge), populated `revision`,
   `extraction_policy: metadata-only`, `raw_copy_allowed: false`.
3. Carry only the four allowed top-level sections: Scope, Why this page exists,
   Where to find the full text, Cross-references.
4. Be word-bounded: 100 < N < 500 (matches W1-A/W2-A/W3-A strict bounds).
5. Avoid the NACE/AMPP-specific raw-text denylist (cover/copyright phrases).
6. Carry a /mnt/ace/O&G-Standards/NACE/ pointer (links-only).

The legacy_code_id bridge test enforces that EVERY NACE/AMPP page carries a
nace-* legacy_code_id mapping to the canonical ampp-* code_id (the 2021
NACE -> AMPP publisher rebrand bridge).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
STANDARDS_DIR = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/standards"

EXPECTED_PAGES = (
    "ampp-mr-0175-pt1",
    "ampp-mr-0175-pt2",
    "ampp-mr-0175-pt3",
    "ampp-mr-0175-1995",
    "ampp-tm-0177",
)

# NACE/AMPP cover/copyright phrases that would only appear if raw PDF text
# bled through. Narrowly scoped; does NOT overlap OCIMF, API, DNV, or ABS
# denylists. Each entry is a contiguous cover-page template token, NOT a
# paraphrasable name.
RAW_TELLTALE_PHRASES = (
    "© NACE International. All rights reserved.",
    "© AMPP. All rights reserved.",
    "Reproduction, copy or transmission of this publication",
    "ISBN 1-57590",
    "ANSI/NACE Standard",
    "Catalog Number",
    "First published",
    "Reaffirmed",
    "AMPP, Houston, TX",
)

# Proximity regex: bare "All rights reserved" allowed unless paired with
# NACE/AMPP within 40 characters.
RAW_PROXIMITY_PATTERNS = (
    re.compile(r"(NACE|AMPP)[^.\n]{0,40}All rights reserved", re.IGNORECASE),
    re.compile(r"All rights reserved[^.\n]{0,40}(NACE|AMPP)", re.IGNORECASE),
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
NACE_REVISION_RE = re.compile(
    r"^(\d{4}(-\d+(st|nd|rd|th)?-Ed)?|public-metadata-required-before-citation-use)$"
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
    assert code_id.startswith("ampp-"), (
        f"{stem}: canonical code_id must use ampp- prefix (current publisher); got {code_id!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_publisher_ampp(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert fm.get("publisher") == "AMPP", (
        f"{stem}: publisher must be 'AMPP'; got {fm.get('publisher')!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_legacy_publisher_nace(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert fm.get("legacy_publisher") == "NACE International", (
        f"{stem}: legacy_publisher must be 'NACE International'; "
        f"got {fm.get('legacy_publisher')!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_legacy_code_id_nace_prefix(stem: str) -> None:
    """Every NACE/AMPP page MUST carry a nace-* legacy_code_id bridge."""
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    legacy = fm.get("legacy_code_id")
    assert legacy, f"{stem}: legacy_code_id missing (rebrand bridge required)"
    assert isinstance(legacy, str)
    assert LOWERCASE_KEBAB_RE.match(legacy), (
        f"{stem}: legacy_code_id must be lowercase-kebab; got {legacy!r}"
    )
    assert legacy.startswith("nace-"), (
        f"{stem}: legacy_code_id must use nace- prefix; got {legacy!r}"
    )
    # Bridge correspondence: the legacy nace-* spelling must match the
    # canonical ampp-* code_id in everything except the publisher prefix.
    canonical_suffix = fm["code_id"][len("ampp-"):]
    legacy_suffix = legacy[len("nace-"):]
    assert canonical_suffix == legacy_suffix, (
        f"{stem}: legacy_code_id suffix {legacy_suffix!r} does not match "
        f"canonical suffix {canonical_suffix!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_revision(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    revision = fm.get("revision")
    assert revision, f"{stem}: revision missing"
    revision_str = str(revision)
    assert NACE_REVISION_RE.match(revision_str), (
        f"{stem}: revision {revision_str!r} does not match NACE/AMPP pattern"
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


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_nace_doc_number(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    doc_num = fm.get("nace_doc_number")
    assert doc_num, f"{stem}: nace_doc_number missing"
    assert isinstance(doc_num, str)
    assert ("MR 0175" in doc_num) or ("TM 0177" in doc_num), (
        f"{stem}: nace_doc_number {doc_num!r} must reference MR 0175 or TM 0177"
    )


def test_iso_equivalent_only_on_2009_parts() -> None:
    """Only the 2009 multi-part Parts carry iso_equivalent (joint NACE/ISO)."""
    iso_holders = {"ampp-mr-0175-pt1", "ampp-mr-0175-pt2", "ampp-mr-0175-pt3"}
    iso_pattern = re.compile(r"^ISO 15156(-[123])?$")
    for stem in EXPECTED_PAGES:
        fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
        iso = fm.get("iso_equivalent")
        if stem in iso_holders:
            assert iso, f"{stem}: iso_equivalent missing on a 2009 Part page"
            assert iso_pattern.match(str(iso)), (
                f"{stem}: iso_equivalent {iso!r} does not match ISO 15156 pattern"
            )
        # Pre-2003 1995 page has no joint-ISO publication; TM 0177 is not
        # ISO-paired. Either absent OR present is permitted on those pages,
        # so no negative assertion needed here.


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_no_raw_pdf_text_bleed_through(stem: str) -> None:
    """Body-only scan: frontmatter is excluded so paraphrased names allowed."""
    text = _page_path(stem).read_text(encoding="utf-8")
    _, body = _split_frontmatter(text)
    leaks = [phrase for phrase in RAW_TELLTALE_PHRASES if phrase in body]
    assert leaks == [], (
        f"{stem}: page contains NACE/AMPP cover/copyright denylist phrases: {leaks!r}"
    )
    proximity_hits = [p.pattern for p in RAW_PROXIMITY_PATTERNS if p.search(body)]
    assert proximity_hits == [], (
        f"{stem}: page contains NACE/AMPP-proximate 'All rights reserved': "
        f"{proximity_hits!r}"
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
    missing = ALLOWED_SECTIONS - set(sections)
    assert not missing, (
        f"{stem}: page is missing required sections: {sorted(missing)!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_links_only_pointer_to_mnt_ace(stem: str) -> None:
    text = _page_path(stem).read_text(encoding="utf-8")
    assert "/mnt/ace/O&G-Standards/NACE/" in text, (
        f"{stem}: page must point to the raw PDF location under "
        "/mnt/ace/O&G-Standards/NACE/"
    )
    _, body = _split_frontmatter(text)
    where_section_marker = "## Where to find the full text"
    assert where_section_marker in body, (
        f"{stem}: missing the 'Where to find the full text' section"
    )
    where_idx = body.index(where_section_marker)
    where_block = body[where_idx:]
    assert "/mnt/ace/O&G-Standards/NACE/" in where_block, (
        f"{stem}: /mnt/ace pointer must live in the 'Where to find' section"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_index_lists_page(stem: str) -> None:
    index_path = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/index.md"
    text = index_path.read_text(encoding="utf-8")
    assert f"standards/{stem}.md" in text, (
        f"index.md is missing a link to standards/{stem}.md"
    )


def test_nace_ampp_legacy_bridge_resolves() -> None:
    """The 2021 NACE -> AMPP rebrand bridge MUST resolve from frontmatter.

    Per plan TDD: the publisher-rebrand bridge MUST be discoverable from
    frontmatter. A future Citation resolver normalization pass uses the
    legacy_code_id field to map nace-* callers to the canonical ampp-* page
    WITHOUT needing to scan filenames or maintain a separate alias table.
    """
    # Build the bridge index from EVERY page's frontmatter, simulating
    # what a resolver would do at calc time. The index must accept both
    # the canonical ampp-* and the legacy nace-* code_id and resolve to
    # the same page.
    bridge: dict[str, Path] = {}
    for stem in EXPECTED_PAGES:
        page_fm, _ = _split_frontmatter(
            _page_path(stem).read_text(encoding="utf-8")
        )
        canonical = page_fm["code_id"]
        legacy = page_fm["legacy_code_id"]
        # No duplicates allowed; each canonical/legacy must map to one page.
        assert canonical not in bridge, (
            f"duplicate canonical code_id in bridge: {canonical}"
        )
        assert legacy not in bridge, (
            f"duplicate legacy_code_id in bridge: {legacy}"
        )
        bridge[canonical] = _page_path(stem)
        bridge[legacy] = _page_path(stem)

    # Forward direction: every canonical ampp-* code_id resolves to the page.
    for stem in EXPECTED_PAGES:
        page = _page_path(stem)
        assert bridge[stem] == page, (
            f"canonical {stem} did not resolve to its own page"
        )

    # Backward direction: nace-* legacy spellings resolve to the same pages.
    legacy_to_canonical = {
        "nace-mr-0175-pt1": "ampp-mr-0175-pt1",
        "nace-mr-0175-pt2": "ampp-mr-0175-pt2",
        "nace-mr-0175-pt3": "ampp-mr-0175-pt3",
        "nace-mr-0175-1995": "ampp-mr-0175-1995",
        "nace-tm-0177": "ampp-tm-0177",
    }
    for legacy, canonical in legacy_to_canonical.items():
        assert legacy in bridge, (
            f"legacy {legacy} not in bridge (rebrand bridge incomplete)"
        )
        assert bridge[legacy] == _page_path(canonical), (
            f"legacy {legacy} must resolve to canonical {canonical} page"
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
