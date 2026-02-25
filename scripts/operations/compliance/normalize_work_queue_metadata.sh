#!/usr/bin/env bash

# ABOUTME: Normalize WRK metadata in active queue items to required schema
# ABOUTME: Optionally relocates files so status and directory are consistent

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
MODE="dry-run"      # dry-run | apply
RELOCATE="false"    # true | false

usage() {
  cat << USAGE
Usage: $(basename "$0") [--mode dry-run|apply] [--relocate true|false]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="${2:-dry-run}"; shift 2 ;;
    --relocate) RELOCATE="${2:-false}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

source "$WORKSPACE_ROOT/scripts/lib/python-resolver.sh"
${PYTHON} - "$WORKSPACE_ROOT" "$MODE" "$RELOCATE" << 'PY'
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

root = Path(sys.argv[1])
mode = sys.argv[2]
relocate = sys.argv[3].lower() == "true"

dirs = {
    "pending": root / ".claude/work-queue/pending",
    "working": root / ".claude/work-queue/working",
    "blocked": root / ".claude/work-queue/blocked",
}

required_defaults = {
    "priority": "medium",
    "complexity": "medium",
    "created_at": "2026-02-17T00:00:00Z",
    "target_repos": ["workspace-hub"],
    "spec_ref": "",
    "plan_reviewed": False,
    "plan_approved": False,
    "provider": "claude",
}

status_map = {
    "on-hold": "blocked",
    "on_hold": "blocked",
}

complexity_map = {
    "moderate": "medium",
}

changes = []
moves = []

for dir_status, d in dirs.items():
    if not d.is_dir():
        continue
    for f in sorted(d.glob("WRK-*.md")):
        text = f.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
        if not m:
            continue

        raw = m.group(1)
        body = text[m.end():]
        try:
            data = yaml.safe_load(raw) if yaml else {}
        except Exception:
            continue
        if not isinstance(data, dict):
            continue

        touched = False

        # normalize status aliases
        status = str(data.get("status", dir_status))
        if status in status_map:
            data["status"] = status_map[status]
            status = data["status"]
            touched = True

        complexity = str(data.get("complexity", ""))
        if complexity in complexity_map:
            data["complexity"] = complexity_map[complexity]
            touched = True

        # fill required defaults if missing
        for k, default in required_defaults.items():
            if k not in data:
                data[k] = default
                touched = True

        # ensure minimal required core presence from filename when missing
        if "id" not in data:
            data["id"] = f.stem
            touched = True
        if "title" not in data:
            data["title"] = f.stem
            touched = True

        # relocate if status-directory mismatch
        target_dir = None
        if status in dirs and status != dir_status:
            target_dir = dirs[status]

        if touched:
            changes.append(str(f.relative_to(root)))
            if mode == "apply":
                new_frontmatter = yaml.safe_dump(data, sort_keys=False, allow_unicode=False).strip()
                f.write_text(f"---\n{new_frontmatter}\n---\n\n{body}", encoding="utf-8")

        if relocate and target_dir is not None:
            moves.append((f, target_dir / f.name))

# execute moves after edits
if mode == "apply":
    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists() and src.resolve() != dst.resolve():
            src.replace(dst)

print(f"mode={mode} relocate={relocate} updated={len(changes)} moves={len(moves)}")
for c in changes[:120]:
    print(f"updated: {c}")
for src, dst in moves[:120]:
    print(f"move: {src.relative_to(root)} -> {dst.relative_to(root)}")
PY
