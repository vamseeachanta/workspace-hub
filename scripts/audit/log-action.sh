#!/usr/bin/env bash
# log-action.sh — Append-only SHA256-chained JSONL audit writer (WRK-1087)
# Usage: log-action.sh <action> <target> [--wrk <id>] [--provider <p>]
# Chain spec: SHA256(printf '%s\n' "$entry") — UTF-8, LF-terminated, no BOM.
# Cross-file continuity: logs/audit/audit-chain-state.json stores terminal hash.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

AUDIT_LOG_DIR="${AUDIT_LOG_DIR:-${REPO_ROOT}/logs/audit}"
ACTIVE_WRK_FILE="${ACTIVE_WRK_FILE:-${REPO_ROOT}/.claude/state/active-wrk}"
SESSION_STATE_FILE="${SESSION_STATE_FILE:-${REPO_ROOT}/.claude/work-queue/session-state.yaml}"

action="${1:-unknown}"
target="${2:-}"
shift 2 || shift || true

wrk_id=""
provider="${CLAUDE_PROVIDER:-claude}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wrk) wrk_id="$2"; shift 2 ;;
    --provider) provider="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$wrk_id" && -f "$ACTIVE_WRK_FILE" ]]; then
  wrk_id="$(head -n1 "$ACTIVE_WRK_FILE" 2>/dev/null | tr -d '[:space:]')"
fi
wrk_id="${wrk_id:-unknown}"

session_id="unknown"
if [[ -f "$SESSION_STATE_FILE" ]]; then
  session_id="$(awk -F': ' '/^session_id:/{gsub(/^"|"$/, "", $2); print $2; exit}' \
    "$SESSION_STATE_FILE" 2>/dev/null || true)"
fi
session_id="${session_id:-unknown}"

mkdir -p "$AUDIT_LOG_DIR"
month="$(date +%Y-%m)"
log_file="${AUDIT_LOG_DIR}/agent-actions-${month}.jsonl"
lock_file="${AUDIT_LOG_DIR}/.lock-${month}"
chain_state="${AUDIT_LOG_DIR}/audit-chain-state.json"
error_log="${AUDIT_LOG_DIR}/errors.log"

# Compress files older than 6 months (best-effort, non-blocking)
find "$AUDIT_LOG_DIR" -name "agent-actions-*.jsonl" -mtime +180 \
  -exec gzip -q {} \; 2>/dev/null || true

_log_error() {
  local msg="$1"
  printf '{"ts":"%s","event":"log_failure","reason":"%s"}\n' \
    "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$msg" >> "$error_log" 2>/dev/null || true
}

# Acquire exclusive lock (fd 9) — prevents concurrent chain corruption
exec 9>"$lock_file"
if ! flock -w 5 9; then
  _log_error "flock timeout"
  exit 1
fi

# Determine prev_hash with cross-file continuity
if [[ -f "$log_file" && -s "$log_file" ]]; then
  # Within same file: hash the last raw line (spec: printf '%s\n' last_line)
  prev_line="$(tail -1 "$log_file")"
  prev_hash="$(printf '%s\n' "$prev_line" | sha256sum | awk '{print $1}')"
elif [[ -f "$chain_state" ]]; then
  # New month file: carry forward terminal hash from chain-state
  prev_hash="$(jq -r '.terminal_hash // "genesis"' "$chain_state" 2>/dev/null || echo "genesis")"
else
  prev_hash="genesis"
fi

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
target_escaped="${target//\"/\\\"}"

entry="{\"ts\":\"${ts}\",\"session_id\":\"${session_id}\",\"wrk_id\":\"${wrk_id}\",\"action\":\"${action}\",\"target\":\"${target_escaped}\",\"provider\":\"${provider}\",\"prev_hash\":\"${prev_hash}\"}"

# Append (spec: LF-terminated via printf)
printf '%s\n' "$entry" >> "$log_file"

# Update chain state with this entry's hash
entry_hash="$(printf '%s\n' "$entry" | sha256sum | awk '{print $1}')"
printf '{"terminal_hash":"%s","updated_at":"%s","file":"%s"}\n' \
  "$entry_hash" "$ts" "$(basename "$log_file")" > "$chain_state"

# Release lock
flock -u 9
exec 9>&-
