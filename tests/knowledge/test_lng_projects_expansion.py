"""Acceptance tests for issue #2612 — lng-projects W5-C topical expansion.

Per the plan at
``docs/plans/2026-05-03-issue-2612-llm-wiki-W5C-lng-projects-expansion.md``,
this test module enforces:

- 8 new concept pages exist on disk under ``knowledge/wikis/lng-projects/wiki/concepts/``
- frontmatter contract (``title``, ``tags``, ``added``, ``last_updated``,
  ``see_also`` >= 2)
- per-page presence of >= 1 named standards body
- noun-phrase reservation for #2541 (SESA / Doris-62092) and #2544
  (Woodfibre / ACMA-31522) — both literal and generalized regex forms
- positive-list assertion that workspace-hub-internal corpus identifiers
  (ACMA project codes, Doris project codes) are NEVER referenced in the
  new concept pages
- word-count discipline (<= 400 words/page)
- ``index.md`` lists the new pages and ``page_count`` is bumped
- routing guard: NO ``wiki/standards/`` directory created in lng-projects
  (lng-projects is outside the routing-principle scope per memory
  ``project_wiki_standards_path_decision.md`` and the #2615 W5-D umbrella
  sanction did NOT extend routing to lng-projects)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI_ROOT = REPO_ROOT / "knowledge" / "wikis" / "lng-projects" / "wiki"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
STANDARDS_DIR = WIKI_ROOT / "standards"
INDEX = WIKI_ROOT / "index.md"
LOG = WIKI_ROOT / "log.md"

NEW_CONCEPT_SLUGS: tuple[str, ...] = (
    "lng-project-lifecycle",
    "lng-liquefaction-processes",
    "lng-storage-tanks",
    "lng-marine-transfer-systems",
    "lng-process-safety",
    "lng-project-shapes",
    "lng-boil-off-gas-management",
    "lng-regulatory-framework",
)

NEW_CONCEPT_PATHS: tuple[Path, ...] = tuple(
    CONCEPTS_DIR / f"{slug}.md" for slug in NEW_CONCEPT_SLUGS
)

# Per dispatch: BLOCK these literal noun-phrases (reserved for #2541 / #2544
# and other modules / specs). Plus the plan's generalized regexes for any
# future ACMA / Doris project code.
RESERVED_LITERAL_PHRASES: tuple[str, ...] = (
    "SESA",
    "Woodfibre",
    "ACMA-31522",
    "Doris-62092",
)

RESERVED_GENERALIZED_PATTERN = re.compile(
    r"\b(SESA|Woodfibre|ACMA[- ]?(?:project[- ]?)?\d{4,6}|Doris[- ]?(?:project[- ]?)?\d{4,6})\b",
    re.IGNORECASE,
)

# Positive-list / known-bad workspace-hub-internal corpus identifiers
INTERNAL_CORPUS_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b31522\b"),
    re.compile(r"\b62092\b"),
    re.compile(r"\bACMA[- _]?project\b", re.IGNORECASE),
    re.compile(r"\bDoris[- _]?project\b", re.IGNORECASE),
)

STANDARDS_BODY_NAMES: tuple[str, ...] = (
    "NFPA",
    "EN 1473",
    "EN1473",
    "IGC",
    "SIGTTO",
    "OCIMF",
    "IACS",
    "ABS",
    "DNV",
    "IMO",
    "API",
    "EEMUA",
    "CEN",
)

WORD_COUNT_LIMIT = 400


# ---------------------------------------------------------------------------
# Frontmatter parser (no PyYAML dependency)
# ---------------------------------------------------------------------------

def _split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---"):
        return {}, text
    end_idx = text.find("\n---", 3)
    if end_idx == -1:
        return {}, text
    fm_block = text[3:end_idx].strip()
    body = text[end_idx + 4 :].lstrip("\n")

    fm: dict[str, object] = {}
    current_key: str | None = None
    current_list: list[str] | None = None
    for raw_line in fm_block.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") or line.startswith("- "):
            if current_list is None:
                continue
            value = line.split("- ", 1)[1].strip().strip('"').strip("'")
            current_list.append(value)
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "":
            current_list = []
            fm[key] = current_list
            current_key = key
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                fm[key] = []
            else:
                items = [
                    p.strip().strip('"').strip("'")
                    for p in inner.split(",")
                ]
                fm[key] = items
            current_list = None
            current_key = key
        else:
            fm[key] = value.strip('"').strip("'")
            current_list = None
            current_key = key
    return fm, body


def _read_page(path: Path) -> tuple[dict[str, object], str]:
    return _split_frontmatter(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_all_eight_pages_exist():
    missing = [str(p.relative_to(REPO_ROOT)) for p in NEW_CONCEPT_PATHS if not p.exists()]
    assert not missing, f"missing concept pages: {missing}"


def test_no_standards_directory_created():
    """Routing guard: lng-projects is NOT in the wiki/standards/ routing
    principle scope per memory ``project_wiki_standards_path_decision.md``
    and was NOT extended by the #2615 W5-D umbrella sanction."""
    assert not STANDARDS_DIR.exists(), (
        "wiki/standards/ must not be created in lng-projects — routing principle "
        "is sanctioned only for {marine-engineering, engineering, naval-architecture, "
        "engineering-standards, asset-management}; #2615 did not extend it to lng-projects"
    )


