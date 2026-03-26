#!/usr/bin/env bash
# workstation-offload.sh — One-command pipeline to offload a GSD phase to
# another machine: package → transfer → execute → collect results.
#
# Usage:
#   # Offload phase 3 to the best-fit remote machine:
#   bash scripts/operations/workstation-offload.sh --phase 3
#
#   # Offload to a specific machine:
#   bash scripts/operations/workstation-offload.sh --phase 3 --machine dev-primary
#
#   # With custom timeout (default 30 minutes):
#   bash scripts/operations/workstation-offload.sh --phase 3 --timeout 3600
#
#   # Dry-run (shows what would happen at each step):
#   bash scripts/operations/workstation-offload.sh --phase 3 --dry-run
#
#   # Skip merge — just fetch and show results:
#   bash scripts/operations/workstation-offload.sh --phase 3 --no-merge
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"

source "${WORKSPACE_HUB}/scripts/lib/workstation-lib.sh"

# ── Parse arguments ─────────────────────────────────────────────────────────
PHASE=""
WRK=""
MACHINE=""
TIMEOUT=1800
DRY_RUN=false
NO_MERGE=false

usage() {
  cat <<'USAGE'
Usage: workstation-offload.sh [OPTIONS]

Offload a GSD phase to another machine: package → transfer → execute → collect.

Options:
  --phase N         Phase number to offload
  --wrk WRK-ID      WRK item to offload
  --machine NAME    Target machine (default: auto-select best fit)
  --timeout SECS    Claude agent timeout (default: 1800 = 30 min)
  --no-merge        Fetch results but don't auto-merge
  --dry-run         Show what would happen without executing
  -h, --help        Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --phase)    PHASE="$2"; shift 2 ;;
    --wrk)      WRK="$2"; shift 2 ;;
    --machine)  MACHINE="$2"; shift 2 ;;
    --timeout)  TIMEOUT="$2"; shift 2 ;;
    --no-merge) NO_MERGE=true; shift ;;
    --dry-run)  DRY_RUN=true; shift ;;
    -h|--help)  usage; exit 0 ;;
    *)
      echo "ERROR: unknown arg: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$PHASE" && -z "$WRK" ]]; then
  echo "ERROR: provide --phase N or --wrk WRK-ID" >&2
  exit 1
fi

log() { echo "[offload] $*"; }

# ── Step 1: Package ─────────────────────────────────────────────────────────
log "Step 1/4: Packaging handoff bundle..."
HANDOFF_ARGS=()
[[ -n "$PHASE" ]] && HANDOFF_ARGS+=(--phase "$PHASE")
[[ -n "$WRK" ]] && HANDOFF_ARGS+=(--wrk "$WRK")

if [[ "$DRY_RUN" == "true" ]]; then
  bash "${SCRIPT_DIR}/workstation-handoff.sh" "${HANDOFF_ARGS[@]}" --dry-run
  BUNDLE="/tmp/handoff-dry-run.tar.gz"
else
  BUNDLE_OUTPUT=$(bash "${SCRIPT_DIR}/workstation-handoff.sh" "${HANDOFF_ARGS[@]}" 2>&1)
  BUNDLE=$(echo "$BUNDLE_OUTPUT" | grep "^Handoff bundle created:" | sed 's/^Handoff bundle created: //')
  RESULT_BRANCH=$(echo "$BUNDLE_OUTPUT" | grep "^Result branch:" | sed 's/^Result branch: *//')
  if [[ -z "$BUNDLE" || ! -f "$BUNDLE" ]]; then
    echo "ERROR: handoff packaging failed" >&2
    echo "$BUNDLE_OUTPUT" >&2
    exit 1
  fi
  log "  Bundle: ${BUNDLE}"
  log "  Result branch: ${RESULT_BRANCH}"
fi

# ── Step 2: Fleet check ────────────────────────────────────────────────────
log "Step 2/4: Checking fleet status..."
if [[ "$DRY_RUN" == "true" ]]; then
  bash "${SCRIPT_DIR}/workstation-status.sh" --quick 2>&1 | sed 's/^/  /'
else
  # Quick reachability check (just verify at least one remote is up)
  STATUS_OUTPUT=$(bash "${SCRIPT_DIR}/workstation-status.sh" --quick --json 2>&1)
  ONLINE_COUNT=$(echo "$STATUS_OUTPUT" | uv run --no-project python -c "
import sys, json
data = json.load(sys.stdin)
online = sum(1 for m in data['machines'] if m['status'] == 'online')
print(online)
" 2>/dev/null || echo "0")
  if [[ "$ONLINE_COUNT" -eq 0 && -z "$MACHINE" ]]; then
    echo "ERROR: no remote machines are online" >&2
    echo "  Use --machine to target a specific machine, or check SSH connectivity" >&2
    exit 1
  fi
  log "  ${ONLINE_COUNT} remote machine(s) online"
fi

# ── Step 3: Dispatch ────────────────────────────────────────────────────────
log "Step 3/4: Dispatching to remote agent..."
AGENT_ARGS=(--bundle "$BUNDLE" --timeout "$TIMEOUT")
[[ -n "$MACHINE" ]] && AGENT_ARGS+=(--machine "$MACHINE")

if [[ "$DRY_RUN" == "true" ]]; then
  if [[ -n "$MACHINE" ]]; then
    log "  Would dispatch to: ${MACHINE}"
  else
    log "  Would auto-select best-fit remote machine with [claude] capability"
  fi
  log "  Timeout: ${TIMEOUT}s"
  echo ""
  log "DRY RUN — would then collect results and merge into current branch"
  exit 0
fi

log "  Sending to remote machine (timeout=${TIMEOUT}s)..."
bash "${SCRIPT_DIR}/workstation-remote-agent.sh" "${AGENT_ARGS[@]}"
AGENT_EXIT=$?

if [[ "$AGENT_EXIT" -ne 0 ]]; then
  echo ""
  log "Remote agent failed (exit ${AGENT_EXIT})"
  log "Bundle preserved at: ${BUNDLE}"
  log "You can retry with: bash scripts/operations/workstation-remote-agent.sh --bundle ${BUNDLE}"
  exit "$AGENT_EXIT"
fi

# ── Step 4: Collect ─────────────────────────────────────────────────────────
log "Step 4/4: Collecting results..."
COLLECT_ARGS=(--branch "$RESULT_BRANCH")
[[ -n "$MACHINE" ]] && COLLECT_ARGS+=(--machine "$MACHINE")

if [[ "$NO_MERGE" == "true" ]]; then
  COLLECT_ARGS+=(--diff-only)
else
  COLLECT_ARGS+=(--merge --cleanup)
fi

bash "${SCRIPT_DIR}/workstation-collect.sh" "${COLLECT_ARGS[@]}"

echo ""
log "Offload complete."
if [[ "$NO_MERGE" == "true" ]]; then
  log "Results on branch: ${RESULT_BRANCH}"
  log "To merge: bash scripts/operations/workstation-collect.sh --branch ${RESULT_BRANCH} --merge"
fi
