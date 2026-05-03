"""Bounded-summary contract test for the W5-A NORSOK engineering-standards pages.

Issue trail:
- Plan: docs/plans/2026-05-03-issue-2610-llm-wiki-W5A-engineering-standards-norsok.md
- Citation contract: .claude/rules/calc-citation-contract.md
- Sibling pattern: tests/knowledge/test_engineering_standards_dnv.py (W2-A precedent)
- Vendor-derivative governance: #2482

Each of the 6 W5-A pages MUST:
1. Exist at the prescribed path under wiki/standards/.
2. Carry frontmatter with `code_id` (lowercase-kebab, equal to filename stem),
   `publisher: "Standards Norway"`, populated `revision`, `extraction_policy: metadata-only`,
   `raw_copy_allowed: false`, `lifecycle_status`, `publisher_current_revision`,
   `iso_relationship` (NEW W5-A; renamed from W4-B's `superseded_by` because
   NORSOK->ISO is parallel-mirror, not supersession).
3. Carry only the four allowed top-level sections: Scope, Why this page exists,
   Where to find the full text, Cross-references (NO body "Lifecycle status"
   section per W5-A r1 P2-5 — lifecycle stays in frontmatter only).
4. Be word-bounded: 0 < N < 500 (strict per plan AC).
5. Avoid the NORSOK-specific raw-text denylist (cover/copyright phrases).
6. Carry a /mnt/ace/O&G-Standards/Norsok/ pointer (links-only).
7. The `iso_relationship` array entries must resolve to either a wiki-internal
   page or carry a `publisher_catalog_url` pointer fallback (NEW W5-A test
   `test_iso_relationship_pointer_resolves`).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
STANDARDS_DIR = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/standards"

EXPECTED_PAGES = (
    "norsok-n-001",
    "norsok-n-004",
    "norsok-m-001",
    "norsok-m-501",
    "norsok-m-710",
    "norsok-d-sr-022",
)

# NORSOK / Standards Norway cover/copyright phrases that would only appear if
# raw PDF text bled through. Narrowly scoped; does NOT overlap DNV / API /
# OCIMF / NACE / BSI / ABS denylists.
RAW_TELLTALE_PHRASES = (
    "© NORSOK Standard",
    "© Standards Norway",
    "Strandveien 18",
    "Postboks 242",
    "N-1326 Lysaker",
    "petroleum.standard.no",
    "Norwegian Petroleum Directorate",
)

# Reverse-and-forward proximity regex: bare "All rights reserved" is generic
# but flagged when adjacent to NORSOK / Standards Norway tokens.
RIGHTS_RESERVED_PROXIMITY = re.compile(
    r"(NORSOK|Standards Norway)[^.]{0,40}All rights reserved"
    r"|All rights reserved[^.]{0,40}(NORSOK|Standards Norway)"
)
# "Statoil and Norsk Hydro" flagged when adjacent to NORSOK boilerplate.
STATOIL_HYDRO_PROXIMITY = re.compile(
    r"Statoil and Norsk Hydro[^.]{0,80}NORSOK"
    r"|NORSOK[^.]{0,80}Statoil and Norsk Hydro"
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
# Per plan TDD literal regex (transcribed verbatim from the fenced-code block):
REVISION_PATTERN = re.compile(
    r"^(\d+(st|nd|rd|th)-Ed-\d{4}|\d{4}|"
    r"public-metadata-required-before-citation-use|"
    r"designation-withdrawn-\d{4})$"
)
ISO_EQUIV_RE = re.compile(r"^ISO \d{4,5}(-\d+)?$")

ALLOWED_NORSOK_SERIES = frozenset({"D", "M", "N"})
ALLOWED_LIFECYCLE = frozenset(
    {
        "in-force-mirror",
        "in-force-shelf-specific",
        "designation-withdrawn",
        "superseded-by-edition",
    }
)
ALLOWED_RELATIONSHIP = frozenset(
    {
        "full-replacement",
        "partial-overlap",
        "parallel-mirror",
        "withdrawn-no-replacement",
    }
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
def test_frontmatter_has_publisher_standards_norway(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert fm.get("publisher") == "Standards Norway", (
        f"{stem}: publisher must be 'Standards Norway'; got {fm.get('publisher')!r}"
    )
    pub_full = fm.get("publisher_full")
    if pub_full is not None:
        assert pub_full == "Standards Norway (NORSOK)", (
            f"{stem}: publisher_full must equal 'Standards Norway (NORSOK)'; got {pub_full!r}"
        )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_revision(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    revision = fm.get("revision")
    assert revision, f"{stem}: revision missing"
    revision_str = str(revision)
    assert REVISION_PATTERN.match(revision_str), (
        f"{stem}: revision {revision_str!r} does not match NORSOK pattern"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_publisher_current_revision(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    pcr = fm.get("publisher_current_revision")
    assert pcr, f"{stem}: publisher_current_revision missing"


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_lifecycle_status(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    ls = fm.get("lifecycle_status")
    assert ls in ALLOWED_LIFECYCLE, (
        f"{stem}: lifecycle_status {ls!r} not in {sorted(ALLOWED_LIFECYCLE)}"
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
def test_frontmatter_has_norsok_series_letter(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    series = fm.get("norsok_series")
    assert series in ALLOWED_NORSOK_SERIES, (
        f"{stem}: norsok_series {series!r} not in {sorted(ALLOWED_NORSOK_SERIES)} for W5-A"
    )
    doc_num = fm.get("norsok_doc_number")
    assert doc_num, f"{stem}: norsok_doc_number missing"
    assert doc_num.startswith(series + "-"), (
        f"{stem}: norsok_doc_number {doc_num!r} must start with series letter {series!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_no_raw_pdf_text_bleed_through(stem: str) -> None:
    text = _page_path(stem).read_text(encoding="utf-8")
    # Body-only scan — split at second '---' delimiter and scan only the body.
    _, body = _split_frontmatter(text)
    leaks = [phrase for phrase in RAW_TELLTALE_PHRASES if phrase in body]
    assert leaks == [], (
        f"{stem}: page body contains NORSOK cover/copyright denylist phrases: {leaks!r}"
    )
    assert not RIGHTS_RESERVED_PROXIMITY.search(body), (
        f"{stem}: 'All rights reserved' appears within proximity of NORSOK/Standards Norway"
    )
    assert not STATOIL_HYDRO_PROXIMITY.search(body), (
        f"{stem}: 'Statoil and Norsk Hydro' appears adjacent to NORSOK boilerplate"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_body_word_count_bounded(stem: str) -> None:
    _, body = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    word_count = len(body.split())
    assert 0 < word_count < 500, (
        f"{stem}: body word count {word_count} outside bounded budget (0<N<500)"
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
    _, body = _split_frontmatter(text)
    where_section_marker = "## Where to find the full text"
    assert where_section_marker in body, (
        f"{stem}: missing the 'Where to find the full text' section"
    )
    where_idx = body.index(where_section_marker)
    where_block = body[where_idx:]
    assert "/mnt/ace/O&G-Standards/Norsok/" in where_block, (
        f"{stem}: /mnt/ace/O&G-Standards/Norsok/ pointer must live in 'Where to find' section"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_index_lists_page(stem: str) -> None:
    index_path = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/index.md"
    text = index_path.read_text(encoding="utf-8")
    assert f"standards/{stem}.md" in text, (
        f"index.md is missing a link to standards/{stem}.md"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_iso_equivalent_optional_field_well_formed(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    iso_eq = fm.get("iso_equivalent")
    if iso_eq is None:
        return
    assert ISO_EQUIV_RE.match(iso_eq), (
        f"{stem}: iso_equivalent {iso_eq!r} does not match '^ISO \\d{{4,5}}(-\\d+)?$'"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_iso_relationship_pointer_resolves(stem: str) -> None:
    """W5-A NEW test (renamed from `test_superseded_by_pointer_resolves` per
    r1 P1-2 because NORSOK->ISO is parallel-mirror, NOT supersession).

    Every entry in the `iso_relationship` array must:
      - have a `code` field (string)
      - have a `relationship` field in ALLOWED_RELATIONSHIP
      - have a `note` field (string)
      - resolve via either (a) a wiki-internal page under any
        knowledge/wikis/*/wiki/standards/<stem>.md (kebab-cased), OR
        (b) the parent page must carry a `publisher_catalog_url` field
        pointing to a public catalog.
    """
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    iso_rel = fm.get("iso_relationship")
    if not iso_rel:
        return  # empty array is allowed
    assert isinstance(iso_rel, list), (
        f"{stem}: iso_relationship must be a list; got {type(iso_rel).__name__}"
    )

    has_catalog_url = bool(fm.get("publisher_catalog_url"))

    for entry in iso_rel:
        assert isinstance(entry, dict), (
            f"{stem}: iso_relationship entries must be dicts; got {entry!r}"
        )
        code = entry.get("code")
        relationship = entry.get("relationship")
        note = entry.get("note")
        assert isinstance(code, str) and code.strip(), (
            f"{stem}: iso_relationship entry missing 'code': {entry!r}"
        )
        assert relationship in ALLOWED_RELATIONSHIP, (
            f"{stem}: iso_relationship 'relationship' {relationship!r} not in "
            f"{sorted(ALLOWED_RELATIONSHIP)}"
        )
        assert isinstance(note, str) and note.strip(), (
            f"{stem}: iso_relationship entry missing 'note': {entry!r}"
        )

        # Resolution: (a) wiki-internal kebab page OR (b) publisher_catalog_url fallback.
        kebab = code.lower().replace(" ", "-").replace("/", "-")
        wiki_hits = list(
            (REPO_ROOT / "knowledge/wikis").glob(f"*/wiki/standards/{kebab}.md")
        )
        resolved = bool(wiki_hits) or has_catalog_url
        assert resolved, (
            f"{stem}: iso_relationship entry {code!r} does not resolve via wiki page "
            f"({kebab}.md) nor does parent page carry publisher_catalog_url fallback"
        )


def test_code_id_unique_across_wiki_domains() -> None:
    """No `code_id` in `knowledge/wikis/*/wiki/standards/*.md` is duplicated."""
    seen: dict[str, Path] = {}
    duplicates: list[str] = []
    for md_path in (REPO_ROOT / "knowledge/wikis").glob("*/wiki/standards/*.md"):
        try:
            fm, _ = _split_frontmatter(md_path.read_text(encoding="utf-8"))
        except (AssertionError, yaml.YAMLError):
            continue
        cid = fm.get("code_id")
        if not cid:
            continue
        if cid in seen and seen[cid] != md_path:
            duplicates.append(
                f"{cid}: {seen[cid].relative_to(REPO_ROOT)} <-> "
                f"{md_path.relative_to(REPO_ROOT)}"
            )
        else:
            seen[cid] = md_path
    assert not duplicates, f"duplicate code_id across wiki standards: {duplicates}"


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_citation_schema_resolvable(stem: str) -> None:
    """Resolver round-trip per .claude/rules/calc-citation-contract.md rule 4."""
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
