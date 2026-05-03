"""Bounded-summary contract test for the W4-B BSI engineering-standards pages.

Issue trail:
- Plan: docs/plans/2026-05-03-issue-2600-llm-wiki-W4B-engineering-standards-bsi.md
- Citation contract: .claude/rules/calc-citation-contract.md
- Sibling pattern: tests/knowledge/test_engineering_standards_dnv.py (W2-A precedent)
- Vendor-derivative governance: #2482

Each of the 8 W4-B pages MUST:
1. Exist at the prescribed path under wiki/standards/.
2. Carry frontmatter with `code_id` (lowercase-kebab, equal to filename stem),
   `publisher: BSI`, populated `revision`, `extraction_policy: metadata-only`,
   `raw_copy_allowed: false`, `jurisdiction: UK`, `bs_doc_number`,
   `superseded_by`.
3. Carry `superseded_by_note` when `bs_doc_number` starts with "BS EN ISO"
   with the BSI-jurisdictional-re-publication clarifier substring (W4-B M4 fix).
4. Carry only the four allowed top-level sections: Scope, Why this page exists,
   Where to find the full text, Cross-references.
5. Be word-bounded: 0 < N < 500 (W4-B strict ceiling; matches W3-A).
6. Avoid the BSI-specific raw-text denylist (cover/copyright phrases).
7. Carry a /mnt/ace/O&G-Standards/BSI/ pointer (links-only).

The `test_superseded_by_pointer_resolves` test enforces the W4-B-specific
contract: every page's `superseded_by` value either resolves to a wiki page
under `knowledge/wikis/*/wiki/standards/<superseded_by>.md` OR carries a
`publisher_catalog_url` whose host is bsigroup.com / knowledge.bsigroup.com /
iso.org AND whose URL string contains the numeric code from the
`superseded_by` value. This is the M3-strengthened resolver contract.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
STANDARDS_DIR = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/standards"

EXPECTED_PAGES = (
    "bs-13628-2-flexible-pipe-subsea",
    "bs-13628-3-tfl-systems",
    "bs-13628-5-subsea-umbilicals",
    "bs-13628-8-rov-interfaces",
    "bs-13533-drill-through-equipment",
    "bs-13625-marine-drilling-riser-couplings",
    "bs-13703-offshore-platform-piping",
    "bs-13626-drilling-well-servicing-structures",
)

# BSI cover/copyright phrases that would only appear if raw PDF text bled
# through. Narrowly scoped; does NOT overlap OCIMF/API/DNV/ABS denylists.
RAW_TELLTALE_PHRASES = (
    "389 Chiswick High Road, London W4 4AL",
    "BSI 389 Chiswick",
    "© BSI",
    "© British Standards Institution",
    "BSI is incorporated by Royal Charter",
    "Reproduction except as permitted by the Copyright",
    "BSI is the national body responsible",
    "This British Standard, having been prepared under the direction",
    "Permission to reproduce extracts",
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
BSI_REVISION_RE = re.compile(
    r"^(\d{4}|public-metadata-required-before-citation-use)$"
)
SUPERSEDED_BY_PREFIX_RE = re.compile(r"^(iso|en-iso)-")
NUMERIC_CODE_RE = re.compile(r"\d{3,5}")
ALLOWED_CATALOG_HOSTS = frozenset(
    {"bsigroup.com", "knowledge.bsigroup.com", "iso.org", "www.iso.org"}
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
def test_frontmatter_has_publisher_bsi(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert fm.get("publisher") == "BSI", (
        f"{stem}: publisher must be 'BSI'; got {fm.get('publisher')!r}"
    )
    publisher_full = fm.get("publisher_full")
    if publisher_full is not None:
        assert publisher_full == "British Standards Institution", (
            f"{stem}: publisher_full must be 'British Standards Institution'"
        )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_revision(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    revision = fm.get("revision")
    assert revision, f"{stem}: revision missing"
    revision_str = str(revision)
    assert BSI_REVISION_RE.match(revision_str), (
        f"{stem}: revision {revision_str!r} does not match BSI pattern "
        "(4-digit year string; corrigenda enumerated separately)"
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
def test_frontmatter_has_jurisdiction_uk(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert fm.get("jurisdiction") == "UK", (
        f"{stem}: jurisdiction must be 'UK'; got {fm.get('jurisdiction')!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_bs_doc_number(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    bs_doc_number = fm.get("bs_doc_number")
    assert bs_doc_number, f"{stem}: bs_doc_number missing"
    assert isinstance(bs_doc_number, str)
    assert bs_doc_number.startswith("BS "), (
        f"{stem}: bs_doc_number must start with 'BS '; got {bs_doc_number!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_superseded_by_pointer_resolves(stem: str) -> None:
    """W4-B-specific: every page's superseded_by must resolve.

    Resolution accepts EITHER:
      (a) a wiki page at knowledge/wikis/*/wiki/standards/<superseded_by>.md, OR
      (b) (M3-strengthened) `publisher_catalog_url` whose host is in the
          allowed BSI/ISO catalog set AND whose URL string contains the
          numeric code extracted from the `superseded_by` value.
    """
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    superseded_by = fm.get("superseded_by")
    assert superseded_by, f"{stem}: superseded_by missing"
    assert isinstance(superseded_by, str)
    assert LOWERCASE_KEBAB_RE.match(superseded_by), (
        f"{stem}: superseded_by must be lowercase-kebab; got {superseded_by!r}"
    )
    assert SUPERSEDED_BY_PREFIX_RE.match(superseded_by), (
        f"{stem}: superseded_by must start with 'iso-' or 'en-iso-'; "
        f"got {superseded_by!r}"
    )

    # (a) wiki-internal link
    wiki_root = REPO_ROOT / "knowledge/wikis"
    candidates = list(wiki_root.glob(f"*/wiki/standards/{superseded_by}.md"))
    if candidates:
        return  # (a) satisfied

    # (b) publisher_catalog_url with host + numeric-code substring
    catalog_url = fm.get("publisher_catalog_url")
    assert catalog_url, (
        f"{stem}: superseded_by={superseded_by!r} did not resolve to a wiki page; "
        "publisher_catalog_url is required as a fallback (W3-B ISO pages "
        "not yet present)"
    )
    parsed = urlparse(str(catalog_url))
    host = parsed.netloc.lower()
    assert host in ALLOWED_CATALOG_HOSTS, (
        f"{stem}: publisher_catalog_url host {host!r} not in allowed set "
        f"{sorted(ALLOWED_CATALOG_HOSTS)}"
    )
    numeric_codes = NUMERIC_CODE_RE.findall(superseded_by)
    assert numeric_codes, (
        f"{stem}: could not extract numeric code from superseded_by={superseded_by!r}"
    )
    primary_code = numeric_codes[0]
    assert primary_code in str(catalog_url), (
        f"{stem}: publisher_catalog_url {catalog_url!r} must contain the "
        f"numeric code {primary_code!r} from superseded_by"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_superseded_by_note_when_bs_en_iso(stem: str) -> None:
    """W4-B M4: machine-enforce the BS-EN-ISO-vs-superseded distinction."""
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    bs_doc_number = fm.get("bs_doc_number", "")
    if not bs_doc_number.startswith("BS EN ISO"):
        pytest.skip(f"{stem}: bs_doc_number not a BS-EN-ISO adoption")
    note = fm.get("superseded_by_note", "")
    assert note, f"{stem}: superseded_by_note required for BS-EN-ISO adoption"
    accepted = (
        "jurisdictional re-publication" in note
        or "not technically superseded" in note
    )
    assert accepted, (
        f"{stem}: superseded_by_note must contain "
        "'jurisdictional re-publication' OR 'not technically superseded'; "
        f"got {note!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_no_raw_pdf_text_bleed_through(stem: str) -> None:
    text = _page_path(stem).read_text(encoding="utf-8")
    leaks = [phrase for phrase in RAW_TELLTALE_PHRASES if phrase in text]
    assert leaks == [], (
        f"{stem}: page contains BSI cover/copyright denylist phrases: {leaks!r}"
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
    # All four allowed sections must be present.
    missing = ALLOWED_SECTIONS - set(sections)
    assert not missing, (
        f"{stem}: page is missing required sections: {sorted(missing)!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_links_only_pointer_to_mnt_ace(stem: str) -> None:
    text = _page_path(stem).read_text(encoding="utf-8")
    assert "/mnt/ace/O&G-Standards/BSI/" in text, (
        f"{stem}: page must point to the raw PDF location under "
        "/mnt/ace/O&G-Standards/BSI/"
    )
    _, body = _split_frontmatter(text)
    where_section_marker = "## Where to find the full text"
    assert where_section_marker in body, (
        f"{stem}: missing the 'Where to find the full text' section"
    )
    where_idx = body.index(where_section_marker)
    where_block = body[where_idx:]
    assert "/mnt/ace/O&G-Standards/BSI/" in where_block, (
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
    """Exercise the resolver: file-read + frontmatter parse must round-trip a Citation."""
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
