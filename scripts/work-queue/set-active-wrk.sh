#!/usr/bin/env bash
# set-active-wrk.sh <WRK-NNN> [--force] — write active WRK id to state file
# Scope guard: blocks activation if another WRK is active and not done/archived (WRK-1174)
set -euo pipefail

# ── Parse arguments ──────────────────────────────────────────────────────────
FORCE=false
WRK_ID=""
for arg in "$@"; do
    case "$arg" in
        --force) FORCE=true ;;
        *) WRK_ID="$arg" ;;
    esac
done

[[ -z "$WRK_ID" ]] && { echo "Usage: set-active-wrk.sh <WRK-NNN> [--force]" >&2; exit 1; }
[[ ! "$WRK_ID" =~ ^WRK-[0-9]+$ ]] && { echo "ERROR: invalid WRK id: $WRK_ID" >&2; exit 1; }

WORKSPACE_HUB="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . \
  || git rev-parse --show-toplevel 2>/dev/null || echo "")}"
[[ -z "$WORKSPACE_HUB" ]] && { echo "ERROR: WORKSPACE_HUB not set" >&2; exit 1; }

STATE_DIR="${WORKSPACE_HUB}/.claude/state"
WQ_DIR="${WORKSPACE_HUB}/.claude/work-queue"
ACTIVE_FILE="${STATE_DIR}/active-wrk"

# Warn (non-fatal) if WRK file not found in any work-queue subdirectory
if [[ -d "$WQ_DIR" ]] && ! find "$WQ_DIR" -maxdepth 3 -name "${WRK_ID}.md" | grep -q .; then
    echo "WARN: ${WRK_ID}.md not found in ${WQ_DIR}; recording anyway" >&2
fi

# ── Scope guard ──────────────────────────────────────────────────────────────
mkdir -p "$STATE_DIR"
if [[ -f "$ACTIVE_FILE" ]] && [[ "$FORCE" == "false" ]]; then
    CURRENT_WRK="$(head -n1 "$ACTIVE_FILE" 2>/dev/null | tr -d '[:space:]')"
    if [[ -n "$CURRENT_WRK" ]] && [[ "$CURRENT_WRK" != "$WRK_ID" ]]; then
        # Check if current WRK is done or archived — allow overwrite if so
        CURRENT_STATUS=""
        WRK_FILE="$(find "$WQ_DIR" -maxdepth 3 -name "${CURRENT_WRK}.md" -print -quit 2>/dev/null || true)"
        if [[ -n "$WRK_FILE" ]] && [[ -f "$WRK_FILE" ]]; then
            CURRENT_STATUS="$(sed -n '/^---$/,/^---$/{ /^status:/{ s/^status:[[:space:]]*//; p; q; } }' "$WRK_FILE")"
        fi
        if [[ "$CURRENT_STATUS" != "done" ]] && [[ "$CURRENT_STATUS" != "archived" ]]; then
            echo "SCOPE_GUARD_WARNING: ${CURRENT_WRK} is still active (status: ${CURRENT_STATUS:-unknown}). Complete or archive it before starting ${WRK_ID}." >&2
            echo "Use --force to bypass: set-active-wrk.sh ${WRK_ID} --force" >&2
            exit 1
        fi
    fi
fi

# ── Write state with timestamp ───────────────────────────────────────────────
printf '%s\nstarted_at: %s\n' "$WRK_ID" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$ACTIVE_FILE"
echo "Active: ${WRK_ID}"
