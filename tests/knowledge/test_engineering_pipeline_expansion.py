"""Engineering wiki — W4-D pipeline sub-domain expansion (issue #2602) tests.

Plan: docs/plans/2026-05-03-issue-2602-llm-wiki-W4D-engineering-pipeline-expansion.md
Sibling/precedent: tests/knowledge/test_engineering_standards_dnv.py (W2-A pattern)
Governance companion: tests/governance/test_2471_citation_scope.py

This module asserts the per-page contract for the 10 new
``knowledge/wikis/engineering/wiki/concepts/pipeline-*.md`` pages:

    - file existence
    - frontmatter required fields, ``pipeline`` tag, ``added`` date
    - ≥1 standards body name (DNV / API / ASME / ISO)
    - ≥2 cross-link references that resolve on disk
    - cluster cross-stitch to the two pre-existing pipeline pages
    - homonym disambiguation (no link to ``orcawave-to-orcaflex-pipeline``)
    - section-dominance scope-creep check (riser/mooring/umbilical)
    - positive pipeline-topic-dominance check
    - per-page word count under 400
    - no redundant corroded-FFS or free-span-VIV content
    - canonical forward-reference marker invariant for not-yet-codified
      standards (paired with the existing relative-wikilink for already-codified
      standards)
    - explicit no-#2471-path-sanction-citation guard (#2596 W3-C erratum)

The page-count and Concepts-table-heading bumps in ``index.md`` are intentionally
NOT asserted here because the index is shared with parallel agents (#2597 riser
expansion and others) and the main session reconciles index updates from the
file set during the commit phase per the plan's parallel-write-only contract.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI_ROOT = REPO_ROOT / "knowledge/wikis/engineering/wiki"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
STANDARDS_DIR = WIKI_ROOT / "standards"

NEW_PAGES = (
    "pipeline-route-selection",
    "pipeline-on-bottom-stability",
    "pipeline-lateral-buckling",
    "pipeline-upheaval-buckling",
    "pipeline-walking",
    "pipeline-soil-interaction",
    "pipeline-installation-methods",
    "pipeline-end-expansion-spool-design",
    "pipeline-trawl-impact-protection",
    "pipeline-coatings",
)

ADDED_DATE = "2026-05-03"

STANDARDS_NAME_PATTERNS = (
    r"DNV-ST-F101",
    r"DNV-RP-F101",
    r"DNV-RP-F105",
    r"DNV-RP-F106",
    r"DNV-RP-F107",
    r"DNV-RP-F109",
    r"DNV-RP-F110",
    r"DNV-RP-F111",
    r"DNV-RP-F114",
    r"DNV-RP-F116",
    r"DNV-RP-H103",
    r"DNV-RP-C205",
    r"API\s?RP\s?1111",
    r"API\s?RP\s?1102",
    r"API\s?RP\s?5L2",
    r"ASME\s?B31\.4",
    r"ASME\s?B31\.8",
    r"ISO\s?13623",
)

PIPELINE_TYPOLOGY_TERMS = (
    r"\bpipeline\b",
    r"\bflowline\b",
    r"\bpipelay\b",
    r"\bS-lay\b",
    r"\bJ-lay\b",
    r"\breel-lay\b",
    r"\bon-bottom stability\b",
    r"\blateral buckling\b",
    r"\bupheaval buckling\b",
    r"\bwalking\b",
    r"\bspool\b",
    r"\bPLET\b",
    r"\btrawl\b",
    r"\bFBE\b",
    r"\b3LPE\b",
    r"\b3LPP\b",
    r"\bcoating\b",
    r"\bsubsea\b",
)

# Section-dominance keyword sets (for scope-creep test)
NON_PIPELINE_KEYWORDS = re.compile(
    r"\b(riser|SCR|TTR|mooring|umbilical)\b", re.IGNORECASE
)
PIPELINE_KEYWORDS = re.compile(
    r"\b(pipeline|flowline|pipelay|S-lay|J-lay|reel-lay|on-bottom|"
    r"free-span|buckling|spool|PLET|trawl|coating|FBE|3LPE|3LPP|"
    r"subsea|tow-out)\b",
    re.IGNORECASE,
)
WHITELIST_HEADINGS = frozenset({"Scope", "Out of Scope"})

# Forbidden-content regexes (boundary against pipeline-integrity-assessment.md
# and free-span-viv-fatigue.md).
CORRODED_FFS_FORBIDDEN = (
    r"\bRSF\b",
    r"\bRSFa\b",
    r"\bLevel 1 assessment\b",
    r"\bLevel 2 assessment\b",
    r"\bLevel 3 assessment\b",
    r"\bpoint defect\b",
    r"\bpatch corrosion\b",
    r"\bFolias factor\b",
)
FREE_SPAN_VIV_FORBIDDEN = (
    r"\bStrouhal\b",
    r"\block-in\b",
    r"\bcross-flow VIV\b",
    r"\bin-line VIV\b",
    r"\bIwan-Blevins\b",
)
CORROSION_TOKEN_RE = re.compile(r"\bcorrosion\b", re.IGNORECASE)
VIV_TOKEN_RE = re.compile(r"\bVIV\b")

WIKILINK_RE = re.compile(r"\[\[([^\]\|]+?)(?:\|[^\]]+)?\]\]")
RELATIVE_LINK_RE = re.compile(r"\]\((\.\./?[^\s\)]+\.md)\)")
TODO_W4_MARKER_RE = re.compile(
    r"<!--\s*TODO\(W4-codify\):\s*replace external URL with "
    r"\[\[\.\./standards/[^\]]+\]\]\s*when standards page lands\s*-->"
)

PAST_TENSE_DRIFT_RE = re.compile(
    r"\b(we added|we created|this page was|completed today|delivered today)\b",
    re.IGNORECASE,
)


def _page_path(stem: str) -> Path:
    return CONCEPTS_DIR / f"{stem}.md"


def _split_frontmatter(text: str) -> tuple[dict, str]:
    assert text.startswith("---\n"), "page must begin with YAML frontmatter"
    parts = text.split("---\n", 2)
    assert len(parts) == 3, "frontmatter must be closed with '---'"
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


def _all_text(stem: str) -> str:
    return _page_path(stem).read_text(encoding="utf-8")


def _h2_sections(body: str) -> list[tuple[str, str]]:
    """Return (heading, section-body) pairs split at H2 boundaries."""
    sections: list[tuple[str, str]] = []
    current_heading = "(prologue)"
    current_lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines)))
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_heading, "\n".join(current_lines)))
    return sections


# ---------------------------------------------------------------------------
# Existence + frontmatter
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_all_ten_pages_exist(stem: str) -> None:
    p = _page_path(stem)
    assert p.is_file(), f"missing wiki page: {p.relative_to(REPO_ROOT)}"


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_frontmatter_required_fields(stem: str) -> None:
    fm, _ = _split_frontmatter(_all_text(stem))
    for field in ("title", "tags", "added", "last_updated"):
        assert fm.get(field), f"{stem}: frontmatter missing required field {field!r}"


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_frontmatter_tag_pipeline(stem: str) -> None:
    fm, _ = _split_frontmatter(_all_text(stem))
    tags = fm.get("tags") or []
    assert "pipeline" in tags, f"{stem}: 'pipeline' must be in tags; got {tags!r}"


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_frontmatter_added_date_2026_05_03(stem: str) -> None:
    fm, _ = _split_frontmatter(_all_text(stem))
    added = str(fm.get("added"))
    assert added == ADDED_DATE, f"{stem}: added must be {ADDED_DATE!r}; got {added!r}"


# ---------------------------------------------------------------------------
# Standards / cross-links
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_at_least_one_standards_reference(stem: str) -> None:
    text = _all_text(stem)
    matches = [p for p in STANDARDS_NAME_PATTERNS if re.search(p, text)]
    assert matches, (
        f"{stem}: must NAME at least one standards body "
        f"(DNV / API / ASME / ISO)"
    )


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_at_least_two_cross_links(stem: str) -> None:
    text = _all_text(stem)
    wikilinks = WIKILINK_RE.findall(text)
    rel_links = RELATIVE_LINK_RE.findall(text)
    total = len(wikilinks) + len(rel_links)
    assert total >= 2, (
        f"{stem}: must contain ≥2 wiki cross-link references; got {total} "
        f"(wikilinks={wikilinks!r}, rel_links={rel_links!r})"
    )


HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _strip_html_comments(text: str) -> str:
    return HTML_COMMENT_RE.sub("", text)


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_cross_links_resolve_on_disk(stem: str) -> None:
    """Every wikilink/relative-link target must resolve to an existing file.

    Resolution rules:
      - ``[[../foo]]`` -> ``CONCEPTS_DIR / .. / foo.md`` (typical when the
        slug starts with ``../``); plain ``[[slug]]`` -> ``CONCEPTS_DIR / slug.md``.
      - Relative links ``](../...md)`` resolve relative to the page's parent
        directory.

    HTML comments (``<!-- ... -->``) are stripped before scanning so the
    placeholder wikilinks inside ``TODO(W4-codify)`` markers do not trip the
    test — those placeholders intentionally point at not-yet-codified
    standards pages.
    """
    page = _page_path(stem)
    text = _strip_html_comments(page.read_text(encoding="utf-8"))
    base = page.parent

    for target in WIKILINK_RE.findall(text):
        slug = target.strip()
        if slug.startswith("../"):
            candidate = (base / f"{slug}.md").resolve()
        else:
            candidate = (CONCEPTS_DIR / f"{slug}.md").resolve()
        assert candidate.is_file(), (
            f"{stem}: wikilink [[{target}]] does not resolve "
            f"(tried {candidate})"
        )

    for target in RELATIVE_LINK_RE.findall(text):
        candidate = (base / target).resolve()
        assert candidate.is_file(), (
            f"{stem}: relative link {target!r} does not resolve "
            f"(tried {candidate})"
        )


def test_at_least_one_cross_link_to_existing_pipeline_page() -> None:
    """≥1 of the 10 new pages must link to ``pipeline-integrity-assessment``
    AND ≥1 must link to ``free-span-viv-fatigue`` (cluster cross-stitch)."""
    integrity_hit = False
    span_hit = False
    for stem in NEW_PAGES:
        text = _all_text(stem)
        if "pipeline-integrity-assessment" in text:
            integrity_hit = True
        if "free-span-viv-fatigue" in text:
            span_hit = True
    assert integrity_hit, (
        "no new page links to concepts/pipeline-integrity-assessment.md"
    )
    assert span_hit, (
        "no new page links to concepts/free-span-viv-fatigue.md"
    )


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_no_cross_link_to_workflows_pipeline(stem: str) -> None:
    """Homonym disambiguation: no new page may link to the data-pipeline workflow."""
    text = _all_text(stem)
    assert "orcawave-to-orcaflex-pipeline" not in text, (
        f"{stem}: must not cross-link to workflows/orcawave-to-orcaflex-pipeline.md"
    )


# ---------------------------------------------------------------------------
# Scope discipline
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_no_scope_creep_into_riser_mooring_umbilical(stem: str) -> None:
    """Per-H2-section keyword-ratio check.

    Sections titled ``## Scope`` or ``## Out of Scope`` are whitelisted
    (boundary callouts allowed). Every other section's pipeline-keyword count
    must be ≥ its non-pipeline-keyword count.
    """
    _, body = _split_frontmatter(_all_text(stem))
    for heading, section_body in _h2_sections(body):
        if heading in WHITELIST_HEADINGS:
            continue
        non_pipeline = len(NON_PIPELINE_KEYWORDS.findall(section_body))
        pipeline = len(PIPELINE_KEYWORDS.findall(section_body))
        assert pipeline >= non_pipeline, (
            f"{stem}: H2 section {heading!r} has scope creep "
            f"(non-pipeline={non_pipeline}, pipeline={pipeline})"
        )


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_pipeline_topic_dominance_positive(stem: str) -> None:
    """Each page must contain ≥3 occurrences of pipeline-typology terms."""
    text = _all_text(stem)
    hits = sum(len(re.findall(p, text)) for p in PIPELINE_TYPOLOGY_TERMS)
    assert hits >= 3, (
        f"{stem}: only {hits} pipeline-typology hits; ≥3 required"
    )


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_word_count_under_400(stem: str) -> None:
    _, body = _split_frontmatter(_all_text(stem))
    word_count = len(body.split())
    assert word_count < 400, (
        f"{stem}: body word count {word_count} exceeds 400-word concept-summary cap"
    )


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_no_redundant_corroded_ffs_content_in_new_pages(stem: str) -> None:
    text = _all_text(stem)
    matches = [p for p in CORRODED_FFS_FORBIDDEN if re.search(p, text)]
    assert not matches, (
        f"{stem}: forbidden corroded-FFS terms present: {matches!r}"
    )
    corrosion_hits = len(CORROSION_TOKEN_RE.findall(text))
    assert corrosion_hits <= 5, (
        f"{stem}: 'corrosion' occurs {corrosion_hits} times (cap 5)"
    )


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_no_redundant_free_span_viv_content_in_new_pages(stem: str) -> None:
    text = _all_text(stem)
    matches = [p for p in FREE_SPAN_VIV_FORBIDDEN if re.search(p, text)]
    assert not matches, (
        f"{stem}: forbidden free-span VIV-mechanics terms present: {matches!r}"
    )
    viv_hits = len(VIV_TOKEN_RE.findall(text))
    assert viv_hits <= 3, f"{stem}: 'VIV' occurs {viv_hits} times (cap 3)"


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_no_past_tense_artifact_drift(stem: str) -> None:
    text = _all_text(stem)
    matches = PAST_TENSE_DRIFT_RE.findall(text)
    assert not matches, (
        f"{stem}: past-tense artifact-claim drift detected: {matches!r}"
    )


# ---------------------------------------------------------------------------
# Forward-reference marker invariant
# ---------------------------------------------------------------------------


def _codeids_with_existing_local_standards_page() -> set[str]:
    """Return code-id stems of standards pages that exist locally on disk
    in the ENGINEERING wiki (paired-wikilink target). Cross-wiki targets
    (``../../../engineering-standards/wiki/standards/...``) are accepted
    as wikilinks too but are scored separately below."""
    if not STANDARDS_DIR.is_dir():
        return set()
    return {p.stem for p in STANDARDS_DIR.glob("*.md")}


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_forward_reference_markers_present(stem: str) -> None:
    """For every external standards-body URL appearing on a page where the
    corresponding standards page does NOT exist locally OR cross-wiki, the
    citation MUST be paired with the canonical TODO(W4-codify) HTML comment.
    """
    text = _all_text(stem)
    # Lines carrying an external standards-body URL (dnv.com / api.org /
    # asme.org / iso.org) must EITHER (a) be paired with the marker on the
    # same line (or the line immediately following), OR (b) the page must
    # also carry a wikilink-resolved cross-wiki standards reference for the
    # same standards body — but the simpler invariant we enforce is the
    # marker pairing because it is mechanically detectable.
    url_re = re.compile(r"https?://(?:www\.)?(dnv|api|asme|iso)\.[a-z]+(?:/[^\s)]*)?")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not url_re.search(line):
            continue
        # The marker may be inline OR on the next non-empty line.
        window = line
        if i + 1 < len(lines):
            window = window + "\n" + lines[i + 1]
        assert TODO_W4_MARKER_RE.search(window), (
            f"{stem}: line {i + 1} carries an external standards-body URL "
            f"without the canonical TODO(W4-codify) marker:\n  {line!r}"
        )


def test_forward_reference_marker_count_emit(capsys: pytest.CaptureFixture) -> None:
    """Emit a count + file list of pending TODO(W4-codify) markers across the
    10 new pages so a future codification plan can use this as a deletion
    checklist. Asserts the count is recorded; does not fail on count > 0.
    """
    counts: dict[str, int] = {}
    for stem in NEW_PAGES:
        text = _all_text(stem)
        counts[stem] = text.count("TODO(W4-codify)")
    total = sum(counts.values())
    print(f"\n[W4-codify] pending markers across {len(NEW_PAGES)} pages: {total}")
    for stem, n in counts.items():
        if n:
            print(f"  - {stem}: {n}")
    assert total >= 0  # informational; do not block on >0


@pytest.mark.parametrize("stem", NEW_PAGES)
def test_codified_standard_uses_wikilink_when_local_page_exists(stem: str) -> None:
    """If a new page mentions DNV-RP-F101 or DNV-RP-F105 (already-codified
    in the local engineering wiki standards/ directory), the relative
    wikilink ``[[../standards/<code-id>]]`` must be present (no bare external
    URL stand-in)."""
    text = _all_text(stem)
    local_codeids = _codeids_with_existing_local_standards_page()
    for codeid_token, kebab in (("DNV-RP-F101", "dnv-rp-f101"),
                                ("DNV-RP-F105", "dnv-rp-f105")):
        if codeid_token in text and kebab in local_codeids:
            assert f"[[../standards/{kebab}]]" in text, (
                f"{stem}: mentions {codeid_token} but missing the wikilink "
                f"[[../standards/{kebab}]] (already-codified standard must "
                "use wikilink, not bare external URL)"
            )


# ---------------------------------------------------------------------------
# #2471 path-sanction over-citation guard (W3-C erratum)
# ---------------------------------------------------------------------------


def test_no_2471_path_sanction_citation() -> None:
    """Per W3-C (#2596) erratum: this test file and the 10 new pages must NOT
    cite #2471 as a generalized path-sanction. A bare reference must be
    allowed only if it lives inside an explicit boundary-callout context
    naming CSA-Z276 or the W3-C erratum.

    Because the 10 concept pages should not need to mention #2471 at all,
    the strict assertion here is: zero ``#2471`` substrings in any of the
    10 pages. This avoids any chance of accidentally seeding a future
    over-citation cascade out of these freshly-authored pages.
    """
    offenders: list[tuple[str, int, str]] = []
    for stem in NEW_PAGES:
        for i, line in enumerate(_all_text(stem).splitlines(), start=1):
            if "#2471" in line:
                offenders.append((stem, i, line))
    assert not offenders, (
        "concept pages should not cite #2471 as a path-sanction "
        "(per W3-C #2596 erratum); offenders:\n"
        + "\n".join(f"  {s}:{i}: {l}" for s, i, l in offenders)
    )
