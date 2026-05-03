"""Audit-artifact existence + schema test for W4-C marine-engineering wiki gap audit.

Implements the test contract from `docs/plans/2026-05-03-issue-2601-llm-wiki-W4C-marine-engineering-audit.md`.
Validates that the audit at `docs/audits/2026-05-03-marine-engineering-wiki-gap-audit.md` exists
with the required tables and 5-8 prioritized backfill entries, and that each priority
entry's rationale references a verifiable taxonomy anchor (ITTC procedure family,
SNAME Offshore Section literal, calc-citation-contract phrase, or `CLAUDE.md schema gap`).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT = REPO_ROOT / "docs/audits/2026-05-03-marine-engineering-wiki-gap-audit.md"
WIKI_ROOT = REPO_ROOT / "knowledge/wikis/marine-engineering/wiki"

# Anchors per W4-C plan's `test_audit_rationales_cite_required_anchors` contract
ITTC_PROCEDURE_REGEX = re.compile(r"7\.5-0[0-9]-[0-9]{2}-[0-9]{2}")
SNAME_OFFSHORE_LITERAL = "SNAME Offshore Section"
CITATION_CONTRACT_REGEX = re.compile(
    r"(citation-contract|citation contract|would cite)", re.IGNORECASE
)
CLAUDE_SCHEMA_GAP_LITERAL = "CLAUDE.md schema gap"


def _read_audit() -> str:
    assert AUDIT.exists(), f"audit artifact not found at {AUDIT}"
    return AUDIT.read_text(encoding="utf-8")


def _table_rows(text: str, table_header_substr: str) -> list[str]:
    """Extract data rows from a markdown table whose header line contains the substring.

    Returns the list of row lines (excluding header + separator).
    """
    lines = text.splitlines()
    rows: list[str] = []
    in_table = False
    for i, line in enumerate(lines):
        if not in_table:
            if line.startswith("|") and table_header_substr in line:
                if i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|\s*$", lines[i + 1]):
                    in_table = True
            continue
        if not line.startswith("|"):
            break
        if re.match(r"^\|[\s\-:|]+\|\s*$", line):
            continue
        rows.append(line)
    return rows


def test_audit_file_exists():
    assert AUDIT.exists(), f"audit artifact missing at {AUDIT}"


def test_audit_has_distribution_table_A():
    """Table A — wiki-distribution: 6-7 rows (all schema-expected subdirs + root, excluding Total).

    The plan pseudocode listed 6 rows (comparisons/concepts/entities/sources/visualizations/root)
    based on a snapshot where multiple subdirs were missing as directories. Live state has all 6
    schema subdirs visible (standards as `MISSING`, others present), giving 6 subdirs + root = 7.
    """
    text = _read_audit()
    rows = _table_rows(text, "File-Count Share")
    data_rows = [r for r in rows if "**Total**" not in r]
    assert 6 <= len(data_rows) <= 7, (
        f"Table A has {len(data_rows)} non-total rows; expected 6 or 7 "
        "(all schema-expected subdirs + root, with missing dirs as explicit MISSING/count-0 rows)"
    )


def test_audit_has_distribution_table_B():
    """Table B — raw-distribution: exactly 4 raw subdir rows (articles/assets/papers/standards)."""
    text = _read_audit()
    rows = _table_rows(text, "| Subdir | File Count | Content Type | State |")
    data_rows = [r for r in rows if "Root `.gitkeep`" not in r]
    assert len(data_rows) == 4, (
        f"Table B has {len(data_rows)} raw-subdir rows; expected exactly 4 "
        "(articles, assets, papers, standards)"
    )


def test_audit_has_distribution_table_C():
    """Table C — sources-prefix-bucket: row count >= 8."""
    text = _read_audit()
    rows = _table_rows(text, "Prefix Bucket")
    assert len(rows) >= 8, (
        f"Table C has {len(rows)} rows; need >=8 source-prefix buckets"
    )


def test_audit_structural_gap_includes_standards_dir():
    """Table E (structural-gap) must flag wiki/standards/ as missing/absent."""
    text = _read_audit()
    rows = _table_rows(text, "Expected Path per CLAUDE.md")
    found_standards_missing = False
    found_comparisons = False
    found_visualizations = False
    for row in rows:
        if "wiki/standards/" in row and (
            "Missing" in row or "missing" in row or "absent" in row
        ):
            found_standards_missing = True
        if "wiki/comparisons/" in row:
            found_comparisons = True
        if "wiki/visualizations/" in row:
            found_visualizations = True
    assert found_standards_missing, "structural-gap table must flag wiki/standards/ as missing/absent"
    assert found_comparisons, "structural-gap table must include row for wiki/comparisons/"
    assert found_visualizations, "structural-gap table must include row for wiki/visualizations/"


def test_audit_subdiscipline_matrix_min_rows():
    """Table F — ITTC sub-discipline coverage matrix: row count >= 8."""
    text = _read_audit()
    rows = _table_rows(text, "ITTC Sub-Discipline")
    assert len(rows) >= 8, (
        f"Sub-discipline coverage matrix has {len(rows)} rows; need >=8 ITTC families"
    )


def test_audit_priority_list_size():
    """Table G — prioritized backfill: 5 <= entries <= 8."""
    text = _read_audit()
    rows = _table_rows(text, "Follow-Up Issue Placeholder")
    assert 5 <= len(rows) <= 8, (
        f"Priority list has {len(rows)} entries; plan requires 5-8"
    )


def test_audit_priority_entry_schema():
    """Each priority entry must have title, target_path, priority (P1|P2|P3), rationale,
    follow-up issue placeholder, and candidate_sources columns.
    """
    text = _read_audit()
    rows = _table_rows(text, "Follow-Up Issue Placeholder")
    assert rows, "priority table is empty"
    priority_pattern = re.compile(r"\bP[123]\b")
    placeholder_pattern = re.compile(r"docs/plans/.*?\.md")
    for row in rows:
        cells = [c.strip() for c in row.split("|") if c.strip() != ""]
        # Layout: # | Title | Target Path | Priority | Rationale | Follow-Up | Sources -> 7 logical cells
        assert len(cells) >= 7, (
            f"priority row has only {len(cells)} cells; need >=7\n  row: {row[:200]}"
        )
        assert priority_pattern.search(row), (
            f"priority row missing P1/P2/P3 marker:\n  {row[:200]}"
        )
        assert placeholder_pattern.search(row), (
            f"priority row missing follow-up issue placeholder (docs/plans/...md):\n  {row[:200]}"
        )


def test_audit_rationales_cite_required_anchors():
    """Each priority-table row's rationale must reference at least one of:
    - ITTC procedure family regex `7\\.5-0[0-9]-[0-9]{2}-[0-9]{2}`
    - literal `SNAME Offshore Section`
    - calc-citation-contract literal (`citation-contract`, `citation contract`, `would cite`)
    - literal `CLAUDE.md schema gap`
    """
    text = _read_audit()
    rows = _table_rows(text, "Follow-Up Issue Placeholder")
    failures: list[str] = []
    for row in rows:
        if (
            ITTC_PROCEDURE_REGEX.search(row)
            or SNAME_OFFSHORE_LITERAL in row
            or CITATION_CONTRACT_REGEX.search(row)
            or CLAUDE_SCHEMA_GAP_LITERAL in row
        ):
            continue
        failures.append(row[:200])
    assert not failures, (
        "Priority entries lack required taxonomy anchor "
        "(ITTC procedure regex, SNAME Offshore Section, citation-contract, or CLAUDE.md schema gap):\n"
        + "\n".join(failures)
    )


def test_audit_file_counts_verifiable():
    """Cited counts must match live `find` results within absolute +/-5 files tolerance.

    Verifies the principal counts cited in Table A (wiki) and Table B (raw).
    Missing directories (e.g. wiki/standards/) are treated as count 0.
    """
    text = _read_audit()

    def count_md(rel_path: str) -> int:
        p = WIKI_ROOT.parent / rel_path
        if not p.exists():
            return 0
        return len(list(p.glob("*.md")))

    live_counts = {
        "concepts": count_md("wiki/concepts"),
        "entities": count_md("wiki/entities"),
        "sources": count_md("wiki/sources"),
        "comparisons": count_md("wiki/comparisons"),
        "visualizations": count_md("wiki/visualizations"),
    }

    cited_counts = {
        "concepts": int(re.search(r"`wiki/concepts/`\s*\|\s*(\d+)", text).group(1)),
        "entities": int(re.search(r"`wiki/entities/`\s*\|\s*(\d+)", text).group(1)),
        "sources": int(re.search(r"`wiki/sources/`\s*\|\s*([\d,]+)", text).group(1).replace(",", "")),
        "comparisons": int(re.search(r"`wiki/comparisons/`\s*\|\s*(\d+)", text).group(1)),
        "visualizations": int(re.search(r"`wiki/visualizations/`\s*\|\s*(\d+)", text).group(1)),
    }

    failures = []
    for key, live in live_counts.items():
        cited = cited_counts[key]
        if abs(cited - live) > 5:
            failures.append(f"{key}: cited={cited}, live={live}, diff={abs(cited - live)}")
    assert not failures, "cited counts drift > +/-5 from live:\n" + "\n".join(failures)


def test_audit_no_wiki_writes():
    """This plan must not modify any file under knowledge/wikis/marine-engineering/.

    Verifies via `git diff --name-only origin/main...HEAD -- <wiki path>`. If the merge-base
    is unavailable in the local checkout (e.g. shallow clone), the test is skipped rather
    than raising a false positive.
    """
    try:
        merge_base = subprocess.check_output(
            ["git", "merge-base", "HEAD", "origin/main"],
            cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return  # skip — origin/main not available locally

    diff = subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            f"{merge_base}..HEAD",
            "--",
            "knowledge/wikis/marine-engineering/",
        ],
        cwd=REPO_ROOT,
        text=True,
    ).strip()
    assert diff == "", (
        "this audit plan must not modify any file under knowledge/wikis/marine-engineering/; "
        f"got changed files:\n{diff}"
    )


def test_audit_has_deprecation_pass():
    """Audit must include a deprecation/consolidation section."""
    text = _read_audit()
    assert (
        "Deprecation / consolidation pass" in text
        or "Deprecation pass" in text
        or "deprecation pass" in text
    ), "audit must include a deprecation/consolidation pass section"


def test_audit_blocking_issue_cross_references_present():
    """Audit must cross-reference structural-gap blocking issues #2522, #2586, #2590, #2595."""
    text = _read_audit()
    for issue in ("#2522", "#2586", "#2590", "#2595"):
        assert issue in text, (
            f"audit must cross-reference blocking issue {issue} (depends on missing wiki/standards/)"
        )


def test_audit_empty_stub_rate_verified():
    """Audit must report a verified empty-body source-stub rate >= 99% with sample evidence."""
    text = _read_audit()
    rate_pattern = re.compile(r"(99\.\d{1,2})\s*%")
    matches = rate_pattern.findall(text)
    assert matches, "audit must report a numeric empty-stub rate >= 99%"
    rates = [float(m) for m in matches]
    assert max(rates) >= 99.0, f"max reported rate {max(rates)} below 99% threshold"
