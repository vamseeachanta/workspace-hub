"""
Checklist completion engine for stage transitions.

Reads checklist from stage YAML, checks completion state from evidence file,
returns structured blockers (TransitionBlocker pattern).

Usage (programmatic):
    from verify_checklist import verify_checklist
    result = verify_checklist(stage_yaml_path, wrk_id, stage, evidence_dir)

Usage (CLI):
    uv run --no-project python scripts/work-queue/verify_checklist.py WRK-NNN 10
    uv run --no-project python scripts/work-queue/verify_checklist.py --dry-run WRK-NNN 10
"""

import argparse
import glob
import os
import sys

import yaml


def verify_checklist(stage_yaml_path, wrk_id, stage, evidence_dir, dry_run=False):
    """Verify all checklist items for a stage are complete.

    Args:
        stage_yaml_path: path to stage-NN-*.yaml
        wrk_id: e.g. "WRK-1316"
        stage: int stage number
        evidence_dir: path to assets/WRK-NNN/evidence/
        dry_run: bool. If True, skip evidence validation; return checklist items only.

    Returns:
        dict with:
          passed: bool
          blockers: list of {id, text, reason}
          items: list of checklist items (always present)
    """
    # Load stage contract
    with open(stage_yaml_path) as f:
        contract = yaml.safe_load(f)

    checklist = contract.get("checklist") or []

    # In dry-run mode, skip validation and just return the items
    if dry_run:
        return {
            "passed": True,
            "blockers": [],
            "items": checklist,
        }

    # Normal verification mode
    if not checklist:
        return {"passed": True, "blockers": [], "items": []}

    # Load completion state
    evidence_path = os.path.join(evidence_dir, f"checklist-{stage:02d}.yaml")
    completed_items = {}
    if os.path.exists(evidence_path):
        with open(evidence_path) as f:
            evidence = yaml.safe_load(f) or {}
        for item in evidence.get("items", []):
            if item.get("completed"):
                completed_items[item["id"]] = item

    # Check each checklist item
    blockers = []
    for item in checklist:
        item_id = item["id"]
        text = item.get("text", "")
        requires_human = item.get("requires_human", False)

        if item_id not in completed_items:
            blockers.append({
                "id": item_id,
                "text": text,
                "reason": f"Item not completed: {text}",
            })
            continue

        completed = completed_items[item_id]

        if requires_human and not completed.get("approved_by"):
            blockers.append({
                "id": item_id,
                "text": text,
                "reason": f"requires_human=true but no approved_by field",
            })

    return {
        "passed": len(blockers) == 0,
        "blockers": blockers,
        "items": checklist,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verify checklist items for a WRK stage")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview checklist items without validating evidence")
    parser.add_argument("wrk_id", help="WRK item ID (e.g., WRK-1323)")
    parser.add_argument("stage", type=int, help="Stage number")

    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    stages_dir = os.path.join(repo_root, "scripts", "work-queue", "stages")
    evidence_dir = os.path.join(
        repo_root, ".claude", "work-queue", "assets", args.wrk_id, "evidence")

    # Find stage YAML
    matches = glob.glob(os.path.join(stages_dir, f"stage-{args.stage:02d}-*.yaml"))
    if not matches:
        print(f"No stage YAML found for stage {args.stage}", file=sys.stderr)
        sys.exit(2)

    result = verify_checklist(matches[0], args.wrk_id, args.stage, evidence_dir,
                              dry_run=args.dry_run)

    # Dry-run mode: print items and exit 0
    if args.dry_run:
        items = result["items"]
        if items:
            print(f"DRY-RUN: stage {args.stage} has {len(items)} checklist items:")
            for item in items:
                item_id = item.get("id", "???")
                text = item.get("text", "(no text)")
                print(f"  {item_id}  {text}")
        else:
            print(f"DRY-RUN: stage {args.stage} has 0 checklist items")
        sys.exit(0)

    # Normal mode: validate and block on failures
    if not result["passed"]:
        print(f"BLOCKED: {len(result['blockers'])} incomplete items:",
              file=sys.stderr)
        for b in result["blockers"]:
            print(f"  - [{b['id']}] {b['reason']}", file=sys.stderr)
        sys.exit(1)

    print(f"PASS: all checklist items complete for stage {args.stage}")
    sys.exit(0)
