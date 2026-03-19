#!/usr/bin/env bash
# archive-item.sh - Move completed item to archive with hardened gates
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
GATE_LOGGER="${WORKSPACE_ROOT}/scripts/work-queue/log-gate-event.sh"

ITEM_ID="${1:-}"
if [[ -z "$ITEM_ID" ]]; then
  echo "Usage: $0 <WRK-NNN>"
  exit 1
fi

# Normalize ID format
[[ "$ITEM_ID" =~ ^WRK- ]] || ITEM_ID="WRK-${ITEM_ID}"

# Find the item file — prefer working > pending > blocked > done order
ITEM_FILE=""
for dir in "working" "pending" "blocked" "done"; do
  if [[ -f "${QUEUE_DIR}/${dir}/${ITEM_ID}.md" ]]; then
    ITEM_FILE="${QUEUE_DIR}/${dir}/${ITEM_ID}.md"
    break
  fi
done

if [[ -z "$ITEM_FILE" ]]; then
  echo "✖ Error: Item ${ITEM_ID} not found." >&2
  exit 1
fi

# GATES
echo "Checking archive gates for ${ITEM_ID}..."

VALIDATOR="${WORKSPACE_ROOT}/scripts/work-queue/verify-gate-evidence.py"

# 1. Merge status check (real git check — no more stub)
GIT_STATUS=$(git -C "${WORKSPACE_ROOT}" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [[ "$GIT_STATUS" -gt 0 ]]; then
  echo "⚠ Warning: working tree has ${GIT_STATUS} uncommitted change(s). Commit or stash before archiving." >&2
else
  echo "✔ Merge status: working tree clean"
fi

# 2. Sync status check (real remote check — no more stub)
REMOTE_DIFF=$(git -C "${WORKSPACE_ROOT}" rev-list --count HEAD..origin/main 2>/dev/null || echo "unknown")
if [[ "$REMOTE_DIFF" == "0" || "$REMOTE_DIFF" == "unknown" ]]; then
  echo "✔ Sync status: in sync with origin/main (or remote unreachable)"
else
  echo "⚠ Warning: ${REMOTE_DIFF} commit(s) behind origin/main — push or pull before archiving." >&2
fi

# 3. Archive-tooling gate (new --phase archive check — WRK-668)
if [[ -x "$GATE_LOGGER" ]]; then
  bash "$GATE_LOGGER" "$ITEM_ID" "archive" "verify_gate_evidence_start" "orchestrator" "phase=archive"
fi
if ! uv run --no-project python "$VALIDATOR" "$ITEM_ID" --phase archive --retry 3; then
  if [[ -x "$GATE_LOGGER" ]]; then
    bash "$GATE_LOGGER" "$ITEM_ID" "archive" "verify_gate_evidence_fail" "orchestrator" "phase=archive"
  fi
  echo "✖ Archive gate evidence verification failed for ${ITEM_ID}; cannot archive." >&2
  echo "  Tip: copy scripts/work-queue/templates/archive-tooling-template.yaml to" >&2
  echo "       .claude/work-queue/assets/${ITEM_ID}/evidence/archive-tooling.yaml and fill it in." >&2
  echo "  For hard blockers: bash scripts/work-queue/create-spinoff-wrk.sh ${ITEM_ID} '<blocker>'" >&2
  exit 1
fi

if [[ -x "$GATE_LOGGER" ]]; then
  bash "$GATE_LOGGER" "$ITEM_ID" "archive" "verify_gate_evidence_pass" "orchestrator" "phase=archive"
  bash "$GATE_LOGGER" "$ITEM_ID" "archive" "verify_gate_evidence" "orchestrator" "archive gate verified"
fi

# Create archive directory for current month
ARCHIVE_DIR="${QUEUE_DIR}/archive/$(date +%Y-%m)"
mkdir -p "$ARCHIVE_DIR"

BASENAME=$(basename "$ITEM_FILE")
ARCHIVE_PATH="${ARCHIVE_DIR}/${BASENAME}"

# Update status to archived
NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
uv run --no-project python <<EOF
import re
with open("$ITEM_FILE", 'r') as f:
    content = f.read()
# Update status to archived
content = re.sub(r"^status:.*$", "status: archived", content, flags=re.MULTILINE)
# Ensure completed_at is set
if "completed_at:" not in content:
    content = re.sub(r"^---\s*\n", "---\ncompleted_at: $NOW_ISO\n", content)
else:
    content = re.sub(r"^completed_at:.*$", "completed_at: $NOW_ISO", content, flags=re.MULTILINE)

with open("$ARCHIVE_PATH", 'w') as f:
    f.write(content)
EOF

# Hard gate: Stage 20 evidence update required before file move (WRK-668 GAP-F)
STAGE_UPDATER="${WORKSPACE_ROOT}/scripts/work-queue/update-stage-evidence.py"
if [[ -f "$STAGE_UPDATER" ]]; then
  if ! uv run --no-project python "$STAGE_UPDATER" "$ITEM_ID" --order 20 --status done --reviewed-by "orchestrator" >/dev/null; then
    echo "✖ Could not update stage-evidence order 20 for ${ITEM_ID}; archive aborted." >&2
    exit 1
  fi
fi

# Remove from all source directories (prevents ghost copies in pending/blocked)
for dir in "working" "pending" "blocked" "done"; do
  stale="${QUEUE_DIR}/${dir}/${ITEM_ID}.md"
  if [[ -f "$stale" ]]; then
    rm "$stale"
    [[ "$stale" != "$ITEM_FILE" ]] && echo "✔ Removed ghost copy: ${dir}/${ITEM_ID}.md"
  fi
done

# Update centralized status index
INDEX_UPDATER="${WORKSPACE_ROOT}/scripts/work-queue/update-wrk-index.sh"
if [[ -x "$INDEX_UPDATER" ]]; then
  bash "$INDEX_UPDATER" "$ITEM_ID" "archived" "$(basename "$0")" || true
fi

# Regenerate index
uv run --no-project python "${QUEUE_DIR}/scripts/generate-index.py"

if [[ -x "$GATE_LOGGER" ]]; then
  bash "$GATE_LOGGER" "$ITEM_ID" "archive" "archive_item" "orchestrator" "work item archived"
  bash "$GATE_LOGGER" "$ITEM_ID" "archive" "close_or_archive" "orchestrator" "terminal archive signal"
fi

echo "✔ Archived: ${ITEM_ID} -> archive/$(date +%Y-%m)/${BASENAME}"

# Best-effort knowledge capture (non-blocking — never fails the archive gate)
CAPTURE_SCRIPT="${WORKSPACE_ROOT}/scripts/knowledge/capture-wrk-summary.sh"
if [[ -x "${CAPTURE_SCRIPT}" ]]; then
  bash "${CAPTURE_SCRIPT}" "${ITEM_ID}" || true
fi

# Auto-unblock items whose dependencies are now resolved
AUTO_UNBLOCK="${WORKSPACE_ROOT}/scripts/work-queue/auto-unblock.sh"
if [[ -x "$AUTO_UNBLOCK" ]]; then
  bash "$AUTO_UNBLOCK" "${ITEM_ID}" || true
fi

# Remove stale checkpoint so /work run does not try to resume an archived item
CHECKPOINT="${WORKSPACE_ROOT}/.claude/work-queue/assets/${ITEM_ID}/checkpoint.yaml"
if [[ -f "$CHECKPOINT" ]]; then
  rm "$CHECKPOINT"
  echo "✔ Checkpoint removed: ${ITEM_ID}"
fi

# Auto-close parent feature if all children are now archived
FEATURE_AUTO_CLOSE="${WORKSPACE_ROOT}/scripts/work-queue/feature-auto-close.sh"
if [[ -x "$FEATURE_AUTO_CLOSE" ]]; then
  bash "$FEATURE_AUTO_CLOSE" "${ITEM_ID}" || true
fi

# Extract category from archived WRK frontmatter
CATEGORY=$(grep -oP '^category:\s*\K\S+' "$ARCHIVE_PATH" 2>/dev/null || echo "uncategorized")

# Close WRK GitHub Issue (non-blocking)
ISSUE_UPDATER="${WORKSPACE_ROOT}/scripts/knowledge/update-github-issue.py"
if [[ -f "$ISSUE_UPDATER" ]]; then
  uv run --no-project python "$ISSUE_UPDATER" "$ITEM_ID" --close 2>/dev/null || true
fi

# Create GitHub Issues for future-work follow-ons (non-blocking)
ASSETS_DIR="${WORKSPACE_ROOT}/.claude/work-queue/assets/${ITEM_ID}"
FW_FILE="${ASSETS_DIR}/evidence/future-work.yaml"
if [[ -f "$FW_FILE" ]]; then
  uv run --no-project python -c "
import sys, re, subprocess
fw_path = sys.argv[1]
wrk_id = sys.argv[2]
category = sys.argv[3] if len(sys.argv) > 3 else 'uncategorized'
text = open(fw_path).read()
titles = re.findall(r'title:\s*[\"'\''](.*?)[\"'\'']|title:\s*(.+)', text)
for match in titles:
    title = (match[0] or match[1]).strip()
    if not title:
        continue
    label_args = ['--label', 'follow-on', '--label', f'cat:{category}']
    body = f'Follow-on from {wrk_id} archive.\n\nSource: {fw_path}'
    subprocess.run(
        ['gh', 'issue', 'create', '--repo', 'vamseeachanta/workspace-hub',
         '--title', f'FW ({wrk_id}): {title}'] + label_args + ['--body', body],
        capture_output=True, text=True, timeout=30
    )
" "$FW_FILE" "$ITEM_ID" "$CATEGORY" 2>/dev/null || true
fi

# Regenerate lifecycle HTML so Stage 20 shows as done (not stale active/pending)
LIFECYCLE_HTML="${WORKSPACE_ROOT}/.claude/work-queue/assets/${ITEM_ID}/${ITEM_ID}-lifecycle.html"
HTML_LOG="${WORKSPACE_ROOT}/.claude/work-queue/assets/${ITEM_ID}/html-gen.log"
if uv run --no-project python "${WORKSPACE_ROOT}/scripts/work-queue/generate-html-review.py" "${ITEM_ID}" --lifecycle 2>>"${HTML_LOG}"; then
  echo "✔ Lifecycle HTML refreshed: ${LIFECYCLE_HTML}"
fi
