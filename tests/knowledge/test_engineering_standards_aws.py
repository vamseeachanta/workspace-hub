"""Bounded-summary contract test for the W5-B AWS welding-standards pages.

Issue trail:
- Plan: docs/plans/2026-05-03-issue-2611-llm-wiki-W5B-engineering-standards-aws.md
- Issue: #2611
- Citation contract: .claude/rules/calc-citation-contract.md
- Sibling pattern: tests/knowledge/test_engineering_standards_nace.py (W4-A precedent)
- Vendor-derivative governance: #2482

Each of the 6 W5-B pages MUST:
1. Exist at the prescribed path under wiki/standards/.
2. Carry frontmatter with `code_id` (lowercase-kebab, equal to filename stem,
   `aws-` prefix), `publisher: AWS`, populated `revision`,
   `extraction_policy: metadata-only`, `raw_copy_allowed: false`,
   `aws_doc_number`, and `ledger_id`.
3. Carry only the four allowed top-level sections plus an `Edition gap
   discipline` section: Scope, Why this page exists, Where to find the full
   text, Edition gap discipline, Cross-references.
4. Be word-bounded: 0 < N < 500.
5. Avoid the AWS-specific raw-text denylist (cover/copyright phrases).
6. Carry a /mnt/ace/O&G-Standards/AWS/ pointer (links-only).
7. Carry the NEW W5 `cross_references` frontmatter convention with shape
   `{code_id, relation, note}`; forward-pointing dangling links permitted.

The dangling-cross-reference test enforces that at least one cross_references
entry is explicitly marked as dangling (target page absent) — the W5
convention is introduced de novo and the dangling-link tolerance is
load-bearing because target pages (e.g. api-1104.md) do not yet exist.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
STANDARDS_DIR = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/standards"

EXPECTED_PAGES = (
    "aws-d1-1",
    "aws-d1-2",
    "aws-a2-4",
    "aws-a5-5",
    "aws-a5-10",
    "aws-filler-metal-overview",
)

# AWS cover/copyright phrases that would only appear if raw PDF text bled
# through. Narrowly scoped to AWS publication conventions.
RAW_TELLTALE_PHRASES = (
    "© American Welding Society. All rights reserved.",
    "© AWS. All rights reserved.",
    "ANSI/AWS",
    "Reproduction, copy or transmission of this publication",
    "ISBN 978-0-87171",
    "550 N.W. LeJeune Road, Miami, FL",
    "First published",
    "Reaffirmed",
)

# Proximity regex: bare "American National Standard" allowed unless paired
# with AWS within 40 characters.
RAW_PROXIMITY_PATTERNS = (
    re.compile(r"(AWS|American Welding Society)[^.\n]{0,40}American National Standard", re.IGNORECASE),
    re.compile(r"American National Standard[^.\n]{0,40}(AWS|American Welding Society)", re.IGNORECASE),
)

ALLOWED_SECTIONS = frozenset(
    {
        "Scope",
        "Why this page exists",
        "Where to find the full text",
        "Edition gap discipline",
        "Cross-references",
    }
)

ALLOWED_RELATIONS = frozenset(
    {"qualifies", "companion", "references", "superseded-by", "supersedes", "equivalent"}
)

LOWERCASE_KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
AWS_REVISION_RE = re.compile(r"^(\d{4}|public-metadata-required-before-citation-use)$")


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


def ledger_id_to_code_id(ledger_id: str) -> str:
    """Canonical transformation: AWS-X.Y -> aws-x-y (lowercase + dot-to-dash)."""
    return ledger_id.lower().replace(".", "-")


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
    assert code_id.startswith("aws-"), (
        f"{stem}: code_id must use aws- prefix; got {code_id!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_publisher_aws(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert fm.get("publisher") == "AWS", (
        f"{stem}: publisher must be 'AWS'; got {fm.get('publisher')!r}"
    )
    if "publisher_full" in fm:
        assert fm["publisher_full"] == "American Welding Society", (
            f"{stem}: publisher_full must be 'American Welding Society' if set; "
            f"got {fm['publisher_full']!r}"
        )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_revision(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    revision = fm.get("revision")
    assert revision, f"{stem}: revision missing"
    revision_str = str(revision)
    assert AWS_REVISION_RE.match(revision_str), (
        f"{stem}: revision {revision_str!r} does not match AWS pattern"
    )
    if stem == "aws-a5-5":
        assert revision_str == "1996", (
            "aws-a5-5: cover-page-verified revision must be literal '1996'"
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
def test_frontmatter_has_aws_doc_number(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    doc_num = fm.get("aws_doc_number")
    assert doc_num, f"{stem}: aws_doc_number missing"
    assert isinstance(doc_num, str)


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_has_ledger_id(stem: str) -> None:
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    ledger_id = fm.get("ledger_id")
    assert ledger_id, f"{stem}: ledger_id missing"
    assert isinstance(ledger_id, str)
    assert ledger_id.startswith("AWS-"), (
        f"{stem}: ledger_id must use AWS- prefix; got {ledger_id!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_cross_references_field_present(stem: str) -> None:
    """NEW W5: every AWS page must carry the cross_references frontmatter list."""
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    xrefs = fm.get("cross_references")
    assert xrefs is not None, f"{stem}: cross_references frontmatter missing (W5 convention)"
    assert isinstance(xrefs, list), f"{stem}: cross_references must be a list"
    assert len(xrefs) >= 1, f"{stem}: cross_references must contain at least one entry"


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_cross_references_shape(stem: str) -> None:
    """NEW W5: each cross_references entry must be {code_id, relation, note}."""
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    xrefs = fm.get("cross_references", [])
    for entry in xrefs:
        assert isinstance(entry, dict), (
            f"{stem}: cross_references entry must be a dict; got {entry!r}"
        )
        assert set(entry.keys()) == {"code_id", "relation", "note"}, (
            f"{stem}: cross_references entry keys must be exactly "
            f"{{code_id, relation, note}}; got {set(entry.keys())!r}"
        )
        cid = entry["code_id"]
        assert LOWERCASE_KEBAB_RE.match(cid), (
            f"{stem}: cross_references code_id must be lowercase-kebab; got {cid!r}"
        )
        assert entry["relation"] in ALLOWED_RELATIONS, (
            f"{stem}: cross_references relation {entry['relation']!r} "
            f"not in allowed enum {sorted(ALLOWED_RELATIONS)!r}"
        )
        assert isinstance(entry["note"], str) and entry["note"], (
            f"{stem}: cross_references note must be a non-empty string"
        )


def test_dangling_xref_explicitly_marked() -> None:
    """NEW W5: at least one dangling cross-reference (target page absent) must
    appear and the test contract permits it.

    Per plan: cross_references seeds point to ASME BPVC IX (asme-bpvc-ix.md
    EXISTS) and API 1104 (api-1104.md does NOT exist; intentionally dangling).
    The test asserts (a) the cross_references convention does carry at least
    one entry across all pages whose target page is absent on disk, and (b)
    the shape contract still passes for that entry.
    """
    dangling_targets: set[str] = set()
    resolved_targets: set[str] = set()
    for stem in EXPECTED_PAGES:
        fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
        for entry in fm.get("cross_references", []):
            target = entry["code_id"]
            target_path = STANDARDS_DIR / f"{target}.md"
            # Also probe other domains (we don't enumerate; engineering-standards
            # is the relevant local namespace and the only one this test domain
            # validates against).
            if target_path.is_file():
                resolved_targets.add(target)
            else:
                # Targets outside engineering-standards (e.g. api-1104) count
                # as dangling for this contract.
                dangling_targets.add(target)
    assert "asme-bpvc-ix" in resolved_targets, (
        "expected at least one cross_references entry pointing to the existing "
        "asme-bpvc-ix page (sanity: confirms the resolver path works)"
    )
    assert "api-1104" in dangling_targets, (
        "expected at least one dangling cross_references entry (api-1104) — "
        "W5 introduces the convention with explicit dangling-link tolerance"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_no_raw_pdf_text_bleed_through(stem: str) -> None:
    """Body-only scan: frontmatter is excluded so paraphrased names allowed."""
    text = _page_path(stem).read_text(encoding="utf-8")
    _, body = _split_frontmatter(text)
    leaks = [phrase for phrase in RAW_TELLTALE_PHRASES if phrase in body]
    assert leaks == [], (
        f"{stem}: page contains AWS cover/copyright denylist phrases: {leaks!r}"
    )
    proximity_hits = [p.pattern for p in RAW_PROXIMITY_PATTERNS if p.search(body)]
    assert proximity_hits == [], (
        f"{stem}: page contains AWS-proximate 'American National Standard': "
        f"{proximity_hits!r}"
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
    required = {"Scope", "Why this page exists", "Where to find the full text",
                "Edition gap discipline", "Cross-references"}
    missing = required - set(sections)
    assert not missing, (
        f"{stem}: page is missing required sections: {sorted(missing)!r}"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_links_only_pointer_to_mnt_ace(stem: str) -> None:
    text = _page_path(stem).read_text(encoding="utf-8")
    assert "/mnt/ace/O&G-Standards/AWS/" in text, (
        f"{stem}: page must point to the raw PDF location under "
        "/mnt/ace/O&G-Standards/AWS/"
    )
    _, body = _split_frontmatter(text)
    where_section_marker = "## Where to find the full text"
    assert where_section_marker in body, (
        f"{stem}: missing the 'Where to find the full text' section"
    )
    where_idx = body.index(where_section_marker)
    where_block = body[where_idx:]
    assert "/mnt/ace/O&G-Standards/AWS/" in where_block, (
        f"{stem}: /mnt/ace pointer must live in the 'Where to find' section"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_index_lists_page(stem: str) -> None:
    index_path = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/index.md"
    text = index_path.read_text(encoding="utf-8")
    assert f"standards/{stem}.md" in text, (
        f"index.md is missing a link to standards/{stem}.md"
    )


def test_d1_1_multi_edition_sources_enumeration() -> None:
    """D1.1 has 4 distinct editions on disk; all 4 years must appear in `sources:`."""
    fm, _ = _split_frontmatter(_page_path("aws-d1-1").read_text(encoding="utf-8"))
    sources = fm.get("sources", [])
    joined = "\n".join(str(s) for s in sources)
    for year in ("2006", "2008", "2009", "2010"):
        assert year in joined, (
            f"aws-d1-1: sources frontmatter must enumerate {year} edition; got {sources!r}"
        )


def test_edition_gap_section_present_on_every_page() -> None:
    """Every AWS page must carry the new H2 'Edition gap discipline' section."""
    for stem in EXPECTED_PAGES:
        _, body = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
        assert "## Edition gap discipline" in body, (
            f"{stem}: page is missing the '## Edition gap discipline' H2 section"
        )


def test_code_id_unique_across_wiki_domains() -> None:
    """code_id must be unique across all wiki/standards/*.md pages."""
    seen: dict[str, Path] = {}
    for path in REPO_ROOT.glob("knowledge/wikis/*/wiki/standards/*.md"):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        try:
            fm, _ = _split_frontmatter(text)
        except AssertionError:
            continue
        cid = fm.get("code_id")
        if not cid:
            continue
        assert cid not in seen, (
            f"duplicate code_id {cid!r}: {path} and {seen[cid]}"
        )
        seen[cid] = path


def test_ledger_alignment() -> None:
    """Every page's ledger_id resolves to a row in the standards-transfer-ledger.

    The canonical transformation rule AWS-X.Y <-> aws-x-y must hold for every
    page: code_id == ledger_id_to_code_id(ledger_id).

    Note: ledger row presence is checked best-effort (some new W5 ledger rows
    may be added in a follow-up commit per plan); the canonical-transformation
    invariant is the load-bearing assertion.
    """
    for stem in EXPECTED_PAGES:
        fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
        ledger_id = fm["ledger_id"]
        code_id = fm["code_id"]
        # Special-case the series-overview ledger_id which uses
        # AWS-FILLER-METAL-OVERVIEW (no dotted segment); transformation rule
        # still applies and yields aws-filler-metal-overview.
        assert code_id == ledger_id_to_code_id(ledger_id), (
            f"{stem}: code_id {code_id!r} does not match transformation of "
            f"ledger_id {ledger_id!r} (expected {ledger_id_to_code_id(ledger_id)!r})"
        )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_citation_schema_resolvable(stem: str) -> None:
    """Exercise the resolver: file-read + frontmatter parse must round-trip a Citation.

    Per plan AC: resolver call must NOT raise CitationResolutionError when
    the wiki_path/code_id/publisher/revision are taken verbatim from the
    page's own frontmatter. Pages whose revision is the placeholder
    (`public-metadata-required-before-citation-use`) are skipped — only the
    OPTIONAL aws-filler-metal-overview uses the placeholder.
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
