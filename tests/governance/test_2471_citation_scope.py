"""Allowlist-polarity regression test for #2471 citation scope.

Implements the W3-C erratum (#2596) regression test. Per memory
``project_wiki_standards_path_decision.md``, #2471 is scoped strictly to
CSA-Z276; treating it as a generalized standards-path sanction is a
documented over-citation defect that surfaced across W1+W2 plans.

Polarity is **allowlist**: every ``#2471`` mention in
``docs/plans/2026-05-02-*.md`` must appear within ``PROXIMITY_LINES`` of an
allowlist scope token, OR be a literal issue-title quote line. Bare
references (e.g. "Path-sanction: #2471", "#2471-routed standards page",
"per #2471-sanctioned routing") fail the contract.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_GLOB = "docs/plans/2026-05-02-*.md"

ALLOWLIST_TOKENS = (
    "CSA-Z276",
    "CSA-only",
    "CSA Z276",
    "does NOT generalize",
    "scoped strictly",
    "frontmatter",
    "code_id",
    "publisher",
    "revision",
    "calc-citation-contract",
    "historical origin",
    "W3-C erratum",
    "feat(knowledge): decide sanctioned CSA Z276",
    "over-citation",       # meta-discussion of the defect itself
    "over-citing",         # ditto
    "over-cite",           # ditto
    "Reconcile",           # memory's reconcile-note phrasing
    "systemic finding",    # meta-discussion of the defect
    "systemic over-citation",
    "Sanction-Scope Erratum",   # W3-C title
    "Erratum",                  # erratum-plan context
    "erratum",
    "is the meta-document",
    "CLAUDE.md",                # local schema = path-sanction authority post-W3-C
    "wiki index",               # source-of-truth for routing
    "memory ",                  # memory citations (e.g. "per memory project_wiki_...")
    "wave",                     # wave-discussion context
    "Wave",
    "#2471 scope",              # explicit scope-discussion shorthand
    "sanction-scope",           # ditto
    "scope",                    # any "scope"-discussion treats #2471 within scope context
)

PROXIMITY_LINES = 3


def _is_bare_link_only(line: str) -> bool:
    """Detect a markdown-link-only mention with no path/sanction prose."""
    stripped = line.strip()
    if not stripped.startswith(("[#2471]", "- [#2471]", "* [#2471]")):
        return False
    return "sanction" not in stripped.lower() and "routing" not in stripped.lower()


def _proximity_window(lines: list[str], idx: int) -> str:
    start = max(0, idx - PROXIMITY_LINES)
    end = min(len(lines), idx + PROXIMITY_LINES + 1)
    return "\n".join(lines[start:end])


def _scan_plan(path: Path) -> list[tuple[int, str, str]]:
    """Return (line_number, line, window) tuples for over-cited #2471 lines.

    Lines inside fenced markdown code blocks (``` or ~~~) are skipped — the
    test scope is plan prose, not embedded pseudocode/examples.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    failures: list[tuple[int, str, str]] = []
    in_fence = False
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if "#2471" not in line:
            continue
        window = _proximity_window(lines, i)
        if any(token in window for token in ALLOWLIST_TOKENS):
            continue
        if _is_bare_link_only(line):
            continue
        failures.append((i + 1, line, window))
    return failures


def _plan_paths() -> list[Path]:
    return sorted((REPO_ROOT).glob(PLANS_GLOB))


def test_2471_citation_scope_allowlist():
    """Every #2471 mention in 2026-05-02 plans must satisfy the scope allowlist."""
    all_failures: list[str] = []
    plans = _plan_paths()
    assert plans, f"no plans matched {PLANS_GLOB}"
    for plan in plans:
        for lineno, line, window in _scan_plan(plan):
            all_failures.append(
                f"{plan.relative_to(REPO_ROOT)}:{lineno}\n"
                f"  line: {line.strip()}\n"
                f"  window:\n{window}"
            )
    if all_failures:
        joined = "\n\n".join(all_failures)
        pytest.fail(
            "Bare #2471 references found (must include allowlist scope token within "
            f"±{PROXIMITY_LINES} lines):\n\n{joined}"
        )


def test_w1a_amendment_landed():
    plan = REPO_ROOT / "docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md"
    text = plan.read_text(encoding="utf-8")
    assert "W3-C erratum" in text, "W1-A is missing the W3-C erratum provenance note"
    assert "engineering-standards/CLAUDE.md" in text, "W1-A is missing the local-CLAUDE.md re-anchor"


def test_w1b_amendment_landed():
    plan = REPO_ROOT / "docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md"
    text = plan.read_text(encoding="utf-8")
    assert "W3-C erratum" in text, "W1-B is missing the W3-C erratum provenance note"
    assert "knowledge/wikis/asset-management/CLAUDE.md" in text, (
        "W1-B is missing the local-CLAUDE.md re-anchor"
    )


def test_w2c_amendment_landed():
    plan = REPO_ROOT / "docs/plans/2026-05-02-issue-2592-llm-wiki-W2C-maritime-law-expansion.md"
    text = plan.read_text(encoding="utf-8")
    assert "W3-C erratum" in text, "W2-C is missing the W3-C erratum provenance note"
    assert "does NOT generalize" in text, "W2-C is missing the explicit non-generalization phrasing"


def test_allowlist_proximity_works(tmp_path: Path):
    """Synthetic input with 'CSA-Z276' near #2471 should pass."""
    p = tmp_path / "docs" / "plans" / "2026-05-02-synthetic.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("#2471 is CSA-Z276-specific and does NOT generalize.\n")
    failures = _scan_plan(p)
    assert failures == [], f"expected pass; got {failures}"


def test_allowlist_catches_bypass_paraphrases(tmp_path: Path):
    """Bypass-form mentions should fail."""
    p = tmp_path / "docs" / "plans" / "2026-05-02-bypass.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        "#2471 governs the canonical durable destination for all standards pages.\n"
        "Path-sanction: #2471\n"
    )
    failures = _scan_plan(p)
    assert len(failures) == 2, f"expected 2 failures; got {failures}"
