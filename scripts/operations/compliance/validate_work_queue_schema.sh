#!/usr/bin/env bash

# ABOUTME: Validate WRK frontmatter schema in work queue items
# ABOUTME: Supports warn/gate mode and changed-only scope for incremental enforcement

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
MODE="warn"          # warn | gate
SCOPE="changed"      # changed | all
BASE_REF="origin/main"
REPORT_FILE=""

usage() {
  cat << USAGE
Usage: $(basename "$0") [--mode warn|gate] [--scope changed|all] [--base-ref <git-ref>] [--report <file>]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-warn}"; shift 2 ;;
    --scope)
      SCOPE="${2:-changed}"; shift 2 ;;
    --base-ref)
      BASE_REF="${2:-origin/main}"; shift 2 ;;
    --report)
      REPORT_FILE="${2:-}"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ "$MODE" != "warn" && "$MODE" != "gate" ]]; then
  echo "Invalid --mode: $MODE" >&2; exit 1
fi
if [[ "$SCOPE" != "changed" && "$SCOPE" != "all" ]]; then
  echo "Invalid --scope: $SCOPE" >&2; exit 1
fi

source "$WORKSPACE_ROOT/scripts/lib/python-resolver.sh"
${PYTHON} - "$WORKSPACE_ROOT" "$MODE" "$SCOPE" "$BASE_REF" "$REPORT_FILE" << 'PY'
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

root = Path(sys.argv[1])
mode = sys.argv[2]
scope = sys.argv[3]
base_ref = sys.argv[4]
report_file = sys.argv[5]

active_dirs = [
    root / ".claude/work-queue/pending",
    root / ".claude/work-queue/working",
    root / ".claude/work-queue/blocked",
]

required = [
    "id", "title", "status", "priority", "complexity", "created_at",
    "target_repos", "spec_ref", "plan_reviewed", "plan_approved", "provider",
]

enum_status = {"pending", "working", "blocked", "archived", "failed", "done"}
enum_priority = {"high", "medium", "low"}
enum_complexity = {"simple", "medium", "complex", "high", "low"}

files = []
for d in active_dirs:
    if d.is_dir():
        files.extend(sorted(d.glob("WRK-*.md")))

if scope == "changed":
    changed = set()
    cmd = ["git", "-C", str(root), "diff", "--name-only", f"{base_ref}...HEAD"]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        out = subprocess.check_output(["git", "-C", str(root), "diff", "--name-only", "HEAD~1..HEAD"], text=True)
    for line in out.splitlines():
        if line.startswith(".claude/work-queue/") and line.endswith(".md"):
            changed.add((root / line).resolve())
    files = [f for f in files if f.resolve() in changed]

issues = []

for f in files:
    text = f.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        issues.append({"file": str(f.relative_to(root)), "kind": "frontmatter_missing", "detail": "Missing YAML frontmatter"})
        continue

    raw = m.group(1)
    if yaml is not None:
        try:
            data = yaml.safe_load(raw) or {}
        except Exception as e:
            issues.append({"file": str(f.relative_to(root)), "kind": "frontmatter_invalid", "detail": f"YAML parse error: {e}"})
            continue
    else:
        data = {}
        for line in raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()

    for key in required:
        if key not in data:
            issues.append({"file": str(f.relative_to(root)), "kind": "missing_field", "detail": key})

    # semantic checks for present fields
    s = data.get("status")
    if s is not None and str(s) not in enum_status:
        issues.append({"file": str(f.relative_to(root)), "kind": "invalid_status", "detail": str(s)})

    p = data.get("priority")
    if p is not None and str(p) not in enum_priority:
        issues.append({"file": str(f.relative_to(root)), "kind": "invalid_priority", "detail": str(p)})

    c = data.get("complexity")
    if c is not None and str(c) not in enum_complexity:
        issues.append({"file": str(f.relative_to(root)), "kind": "invalid_complexity", "detail": str(c)})

    tr = data.get("target_repos")
    if tr is not None and not isinstance(tr, list):
        issues.append({"file": str(f.relative_to(root)), "kind": "invalid_target_repos", "detail": "must be list"})

    # Route-C guard: if complexity=complex, require non-empty spec_ref
    if str(c) == "complex" and not str(data.get("spec_ref", "")).strip():
        issues.append({"file": str(f.relative_to(root)), "kind": "missing_spec_ref", "detail": "complex item requires spec_ref"})

summary = {
    "mode": mode,
    "scope": scope,
    "base_ref": base_ref,
    "checked_files": len(files),
    "issue_count": len(issues),
    "issues": issues,
}

# directory/status consistency check
for f in files:
    rel = f.relative_to(root).as_posix()
    if "/pending/" in rel:
        expected = "pending"
    elif "/working/" in rel:
        expected = "working"
    elif "/blocked/" in rel:
        expected = "blocked"
    else:
        expected = None
    if expected:
        text = f.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if m:
            data = yaml.safe_load(m.group(1)) if yaml is not None else {}
            if isinstance(data, dict):
                actual = str(data.get("status", ""))
                # allow terminal states to remain in active dirs pending archival
                if actual in {"done", "archived", "failed"}:
                    continue
                if actual and actual != expected:
                    issues.append({"file": str(f.relative_to(root)), "kind": "status_directory_mismatch", "detail": f"status={actual}, dir={expected}"})

summary["issue_count"] = len(issues)
summary["issues"] = issues

print(json.dumps(summary, indent=2))

if report_file:
    Path(report_file).parent.mkdir(parents=True, exist_ok=True)
    Path(report_file).write_text(json.dumps(summary, indent=2), encoding="utf-8")

if mode == "gate" and issues:
    sys.exit(2)
PY
