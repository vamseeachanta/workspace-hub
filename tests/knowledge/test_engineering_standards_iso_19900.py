"""W3-B bounded summary contract — ISO 19900-series engineering standards.

Per the approved plan
``docs/plans/2026-05-02-issue-2595-llm-wiki-W3B-engineering-standards-iso-19900.md``
(Tier B approval 2026-05-03), this test enforces the bounded-summary contract
for the eight priority ISO 19900-series offshore-structures standards pages.

Key W3-B specifics over the W1-A (API) and W2-A (DNV) precedents:

- Every on-disk ISO 19900-series PDF/doc under ``/mnt/ace/O&G-Standards/ISO/``
  is a draft (DIS, FDIS, CD) or comment-response artifact — NOT a published
  edition. Each page MUST therefore declare a ``revision_source_status``
  field distinguishing ``on-disk-draft`` from ``published-edition`` (and
  reserve ``mixed-with-citation`` for future use), and the
  ``revision_source`` value MUST be a publisher portal URL — never a
  ``/mnt/ace`` draft path.
- The ISO catalog URL MUST appear in the body's "Where to find" section
  (canonical pointer is the ISO portal even when an on-disk draft exists).
- The umbrella page ``iso-19900.md`` is exempted from the umbrella
  back-reference test (it IS the umbrella).
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


# Top-8 selection per the user task — drops iso-19905-1 (1 internal ref;
# documented in the plan's Risks as the swap candidate when the count is 8).
EXPECTED_PAGES: tuple[str, ...] = (
    "iso-19900",
    "iso-19901-1",
    "iso-19901-2",
    "iso-19901-4",
    "iso-19901-7",
    "iso-19902",
    "iso-19903",
    "iso-19904-1",
)

UMBRELLA_PAGE = "iso-19900"


# Allowed body section headings (positive-shape constraint).
ALLOWED_SECTIONS = frozenset(
    {
        "Scope",
        "Why this page exists",
        "Where to find the full text",
        "Cross-references",
    }
)


# Narrowly-scoped ISO publication front-matter / cover-page / committee-draft
# telltales. These would only appear if raw PDF text bled into the page.
# Excludes the standard's title and code identifier (which are required).
RAW_TELLTALE_PHRASES: tuple[str, ...] = (
    "All rights reserved",
    "Reproduction or use in any form",
    "Case postale 56",
    "CH-1211 Geneva",
    "Reference number ISO",
    "INTERNATIONAL STANDARD ISO",
    # Working-draft / ballot / committee telltales (W3-B MINOR-4 fix).
    "FDIS ballot",
    "DIS comment",
    "ISO/TC 67/SC 7",
    "ISO/TC 67",
    "Editing committee",
    "track changes",
)


# Allowed values for the W3-B-specific revision_source_status field.
ALLOWED_REVISION_SOURCE_STATUS = frozenset(
    {"on-disk-draft", "published-edition", "mixed-with-citation"}
)


LOWERCASE_KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ISO_REVISION_RE = re.compile(
    r"^(\d{4}|public-metadata-required-before-citation-use)$"
)
ISO_PORTAL_URL_RE = re.compile(r"https?://www\.iso\.org/standard/\d+\.html")
ISO_DRAFT_TELLTALES = ("DIS", "FDIS", "CD", "markup", "responses")


# Word-count budget — strict on both bounds, matches W1-A / W2-A precedent.
WORD_COUNT_LOWER = 100
WORD_COUNT_UPPER = 500


def _page_path(stem: str) -> Path:
    return STANDARDS_DIR / f"{stem}.md"


def _split_frontmatter(text: str) -> tuple[dict, str]:
    assert text.startswith("---\n"), "page must begin with YAML frontmatter"
    parts = text.split("---\n", 2)
    assert len(parts) == 3, "frontmatter must be closed with '---'"
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


def _top_level_sections(body: str) -> list[str]:
    return [line[3:].strip() for line in body.splitlines() if line.startswith("## ")]


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
def test_frontmatter_has_publisher_iso(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert fm.get("publisher") == "ISO", (
        f"{stem}: publisher must be 'ISO'; got {fm.get('publisher')!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_revision(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    revision = fm.get("revision")
    assert revision, f"{stem}: revision missing"
    revision_str = str(revision)
    assert ISO_REVISION_RE.match(revision_str), (
        f"{stem}: revision {revision_str!r} does not match ISO pattern"
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
def test_revision_source_field_present(stem: str) -> None:
    """W3-B MAJOR fix — distinguish on-disk-draft vs publisher-current.

    The field MUST be a publisher portal URL (never a /mnt/ace draft path),
    and a companion ``revision_source_status`` field MUST be set to one of
    {on-disk-draft, published-edition, mixed-with-citation}.
    """
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))

    revision_source = fm.get("revision_source")
    assert revision_source, f"{stem}: revision_source missing"
    assert isinstance(revision_source, str)
    assert revision_source.startswith(("http://", "https://")), (
        f"{stem}: revision_source must be a URL (publisher portal), "
        f"never a /mnt/ace draft path; got {revision_source!r}"
    )
    assert "/mnt/ace" not in revision_source, (
        f"{stem}: revision_source must not point at a /mnt/ace draft path"
    )

    status = fm.get("revision_source_status")
    assert status in ALLOWED_REVISION_SOURCE_STATUS, (
        f"{stem}: revision_source_status must be one of "
        f"{sorted(ALLOWED_REVISION_SOURCE_STATUS)}; got {status!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_distinguishes_draft_vs_published_revision(stem: str) -> None:
    """If any source path looks like a /mnt/ace ISO draft (DIS/FDIS/CD/markup/
    responses), the page must declare revision_source_status='on-disk-draft'
    and revision_source must remain a publisher-portal URL.
    """
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    sources = fm.get("sources") or []
    has_draft_on_disk = any(
        isinstance(s, str)
        and "/mnt/ace" in s
        and any(t in s for t in ISO_DRAFT_TELLTALES)
        for s in sources
    )
    revision_source = str(fm.get("revision_source", ""))
    status = fm.get("revision_source_status")

    if has_draft_on_disk:
        assert status == "on-disk-draft", (
            f"{stem}: page lists /mnt/ace draft sources but "
            f"revision_source_status is {status!r}, expected 'on-disk-draft'"
        )
        assert "/mnt/ace" not in revision_source, (
            f"{stem}: revision_source must NOT cite the draft path"
        )
        assert ISO_PORTAL_URL_RE.search(revision_source), (
            f"{stem}: revision_source must cite ISO portal URL when on-disk draft exists"
        )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_no_raw_pdf_text_bleed_through(stem: str) -> None:
    text = _page_path(stem).read_text(encoding="utf-8")
    leaks = [phrase for phrase in RAW_TELLTALE_PHRASES if phrase in text]
    assert leaks == [], (
        f"{stem}: page contains ISO cover/copyright/draft denylist phrases: {leaks!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_body_word_count_bounded(stem: str) -> None:
    _, body = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    word_count = len(body.split())
    assert WORD_COUNT_LOWER < word_count < WORD_COUNT_UPPER, (
        f"{stem}: body word count {word_count} outside bounded budget "
        f"({WORD_COUNT_LOWER}<N<{WORD_COUNT_UPPER})"
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
def test_links_only_pointer_to_iso_portal(stem: str) -> None:
    """The 'Where to find' section must cite the canonical ISO portal URL."""
    text = _page_path(stem).read_text(encoding="utf-8")
    _, body = _split_frontmatter(text)
    where_marker = "## Where to find the full text"
    assert where_marker in body, (
        f"{stem}: missing the 'Where to find the full text' section"
    )
    where_block = body[body.index(where_marker):]
    assert ISO_PORTAL_URL_RE.search(where_block), (
        f"{stem}: 'Where to find' section must cite the ISO portal URL "
        f"(regex {ISO_PORTAL_URL_RE.pattern!r})"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_umbrella_cross_reference(stem: str) -> None:
    """Every part page must back-reference the umbrella iso-19900.

    The umbrella page itself is exempted (it IS the umbrella).
    """
    if stem == UMBRELLA_PAGE:
        pytest.skip(f"{stem}: umbrella page is exempt from the back-reference rule")
    _, body = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert "[[iso-19900]]" in body, (
        f"{stem}: body must back-reference [[iso-19900]] umbrella"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_cross_reference_budget_bounded(stem: str) -> None:
    """Part pages must list at most umbrella + 2 normative siblings (≤3 total).

    The umbrella page is exempt — it lists every part by design.
    """
    if stem == UMBRELLA_PAGE:
        pytest.skip(f"{stem}: umbrella exempt from cross-ref budget")
    _, body = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    iso_links = re.findall(r"\[\[iso-[a-z0-9-]+\]\]", body)
    # Exclude self-references (paranoia — should not occur).
    iso_links = [l for l in iso_links if l != f"[[{stem}]]"]
    assert len(iso_links) <= 3, (
        f"{stem}: cross-reference budget exceeded — found "
        f"{len(iso_links)} [[iso-...]] links: {iso_links!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_index_lists_page(stem: str) -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")
    assert f"standards/{stem}.md" in text, (
        f"index.md is missing a link to standards/{stem}.md"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_citation_schema_resolvable(stem: str) -> None:
    """Resolver round-trip: page frontmatter must satisfy validate_citation."""
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
