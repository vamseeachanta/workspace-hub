#!/usr/bin/env bash
# improve.sh — Autonomous ecosystem improvement from session signals
# Trigger: Stop hook #9 (runs after ecosystem-health-check.sh)
# Implements /improve skill phases as shell + Anthropic API hybrid
#
# Usage:
#   bash improve.sh              # Full mode (all 7 phases)
#   bash improve.sh --quick      # Shell-only phases (skip API calls)
#   bash improve.sh --dry-run    # All phases, no file writes
#
# Platform: Linux, macOS
# Dependencies: bash, jq, curl, yq (optional)

set -uo pipefail

# Drain stdin (stop hook may pipe data)
if [[ ! -t 0 ]]; then
    cat > /dev/null 2>&1 || true
fi

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"

# Workspace resolution
if [[ -f "${SCRIPT_DIR}/../../.claude/hooks/resolve-workspace.sh" ]]; then
    source "${SCRIPT_DIR}/../../.claude/hooks/resolve-workspace.sh" 2>/dev/null
fi
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"

STATE_DIR="${WORKSPACE_HUB}/.claude/state"
REVIEW_DIR="${STATE_DIR}/pending-reviews"
IMPROVE_WORKDIR="${STATE_DIR}/improve-workdir"
CHANGELOG="${STATE_DIR}/improve-changelog.yaml"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_TAG=$(date +%Y%m%d)

# --- Parse flags ---
QUICK_MODE=false
DRY_RUN=false
for arg in "$@"; do
    case "$arg" in
        --quick) QUICK_MODE=true ;;
        --dry-run) DRY_RUN=true ;;
    esac
done

export WORKSPACE_HUB STATE_DIR REVIEW_DIR IMPROVE_WORKDIR CHANGELOG
export TIMESTAMP DATE_TAG QUICK_MODE DRY_RUN

# --- Guard: exit if no signals ---
has_signals=false
for f in "${REVIEW_DIR}"/*.jsonl; do
    [[ ! -f "$f" ]] && continue
    [[ "$(basename "$f")" == "session-summaries.jsonl" ]] && continue
    if [[ -s "$f" ]]; then
        has_signals=true
        break
    fi
done

# Also check accumulator for mature patterns
if [[ -f "${STATE_DIR}/accumulator.json" ]]; then
    mature_count=$(jq '[.skill_patterns // {} | to_entries[] | select(.value.mature == true)] | length' \
        "${STATE_DIR}/accumulator.json" 2>/dev/null || echo "0")
    [[ "$mature_count" -gt 0 ]] && has_signals=true
fi

if [[ "$has_signals" == "false" ]]; then
    echo "improve: no signals to process, skipping"
    exit 0
fi

# --- Setup work directory ---
mkdir -p "$IMPROVE_WORKDIR" 2>/dev/null

# --- Source lib modules ---
for lib in collect classify ecosystem guard apply log cleanup; do
    if [[ -f "${LIB_DIR}/${lib}.sh" ]]; then
        source "${LIB_DIR}/${lib}.sh"
    else
        echo "improve: missing lib/${lib}.sh, skipping" >&2
        exit 1
    fi
done

# --- Execute phases ---
echo "improve: starting (quick=${QUICK_MODE}, dry_run=${DRY_RUN})"

# Phase 1: COLLECT (always runs — pure shell)
phase_collect || { echo "improve: collect phase failed" >&2; exit 0; }

# Phase 2: CLASSIFY (skip in quick mode — API call)
if [[ "$QUICK_MODE" == "false" ]]; then
    phase_classify || echo "improve: classify phase failed, continuing with shell-only" >&2
fi

# Phase 3: ECOSYSTEM REVIEW (partial in quick mode)
phase_ecosystem || echo "improve: ecosystem phase failed, continuing" >&2

# Phase 4: GUARD (always runs — pure shell)
phase_guard || { echo "improve: guard phase rejected all improvements" >&2; phase_cleanup; exit 0; }

# Phase 5: APPLY (skip in quick mode — API call)
if [[ "$QUICK_MODE" == "false" ]]; then
    phase_apply || echo "improve: apply phase failed" >&2
fi

# Phase 6: LOG (always runs — pure shell)
phase_log || echo "improve: log phase failed" >&2

# Phase 7: CLEANUP (always runs — pure shell)
phase_cleanup || echo "improve: cleanup phase failed" >&2

# --- Summary ---
changes_applied=$(cat "${IMPROVE_WORKDIR}/changes_count" 2>/dev/null || echo "0")
echo "improve: done — ${changes_applied} change(s) applied"

# Clean up work directory
rm -rf "$IMPROVE_WORKDIR" 2>/dev/null
exit 0
