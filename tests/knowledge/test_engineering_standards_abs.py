"""Bounded-summary contract test for the W3-A ABS engineering-standards pages.

Issue trail:
- Plan: docs/plans/2026-05-02-issue-2594-llm-wiki-W3A-engineering-standards-abs.md
- Citation contract: .claude/rules/calc-citation-contract.md
- Sibling pattern: tests/knowledge/test_engineering_standards_dnv.py (W2-A precedent)
- Vendor-derivative governance: #2482

Each of the 8 W3-A pages MUST:
1. Exist at the prescribed path under wiki/standards/.
2. Carry frontmatter with `code_id` (lowercase-kebab, equal to filename stem),
   `publisher: ABS`, populated `revision`, `extraction_policy: metadata-only`,
   `raw_copy_allowed: false`, `abs_doc_number`.
3. Carry only the four allowed top-level sections: Scope, Why this page exists,
   Where to find the full text, Cross-references — and ALL four must be present.
4. Be word-bounded: 0 < N < 500 (strict ceiling per W2-A P3-4 fix).
5. Avoid the ABS-specific raw-text denylist (cover/copyright phrases).
6. Carry a /mnt/ace/O&G-Standards/ABS/ pointer in the 'Where to find' section.

The abs_part_section bridge test enforces that ONLY the three abs-rules-*.md
pages carry `abs_part_section` (multi-part rule-book numbering); the five
Guide / GN pages MUST NOT carry the key (omitted entirely, not set to null).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
STANDARDS_DIR = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/standards"

EXPECTED_PAGES = (
    "abs-rules-offshore-installations",
    "abs-rules-coc-part1-offshore",
    "abs-rules-steel-vessels-part3",
    "abs-gui-002-fpso",
    "abs-gui-101-fpso-dla",
    "abs-gui-115-fatigue-offshore",
    "abs-gui-123-offshore-risers",
    "abs-gn-239-cathodic-protection-offshore",
)

# The three pages that MUST carry abs_part_section (multi-part rule books).
RULES_PAGES_WITH_PART_SECTION = frozenset(
    {
        "abs-rules-offshore-installations",
        "abs-rules-coc-part1-offshore",
        "abs-rules-steel-vessels-part3",
    }
)

# ABS cover/copyright phrases that would only appear if raw PDF text bled
# through. Narrowly scoped; does NOT overlap OCIMF, API, or DNV denylists.
RAW_TELLTALE_PHRASES = (
    "ABS Plaza",
    "1701 City Plaza Drive",
    "Spring TX",
    "Spring, TX",
    "Houston, Texas, USA",
    "© American Bureau of Shipping",
    "© ABS",
    "Reproduction, copy or transmission of this publication",
    "ABS Rules and Guides are reviewed",
    "All rights reserved.",
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
ABS_REVISION_RE = re.compile(
    r"^(\d{4}|public-metadata-required-before-citation-use)$"
)
MAX_BODY_WORDS = 500


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
def test_frontmatter_has_publisher_abs(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert fm.get("publisher") == "ABS", (
        f"{stem}: publisher must be 'ABS'; got {fm.get('publisher')!r}"
    )
    publisher_full = fm.get("publisher_full")
    if publisher_full is not None:
        assert publisher_full == "American Bureau of Shipping", (
            f"{stem}: publisher_full when present must be 'American Bureau of "
            f"Shipping'; got {publisher_full!r}"
        )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_revision(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    revision = fm.get("revision")
    assert revision, f"{stem}: revision missing"
    revision_str = str(revision)
    assert ABS_REVISION_RE.match(revision_str), (
        f"{stem}: revision {revision_str!r} does not match ABS pattern (year or stub)"
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
def test_frontmatter_has_abs_doc_number(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    abs_doc_number = fm.get("abs_doc_number")
    assert abs_doc_number, f"{stem}: abs_doc_number missing"
    assert isinstance(abs_doc_number, str) and abs_doc_number.strip()


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_part_section_only_on_multipart_rules(stem: str) -> None:
    """Only the three abs-rules-*.md pages carry abs_part_section.

    Guide and GN pages are single-document; Part-numbering is a Rules-only
    artifact. The key MUST be omitted entirely from non-rules pages, not set
    to YAML null (which would still register the key as present).
    """
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    has_key = "abs_part_section" in fm
    if stem in RULES_PAGES_WITH_PART_SECTION:
        assert has_key, (
            f"{stem}: rules page must carry abs_part_section frontmatter"
        )
        value = fm["abs_part_section"]
        assert isinstance(value, str) and value.strip(), (
            f"{stem}: abs_part_section must be a non-empty string; got {value!r}"
        )
    else:
        assert not has_key, (
            f"{stem}: non-rules page must NOT carry abs_part_section "
            f"(found {fm.get('abs_part_section')!r})"
        )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_no_raw_pdf_text_bleed_through(stem: str) -> None:
    text = _page_path(stem).read_text(encoding="utf-8")
    leaks = [phrase for phrase in RAW_TELLTALE_PHRASES if phrase in text]
    assert leaks == [], (
        f"{stem}: page contains ABS cover/copyright denylist phrases: {leaks!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_body_word_count_bounded(stem: str) -> None:
    _, body = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    word_count = len(body.split())
    assert 0 < word_count < MAX_BODY_WORDS, (
        f"{stem}: body word count {word_count} outside bounded budget "
        f"(0<N<{MAX_BODY_WORDS})"
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
    assert "/mnt/ace/O&G-Standards/ABS/" in text, (
        f"{stem}: page must point to the raw PDF location under "
        f"/mnt/ace/O&G-Standards/ABS/"
    )
    _, body = _split_frontmatter(text)
    where_section_marker = "## Where to find the full text"
    assert where_section_marker in body, (
        f"{stem}: missing the 'Where to find the full text' section"
    )
    where_idx = body.index(where_section_marker)
    where_block = body[where_idx:]
    assert "/mnt/ace/O&G-Standards/ABS/" in where_block, (
        f"{stem}: /mnt/ace pointer must live in the 'Where to find' section"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_index_lists_page(stem: str) -> None:
    index_path = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/index.md"
    text = index_path.read_text(encoding="utf-8")
    assert f"standards/{stem}.md" in text, (
        f"index.md is missing a link to standards/{stem}.md"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_citation_schema_resolvable(stem: str) -> None:
    """Exercise the resolver: file-read + frontmatter parse must round-trip a Citation.

    Per plan AC: resolver call must NOT raise CitationResolutionError when
    the wiki_path/code_id/publisher/revision are taken verbatim from the
    page's own frontmatter. Pages whose revision is held as the
    `public-metadata-required-before-citation-use` stub are skipped.
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

    wiki_path = (
        f"knowledge/wikis/engineering-standards/wiki/standards/{stem}.md"
    )
    citation = Citation(
        code_id=fm["code_id"],
        publisher=fm["publisher"],
        revision=revision,
        section="bounded-summary",
        wiki_path=wiki_path,
    )
    validate_citation(citation, repo_root=REPO_ROOT)


def test_code_id_unique_across_wiki_domains() -> None:
    """No code_id appears twice across knowledge/wikis/*/wiki/standards/*.md.

    Inherited from W2-A AC. For ABS this is currently vacuous (no pre-existing
    ABS pages elsewhere — confirmed via plan resource-intel section), but the
    assertion guards against future drift.
    """
    wikis_root = REPO_ROOT / "knowledge/wikis"
    seen: dict[str, Path] = {}
    duplicates: list[str] = []
    for page in wikis_root.glob("*/wiki/standards/*.md"):
        try:
            fm, _ = _split_frontmatter(page.read_text(encoding="utf-8"))
        except AssertionError:
            # not a frontmatter page; skip
            continue
        code_id = fm.get("code_id")
        if not code_id:
            continue
        if code_id in seen:
            duplicates.append(
                f"code_id={code_id!r} duplicated at "
                f"{seen[code_id].relative_to(REPO_ROOT)} and "
                f"{page.relative_to(REPO_ROOT)}"
            )
        else:
            seen[code_id] = page
    assert not duplicates, "code_id duplicates found: " + "; ".join(duplicates)
