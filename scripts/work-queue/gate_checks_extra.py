"""
gate_checks_extra.py — D9 and D10 check functions shared by
verify-gate-evidence.py and stage_exit_checks.py.
"""
from __future__ import annotations

import re
from pathlib import Path


def check_plan_eval_count(plan_path: Path) -> tuple[bool | None, str]:
    """FAIL when plan.md Tests/Evals section has fewer than 3 table rows.

    D9 — ensures the plan contains a meaningful test matrix before Stage 4 exit.
    """
    if not plan_path.exists():
        return None, f"plan file absent: {plan_path}"
    text = plan_path.read_text(encoding="utf-8")
    # Find ## Tests or ## Tests / Evals section
    section_match = re.search(
        r"^##\s+Tests?.*?$(.+?)(?=^##|\Z)",
        text,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if not section_match:
        return False, "Tests/Evals section not found in plan.md"
    section = section_match.group(1)
    # Count table rows (lines starting with | but not separator lines)
    rows = [
        ln for ln in section.splitlines()
        if ln.strip().startswith("|")
        and not re.match(r"^\s*\|[\s\-|:]+\|?\s*$", ln)
        and not re.match(r"^\s*\|\s*(Test|T\s*\||D-item|Scenario)", ln, re.IGNORECASE)
    ]
    count = len(rows)
    if count < 3:
        return False, f"Tests/Evals section has {count} row(s); need ≥ 3"
    return True, f"Tests/Evals section has {count} rows OK"


def check_route_cross_review_count(
    assets_dir: Path, front: dict
) -> tuple[bool | None, str]:
    """FAIL when cross-review file count doesn't match the WRK route.

    D10 — hard block (not warn-only):
    - Route A: exactly 1 cross-review file required
    - Route B/C: exactly 3 cross-review files required
    """
    route = str(front.get("route", "") or "B").strip().upper()
    evidence_dir = assets_dir / "evidence"
    review_files = list(evidence_dir.glob("cross-review-*.md")) if evidence_dir.exists() else []
    count = len(review_files)
    expected = 1 if route == "A" else 3
    if count < expected:
        return False, (
            f"Route {route}: found {count} cross-review file(s), need {expected}"
        )
    if route == "A" and count > 1:
        return False, (
            f"Route A should have 1 cross-review file, found {count} "
            f"— WRK may be mis-routed or files are fabricated"
        )
    return True, f"Route {route}: {count} cross-review file(s) OK"
