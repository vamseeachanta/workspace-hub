#!/usr/bin/env bash
set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$AGENTS_DIR/lib/workflow-guards.sh"

wrk_id=""
all_providers=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        WRK-*) wrk_id="$1"; shift ;;
        --all-providers) all_providers=true; shift ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

[[ -z "$wrk_id" ]] && { echo "Usage: review.sh WRK-### [--all-providers]" >&2; exit 2; }

file="$(resolve_wrk_file "$wrk_id")" || { echo "ERROR: work item not found: $wrk_id" >&2; exit 2; }
session_record_stage "$wrk_id" "cross_review"

input_file="$file"
if [[ "$all_providers" == "true" ]]; then
    "$WS_HUB/scripts/review/cross-review.sh" "$input_file" all --type implementation
else
    "$WS_HUB/scripts/review/cross-review.sh" "$input_file" codex --type implementation
fi

echo "Review stage completed for $wrk_id"
