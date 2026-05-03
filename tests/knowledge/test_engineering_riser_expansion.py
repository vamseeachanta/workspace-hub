"""Test contract for the W3-D engineering-wiki riser sub-domain expansion.

Issue trail:
- Plan: docs/plans/2026-05-02-issue-2597-llm-wiki-W3D-engineering-riser-expansion.md
- Issue: https://github.com/vamseeachanta/workspace-hub/issues/2597
- Sibling: tests/knowledge/test_engineering_standards_dnv.py (W2-A pattern)
- Schema authority: knowledge/wikis/engineering/CLAUDE.md

Each of the 10 W3-D riser concept pages MUST:
1. Exist at the prescribed path under wiki/concepts/.
2. Carry frontmatter with required CLAUDE.md schema fields plus the `riser` tag.
3. Cite at least one standards body (API / DNV / ISO / BS) — by name, not by clause.
4. Cross-link at least 2 other engineering-wiki pages that exist on disk.
5. Stay below the 400-word concept-summary cap.
6. Maintain riser-topic dominance (boundary discipline) — riser keywords MUST NOT
   be eclipsed by mooring/umbilical/pipeline keywords.
7. At least one page MUST link back to the existing viv-riser-fatigue.md anchor.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CONCEPTS_DIR = REPO_ROOT / "knowledge/wikis/engineering/wiki/concepts"
ENG_WIKI = REPO_ROOT / "knowledge/wikis/engineering/wiki"
STANDARDS_WIKI = REPO_ROOT / "knowledge/wikis/engineering-standards/wiki/standards"

EXPECTED_PAGES = (
    "riser-configurations",
    "riser-steel-catenary-design",
    "riser-top-tensioned-design",
    "riser-flexible-design",
    "riser-hybrid-tower",
    "riser-drilling-system",
    "riser-global-analysis-load-cases",
    "riser-soil-interaction",
    "riser-installation-methods",
    "riser-composite-design",
)

# Standards-body name patterns — the page must NAME a standards body (no clauses).
STANDARDS_NAME_PATTERNS = (
    re.compile(r"\bAPI\s*RP\s*1?7[BJ]\b", re.IGNORECASE),
    re.compile(r"\bAPI\s*RP\s*16Q\b", re.IGNORECASE),
    re.compile(r"\bAPI\s*STD\s*2RD\b", re.IGNORECASE),
    re.compile(r"\bAPI\s*RP\s*2RD\b", re.IGNORECASE),
    re.compile(r"\bAPI\s*SPEC\s*17J\b", re.IGNORECASE),
    re.compile(r"\bDNV-?OS-?F201\b", re.IGNORECASE),
    re.compile(r"\bDNV-?RP-?F202\b", re.IGNORECASE),
    re.compile(r"\bDNV-?RP-?F204\b", re.IGNORECASE),
    re.compile(r"\bDNV-?RP-?H103\b", re.IGNORECASE),
    re.compile(r"\bISO\s*19901-?7\b", re.IGNORECASE),
    re.compile(r"\bISO\s*13624-?1\b", re.IGNORECASE),
    re.compile(r"\bISO\s*13628-?[27]\b", re.IGNORECASE),
    re.compile(r"\bBS\s*13625\b", re.IGNORECASE),
)

# Riser-keyword set (positive presence).
RISER_KEYWORDS_RE = re.compile(
    r"\b(riser|SCR|TTR|catenary|flexible riser|hybrid tower|hybrid riser|drilling riser|TDP|TDZ|tensioner|stress joint|taper joint|keel joint|bend stiffener|end-fitting|tensile armour|tensile-armour|pressure-armour|pressure armour|carcass|SLOR|composite riser)\b",
    re.IGNORECASE,
)

# Non-riser keywords — riser pages must NOT be dominated by these.
NON_RISER_KEYWORDS_RE = re.compile(
    r"\b(mooring|umbilical|pipeline|flowline)\b",
    re.IGNORECASE,
)

# Banned VIV-fatigue-mechanics phrases (those belong on viv-riser-fatigue.md).
BANNED_VIV_PHRASES = (
    "rainflow counting",
    "Strouhal",
    "lock-in",
    "Iwan-Blevins",
    "S-N curve",
    "S-N curves",
    "Miner's rule",
    "DFF =",
    "Design Fatigue Factor =",
)

WIKILINK_RE = re.compile(r"\[\[([a-z0-9_-]+)\]\]")
RELATIVE_MD_LINK_RE = re.compile(r"\]\(((?:\.\./)+[a-z0-9_/-]+\.md)\)")


def _page_path(stem: str) -> Path:
    return CONCEPTS_DIR / f"{stem}.md"


def _split_frontmatter(text: str) -> tuple[dict, str]:
    assert text.startswith("---\n"), "page must begin with YAML frontmatter"
    parts = text.split("---\n", 2)
    assert len(parts) == 3, "frontmatter must be closed with '---'"
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


def _h2_sections(body: str) -> dict[str, str]:
    """Return a dict of H2 heading -> section body text."""
    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines)
            current_heading = line[3:].strip()
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)
    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines)
    return sections


# -----------------------------------------------------------------------------
# Existence and frontmatter
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_page_exists(stem: str) -> None:
    p = _page_path(stem)
    assert p.is_file(), f"missing wiki page: {p.relative_to(REPO_ROOT)}"


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_required_fields(stem: str) -> None:
    """CLAUDE.md schema: title, tags, added, last_updated all required."""
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    for field in ("title", "tags", "added", "last_updated"):
        assert fm.get(field), f"{stem}: required field {field!r} missing or empty"
    assert isinstance(fm["tags"], list) and fm["tags"], (
        f"{stem}: tags must be a non-empty list"
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_tag_riser(stem: str) -> None:
    """Each new page must carry the `riser` tag for cluster discoverability."""
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    tags = [str(t).lower() for t in fm.get("tags", [])]
    assert "riser" in tags, f"{stem}: tags must include `riser`; got {tags!r}"


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_frontmatter_dates_2026_05_02(stem: str) -> None:
    """Per plan: added=2026-05-02, last_updated=2026-05-02."""
    fm, _ = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    assert str(fm["added"]) == "2026-05-02", (
        f"{stem}: added={fm['added']!r}; expected 2026-05-02"
    )
    assert str(fm["last_updated"]) == "2026-05-02", (
        f"{stem}: last_updated={fm['last_updated']!r}; expected 2026-05-02"
    )


# -----------------------------------------------------------------------------
# Standards citation (name only, no clauses)
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_at_least_one_standards_reference(stem: str) -> None:
    """Each page must NAME at least one standards body."""
    text = _page_path(stem).read_text(encoding="utf-8")
    matches = [pat.pattern for pat in STANDARDS_NAME_PATTERNS if pat.search(text)]
    assert matches, (
        f"{stem}: page must cite at least one standards body by name; none matched"
    )


# -----------------------------------------------------------------------------
# Cross-link discipline
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_at_least_two_cross_links(stem: str) -> None:
    """Each page must contain >=2 resolvable [[wikilink]] OR ../ relative-md
    cross-references to other engineering-wiki or sibling-wiki pages on disk.
    """
    text = _page_path(stem).read_text(encoding="utf-8")
    resolvable = 0

    # [[wikilink]] -> resolves under wiki/concepts/, wiki/entities/, wiki/sources/
    for slug in WIKILINK_RE.findall(text):
        for subdir in ("concepts", "entities", "sources", "standards", "workflows"):
            candidate = ENG_WIKI / subdir / f"{slug}.md"
            if candidate.exists():
                resolvable += 1
                break

    # Relative ../ markdown links -> resolve from the page's directory
    page_dir = _page_path(stem).parent
    for rel in RELATIVE_MD_LINK_RE.findall(text):
        candidate = (page_dir / rel).resolve()
        if candidate.exists():
            resolvable += 1

    assert resolvable >= 2, (
        f"{stem}: only {resolvable} resolvable cross-links found; need >=2"
    )


def test_at_least_one_cross_link_to_viv_riser_fatigue() -> None:
    """At least one of the 10 new pages must link back to viv-riser-fatigue
    for cluster cross-stitch."""
    found = False
    for stem in EXPECTED_PAGES:
        text = _page_path(stem).read_text(encoding="utf-8")
        if "viv-riser-fatigue" in text:
            found = True
            break
    assert found, (
        "no new riser page links back to viv-riser-fatigue; "
        "cluster cross-stitch missing"
    )


# -----------------------------------------------------------------------------
# Word-count discipline
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_word_count_under_400(stem: str) -> None:
    """Concept-summary discipline per #2482 — no chapter copy."""
    body = _page_path(stem).read_text(encoding="utf-8")
    assert len(body.split()) < 400, (
        f"{stem}: word count {len(body.split())} exceeds 400-word concept cap"
    )