@pytest.mark.parametrize("path", NEW_CONCEPT_PATHS, ids=NEW_CONCEPT_SLUGS)
def test_frontmatter_required_fields(path: Path):
    fm, _ = _read_page(path)
    for required in ("title", "tags", "added", "last_updated"):
        assert required in fm and fm[required], (
            f"{path.relative_to(REPO_ROOT)} missing or empty frontmatter field {required!r}"
        )


@pytest.mark.parametrize("path", NEW_CONCEPT_PATHS, ids=NEW_CONCEPT_SLUGS)
def test_frontmatter_see_also_min_two(path: Path):
    fm, _ = _read_page(path)
    see_also = fm.get("see_also") or []
    assert isinstance(see_also, list) and len(see_also) >= 2, (
        f"{path.relative_to(REPO_ROOT)} must list >= 2 see_also entries; got {see_also!r}"
    )


@pytest.mark.parametrize("path", NEW_CONCEPT_PATHS, ids=NEW_CONCEPT_SLUGS)
def test_see_also_paths_resolve(path: Path):
    fm, _ = _read_page(path)
    see_also = fm.get("see_also") or []
    page_dir = path.parent
    for entry in see_also:
        target = (page_dir / str(entry)).resolve()
        assert target.exists(), (
            f"{path.relative_to(REPO_ROOT)}: see_also entry does not resolve: {entry!r} -> {target}"
        )


@pytest.mark.parametrize("path", NEW_CONCEPT_PATHS, ids=NEW_CONCEPT_SLUGS)
def test_at_least_one_standards_body_named(path: Path):
    _, body = _read_page(path)
    matches = [name for name in STANDARDS_BODY_NAMES if re.search(rf"\b{re.escape(name)}\b", body)]
    assert matches, (
        f"{path.relative_to(REPO_ROOT)} must NAME >= 1 standards body "
        f"(NFPA / EN / IGC / SIGTTO / OCIMF / IACS / ABS / DNV / IMO / API / EEMUA / CEN)"
    )


@pytest.mark.parametrize("path", NEW_CONCEPT_PATHS, ids=NEW_CONCEPT_SLUGS)
def test_word_count_under_400(path: Path):
    _, body = _read_page(path)
    word_count = len(body.split())
    assert word_count < WORD_COUNT_LIMIT, (
        f"{path.relative_to(REPO_ROOT)}: body word count {word_count} >= {WORD_COUNT_LIMIT} "
        "(concept-summary discipline per #2482 deny-list)"
    )


def test_no_reserved_noun_phrases_literal():
    """BLOCK the four literal noun-phrases per dispatch:
    SESA, Woodfibre, ACMA-31522, Doris-62092 — reserved for other modules/specs.
    """
    failures: list[str] = []
    for path in NEW_CONCEPT_PATHS:
        text = path.read_text(encoding="utf-8")
        for phrase in RESERVED_LITERAL_PHRASES:
            if re.search(rf"\b{re.escape(phrase)}\b", text, re.IGNORECASE):
                failures.append(
                    f"{path.relative_to(REPO_ROOT)}: contains reserved literal phrase {phrase!r}"
                )
    assert not failures, "\n".join(failures)


def test_no_reserved_noun_phrases_generalized():
    """Generalized regex blocking any ACMA-NNNN / Doris-NNNN / SESA / Woodfibre form."""
    failures: list[str] = []
    for path in NEW_CONCEPT_PATHS:
        text = path.read_text(encoding="utf-8")
        for match in RESERVED_GENERALIZED_PATTERN.finditer(text):
            failures.append(
                f"{path.relative_to(REPO_ROOT)}: matched reserved pattern {match.group(0)!r}"
            )
    assert not failures, "\n".join(failures)


