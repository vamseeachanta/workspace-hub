#!/usr/bin/env bash
# harness-update-windows.sh — AI harness update for Windows (Git Bash / MINGW64).
# Only npm-global tools: Claude Code, Codex, Gemini CLI.
# Issues: #1668, #1675 (Phase 4)
set -uo pipefail

if [[ -n "${APPDATA:-}" ]]; then
  NPM_GLOBAL="$(cygpath "$APPDATA")/npm"
  export PATH="${NPM_GLOBAL}:${PATH}"
fi
export PATH="${HOME}/.local/bin:${HOME}/.npm-global/bin:${PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_DIR="${WORKSPACE_HUB}/logs/maintenance"
LOG_FILE="${LOG_DIR}/harness-update-$(date +%Y-%m-%d).log"
TRANSACTION_FILE="${LOG_DIR}/harness-update-transactions.yaml"
TIMESTAMP="$(date '+%Y-%m-%dT%H:%M:%S')"
HOSTNAME_SHORT="$(hostname -s 2>/dev/null || echo "${COMPUTERNAME:-unknown}")"

DRY_RUN=false
for arg in "$@"; do [[ "$arg" == "--dry-run" ]] && DRY_RUN=true; done
mkdir -p "$LOG_DIR"

declare -a SUMMARY_TOOL=() SUMMARY_BEFORE=() SUMMARY_AFTER=() SUMMARY_STATUS=() SUMMARY_HEALTH=()
log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
record() {
  SUMMARY_TOOL+=("$1"); SUMMARY_BEFORE+=("$2"); SUMMARY_AFTER+=("$3")
  SUMMARY_STATUS+=("$4"); SUMMARY_HEALTH+=("${5:-ok}")
}
write_transaction() {
  printf -- '- timestamp: "%s"\n  machine: "%s"\n  tool: "%s"\n  pre_version: "%s"\n  target_version: "%s"\n  final_version: "%s"\n  status: "%s"\n  rollback_attempted: %s\n  health: "%s"\n  node_version: "%s"\n' \
    "$TIMESTAMP" "$HOSTNAME_SHORT" "$1" "$2" "$3" "$4" "$5" "${6:-false}" "${7:-unknown}" \
    "$(node --version 2>/dev/null || echo N/A)" >> "$TRANSACTION_FILE"
}

health_check_claude() { claude --version &>/dev/null; }
health_check_codex() { codex --version &>/dev/null; }
health_check_gemini() { gemini --version &>/dev/null; }

is_major_bump() {
  local c=$(echo "$1" | cut -d. -f1) l=$(echo "$2" | cut -d. -f1)
  [[ -n "$c" && -n "$l" && "$c" != "$l" ]]
}

rollback_npm() {
  local pkg="$1" prev="$2"
  [[ -z "$prev" || "$prev" == "not-installed" ]] && return 1
  log "ROLLBACK" "Restoring $pkg to $prev"
  npm install -g "${pkg}@${prev}" 2>&1 | tee -a "$LOG_FILE" || return 1
  local restored=$(npm list -g "$pkg" --depth=0 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "?")
  [[ "$restored" == "$prev" ]]
}

verify_cmd_shim() {
  if [[ -n "${APPDATA:-}" ]]; then
    local shim="$(cygpath "$APPDATA")/npm/${1}.cmd"
    [[ -f "$shim" ]] && log "SHIM" "$1: .cmd OK" || log "WARN" "$1: .cmd MISSING at $shim"
  fi
}

