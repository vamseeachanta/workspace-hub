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
        ls -1 "$WS_HUB/.claude/work-queue/pending" "$WS_HUB/.claude/work-queue/working" "$WS_HUB/.claude/work-queue/blocked" 2>/dev/null || true
        ;;
    *)
        echo "Unsupported subcommand for wrapper: $subcmd" >&2
        exit 2
        ;;
esac
