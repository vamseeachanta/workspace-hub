"""
stage_dispatch.py — Dispatcher that maps stage numbers to D-item check functions.

Called by exit_stage.py._deterministic_stage_check (WRK-1044).
"""
from __future__ import annotations

import sys
from pathlib import Path

from gate_checks_extra import check_plan_eval_count, check_route_cross_review_count  # type: ignore[import]
from stage_exit_checks import (  # type: ignore[import]
    check_s1_capture_gate,
    check_s5_browser_timestamps,
    check_s5_publish_order,
    check_s6_p1_pause,
    check_s8_sentinel_fields,
    check_s14_gate_summary,
    check_s15_future_work,
    check_s17_reviewer_allowlist,
    check_s19_integrated_tests,
    check_s19_stage_evidence,
)


def _read_wrk_front(repo_root: str, wrk_id: str) -> dict:
    queue_dir = Path(repo_root) / ".claude" / "work-queue"
    for folder in ("working", "done", "pending"):
        candidate = queue_dir / folder / f"{wrk_id}.md"
        if candidate.exists():
            front: dict = {}
            for line in candidate.read_text(encoding="utf-8").splitlines():
                if ":" in line and not line.startswith(" "):
                    k, _, v = line.partition(":")
                    front[k.strip()] = v.strip().strip('"').strip("'")
            return front
    return {}


def run_d_item_checks(stage: int, assets_dir: Path, repo_root: str) -> bool:
    """Run D-item deterministic checks for the given stage.

    Returns True; sys.exit(1) on hard failure, prints WARN for None results.
    """
    wrk_id = assets_dir.name
    checks: list = []

    if stage == 1:
        checks.append(lambda: check_s1_capture_gate(assets_dir))
    if stage == 4:
        plan_path = Path(repo_root) / "specs" / "wrk" / wrk_id / "plan.md"
        checks.append(lambda: check_plan_eval_count(plan_path))
    if stage == 5:
        checks.append(lambda: check_s5_browser_timestamps(assets_dir))
        checks.append(lambda: check_s5_publish_order(assets_dir))
    if stage == 6:
        checks.append(lambda: check_s6_p1_pause(assets_dir))
        front = _read_wrk_front(repo_root, wrk_id)
        checks.append(lambda: check_route_cross_review_count(assets_dir, front))
    if stage == 8:
        checks.append(lambda: check_s8_sentinel_fields(assets_dir))
    if stage == 14:
        checks.append(lambda: check_s14_gate_summary(assets_dir))
    if stage == 15:
        checks.append(lambda: check_s15_future_work(assets_dir))
    if stage == 17:
        checks.append(lambda: check_s17_reviewer_allowlist(assets_dir))
    if stage == 19:
        checks.append(lambda: check_s19_integrated_tests(assets_dir))
        checks.append(lambda: check_s19_stage_evidence(repo_root, wrk_id))

    for fn in checks:
        ok, msg = fn()
        if ok is False:
            print(f"[ERROR] D-ITEM: {msg}", file=sys.stderr)
            sys.exit(1)
        elif ok is None:
            print(f"[WARN] D-ITEM: {msg}", file=sys.stderr)

    return True
