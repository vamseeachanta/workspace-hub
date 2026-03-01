#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "Usage: $0 WRK-xxx stage action provider [notes]" >&2
  exit 1
fi
wrk_id="$1"
stage="$2"
action="$3"
provider="$4"
notes="${5:-}"
workspace_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
log_dir="$workspace_root/.claude/work-queue/logs"
mkdir -p "$log_dir"
log_file="$log_dir/${wrk_id}-${stage}.log"

timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
{
  echo "timestamp: $timestamp"
  echo "wrk_id: $wrk_id"
  echo "stage: $stage"
  echo "action: $action"
  echo "provider: $provider"
  if [[ -n "$notes" ]]; then
    echo "notes: $notes"
  fi
  echo ""
} >> "$log_file"