def test_no_internal_corpus_identifiers():
    """Workspace-hub-internal corpus identifiers (ACMA-project / Doris-project / 31522 / 62092)
    must never appear in new concept-page bodies."""
    failures: list[str] = []
    for path in NEW_CONCEPT_PATHS:
        text = path.read_text(encoding="utf-8")
        for pattern in INTERNAL_CORPUS_PATTERNS:
            for match in pattern.finditer(text):
                failures.append(
                    f"{path.relative_to(REPO_ROOT)}: matched internal corpus identifier {match.group(0)!r}"
                )
    assert not failures, "\n".join(failures)


def test_index_lists_all_new_pages():
    """index.md must hyperlink every new concept page."""
    text = INDEX.read_text(encoding="utf-8")
    missing = [
        slug for slug in NEW_CONCEPT_SLUGS
        if f"concepts/{slug}.md" not in text
    ]
    assert not missing, f"index.md missing links for: {missing}"


def test_index_page_count_bumped():
    fm, _ = _split_frontmatter(INDEX.read_text(encoding="utf-8"))
    page_count = fm.get("page_count")
    try:
        n = int(str(page_count))
    except (TypeError, ValueError):
        pytest.fail(f"index.md page_count is not an integer: {page_count!r}")
    assert n >= 11, f"index.md page_count must be >= 11; got {n}"


def test_log_entry_appended():
    text = LOG.read_text(encoding="utf-8")
    assert "[2026-05-03] expand" in text and "lng-projects W5-C" in text, (
        "log.md must carry a [2026-05-03] expand | lng-projects W5-C entry"
    )


def test_no_pdf_extraction_markers():
    """Heuristic: no Page-N-of-M stamps and no super-long single paragraphs."""
    page_marker = re.compile(r"\bPage\s+\d+\s+of\s+\d+\b", re.IGNORECASE)
    for path in NEW_CONCEPT_PATHS:
        _, body = _read_page(path)
        assert not page_marker.search(body), (
            f"{path.relative_to(REPO_ROOT)}: found Page-N-of-M PDF copy marker"
        )
        # Split on blank lines first, then on bullet boundaries within a block
        # — a long bulleted list is not a PDF-extracted paragraph.
        for block in re.split(r"\n\s*\n", body):
            for chunk in re.split(r"\n(?=\s*[-*]\s)", block):
                words = chunk.split()
                assert len(words) <= 120, (
                    f"{path.relative_to(REPO_ROOT)}: paragraph >120 words "
                    f"({len(words)}) — likely PDF copy-paste"
                )


def test_no_thresholds_or_clauses_enumerated():
    """Concept bodies must not enumerate specific NFPA/EN/IGC clause numbers."""
    clause_patterns = (
        re.compile(r"\bNFPA\s+59A\s+\d+\.\d+", re.IGNORECASE),
        re.compile(r"\bEN\s*1473\s*[§\d]", re.IGNORECASE),
        re.compile(r"\bIGC\s+Code\s+\d+\.\d+", re.IGNORECASE),
    )
    failures: list[str] = []
    for path in NEW_CONCEPT_PATHS:
        text = path.read_text(encoding="utf-8")
        for pattern in clause_patterns:
            for match in pattern.finditer(text):
                failures.append(
                    f"{path.relative_to(REPO_ROOT)}: matched clause pattern {match.group(0)!r}"
                )
    assert not failures, "\n".join(failures)


def test_no_tandem_mooring_duplication():
    """concepts/lng-marine-transfer-systems.md must not duplicate the engineering
    OCIMF tandem-mooring page — tandem mooring is named by reference, not reproduced."""
    page = CONCEPTS_DIR / "lng-marine-transfer-systems.md"
    body = page.read_text(encoding="utf-8")
    occurrences = len(re.findall(r"tandem mooring", body, re.IGNORECASE))
    assert occurrences <= 3, (
        f"{page.relative_to(REPO_ROOT)}: 'tandem mooring' appears {occurrences} times — "
        "should be referenced not reproduced"
    )

    engineering_page = (
        REPO_ROOT
        / "knowledge"
        / "wikis"
        / "engineering"
        / "wiki"
        / "standards"
        / "ocimf-tandem-mooring.md"
    )
    if engineering_page.exists():
        engineering_text = engineering_page.read_text(encoding="utf-8")
        for paragraph in re.split(r"\n\s*\n", engineering_text):
            paragraph = paragraph.strip()
            if len(paragraph.split()) >= 25 and paragraph in body:
                pytest.fail(
                    f"{page.relative_to(REPO_ROOT)}: reproduces a >=25-word paragraph from "
                    f"the engineering OCIMF tandem-mooring page verbatim"
                )
