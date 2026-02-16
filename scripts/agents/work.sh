#!/usr/bin/env bash
set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$AGENTS_DIR/lib/workflow-guards.sh"

provider=""
subcmd=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --provider) provider="$2"; shift 2 ;;
        *) subcmd="$1"; shift; break ;;
    esac
done

[[ -z "$provider" ]] && { echo "ERROR: --provider required" >&2; exit 2; }
assert_provider "$provider"
assert_orchestrator_or_fail "$provider"

case "$subcmd" in
    run|"" )
        echo "Workflow orchestrator '$provider' acknowledged /work run contract."
        ;;
    list)
        check_stale_items || true
        echo "── pending/ ──"
        for f in "$WS_HUB/.claude/work-queue/pending"/WRK-*.md; do
            [[ -f "$f" ]] || continue
            local_id="$(basename "$f" .md)"
            local_stale="$(wrk_get_frontmatter_value "$f" "stale")"
            local_lock="$(wrk_get_frontmatter_value "$f" "locked_by")"
            marker=""
            [[ -n "$local_stale" ]] && marker=" [STALE:$local_stale]"
            [[ -n "$local_lock" ]] && marker="$marker [LOCKED:$local_lock]"
            echo "  $local_id$marker"
        done
        echo "── working/ ──"
        for f in "$WS_HUB/.claude/work-queue/working"/WRK-*.md; do
            [[ -f "$f" ]] || continue
            local_id="$(basename "$f" .md)"
            local_stale="$(wrk_get_frontmatter_value "$f" "stale")"
            local_lock="$(wrk_get_frontmatter_value "$f" "locked_by")"
            marker=""
            [[ -n "$local_stale" ]] && marker=" [STALE:$local_stale]"
            [[ -n "$local_lock" ]] && marker="$marker [LOCKED:$local_lock]"
            echo "  $local_id$marker"
        done
        echo "── blocked/ ──"
        ls -1 "$WS_HUB/.claude/work-queue/blocked" 2>/dev/null || true
        ;;
    *)
        echo "Unsupported subcommand for wrapper: $subcmd" >&2
        exit 2
        ;;
esac
