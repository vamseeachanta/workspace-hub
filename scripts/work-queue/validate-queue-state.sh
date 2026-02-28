#!/usr/bin/env bash
# validate-queue-state.sh - Lint work-queue state, folder consistency, and phased workflow evidence
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

python3 - "$WORKSPACE_ROOT" <<'PY'
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

workspace_root = Path(sys.argv[1])
queue_dir = workspace_root / ".claude" / "work-queue"

allowed_statuses = {"pending", "working", "done", "archived", "blocked", "failed"}
legacy_statuses = {"complete", "completed", "closed", "merged"}
active_dirs = {"pending": "pending", "working": "working", "blocked": "blocked", "done": "done"}
errors = []
warnings = []


def extract_frontmatter(path: Path):
    lines = []
    with path.open("r", encoding="utf-8") as handle:
        first = handle.readline()
        if first.strip() != "---":
            errors.append(f"{path.name}: missing YAML frontmatter")
            return ""
        for line in handle:
            if line.strip() == "---":
                return "".join(lines)
            lines.append(line)
    if not lines:
        errors.append(f"{path.name}: missing YAML frontmatter")
        return ""
    errors.append(f"{path.name}: unterminated YAML frontmatter")
    return ""


def frontmatter_value(frontmatter: str, field: str):
    match = re.search(rf"^{re.escape(field)}:\s*(.*)$", frontmatter, re.MULTILINE)
    return match.group(1).strip() if match else ""


def parse_iso8601(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def wrk_number(path: Path):
    match = re.search(r"WRK-(\d+)", path.stem)
    return int(match.group(1)) if match else None


def path_exists(value: str):
    value = value.strip()
    if not value:
        return False
    candidate = Path(value) if value.startswith("/") else workspace_root / value
    return candidate.exists()


def check_workflow_evidence(path: Path, frontmatter: str):
    wrk_id = frontmatter_value(frontmatter, "id") or path.stem
    wrk_num = wrk_number(path)
    status = frontmatter_value(frontmatter, "status")
    route = frontmatter_value(frontmatter, "route")
    plan_reviewed = frontmatter_value(frontmatter, "plan_reviewed").lower() == "true"

    if wrk_num is None or wrk_num < 624:
        return

    html_output_ref = frontmatter_value(frontmatter, "html_output_ref")
    if not html_output_ref:
        warnings.append(f"{wrk_id}: missing html_output_ref for phased workflow contract")
    elif not path_exists(html_output_ref):
        warnings.append(f"{wrk_id}: html_output_ref does not exist -> {html_output_ref}")

    if not frontmatter_value(frontmatter, "orchestrator"):
        warnings.append(f"{wrk_id}: missing orchestrator")

    if not frontmatter_value(frontmatter, "claim_routing_ref"):
        warnings.append(f"{wrk_id}: missing claim_routing_ref")

    if route in {"B", "C"} or plan_reviewed:
        for field in ("plan_html_review_draft_ref", "plan_html_review_final_ref"):
            value = frontmatter_value(frontmatter, field)
            if not value:
                warnings.append(f"{wrk_id}: missing {field}")
            elif not path_exists(value):
                warnings.append(f"{wrk_id}: {field} does not exist -> {value}")

    if status in {"done", "archived"}:
        value = frontmatter_value(frontmatter, "html_verification_ref")
        if not value:
            warnings.append(f"{wrk_id}: missing html_verification_ref")
        elif not path_exists(value):
            warnings.append(f"{wrk_id}: html_verification_ref does not exist -> {value}")


def check_file(path: Path, expected_status: str | None):
    frontmatter = extract_frontmatter(path)
    if not frontmatter:
        return

    status = frontmatter_value(frontmatter, "status")
    if not status:
        errors.append(f"{path.name}: missing status")
        return

    if status in legacy_statuses:
        warnings.append(f"{path.name}: legacy status '{status}' should be migrated")
        return

    if status not in allowed_statuses:
        errors.append(f"{path.name}: invalid status '{status}'")
        return

    if expected_status and status != expected_status:
        errors.append(f"{path.name}: status '{status}' does not match containing folder '{expected_status}/'")

    if expected_status == "working":
        timestamp = frontmatter_value(frontmatter, "updated_at") or frontmatter_value(frontmatter, "created_at")
        dt = parse_iso8601(timestamp)
        if dt is None:
            warnings.append(f"{path.name}: working item missing parseable updated_at/created_at")
        else:
            age_days = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).days
            if age_days > 7:
                warnings.append(f"{path.name}: working item is stale ({age_days} days old)")

    check_workflow_evidence(path, frontmatter)


print("Scanning work-queue for inconsistencies...")

for folder, expected in active_dirs.items():
    dir_path = queue_dir / folder
    if dir_path.exists():
        for path in dir_path.glob("WRK-*.md"):
            check_file(path, expected)

archive_dir = queue_dir / "archive"
if archive_dir.exists():
    for path in archive_dir.rglob("WRK-*.md"):
        check_file(path, "archived")

if errors:
    print(f"\nErrors found ({len(errors)}):")
    for item in errors:
        print(f"  ✖ {item}")

if warnings:
    print(f"\nWarnings found ({len(warnings)}):")
    for item in warnings:
        print(f"  ⚠ {item}")

if errors:
    print("\nQueue state validation failed.")
    sys.exit(1)

print("\nQueue state validation passed.")
PY
