#!/usr/bin/env bash
# cadence-common.sh — Shared helpers for ecosystem health cadence cron scripts.
# Issues: #2313, #2314, #2315, #2316, #2317, #2318, #2319 (workspace-hub),
#         worldenergydata#309
# Plan: docs/plans/2026-04-17-cadence-cron-infrastructure.md
#
# Sourced (not executed). Every cadence cron script starts with:
#   source "$(dirname "$0")/lib/cadence-common.sh"
#   cadence_init_repo_root
#
# Provides:
#   cadence_init_repo_root       — resolve REPO_ROOT from env|git|pwd (Codex P1)
#   emit_report_header <name> <period> <status> <summary>
#   compute_status_band <value> <warn> <block>   — float-safe (Claude P3)
#   cadence_period weekly|monthly|quarterly      — TZ=UTC pinned (Gemini P2)
#
# Threshold semantics (Claude P1 — pinned after review):
#   value > block           → RED
#   warn < value ≤ block    → YELLOW
#   value ≤ warn            → GREEN

export TZ=UTC

cadence_init_repo_root() {
    # Order: explicit env > git rev-parse > pwd. Idempotent.
    if [[ -n "${REPO_ROOT:-}" ]]; then return 0; fi
    REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
    export REPO_ROOT
}

emit_report_header() {
    local name="$1" period="$2" status="$3" summary="$4"
    cat <<HEADER
# ${name} — ${period}

**Status:** ${status} — ${summary}

HEADER
}

compute_status_band() {
    # float-safe comparison via awk
    local value="$1" warn="$2" block="$3"
    if awk "BEGIN{exit !($value > $block)}" 2>/dev/null; then echo RED;    return; fi
    if awk "BEGIN{exit !($value > $warn)}"  2>/dev/null; then echo YELLOW; return; fi
    echo GREEN
}

cadence_period() {
    case "$1" in
        weekly)    date +%Y-W%V ;;
        monthly)   date +%Y-%m ;;
        quarterly) printf '%s-Q%d\n' "$(date +%Y)" "$(( ($(date +%-m) - 1) / 3 + 1 ))" ;;
        *) echo "cadence_period: unknown period '$1'" >&2; return 1 ;;
    esac
}
