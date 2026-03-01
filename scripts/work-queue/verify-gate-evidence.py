#!/usr/bin/env python3
"""Validate orchestrator gate evidence for a WRK item."""

import re
import sys
from pathlib import Path


def parse_frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("front matter not found")
    return parts[1]


def get_field(front: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:[ \t]*(.+?)$", front, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def has_nonempty_field(front: str, key: str) -> bool:
    scalar = get_field(front, key)
    if scalar and scalar not in {"[]", "null", "~"}:
        return True
    block = re.search(rf"^{re.escape(key)}:\s*\n((?:\s+-[^\n]*\n?)*)", front, re.MULTILINE)
    if not block:
        return False
    return bool(re.search(r"^\s+-\s+\S+", block.group(1), re.MULTILINE))


def parse_bool(value: str | None) -> bool:
    if not value:
        return False
    return value.lower() in {"1", "true", "yes", "y"}


def abs_path(workspace_root: Path, referenced: str) -> Path:
    candidate = Path(referenced)
    if candidate.is_absolute():
        return candidate
    if referenced.startswith("./") or referenced.startswith("../") or referenced.startswith("."):
        return (workspace_root / referenced).resolve()
    return (workspace_root / referenced).resolve()


def first_matching_file(directory: Path, names: list[str]) -> Path | None:
    for name in names:
        candidate = directory / name
        if candidate.exists():
            return candidate
    return None


def run_checks(wrk_id: str) -> int:
    workspace_root = Path(__file__).resolve().parents[2]
    queue_dir = workspace_root / ".claude" / "work-queue"
    wrk_path = None
    for folder in ["pending", "working", "done"]:
        candidate = queue_dir / folder / f"{wrk_id}.md"
        if candidate.exists():
            wrk_path = candidate
            break
    if wrk_path is None:
        print(f"✖ Work item {wrk_id} not found in pending/ or working/", file=sys.stderr)
        return 2

    front = parse_frontmatter(wrk_path.read_text(encoding="utf-8"))
    assets_dir = queue_dir / "assets" / wrk_id
    if not assets_dir.is_dir():
        print(f"✖ Assets directory missing: {assets_dir}", file=sys.stderr)
        return 2

    plan_reviewed = parse_bool(get_field(front, "plan_reviewed"))
    plan_approved = parse_bool(get_field(front, "plan_approved"))
    plan_ref = get_field(front, "plan_html_review_final_ref")
    plan_path = abs_path(workspace_root, plan_ref) if plan_ref else assets_dir / "plan-html-review-final.md"

    review_file = first_matching_file(assets_dir, ["review.html", "review.md", "results.md", "review-results.md", "review-synthesis.md"])
    test_candidates = list(p for p in assets_dir.glob("*.md") if "test" in p.name.lower())
    legal_file = first_matching_file(assets_dir, ["legal-scan.md"])

    gates = []
    gates.append(
        {
            "name": "Plan gate",
            "ok": plan_reviewed and plan_approved and plan_path.exists(),
            "details": f"reviewed={plan_reviewed}, approved={plan_approved}, artifact={'missing' if not plan_path.exists() else plan_path}",
        }
    )
    gates.append(
        {
            "name": "Workstation contract gate",
            "ok": has_nonempty_field(front, "plan_workstations") and has_nonempty_field(front, "execution_workstations"),
            "details": (
                f"plan_workstations={get_field(front, 'plan_workstations') or 'missing'}, "
                f"execution_workstations={get_field(front, 'execution_workstations') or 'missing'}"
            ),
        }
    )
    gates.append(
        {"name": "Cross-review gate", "ok": bool(review_file), "details": f"artifact={'none' if not review_file else review_file}"}
    )
    gates.append(
        {
            "name": "TDD gate",
            "ok": len(test_candidates) > 0,
            "details": f"test files={[p.name for p in test_candidates]}" if test_candidates else "none",
        }
    )
    legal_notes = "none"
    legal_ok = False
    if legal_file:
        contents = legal_file.read_text(encoding="utf-8")
        match = re.search(r"^result:\s*(.+)$", contents, re.MULTILINE | re.IGNORECASE)
        legal_result = match.group(1).strip() if match else None
        legal_ok = bool(legal_result and "pass" in legal_result.lower())
        legal_notes = f"result={legal_result or 'missing'}"
    gates.append({"name": "Legal gate", "ok": legal_ok, "details": f"artifact={legal_file if legal_file else 'missing'}, {legal_notes}"})

    success = True
    print(f"Gate evidence for {wrk_id} (assets: {assets_dir}):")
    for gate in gates:
        status = "OK" if gate["ok"] else "MISSING"
        print(f"  - {gate['name']}: {status} ({gate['details']})")
        if not gate["ok"]:
            success = False

    if not success:
        print("→ Gate evidence incomplete. Please collect the missing artifacts before claiming.", file=sys.stderr)
        return 1

    print("→ All orchestrator gates have documented evidence.")
    return 0


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: verify-gate-evidence.py WRK-<id>")
        sys.exit(1)
    wrk_id = sys.argv[1]
    code = run_checks(wrk_id)
    sys.exit(code)


if __name__ == "__main__":
    main()
