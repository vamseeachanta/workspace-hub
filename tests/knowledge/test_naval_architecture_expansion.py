"""W1-D naval-architecture topical-expansion contract test (#2589).

Issue trail:
- Plan: docs/plans/2026-05-02-issue-2589-llm-wiki-W1D-naval-architecture-expansion.md
- Wiki schema: knowledge/wikis/naval-architecture/CLAUDE.md
- Reservation context: #2568 (turning-circle / tactical-diameter / Nomoto)
- Existing legitimate occurrences of reserved phrases: maneuvering-validation-metrics.md
  (per W1-D MAJOR-3 — those occurrences pre-date this expansion and must be excluded
  from the reserved-phrase test).

Each of the 10 new pages MUST:
1. Exist at the prescribed path under wiki/concepts/ or wiki/entities/.
2. Carry CLAUDE.md frontmatter (title, tags, added, last_updated) plus
   see_also with at least 2 entries that resolve to real files.
3. Cite at least one of {IMO, ITTC, IACS, SNAME} in body text.
4. Be word-bounded: 0 < N < 400.
5. Avoid the #2568 reserved phrase set.

Plus router-page invariants:
- concepts/resistance-propulsion.md MUST NOT enumerate the resistance-component
  bullets, propulsor-type bullets, or propeller-open-water bullets that have
  been moved to the three new pages (per W1-D MAJOR-1).
- concepts/stability.md MUST NOT carry the long intact/damage stability bullets
  (per W1-D MAJOR-2 — defers to sibling pages).

Plus index/log invariants:
- index.md frontmatter page_count >= 71.
- index.md catalogues every new page.
- log.md carries a 2026-05-02 expand entry.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI_ROOT = REPO_ROOT / "knowledge/wikis/naval-architecture/wiki"

NEW_CONCEPT_PAGES = (
    "concepts/hull-form-geometry.md",
    "concepts/intact-stability-criteria.md",
    "concepts/damage-stability.md",
    "concepts/ship-resistance-components.md",
    "concepts/marine-propulsors.md",
    "concepts/propeller-theory.md",
    "concepts/wave-theory-and-spectra.md",
    "concepts/ship-structural-strength.md",
    "concepts/ship-weights-and-loading.md",
)

NEW_ENTITY_PAGES = (
    "entities/classification-societies.md",
)

ALL_NEW_PAGES = NEW_CONCEPT_PAGES + NEW_ENTITY_PAGES

REQUIRED_FRONTMATTER_KEYS = ("title", "tags", "added", "last_updated")

STANDARDS_BODIES_RE = re.compile(r"\b(IMO|ITTC|IACS|SNAME)\b")

# Reserved phrases per #2568. Case-insensitive.
RESERVED_PHRASES_RE = re.compile(
    r"\b(turning circle|tactical diameter|Nomoto|advance|transfer)\b",
    re.IGNORECASE,
)
# Tighter regex for the new pages: exclude generic English uses of "advance"
# and "transfer" that don't carry the maneuvering meaning. The new pages
# should not use the phrases at all in their domain meaning. We rely on the
# bullet-content of the new pages being domain-tight enough that the generic
# regex below is sufficient. If a future page legitimately needs the word
# "advance" in a non-maneuvering sense, the test below restricts to the
# narrow set {turning circle, tactical diameter, Nomoto}.
RESERVED_PHRASES_NARROW_RE = re.compile(
    r"\b(turning circle|tactical diameter|Nomoto)\b",
    re.IGNORECASE,
)

MAX_BODY_WORDS = 400

# Existing page that legitimately contains reserved phrases (the #2564 pack).
# Per W1-D MAJOR-3 the test must EXCLUDE this file from the reserved-phrase
# scan AND must enforce that the count of reserved-phrase matches in the file
# does not grow as a side effect of this expansion.
EXISTING_LEGITIMATE_RESERVED_FILE = (
    WIKI_ROOT / "concepts/maneuvering-validation-metrics.md"
)
# Baseline count snapshot taken 2026-05-02 prior to this expansion. Counted
# with RESERVED_PHRASES_RE over the entire file body. This number must not
# grow.
EXISTING_RESERVED_BASELINE = 7

# Bullet phrases that must NOT remain on the resistance-propulsion router page
# after the W1-D MAJOR-1 split.
RESISTANCE_PROPULSION_FORBIDDEN_BULLETS = (
    "Frictional resistance (Rf)",
    "Residuary resistance (Rr)",
    "Air resistance",
    "Appendage resistance",
    "Froude number regime",
    "Propeller open water characteristics",
    "Propeller-hull interaction",
    "Controllable pitch vs fixed pitch",
    "Azimuth thrusters",
    "Waterjets",
    "Podded propulsion",
    "Rudder-propellers / pod drives",
)

# Long-bullet phrases that must NOT remain on the stability router page after
# the W1-D MAJOR-2 reduction. Short references / pointer lines are fine.
STABILITY_FORBIDDEN_LONG_BULLETS = (
    "IMO, SOLAS requirements for minimum stability",
    "stability after compartment flooding; SOLAS subdivision requirements",
)


def _split_frontmatter(text: str) -> tuple[dict, str]:
    assert text.startswith("---\n"), "page must begin with YAML frontmatter"
    parts = text.split("---\n", 2)
    assert len(parts) == 3, "frontmatter must be closed with '---'"
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


def _page_text(rel_path: str) -> str:
    return (WIKI_ROOT / rel_path).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Per-page invariants
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rel_path", ALL_NEW_PAGES)
def test_all_ten_pages_exist(rel_path: str) -> None:
    p = WIKI_ROOT / rel_path
    assert p.is_file(), f"missing wiki page: {p.relative_to(REPO_ROOT)}"


@pytest.mark.parametrize("rel_path", ALL_NEW_PAGES)
def test_frontmatter_required_fields(rel_path: str) -> None:
    fm, _ = _split_frontmatter(_page_text(rel_path))
    for key in REQUIRED_FRONTMATTER_KEYS:
        assert fm.get(key), f"{rel_path}: frontmatter missing required key '{key}'"


@pytest.mark.parametrize("rel_path", ALL_NEW_PAGES)
def test_frontmatter_see_also_min_two(rel_path: str) -> None:
    fm, _ = _split_frontmatter(_page_text(rel_path))
    see_also = fm.get("see_also") or []
    assert isinstance(see_also, list), f"{rel_path}: see_also must be a list"
    assert len(see_also) >= 2, (
        f"{rel_path}: see_also must list >=2 entries; got {len(see_also)}"
    )


@pytest.mark.parametrize("rel_path", ALL_NEW_PAGES)
def test_see_also_paths_resolve(rel_path: str) -> None:
    fm, _ = _split_frontmatter(_page_text(rel_path))
    see_also = fm.get("see_also") or []
    for entry in see_also:
        target = WIKI_ROOT / entry
        assert target.is_file(), (
            f"{rel_path}: see_also entry {entry!r} does not resolve to an "
            f"existing file ({target.relative_to(REPO_ROOT)})"
        )


@pytest.mark.parametrize("rel_path", ALL_NEW_PAGES)
def test_at_least_one_standards_reference(rel_path: str) -> None:
    _, body = _split_frontmatter(_page_text(rel_path))
    assert STANDARDS_BODIES_RE.search(body), (
        f"{rel_path}: body must cite at least one of IMO/ITTC/IACS/SNAME"
    )


@pytest.mark.parametrize("rel_path", ALL_NEW_PAGES)
def test_word_count_under_400(rel_path: str) -> None:
    _, body = _split_frontmatter(_page_text(rel_path))
    word_count = len(body.split())
    assert 0 < word_count < MAX_BODY_WORDS, (
        f"{rel_path}: body word count {word_count} outside bound (0<N<{MAX_BODY_WORDS})"
    )


@pytest.mark.parametrize("rel_path", ALL_NEW_PAGES)
def test_no_pdf_extraction_markers(rel_path: str) -> None:
    """No 'Page N of M' stamps and no monster paragraphs (>80 words)."""
    _, body = _split_frontmatter(_page_text(rel_path))
    assert not re.search(r"\bPage \d+ of \d+\b", body), (
        f"{rel_path}: contains 'Page N of M' stamp suggesting raw PDF copy"
    )
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    flagged = [p for p in paragraphs if not p.startswith(("-", "*", "#")) and len(p.split()) > 80]
    assert not flagged, (
        f"{rel_path}: {len(flagged)} paragraph(s) exceed 80-word heuristic threshold"
    )


# ---------------------------------------------------------------------------
# #2568 reservation hygiene (W1-D MAJOR-3)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rel_path", ALL_NEW_PAGES)
def test_no_reservation_overlap_in_new_pages(rel_path: str) -> None:
    """New pages MUST NOT contain the narrow reserved-phrase set per #2568.

    The narrow set is {turning circle, tactical diameter, Nomoto}; the broader
    {advance, transfer} terms have generic-English uses and are checked only
    against the existing-page no-expansion contract below.
    """
    _, body = _split_frontmatter(_page_text(rel_path))
    matches = RESERVED_PHRASES_NARROW_RE.findall(body)
    assert not matches, (
        f"{rel_path}: new page contains reserved phrase(s): {matches!r} "
        f"— #2568 reservation"
    )


def test_no_expansion_of_reserved_phrases_in_existing_maneuvering_page() -> None:
    """The existing maneuvering-validation-metrics.md legitimately uses
    reserved phrases (per #2564 pack). This test pins the count so the W1-D
    expansion does not silently grow it. Per W1-D MAJOR-3.
    """
    text = EXISTING_LEGITIMATE_RESERVED_FILE.read_text(encoding="utf-8")
    matches = RESERVED_PHRASES_RE.findall(text)
    assert len(matches) <= EXISTING_RESERVED_BASELINE, (
        f"{EXISTING_LEGITIMATE_RESERVED_FILE.relative_to(REPO_ROOT)}: "
        f"reserved-phrase count grew from baseline "
        f"{EXISTING_RESERVED_BASELINE} to {len(matches)} — W1-D may have "
        f"silently expanded reserved-phrase usage; matches={matches!r}"
    )


# ---------------------------------------------------------------------------
# Cross-page content uniqueness (W1-D MAJOR-1 / MAJOR-2)
# ---------------------------------------------------------------------------


def test_no_redundant_content_between_old_and_new_pages() -> None:
    """resistance-propulsion.md must be reduced to a router (no detail bullets);
    stability.md must defer intact/damage criteria to sibling pages.

    This is the W1-D MAJOR-1 + MAJOR-2 cross-page content uniqueness check.
    """
    rp_text = _page_text("concepts/resistance-propulsion.md")
    rp_failures = [b for b in RESISTANCE_PROPULSION_FORBIDDEN_BULLETS if b in rp_text]
    assert not rp_failures, (
        f"concepts/resistance-propulsion.md still contains bullets that should "
        f"have been moved to ship-resistance-components.md / marine-propulsors.md / "
        f"propeller-theory.md: {rp_failures!r}"
    )

    stab_text = _page_text("concepts/stability.md")
    stab_failures = [b for b in STABILITY_FORBIDDEN_LONG_BULLETS if b in stab_text]
    assert not stab_failures, (
        f"concepts/stability.md still contains long criteria bullets that should "
        f"have been moved to intact-stability-criteria.md / damage-stability.md: "
        f"{stab_failures!r}"
    )


# ---------------------------------------------------------------------------
# Index + log invariants
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rel_path", ALL_NEW_PAGES)
def test_index_lists_page(rel_path: str) -> None:
    index_text = (WIKI_ROOT / "index.md").read_text(encoding="utf-8")
    assert rel_path in index_text, (
        f"index.md is missing a link to {rel_path}"
    )


def test_index_links_resolve() -> None:
    """Every relative .md link in index.md Concepts + Entities tables resolves."""
    index_text = (WIKI_ROOT / "index.md").read_text(encoding="utf-8")
    # match markdown links of the form [...](path.md) or [...](path.md#anchor)
    link_re = re.compile(r"\]\((?!https?://)([^)]+\.md)(?:#[^)]*)?\)")
    failures = []
    for m in link_re.finditer(index_text):
        rel = m.group(1)
        # index.md links use paths like "concepts/foo.md" or "entities/bar.md"
        # — relative to wiki/ root.
        target = (WIKI_ROOT / rel).resolve()
        if not target.is_file():
            failures.append(rel)
    assert not failures, f"index.md links do not resolve: {failures!r}"


def test_index_page_count_bumped() -> None:
    fm, _ = _split_frontmatter((WIKI_ROOT / "index.md").read_text(encoding="utf-8"))
    page_count = fm.get("page_count")
    assert isinstance(page_count, int) and page_count >= 71, (
        f"index.md page_count must be >=71 after W1-D expansion; got {page_count!r}"
    )


def test_log_entry_appended() -> None:
    log_text = (WIKI_ROOT / "log.md").read_text(encoding="utf-8")
    assert re.search(r"\[2026-05-02\]\s+expand\s*\|\s*naval-arch W1-D", log_text), (
        "log.md must carry a '[2026-05-02] expand | naval-arch W1-D' entry"
    )
