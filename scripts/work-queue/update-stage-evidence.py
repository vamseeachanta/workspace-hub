#!/usr/bin/env python3
"""Update a WRK stage-evidence ledger row by order."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
from pathlib import Path

try:
    import yaml  # type: ignore[import]
except Exception:  # pragma: no cover - handled at runtime
    yaml = None


ALLOWED_STATUS = {"pending", "in_progress", "done", "n/a", "blocked"}

CANONICAL_STAGES = [
    "Capture", "Resource Intelligence", "Triage", "Plan Draft",
    "User Review - Plan Draft", "Cross-Review", "User Review - Plan Final",
    "Claim / Activation", "Work-Queue Routing", "Work Execution",
    "Artifact Generation", "TDD / Eval", "Agent Cross-Review",
    "Verify Gate Evidence", "Future Work Synthesis",
    "Resource Intelligence Update", "User Review - Implementation",
    "Reclaim", "Close", "Archive",
]


def _bootstrap_stage_evidence(stage_file: Path, wrk_id: str) -> dict:
    """Create initial stage-evidence.yaml with all 20 stages pending."""
    stage_file.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "wrk_id": wrk_id,
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reviewed_by": "agent",
        "stages": [
            {"order": i + 1, "stage": name, "status": "pending", "evidence": ""}
            for i, name in enumerate(CANONICAL_STAGES)
        ],
    }
    stage_file.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return data


def parse_frontmatter(text: str) -> tuple[str, str] | None:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not match:
        return None
    return match.group(1), match.group(2)


def get_scalar(frontmatter: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.+)$", frontmatter, re.MULTILINE)
    return m.group(1).strip() if m else None


def resolve_stage_evidence_path(workspace_root: Path, wrk_id: str) -> Path:
    queue_root = workspace_root / ".claude" / "work-queue"
    candidates: list[Path] = []
    for folder in ("pending", "working", "done", "blocked"):
        candidates.append(queue_root / folder / f"{wrk_id}.md")
    archive_root = queue_root / "archive"
    if archive_root.exists():
        candidates.extend(sorted(archive_root.glob(f"*/{wrk_id}.md")))

    for wrk_file in candidates:
        if not wrk_file.exists():
            continue
        parsed = parse_frontmatter(wrk_file.read_text(encoding="utf-8"))
        if not parsed:
            continue
        front, _ = parsed
        ref = get_scalar(front, "stage_evidence_ref")
        if ref:
            return (workspace_root / ref).resolve()

    fallback = queue_root / "assets" / wrk_id / "evidence" / "stage-evidence.yaml"
    return fallback.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description="Update stage-evidence status for a WRK item.")
    parser.add_argument("wrk_id", help="WRK id, e.g. WRK-690")
    parser.add_argument("--order", type=int, required=True, help="Stage order number (1..20)")
    parser.add_argument("--status", required=True, help="Stage status")
    parser.add_argument("--evidence", default="", help="Optional evidence ref to overwrite")
    parser.add_argument("--reviewed-by", default="", help="Optional reviewed_by override")
    parser.add_argument("--dry-run", action="store_true", help="Print planned change only")
    args = parser.parse_args()

    if yaml is None:
        raise RuntimeError("PyYAML is required. Run with uv environment.")

    wrk_id = args.wrk_id if args.wrk_id.startswith("WRK-") else f"WRK-{args.wrk_id}"
    status = args.status.strip().lower()
    if status not in ALLOWED_STATUS:
        raise ValueError(f"invalid status '{args.status}'. allowed={sorted(ALLOWED_STATUS)}")
    if args.order < 1 or args.order > 20:
        raise ValueError("order must be between 1 and 20")

    workspace_root = Path(os.getenv("WORKSPACE_ROOT", Path(__file__).resolve().parents[2]))
    stage_file = resolve_stage_evidence_path(workspace_root, wrk_id)
    if not stage_file.exists():
        data = _bootstrap_stage_evidence(stage_file, wrk_id)
        print(f"[BOOTSTRAP] created {stage_file}")
    else:
        data = yaml.safe_load(stage_file.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{stage_file} must be a YAML mapping")
    stages = data.get("stages")
    if not isinstance(stages, list):
        raise ValueError(f"{stage_file} missing 'stages' list")

    updated = False
    for row in stages:
        if not isinstance(row, dict):
            continue
        if row.get("order") == args.order:
            row["status"] = status
            if args.evidence:
                row["evidence"] = args.evidence
            updated = True
            break

    if not updated:
        raise ValueError(f"stage order {args.order} not found in {stage_file}")

    data["wrk_id"] = wrk_id
    data["generated_at"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if args.reviewed_by:
        data["reviewed_by"] = args.reviewed_by

    if args.dry_run:
        print(f"[DRY-RUN] {wrk_id} -> stage {args.order} status={status}")
        print(f"[DRY-RUN] file: {stage_file}")
        return 0

    stage_file.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    print(f"[APPLY] {wrk_id} -> stage {args.order} status={status}")
    print(f"[APPLY] file: {stage_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
