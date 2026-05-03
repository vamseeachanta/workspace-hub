"""W1-B asset-management wiki TDD assertion suite.

Per the approved plan
``docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md``
(issue #2587), this test enforces the topical-scaffold contract for the
engineering / integrity asset-management wiki:

- Every concept page carries the required YAML frontmatter (title, tags,
  added, last_updated) plus a ``manual-review`` field.
- Every standards page carries the #2471-required triple
  (``code_id``/``publisher``/``revision``) plus the #2615 sanction marker
  (``Sanctioned-by``) — required because asset-management is a #2615 W5-D
  formally-sanctioned wiki for ``wiki/standards/<code-id>.md`` routing.
- Every new page has a ``## Scope`` heading and at least one cross-link.
- ``index.md`` carries a Scope-boundary block distinguishing engineering
  asset management (in scope) from financial / portfolio asset management
  (NOT in scope).
- No concept page cites ``wiki/sources/`` or contains the deny-list
  slug-tokens (``casa-grande``, ``assethold``) per #2482.
- At least 8 of 12 concept pages link to a ``wiki/standards/<code-id>.md``
  page, and every such link resolves on disk.
- Index Concepts/Standards table row counts equal filesystem counts.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI_ROOT = REPO_ROOT / "knowledge" / "wikis" / "asset-management" / "wiki"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
STANDARDS_DIR = WIKI_ROOT / "standards"
INDEX_PATH = WIKI_ROOT / "index.md"


REQUIRED_FRONTMATTER_FIELDS = ("title", "tags", "added", "last_updated")
REQUIRED_STANDARDS_FIELDS = ("code_id", "publisher", "revision", "Sanctioned-by")

# Per #2482 vendor-derivative deny-list (strengthened per r1 review m5).
DENYLIST_SLUG_TOKENS = ("casa-grande", "assethold")

# Per memory ``project_wiki_standards_path_decision.md`` plus #2615:
# asset-management is a formally-sanctioned in-principle wiki and every
# standards page in this scaffold MUST cite #2615 in frontmatter.
SANCTION_ISSUE = "#2615"


def _split_frontmatter(text: str) -> tuple[dict, str]:
    assert text.startswith("---\n"), "page must begin with YAML frontmatter"
    parts = text.split("---\n", 2)
    assert len(parts) == 3, "frontmatter must be closed with '---'"
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


def _concept_pages() -> list[Path]:
    return sorted(CONCEPTS_DIR.glob("*.md"))


def _standards_pages() -> list[Path]:
    return sorted(STANDARDS_DIR.glob("*.md"))


def _all_new_pages() -> list[Path]:
    return _concept_pages() + _standards_pages()


# ---------------------------------------------------------------------------
# Frontmatter contract — concept pages
# ---------------------------------------------------------------------------


def test_every_concept_page_has_yaml_frontmatter() -> None:
    pages = _concept_pages()
    assert pages, "no concept pages found"
    for page in pages:
        fm, _ = _split_frontmatter(page.read_text(encoding="utf-8"))
        missing = [f for f in REQUIRED_FRONTMATTER_FIELDS if f not in fm]
        assert not missing, f"{page.name}: missing required frontmatter fields {missing!r}"


def test_manual_review_flag_present() -> None:
    """Each of the 12 concept pages has ``manual-review`` field in frontmatter."""
    pages = _concept_pages()
    assert len(pages) == 12, f"expected 12 concept pages; got {len(pages)}"
    for page in pages:
        fm, _ = _split_frontmatter(page.read_text(encoding="utf-8"))
        assert "manual-review" in fm, (
            f"{page.name}: missing 'manual-review' frontmatter field"
        )
        assert fm["manual-review"] in ("pending", "approved"), (
            f"{page.name}: 'manual-review' must be 'pending' or 'approved'; "
            f"got {fm['manual-review']!r}"
        )


# ---------------------------------------------------------------------------
# Frontmatter contract — standards pages (#2471 + #2615 sanction)
# ---------------------------------------------------------------------------


def test_every_standards_page_has_code_id_publisher_revision() -> None:
    pages = _standards_pages()
    assert pages, "no standards pages found"
    for page in pages:
        fm, _ = _split_frontmatter(page.read_text(encoding="utf-8"))
        for field in REQUIRED_STANDARDS_FIELDS:
            assert field in fm, (
                f"{page.name}: missing required standards-page field {field!r}"
            )
            assert fm[field], f"{page.name}: standards-page field {field!r} is empty"


def test_every_standards_page_carries_sanction_2615() -> None:
    """Per #2615 W5-D umbrella sanction, every asset-management standards page
    must carry a ``Sanctioned-by: #2615`` frontmatter field — required because
    asset-management is a formally-sanctioned in-principle wiki and the path
    routing must be traceable to its sanctioning issue.
    """
    for page in _standards_pages():
        fm, _ = _split_frontmatter(page.read_text(encoding="utf-8"))
        sanctioned_by = str(fm.get("Sanctioned-by", ""))
        assert SANCTION_ISSUE in sanctioned_by, (
            f"{page.name}: 'Sanctioned-by' must reference {SANCTION_ISSUE}; "
            f"got {sanctioned_by!r}"
        )


# ---------------------------------------------------------------------------
# Body shape — Scope section + cross-links on every new page
# ---------------------------------------------------------------------------


def test_every_new_page_has_scope_section() -> None:
    for page in _all_new_pages():
        text = page.read_text(encoding="utf-8")
        assert "\n## Scope\n" in text or text.endswith("## Scope\n"), (
            f"{page.name}: missing required '## Scope' section"
        )


_MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_WIKI_LINK_RE = re.compile(r"\[\[[^\]]+\]\]")


def test_every_new_page_has_at_least_one_cross_link() -> None:
    """Each page has >=1 markdown link to another page in this wiki OR to
    cross-links.md.
    """
    for page in _all_new_pages():
        _, body = _split_frontmatter(page.read_text(encoding="utf-8"))
        links = _MD_LINK_RE.findall(body) + _WIKI_LINK_RE.findall(body)
        # Inbound link to ANY other page in this wiki, including index.md, or
        # to cross-links.md.
        ok = any(
            ("./" in lnk)
            or ("../" in lnk)
            or ("cross-links.md" in lnk)
            or lnk.endswith(".md")
            for lnk in links
        )
        assert ok, f"{page.name}: no cross-link found"


# ---------------------------------------------------------------------------
# Scope-boundary disclaimer — load-bearing per the plan
# ---------------------------------------------------------------------------


def test_index_has_scope_boundary_block() -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")
    assert "## Scope boundary" in text, "index.md missing '## Scope boundary' heading"


def test_scope_boundary_disclaimer_text() -> None:
    """index.md contains the literal phrases 'engineering / integrity asset
    management' AND a 'NOT … financial / portfolio' disclaimer.
    """
    text = INDEX_PATH.read_text(encoding="utf-8")
    assert "engineering / integrity asset management" in text, (
        "index.md missing the in-scope phrase 'engineering / integrity asset management'"
    )
    # Tolerate elision/hyphen variants of the NOT…financial/portfolio phrasing.
    assert "NOT" in text and "financial / portfolio" in text, (
        "index.md missing the out-of-scope 'NOT … financial / portfolio' disclaimer"
    )


# ---------------------------------------------------------------------------
# Vendor-derivative deny-list (#2482) — strengthened per r1 review m5
# ---------------------------------------------------------------------------


def test_no_vendor_derivative_citation_in_concept_pages() -> None:
    """No concept page links to ``wiki/sources/`` AND no concept-page body
    contains the deny-list slug-tokens (``casa-grande``, ``assethold``).
    """
    for page in _concept_pages():
        text = page.read_text(encoding="utf-8")
        assert "wiki/sources/" not in text and "/sources/" not in text, (
            f"{page.name}: concept page must NOT cite wiki/sources/* per #2482"
        )
        for token in DENYLIST_SLUG_TOKENS:
            assert token not in text, (
                f"{page.name}: deny-listed slug-token {token!r} found per #2482"
            )


# ---------------------------------------------------------------------------
# Concept ↔ Standards linkage and link resolution
# ---------------------------------------------------------------------------


_STANDARDS_LINK_RE = re.compile(
    r"\(\.\./standards/([a-z0-9._-]+\.md)\)"
)


def _concept_pages_linking_to_standards() -> list[Path]:
    out: list[Path] = []
    for page in _concept_pages():
        body = page.read_text(encoding="utf-8")
        if _STANDARDS_LINK_RE.search(body):
            out.append(page)
    return out


def test_concept_pages_link_to_standards_pages() -> None:
    """At least 8 of 12 concept pages link to a wiki/standards/<code-id>.md page."""
    linkers = _concept_pages_linking_to_standards()
    assert len(linkers) >= 8, (
        f"expected >=8 concept pages linking to standards/; got {len(linkers)} "
        f"({[p.name for p in linkers]!r})"
    )


def test_all_internal_links_resolve() -> None:
    """Every concept-page link to a wiki/standards/...md target resolves to an
    existing file (per r1 review m3 — converts shape-test to content-test).
    """
    for page in _concept_pages():
        body = page.read_text(encoding="utf-8")
        for stem_md in _STANDARDS_LINK_RE.findall(body):
            target = STANDARDS_DIR / stem_md
            assert target.is_file(), (
                f"{page.name}: link to ../standards/{stem_md} does not resolve "
                f"({target.relative_to(REPO_ROOT)} missing)"
            )


# ---------------------------------------------------------------------------
# Engineering-wiki cross-references (per r1 review m2 — replaces the
# cross-links.md-targeted test which depends on the auto-generator running).
#
# This wiki is auto-indexed by ``scripts/knowledge/wiki-cross-links.py`` —
# we cannot edit ``cross-links.md`` directly under the W1-B write-only
# isolation contract. We instead assert the **prerequisite**: at least one
# concept page contains a cross-wiki reference into the engineering wiki,
# which is what the auto-generator picks up on its next run.
# ---------------------------------------------------------------------------


def test_asset_management_has_engineering_wiki_cross_references() -> None:
    """At least one concept page links into the engineering wiki — the
    prerequisite for cross-links.md auto-generation to pick up
    asset-management as a source/target.
    """
    found_any = False
    for page in _concept_pages():
        body = page.read_text(encoding="utf-8")
        if "engineering/wiki/" in body or "engineering/concepts/" in body:
            found_any = True
            break
    assert found_any, (
        "no concept page references the engineering wiki — cross-link "
        "auto-generation will not pick up asset-management on its next run"
    )


# ---------------------------------------------------------------------------
# Index ↔ filesystem reconciliation
# ---------------------------------------------------------------------------


def test_index_table_count_matches_filesystem() -> None:
    """index.md Concepts and Standards table row counts equal filesystem counts.
    """
    text = INDEX_PATH.read_text(encoding="utf-8")
    concept_files = _concept_pages()
    standards_files = _standards_pages()

    # Count distinct concept-link targets in index.md
    concept_links = set(re.findall(r"\(concepts/([a-z0-9._-]+\.md)\)", text))
    standards_links = set(re.findall(r"\(standards/([a-z0-9._-]+\.md)\)", text))

    expected_concepts = {p.name for p in concept_files}
    expected_standards = {p.name for p in standards_files}

    assert concept_links == expected_concepts, (
        f"index.md concept links {sorted(concept_links)} != "
        f"filesystem {sorted(expected_concepts)}"
    )
    assert standards_links == expected_standards, (
        f"index.md standards links {sorted(standards_links)} != "
        f"filesystem {sorted(expected_standards)}"
    )
