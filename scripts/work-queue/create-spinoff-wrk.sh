#!/usr/bin/env bash
# create-spinoff-wrk.sh — scaffold a pending WRK for an archive blocker (WRK-668)
#
# Usage: create-spinoff-wrk.sh <source-WRK> <blocker-description>
#            [--owner <provider>] [--workstation <machine>]
#
# Outputs:  pending/WRK-NNN.md  (new spin-off item)
#           Appends spin-off ID to source archive-tooling.yaml (if present)
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
SCRIPTS_DIR="${WORKSPACE_ROOT}/scripts/work-queue"

# ── Parse arguments ────────────────────────────────────────────────────────────
SOURCE_WRK="${1:-}"
BLOCKER_DESC="${2:-}"
OWNER="claude"
WORKSTATION="ace-linux-1"

if [[ -z "$SOURCE_WRK" || -z "$BLOCKER_DESC" ]]; then
  echo "Usage: $0 <source-WRK> <blocker-description> [--owner <provider>] [--workstation <machine>]" >&2
  exit 1
fi

shift 2
while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner)      OWNER="${2:-claude}";         shift 2 ;;
    --workstation) WORKSTATION="${2:-ace-linux-1}"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Normalize source WRK id
[[ "$SOURCE_WRK" =~ ^WRK- ]] || SOURCE_WRK="WRK-${SOURCE_WRK}"

# ── Allocate next WRK id ───────────────────────────────────────────────────────
# Use next-id.sh; fall back to Python if it fails (e.g. non-numeric WRK filenames present)
_RAW_ID=$(bash "${SCRIPTS_DIR}/next-id.sh" 2>/dev/null) || _RAW_ID=""
if [[ -z "$_RAW_ID" ]]; then
  _QUEUE_DIR="$QUEUE_DIR"
  _RAW_ID=$(uv run --no-project python -c "
import re
from pathlib import Path
q = Path('${_QUEUE_DIR}')
ids = []
for d in ('pending','working','done','blocked'):
    for f in (q/d).glob('WRK-*.md'):
        m = re.fullmatch(r'WRK-(\d+)', f.stem)
        if m: ids.append(int(m.group(1)))
for f in (q/'archive').rglob('WRK-*.md'):
    m = re.fullmatch(r'WRK-(\d+)', f.stem)
    if m: ids.append(int(m.group(1)))
print(f'{(max(ids)+1 if ids else 1):03d}')
  ")
fi
[[ "$_RAW_ID" =~ ^WRK- ]] && NEW_ID="$_RAW_ID" || NEW_ID="WRK-${_RAW_ID}"

NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PENDING_FILE="${QUEUE_DIR}/pending/${NEW_ID}.md"

# ── Scaffold the pending WRK file ─────────────────────────────────────────────
cat > "$PENDING_FILE" << EOF
---
id: ${NEW_ID}
title: "fix: archive blocker from ${SOURCE_WRK} — ${BLOCKER_DESC:0:60}"
status: pending
route: A
priority: high
complexity: simple
compound: false
created_at: ${NOW_ISO}
target_repos:
  - workspace-hub
commit:
spec_ref:
related:
  - ${SOURCE_WRK}
blocked_by: []
synced_to: []
plan_reviewed: false
plan_approved: false
percent_complete: 0
brochure_status: n/a
computer: ${WORKSTATION}
execution_workstations: [${WORKSTATION}]
plan_workstations: [${WORKSTATION}]
provider: ${OWNER}
orchestrator: ${OWNER}
cross_review: pending
stage_evidence_ref: .claude/work-queue/assets/${NEW_ID}/evidence/stage-evidence.yaml
subcategory: work-queue
category: harness
---
# fix: Archive Blocker from ${SOURCE_WRK}

## Mission

Resolve archive blocker identified during ${SOURCE_WRK} archiving.

## What

${BLOCKER_DESC}

## Why

${SOURCE_WRK} could not be archived due to this unresolved blocker. Spinning off
as a separate work item to keep ${SOURCE_WRK} archivable and track remediation
independently.

## Acceptance Criteria

- [ ] Blocker resolved: ${BLOCKER_DESC}
- [ ] ${SOURCE_WRK} can be archived cleanly after this item is done
- [ ] archive-tooling.yaml in ${SOURCE_WRK} updated with resolution reference
EOF

echo "✔ Spin-off created: ${NEW_ID} → ${PENDING_FILE}"

# ── Append spin-off to source archive-tooling.yaml if it exists ───────────────
TOOLING="${WORKSPACE_ROOT}/.claude/work-queue/assets/${SOURCE_WRK}/evidence/archive-tooling.yaml"
if [[ -f "$TOOLING" ]]; then
  _NEW_ID="$NEW_ID" _TOOLING="$TOOLING" uv run --no-project python -c "
import yaml, os
from pathlib import Path
tooling = Path(os.environ['_TOOLING'])
new_id = os.environ['_NEW_ID']
data = yaml.safe_load(tooling.read_text(encoding='utf-8')) or {}
spin_offs = list(data.get('spin_off_wrks') or [])
if new_id not in spin_offs:
    spin_offs.append(new_id)
data['spin_off_wrks'] = spin_offs
tooling.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding='utf-8')
"
  echo "✔ Recorded spin-off in ${TOOLING}"
fi

# ── Regenerate queue index ─────────────────────────────────────────────────────
uv run --no-project python "${QUEUE_DIR}/scripts/generate-index.py" >/dev/null 2>&1 || true

echo "${NEW_ID}"