# -----------------------------------------------------------------------------
# Boundary discipline — riser-topic dominance per H2 section + positive presence
# -----------------------------------------------------------------------------

WHITELISTED_SECTIONS = frozenset({"Scope", "Out of Scope"})


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_section_dominance_riser_over_non_riser(stem: str) -> None:
    """For each non-whitelisted H2 section, riser-keyword count must be >=
    non-riser-keyword count. Whitelist: ## Scope, ## Out of Scope (boundary
    callouts are legitimate adjacency).
    """
    _, body = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    sections = _h2_sections(body)
    failures: list[str] = []
    for heading, section_body in sections.items():
        if heading in WHITELISTED_SECTIONS:
            continue
        riser_hits = len(RISER_KEYWORDS_RE.findall(section_body))
        non_riser_hits = len(NON_RISER_KEYWORDS_RE.findall(section_body))
        if non_riser_hits > riser_hits:
            failures.append(
                f"{stem} :: ## {heading} :: non-riser={non_riser_hits} > riser={riser_hits}"
            )
    assert not failures, (
        "Riser dominance violated in non-whitelisted sections:\n"
        + "\n".join(failures)
    )


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_riser_topic_dominance_positive(stem: str) -> None:
    """Each page must contain >=3 riser-keyword hits in body text — proves
    riser is the dominant topic and complements the section-dominance test
    against synonym-attack false negatives.
    """
    _, body = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    hits = len(RISER_KEYWORDS_RE.findall(body))
    assert hits >= 3, (
        f"{stem}: only {hits} riser-keyword hits in body; need >=3"
    )


