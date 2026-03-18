"""
Checklist completion engine for stage transitions.

Reads checklist from stage YAML, checks completion state from evidence file,
returns structured blockers (TransitionBlocker pattern).

Usage (programmatic):
    from verify_checklist import verify_checklist
    result = verify_checklist(stage_yaml_path, wrk_id, stage, evidence_dir)

Usage (CLI):
    uv run --no-project python scripts/work-queue/verify_checklist.py WRK-NNN 10
"""

import os
import sys

import yaml


def verify_checklist(stage_yaml_path, wrk_id, stage, evidence_dir):
    """Verify all checklist items for a stage are complete.

    Args:
        stage_yaml_path: path to stage-NN-*.yaml
        wrk_id: e.g. "WRK-1316"
        stage: int stage number
        evidence_dir: path to assets/WRK-NNN/evidence/

    Returns:
        dict with:
          passed: bool
          blockers: list of {id, text, reason}
    """
    # Load stage contract
    with open(stage_yaml_path) as f:
        contract = yaml.safe_load(f)

    checklist = contract.get("checklist")
    if not checklist:
        return {"passed": True, "blockers": []}

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
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: verify_checklist.py WRK-NNN STAGE", file=sys.stderr)
        sys.exit(2)

    wrk_id = sys.argv[1]
    stage = int(sys.argv[2])

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    stages_dir = os.path.join(repo_root, "scripts", "work-queue", "stages")
    evidence_dir = os.path.join(
        repo_root, ".claude", "work-queue", "assets", wrk_id, "evidence")

    # Find stage YAML
    import glob
    matches = glob.glob(os.path.join(stages_dir, f"stage-{stage:02d}-*.yaml"))
    if not matches:
        print(f"No stage YAML found for stage {stage}", file=sys.stderr)
        sys.exit(2)

    result = verify_checklist(matches[0], wrk_id, stage, evidence_dir)

    if not result["passed"]:
        print(f"BLOCKED: {len(result['blockers'])} incomplete items:",
              file=sys.stderr)
        for b in result["blockers"]:
            print(f"  - [{b['id']}] {b['reason']}", file=sys.stderr)
        sys.exit(1)

    print(f"PASS: all checklist items complete for stage {stage}")
    sys.exit(0)