update_npm_tool() {
  local name="$1" pkg="$2" hfn="$3" cmd="${4:-}"
  command -v npm &>/dev/null || { record "$name" "-" "-" "not-installed"; return; }
  local before=$(npm list -g "$pkg" --depth=0 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "not-installed")
  [[ "$before" == "not-installed" ]] && { record "$name" "-" "-" "not-installed"; return; }
  local latest=$(npm view "$pkg" version 2>/dev/null || echo "unknown")
  [[ "$latest" == "unknown" ]] && { log "WARN" "$name: registry unreachable"; record "$name" "$before" "?" "registry-unreachable" "healthy"; return; }
  is_major_bump "$before" "$latest" && { log "WARN" "$name: major bump $before -> $latest — skip"; record "$name" "$before" "$latest" "major-bump-skipped"; return; }
  [[ "$before" == "$latest" ]] && { [[ -n "$cmd" ]] && verify_cmd_shim "$cmd"; log "$name: at latest ($before)"; record "$name" "$before" "$latest" "up-to-date" "healthy"; write_transaction "$name" "$before" "$latest" "$before" "up-to-date" "false" "healthy"; return; }
  [[ "$DRY_RUN" == "true" ]] && { log "$name: [dry-run] $before -> $latest"; record "$name" "$before" "(dry-run)" "dry-run"; return; }
  log "$name: updating $before -> $latest"
  if npm install -g "${pkg}@latest" 2>&1 | tee -a "$LOG_FILE"; then
    local after=$(npm list -g "$pkg" --depth=0 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
    [[ -n "$cmd" ]] && verify_cmd_shim "$cmd"
    if $hfn; then
      record "$name" "$before" "$after" "updated" "healthy"
      write_transaction "$name" "$before" "$latest" "$after" "updated" "false" "healthy"
    else
      log "CRITICAL" "$name: BROKEN — rolling back"
      local rb=false; rollback_npm "$pkg" "$before" && rb=true
      after=$(npm list -g "$pkg" --depth=0 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "?")
      [[ "$rb" == "true" ]] && record "$name" "$before" "$after" "BROKEN-rollback" "broken" || record "$name" "$before" "$after" "BROKEN-no-rollback" "broken"
      write_transaction "$name" "$before" "$latest" "$after" "rollback" "$rb" "broken"
    fi
  else
    record "$name" "$before" "?" "failed" "unknown"
    write_transaction "$name" "$before" "$latest" "?" "failed" "false" "unknown"
  fi
}

print_summary() {
  local sep="+-----------------+----------------------+----------------------+---------------------+----------+"
  log ""; log "═══ Harness Update Summary (${HOSTNAME_SHORT} — Windows) ═══"; log "$sep"
  printf "| %-15s | %-20s | %-20s | %-19s | %-8s |\n" "Tool" "Before" "After" "Status" "Health" | tee -a "$LOG_FILE"
  log "$sep"
  for i in "${!SUMMARY_TOOL[@]}"; do
    printf "| %-15s | %-20s | %-20s | %-19s | %-8s |\n" \
      "${SUMMARY_TOOL[$i]}" "${SUMMARY_BEFORE[$i]}" "${SUMMARY_AFTER[$i]}" \
      "${SUMMARY_STATUS[$i]}" "${SUMMARY_HEALTH[$i]:-ok}" | tee -a "$LOG_FILE"
  done; log "$sep"
}

send_notification() {
  local fc=0 bc=0
  for i in "${!SUMMARY_STATUS[@]}"; do
    [[ "${SUMMARY_STATUS[$i]}" == "failed" ]] && ((fc++)) || true
    [[ "${SUMMARY_HEALTH[$i]:-ok}" == "broken" ]] && ((bc++)) || true
  done
  local st="pass"; [[ "$bc" -gt 0 ]] && st="fail"; [[ "$fc" -gt 0 && "$st" == "pass" ]] && st="warn"
  [[ "$DRY_RUN" != "true" && -f "${WORKSPACE_HUB}/scripts/notify.sh" ]] && \
    bash "${WORKSPACE_HUB}/scripts/notify.sh" cron harness-update "$st" "machine=${HOSTNAME_SHORT},tools=${#SUMMARY_TOOL[@]},failed=${fc},broken=${bc}" 2>/dev/null || true
  [[ "$bc" -gt 0 ]] && log "⚠ BROKEN TOOLS on ${HOSTNAME_SHORT} (Windows)"
}

log "==========================================="; log "Harness Update — ${TIMESTAMP} (${HOSTNAME_SHORT} — Windows)"
[[ "$DRY_RUN" == "true" ]] && log "MODE: dry-run"
log "==========================================="; log "Runtime: node=$(node --version 2>/dev/null || echo N/A) npm=$(npm --version 2>/dev/null || echo N/A)"

update_npm_tool "Claude Code" "@anthropic-ai/claude-code" health_check_claude "claude"
update_npm_tool "Codex" "@openai/codex" health_check_codex "codex"
update_npm_tool "Gemini CLI" "@google/gemini-cli" health_check_gemini "gemini"

print_summary; send_notification
log ""; log "Completed at $(date '+%Y-%m-%dT%H:%M:%S')"
find "$LOG_DIR" -name "harness-update-*.log" -mtime +30 -delete 2>/dev/null || true
exit 0
