"""Bounded-summary contract for ASME wiki standards pages (#2591, W2-B).

Asserts the 10 priority ASME pages under
``knowledge/wikis/engineering-standards/wiki/standards/asme-*.md`` carry
the required frontmatter triple, contain ZERO verbatim ASME PDF
front-matter / copyright phrasing, stay under the tightened ≤500-word
ceiling (down from prior W1-A baseline; aggressive ASME copyright
enforcement justifies the tighter bound), and limit body structure to
the four whitelisted sections {Scope, Why this page exists, Where to
find the full text, Cross-references}.

Companion plan: docs/plans/2026-05-02-issue-2591-llm-wiki-W2B-engineering-standards-asme.md

# Denylist provenance
#
# RAW_TELLTALE_PHRASES below were extracted by sampling the cover and
# copyright pages of three on-disk PDFs on 2026-05-02 (per plan
# acceptance criterion / MINOR-4):
#
#   - ASME B31.3 - Process Piping/ASME B31.3 2012 - Processing Piping.pdf
#       observed: "Three Park Avenue", "New York, NY", "10016",
#       "Date of Issuance: January 10, 2013",
#       "ASME is the registered trademark of The American Society of
#       Mechanical Engineers", "All rights reserved", "Printed in U.s.A.",
#       "Copyright © 2013 by", "THE AMERICAN SOCIETY OF MECHANICAL
#       ENGINEERS", "No part of this document may be reproduced in any
#       form".
#
#   - ASME VIII/ASME VIII DIV 1 (2010) Rules for Construction of High
#     Pressure Vessels.pdf
#       observed: "Three Park Avenue", "Library of Congress Catalog Card
#       Number: 56-3934", "Adopted by the Council of the American
#       Society of Mechanical Engineers, 1914", "Copyright © 2010 by",
#       "All Rights Reserved", "AS ME is the trademark of the American
#       Society of Mechanical Engineers".
#
#   - BS/ASME B16.5-2013.pdf
#       observed: "Two Park Avenue", "New York, NY", "10016",
#       "Date of Issuance: April 29, 2013",
#       "No reproduction may be made of this material without written
#       consent of ASME", "Copyright c 2013 by the American Society of
#       Mechanical Engineers", "Copyright © 2013 by", "ASME is the
#       registered trademark of The American Society of Mechanical
#       Engineers".
#
# The denylist below intentionally excludes the standard's title and
# code identifier (those are required on the wiki page); it targets
# unambiguous ASME footer / copyright / publisher-address phrases.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
_DIGITALMODEL_SRC = REPO_ROOT / "digitalmodel" / "src"
if str(_DIGITALMODEL_SRC) not in sys.path:
    sys.path.insert(0, str(_DIGITALMODEL_SRC))

from digitalmodel.citations.schema import (  # noqa: E402
    Citation,
    CitationResolutionError,
    validate_citation,
)
WIKI_DIR = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/standards"
INDEX_PATH = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/index.md"

EXPECTED_PAGES = (
    "asme-b31-3",
    "asme-b31-4",
    "asme-b31-8",
    "asme-bpvc-viii-1",
    "asme-bpvc-viii-2",
    "asme-bpvc-ii-d",
    "asme-bpvc-ix",
    "asme-pcc-1",
    "asme-b16-5",
    "asme-b16-34",
)

ALLOWED_HEADINGS = {
    "Scope",
    "Why this page exists",
    "Where to find the full text",
    "Cross-references",
}

ALLOWED_METHODOLOGY = {"current", "stale-as-of-publisher-cycle", "unknown"}

# ASME-specific footer / copyright phrasing observed on the cover/copyright
# pages of three on-disk PDFs (B31.3-2012, BPVC VIII-1-2010, B16.5-2013).
# The list MUST contain ≥ 3 ASME-specific footer phrases per plan MAJOR-3.
RAW_TELLTALE_PHRASES = (
    "American Society of Mechanical Engineers",
    "AMERICAN SOCIETY OF MECHANICAL ENGINEERS",
    "Three Park Avenue",
    "Two Park Avenue",
    "10016-5990",
    "10016 5990",
    "No part of this document may be reproduced",
    "No reproduction may be made of this material without written consent of ASME",
    "Library of Congress Catalog Card Number: 56-3934",
    "Adopted by the Council of the American Society of Mechanical Engineers, 1914",
    "ASME is the registered trademark of The American Society of Mechanical Engineers",
)


# Sanity check on the denylist itself (load-bearing for plan MAJOR-3).
def test_denylist_has_at_least_three_asme_footer_phrases() -> None:
    asme_specific = [
        p
        for p in RAW_TELLTALE_PHRASES
        if "American Society of Mechanical Engineers" in p
        or "ASME" in p
        or "Park Avenue" in p
        or "10016" in p
    ]
    assert len(asme_specific) >= 3, (
        f"Denylist must include ≥3 ASME-specific footer phrases; got {len(asme_specific)}"
    )


def _read(page_id: str) -> str:
    path = WIKI_DIR / f"{page_id}.md"
    return path.read_text(encoding="utf-8")


def _split_frontmatter(text: str) -> tuple[dict, str]:
    assert text.startswith("---\n"), "page must begin with YAML frontmatter"
    parts = text.split("---\n", 2)
    assert len(parts) == 3, "frontmatter must be closed with '---'"
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


@pytest.mark.parametrize("page_id", EXPECTED_PAGES)
def test_page_exists(page_id: str) -> None:
    assert (WIKI_DIR / f"{page_id}.md").is_file(), (
        f"missing wiki page: {WIKI_DIR / (page_id + '.md')}"
    )


@pytest.mark.parametrize("page_id", EXPECTED_PAGES)
def test_frontmatter_has_code_id(page_id: str) -> None:
    fm, _ = _split_frontmatter(_read(page_id))
    assert fm.get("code_id") == page_id, (
        f"code_id must equal filename stem ({page_id!r}); got {fm.get('code_id')!r}"
    )
    assert re.fullmatch(r"[a-z0-9-]+", fm["code_id"]), "code_id must be kebab-case"


@pytest.mark.parametrize("page_id", EXPECTED_PAGES)
def test_frontmatter_has_publisher_asme(page_id: str) -> None:
    fm, _ = _split_frontmatter(_read(page_id))
    assert fm.get("publisher") == "ASME"


@pytest.mark.parametrize("page_id", EXPECTED_PAGES)
def test_frontmatter_has_revision(page_id: str) -> None:
    fm, _ = _split_frontmatter(_read(page_id))
    rev = fm.get("revision")
    assert isinstance(rev, str) and rev.strip(), "revision must be non-empty string"


@pytest.mark.parametrize("page_id", EXPECTED_PAGES)
def test_frontmatter_has_methodology_status(page_id: str) -> None:
    fm, _ = _split_frontmatter(_read(page_id))
    status = fm.get("methodology_status")
    assert status in ALLOWED_METHODOLOGY, (
        f"methodology_status must be one of {ALLOWED_METHODOLOGY!r}; got {status!r}"
    )
    if page_id == "asme-b31-3":
        assert status == "stale-as-of-publisher-cycle", (
            "asme-b31-3 MUST set methodology_status='stale-as-of-publisher-cycle' "
            "due to 2024/2026 SIF method change"
        )


@pytest.mark.parametrize("page_id", EXPECTED_PAGES)
def test_frontmatter_has_extraction_policy_metadata_only(page_id: str) -> None:
    fm, _ = _split_frontmatter(_read(page_id))
    assert fm.get("extraction_policy") == "metadata-only"
    assert fm.get("raw_copy_allowed") is False


@pytest.mark.parametrize("page_id", EXPECTED_PAGES)
def test_no_raw_pdf_text_bleed_through(page_id: str) -> None:
    text = _read(page_id)
    leaks = [phrase for phrase in RAW_TELLTALE_PHRASES if phrase in text]
    assert leaks == [], (
        f"page {page_id!r} contains ASME footer/copyright phrases that would "
        f"breach the metadata-only boundary: {leaks!r}"
    )


@pytest.mark.parametrize("page_id", EXPECTED_PAGES)
def test_body_word_count_bounded(page_id: str) -> None:
    _, body = _split_frontmatter(_read(page_id))
    n = len(body.split())
    assert 100 <= n <= 500, (
        f"page {page_id!r} body has {n} words; ASME bounded-summary budget is "
        "100 ≤ N ≤ 500 (tightened per plan MAJOR-3)"
    )


@pytest.mark.parametrize("page_id", EXPECTED_PAGES)
def test_body_structure_is_whitelisted_only(page_id: str) -> None:
    _, body = _split_frontmatter(_read(page_id))
    headings = re.findall(r"^##\s+(.+?)\s*$", body, re.MULTILINE)
    forbidden = [h for h in headings if re.search(r"clauses|formulas", h, re.IGNORECASE)]
    assert forbidden == [], (
        f"page {page_id!r} contains forbidden Clauses/Formulas section heading(s): {forbidden!r}"
    )
    extra = [h for h in headings if h not in ALLOWED_HEADINGS]
    assert extra == [], (
        f"page {page_id!r} contains non-whitelisted top-level headings: {extra!r}; "
        f"allowed = {sorted(ALLOWED_HEADINGS)!r}"
    )


@pytest.mark.parametrize("page_id", EXPECTED_PAGES)
def test_links_only_pointer_to_mnt_ace(page_id: str) -> None:
    _, body = _split_frontmatter(_read(page_id))
    assert re.search(r"/mnt/ace/O&G-Standards/ASME/", body), (
        f"page {page_id!r} must mention the raw /mnt/ace/O&G-Standards/ASME/ path"
    )


@pytest.mark.parametrize("page_id", EXPECTED_PAGES)
def test_citation_schema_resolvable(page_id: str) -> None:
    fm, _ = _split_frontmatter(_read(page_id))
    rev = fm["revision"]
    wiki_path = f"knowledge/wikis/engineering-standards/wiki/standards/{page_id}.md"
    citation = Citation(
        code_id=page_id,
        publisher="ASME",
        revision=rev,
        section="placeholder",
        wiki_path=wiki_path,
    )
    try:
        validate_citation(citation, repo_root=REPO_ROOT)
    except CitationResolutionError as exc:  # pragma: no cover - failure path is the assertion
        pytest.fail(f"validate_citation failed for {page_id}: {exc}")


def test_index_lists_all_ten() -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")
    for page_id in EXPECTED_PAGES:
        assert f"standards/{page_id}.md" in text, (
            f"engineering-standards/wiki/index.md must link standards/{page_id}.md"
        )


def test_engineering_wiki_ffs1_remains_reachable() -> None:
    """Positive discipline-boundary guard: W2-B must NOT orphan or modify
    the existing joint API 579-1 / ASME FFS-1 page in the *other* wiki.
    """
    ffs_path = REPO_ROOT / "knowledge/wikis/engineering/wiki/standards/api-579-ffs.md"
    assert ffs_path.is_file(), "engineering-wiki FFS-1 page must remain present"
    fm, body = _split_frontmatter(ffs_path.read_text(encoding="utf-8"))
    # The engineering-wiki schema (not engineering-standards) does not require
    # code_id; the durability assertion here is that the page's title-and-tags
    # frontmatter survived and the body still anchors on the joint API/ASME framing.
    assert fm.get("title"), "FFS-1 page frontmatter must retain title"
    assert "asme" in fm.get("tags", []), "FFS-1 page must remain tagged as joint ASME work"
    assert "Fitness-for-Service" in body, "FFS-1 page body must remain on-topic"