# -----------------------------------------------------------------------------
# No-redundancy with viv-riser-fatigue mechanics
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_no_redundant_viv_mechanics_content(stem: str) -> None:
    """New pages MUST NOT re-introduce S-N tables, DFF tables, rainflow prose,
    or VIV-mechanics jargon (Strouhal, lock-in, Iwan-Blevins) OUTSIDE of the
    `## Scope` boundary callout. The Scope section is whitelisted because
    legitimate boundary discipline says "X is NOT covered here, see Y" — that
    must mention the keyword to be useful. Those keywords belong on
    viv-riser-fatigue.md / sn-curve-fatigue-definitions.md as substantive
    content.
    """
    _, body = _split_frontmatter(_page_path(stem).read_text(encoding="utf-8"))
    sections = _h2_sections(body)
    # Strip the Scope section from the leak-check surface
    non_scope_text = "\n".join(
        sec_body for heading, sec_body in sections.items()
        if heading not in WHITELISTED_SECTIONS
    )
    leaks = [phrase for phrase in BANNED_VIV_PHRASES if phrase in non_scope_text]
    assert leaks == [], (
        f"{stem}: page contains banned VIV-mechanics phrases outside `## Scope` "
        f"(must live on viv-riser-fatigue.md only): {leaks!r}"
    )


# Pages where the `fatigue` cap is relaxed because the page's subject
# legitimately enumerates fatigue as one named limit state alongside others.
# The load-case taxonomy MUST cite FLS (Fatigue Limit State); capping it to 5
# would force pruning of legitimate taxonomy content. The cap remains in force
# for all design-state pages where fatigue is adjacent rather than the topic.
FATIGUE_CAP_EXEMPT = frozenset({"riser-global-analysis-load-cases"})


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_fatigue_noun_capped(stem: str) -> None:
    """Cap occurrences of `fatigue` to <=5 per page — design-state pages
    should reference fatigue in passing only; the canonical fatigue page is
    viv-riser-fatigue.md. The load-case taxonomy page is exempt because it
    enumerates FLS (Fatigue Limit State) as one of four named limit states.
    """
    if stem in FATIGUE_CAP_EXEMPT:
        pytest.skip(f"{stem}: exempt from fatigue-noun cap (taxonomy page)")
    text = _page_path(stem).read_text(encoding="utf-8")
    count = len(re.findall(r"\bfatigue\b", text, re.IGNORECASE))
    assert count <= 5, (
        f"{stem}: `fatigue` appears {count} times; cap is <=5 (design-state "
        "pages should defer fatigue mechanics to viv-riser-fatigue.md)"
    )


# -----------------------------------------------------------------------------
# Past-tense drift check (per memory feedback_plan_past_tense_artifact_claims.md)
# -----------------------------------------------------------------------------


PAST_TENSE_ANTI_PATTERNS = (
    re.compile(r"\bwe added\b", re.IGNORECASE),
    re.compile(r"\bwe created\b", re.IGNORECASE),
    re.compile(r"\bthis page was\b", re.IGNORECASE),
)


@pytest.mark.parametrize("stem", EXPECTED_PAGES)
def test_no_past_tense_artifact_drift(stem: str) -> None:
    """No new page should contain past-tense self-claims like 'we added' or
    'this page was'. Concept pages describe the subject, not their own
    creation.
    """
    text = _page_path(stem).read_text(encoding="utf-8")
    matches = [pat.pattern for pat in PAST_TENSE_ANTI_PATTERNS if pat.search(text)]
    assert not matches, (
        f"{stem}: past-tense artifact-drift phrases present: {matches!r}"
    )
