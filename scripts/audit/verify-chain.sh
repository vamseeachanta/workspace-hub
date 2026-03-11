#!/usr/bin/env bash
# verify-chain.sh — Validate SHA256 chain integrity of an audit log (WRK-1087)
# Usage: verify-chain.sh [file] [--prev-hash <hash>]
#   If no file given, verifies current month's log.
#   --prev-hash <hash>: seed hash for first entry (default: "genesis" or from chain-state)
# Chain spec: SHA256(printf '%s\n' "$line") — UTF-8, LF-terminated.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
AUDIT_LOG_DIR="${AUDIT_LOG_DIR:-${REPO_ROOT}/logs/audit}"

log_file=""
seed_hash=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prev-hash) seed_hash="$2"; shift 2 ;;
    *) log_file="$1"; shift ;;
  esac
done

if [[ -z "$log_file" ]]; then
  log_file="${AUDIT_LOG_DIR}/agent-actions-$(date +%Y-%m).jsonl"
fi

if [[ ! -f "$log_file" ]]; then
  echo "No log file: $log_file" >&2
  exit 1
fi

if [[ -z "$seed_hash" ]]; then
  seed_hash="genesis"
fi

prev_hash="$seed_hash"
line_no=0
errors=0

while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  line_no=$((line_no + 1))
  entry_prev=$(printf '%s' "$line" | jq -r '.prev_hash // ""' 2>/dev/null)
  if [[ "$entry_prev" != "$prev_hash" ]]; then
    echo "BROKEN at line ${line_no}: expected prev_hash='${prev_hash}', got '${entry_prev}'"
    errors=$((errors + 1))
  fi
  # Spec: hash of printf '%s\n' "$line" (LF-terminated)
  prev_hash="$(printf '%s\n' "$line" | sha256sum | awk '{print $1}')"
done < "$log_file"

if [[ "$errors" -eq 0 ]]; then
  echo "OK — chain valid (${line_no} entries, terminal_hash=${prev_hash})"
  exit 0
else
  echo "INVALID — ${errors} broken link(s) in ${line_no} entries"
  exit 1
fi
