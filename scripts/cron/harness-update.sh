#!/usr/bin/env bash
# harness-update.sh — Daily AI harness tool lifecycle manager.
#
# Updates all AI tools, runs per-tool health checks, detects git drift,
# rolls back failures, and sends active notifications.
#
# Usage: bash scripts/cron/harness-update.sh [--dry-run]
# Cron:  Staggered per machine (see schedule-tasks.yaml)
#        dev-primary: 01:15, dev-secondary: 01:45, win-*: 02:15
#
# Exit 0 always (individual tool failures are non-fatal to cron).
# Failures are flagged in summary + notification.
#
# Issues: #1668 (parent), #1672 (Phase 1), #1673 (Phase 2),
#         #1674 (Phase 3), #1675 (Phase 4)
set -uo pipefail

# ── Environment ──────────────────────────────────────────────────────────────
export PATH="${HOME}/.local/bin:${HOME}/.npm-global/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_DIR="${WORKSPACE_HUB}/logs/maintenance"
LOG_FILE="${LOG_DIR}/harness-update-$(date +%Y-%m-%d).log"
TRANSACTION_FILE="${LOG_DIR}/harness-update-transactions.yaml"
DRIFT_POLICY="${WORKSPACE_HUB}/config/agents/drift-policy.yaml"
PATCH_DIR="${WORKSPACE_HUB}/config/agents/hermes/patches"
TIMESTAMP="$(date '+%Y-%m-%dT%H:%M:%S')"
HOSTNAME_SHORT="$(hostname -s)"

DRY_RUN=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

mkdir -p "$LOG_DIR"

# ── PID lock (prevent overlapping runs) ──────────────────────────────────────
LOCK_FILE="${LOG_DIR}/.harness-update.lock"
if command -v flock &>/dev/null; then
  exec 200>"$LOCK_FILE"
  if ! flock -n 200; then
    echo "[$(date '+%H:%M:%S')] Another harness-update is running — exiting" | tee -a "$LOG_FILE"
    exit 0
  fi
fi

# ── Summary accumulators ────────────────────────────────────────────────────
declare -a SUMMARY_TOOL=()
declare -a SUMMARY_BEFORE=()
declare -a SUMMARY_AFTER=()
declare -a SUMMARY_STATUS=()
declare -a SUMMARY_HEALTH=()

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

record() {
  local tool="$1" before="$2" after="$3" status="$4" health="${5:-ok}"
  SUMMARY_TOOL+=("$tool")
  SUMMARY_BEFORE+=("$before")
  SUMMARY_AFTER+=("$after")
  SUMMARY_STATUS+=("$status")
  SUMMARY_HEALTH+=("$health")
}

# ── Transaction logging (Phase 2) ───────────────────────────────────────────

write_transaction() {
  local tool="$1" pre_ver="$2" target_ver="$3" final_ver="$4" status="$5"
  local rollback="${6:-false}" health="${7:-unknown}"
  printf -- '- timestamp: "%s"\n  machine: "%s"\n  tool: "%s"\n  pre_version: "%s"\n  target_version: "%s"\n  final_version: "%s"\n  status: "%s"\n  rollback_attempted: %s\n  health: "%s"\n  node_version: "%s"\n  python_version: "%s"\n' \
    "${TIMESTAMP}" "${HOSTNAME_SHORT}" "${tool}" "${pre_ver}" "${target_ver}" \
    "${final_ver}" "${status}" "${rollback}" "${health}" \
    "$(node --version 2>/dev/null || echo N/A)" \
    "$(python3 --version 2>/dev/null | awk '{print $2}' || echo N/A)" \
    >> "$TRANSACTION_FILE"
}

# ── Health check contracts (Phase 1) ────────────────────────────────────────

health_check_hermes() {
  local venv_python="${HOME}/.hermes/hermes-agent/.venv/bin/python3"
  if [[ ! -x "$venv_python" ]]; then
    log "HEALTH" "Hermes: venv python not found at $venv_python"
    return 1
  fi
  if ! "$venv_python" -c "from hermes_cli.main import main; print('ok')" &>/dev/null; then
    log "HEALTH" "Hermes: import chain broken (hermes_cli.main)"
    return 1
  fi
  if ! hermes --version &>/dev/null; then
    log "HEALTH" "Hermes: --version failed"
    return 1
  fi
  return 0
}

health_check_claude() {
  claude --version &>/dev/null || { log "HEALTH" "Claude Code: --version failed"; return 1; }
}

health_check_codex() {
  codex --version &>/dev/null || { log "HEALTH" "Codex: --version failed"; return 1; }
}

health_check_gemini() {
  gemini --version &>/dev/null || { log "HEALTH" "Gemini: --version failed"; return 1; }
}

health_check_gstack() {
  local dir="${HOME}/.claude/skills/gstack"
  git -C "$dir" rev-parse HEAD &>/dev/null || { log "HEALTH" "GStack: git repo corrupt"; return 1; }
}

health_check_superpowers() {
  local dir="${HOME}/.claude/plugins/superpowers"
  if [[ -d "$dir/.git" ]]; then
    git -C "$dir" rev-parse HEAD &>/dev/null || { log "HEALTH" "Superpowers: git repo corrupt"; return 1; }
  fi
  return 0
}

health_check_gsd() {
  command -v gsd &>/dev/null || { log "HEALTH" "GSD: binary not found"; return 1; }
}

# ── Rollback functions (Phase 2) ────────────────────────────────────────────

rollback_npm() {
  local pkg="$1" previous="$2"
  if [[ -z "$previous" || "$previous" == "not-installed" || "$previous" == "unknown" ]]; then
    log "ROLLBACK" "Cannot rollback $pkg — no previous version recorded"
    return 1
  fi
  log "ROLLBACK" "Restoring $pkg to $previous"
  if npm install -g "${pkg}@${previous}" 2>&1 | tee -a "$LOG_FILE"; then
    local restored
    restored=$(npm list -g "$pkg" --depth=0 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
    if [[ "$restored" == "$previous" ]]; then
      log "ROLLBACK" "$pkg restored to $previous — verified"
      return 0
    fi
  fi
  log "CRITICAL" "$pkg rollback FAILED"
  return 1
}

rollback_git() {
  local dir="$1" pre_sha="$2"
  if [[ -z "$pre_sha" || "$pre_sha" == "unknown" ]]; then
    log "ROLLBACK" "Cannot rollback $(basename "$dir") — no pre-update SHA"
    return 1
  fi
  git -C "$dir" rebase --abort 2>/dev/null || true
  log "ROLLBACK" "Restoring $(basename "$dir") to $pre_sha"
  if git -C "$dir" reset --hard "$pre_sha" 2>&1 | tee -a "$LOG_FILE"; then
    log "ROLLBACK" "$(basename "$dir") restored to $pre_sha"
    return 0
  fi
  log "CRITICAL" "$(basename "$dir") git reset FAILED"
  return 1
}

# ── Major version bump guard (Phase 2) ──────────────────────────────────────

is_major_bump() {
  local current="$1" latest="$2"
  local cur_major lat_major
  cur_major=$(echo "$current" | cut -d. -f1)
  lat_major=$(echo "$latest" | cut -d. -f1)
  [[ -n "$cur_major" && -n "$lat_major" && "$cur_major" != "$lat_major" ]]
}

# ── Drift detection (Phase 3) ───────────────────────────────────────────────

check_drift() {
  local tool_dir="$1" tool_name="$2"
  [[ -d "$tool_dir/.git" ]] || return
  local dirty
  dirty=$(git -C "$tool_dir" status --porcelain 2>/dev/null)
  [[ -z "$dirty" ]] && { log "DRIFT" "$tool_name: clean"; return; }
  local dirty_count
  dirty_count=$(echo "$dirty" | wc -l)
  log "DRIFT" "$tool_name: $dirty_count uncommitted change(s):"
  echo "$dirty" | while IFS= read -r line; do
    local file_path="${line:3}" classification="unclassified"
    if [[ -f "$DRIFT_POLICY" ]]; then
      if grep -q "path: \"$file_path\"" "$DRIFT_POLICY" 2>/dev/null; then
        if grep -B5 "path: \"$file_path\"" "$DRIFT_POLICY" | grep -q "machine_specific" 2>/dev/null; then
          classification="machine_specific"
        elif grep -B5 "path: \"$file_path\"" "$DRIFT_POLICY" | grep -q "portable" 2>/dev/null; then
          classification="portable"
        fi
      fi
    fi
    log "DRIFT" "  ${line:0:2} $file_path [$classification]"
  done
}

# ── Per-tool update functions ────────────────────────────────────────────────

update_gstack() {
  local dir="${HOME}/.claude/skills/gstack"
  if [[ ! -d "$dir/.git" ]]; then
    log "GStack: not installed — skipping"; record "GStack" "-" "-" "not-installed"; return
  fi
  local before after pre_sha
  before=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
  pre_sha=$(git -C "$dir" rev-parse HEAD 2>/dev/null || echo "unknown")
  if [[ "$DRY_RUN" == "true" ]]; then
    log "GStack: [dry-run] would git pull"; record "GStack" "$before" "(dry-run)" "dry-run"; return
  fi
  log "GStack: updating via git pull --rebase --autostash"
  if git -C "$dir" pull --rebase --autostash 2>&1 | tee -a "$LOG_FILE"; then
    after=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
    if health_check_gstack; then
      local s; [[ "$before" == "$after" ]] && s="up-to-date" || s="updated"
      log "GStack: $s ($before -> $after)"
      record "GStack" "$before" "$after" "$s" "healthy"
      write_transaction "gstack" "$before" "latest" "$after" "$s" "false" "healthy"
    else
      log "CRITICAL" "GStack: BROKEN — rolling back"
      rollback_git "$dir" "$pre_sha"
      after=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
      record "GStack" "$before" "$after" "BROKEN-rollback" "broken"
      write_transaction "gstack" "$before" "latest" "$after" "rollback" "true" "broken"
    fi
  else
    git -C "$dir" rebase --abort 2>/dev/null || true
    after=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
    log "GStack: git pull failed — aborted rebase"
    record "GStack" "$before" "$after" "failed" "unknown"
    write_transaction "gstack" "$before" "latest" "$after" "failed" "false" "unknown"
  fi
  check_drift "$dir" "GStack"
}

update_hermes() {
  if ! command -v hermes &>/dev/null; then
    log "Hermes: not installed — skipping"; record "Hermes" "-" "-" "not-installed"; return
  fi
  local before after pre_sha hermes_dir="${HOME}/.hermes/hermes-agent"
  before=$(hermes --version 2>/dev/null | head -1 || echo "installed")
  pre_sha=$(git -C "$hermes_dir" rev-parse HEAD 2>/dev/null || echo "unknown")
  if [[ "$DRY_RUN" == "true" ]]; then
    log "Hermes: [dry-run] would run hermes update"; record "Hermes" "$before" "(dry-run)" "dry-run"; return
  fi
  log "Hermes: updating via hermes update"
  if hermes update 2>&1 | tee -a "$LOG_FILE"; then
    if [[ -d "$PATCH_DIR" ]]; then
      for pf in "$PATCH_DIR"/*.patch; do
        [[ -f "$pf" ]] || continue
        if git -C "$hermes_dir" apply --check "$pf" 2>/dev/null; then
          git -C "$hermes_dir" apply "$pf" 2>&1 | tee -a "$LOG_FILE"
          log "PATCH" "Applied $(basename "$pf")"
        else
          log "PATCH" "$(basename "$pf") — skipped (already applied or conflict)"
        fi
      done
    fi
    after=$(hermes --version 2>/dev/null | head -1 || echo "unknown")
    if health_check_hermes; then
      local s; [[ "$before" == "$after" ]] && s="up-to-date" || s="updated"
      log "Hermes: $s ($before -> $after)"
      record "Hermes" "$before" "$after" "$s" "healthy"
      write_transaction "hermes" "$before" "latest" "$after" "$s" "false" "healthy"
    else
      log "CRITICAL" "Hermes: BROKEN — rolling back to $pre_sha"
      rollback_git "$hermes_dir" "$pre_sha"
      after=$(hermes --version 2>/dev/null | head -1 || echo "rollback")
      record "Hermes" "$before" "$after" "BROKEN-rollback" "broken"
      write_transaction "hermes" "$before" "latest" "$after" "rollback" "true" "broken"
    fi
  else
    after=$(hermes --version 2>/dev/null | head -1 || echo "unknown")
    log "Hermes: update failed"
    record "Hermes" "$before" "$after" "failed" "unknown"
    write_transaction "hermes" "$before" "latest" "$after" "failed" "false" "unknown"
  fi
  check_drift "$hermes_dir" "Hermes"
}

update_superpowers() {
  if ! command -v claude &>/dev/null; then
    log "Superpowers: claude CLI not installed — skipping"; record "Superpowers" "-" "-" "not-installed"; return
  fi
  local before sp_installed=false
  if claude plugin list 2>/dev/null | grep -qi superpowers; then
    sp_installed=true
    before=$(claude plugin list 2>/dev/null | grep -i superpowers | sed 's/^[[:space:]]*[^a-zA-Z]*//' | head -1)
  fi
  if [[ "$sp_installed" == "false" ]]; then
    local sp_dir="${HOME}/.claude/plugins/superpowers"
    if [[ -d "$sp_dir/.git" ]]; then
      sp_installed=true; before=$(git -C "$sp_dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
    else
      log "Superpowers: not installed — skipping"; record "Superpowers" "-" "-" "not-installed"; return
    fi
  fi
  if [[ "$DRY_RUN" == "true" ]]; then
    log "Superpowers: [dry-run]"; record "Superpowers" "$before" "(dry-run)" "dry-run"; return
  fi
  log "Superpowers: updating"
  local after
  if timeout 60 claude plugin update superpowers 2>&1 | tee -a "$LOG_FILE"; then
    after=$(claude plugin list 2>/dev/null | grep -i superpowers | head -1 || echo "unknown")
    if health_check_superpowers; then
      record "Superpowers" "$before" "$after" "updated" "healthy"
      write_transaction "superpowers" "$before" "latest" "$after" "updated" "false" "healthy"
    else
      record "Superpowers" "$before" "$after" "BROKEN" "broken"
      write_transaction "superpowers" "$before" "latest" "$after" "broken" "false" "broken"
    fi
  else
    record "Superpowers" "$before" "-" "failed" "unknown"
    write_transaction "superpowers" "$before" "latest" "-" "failed" "false" "unknown"
  fi
}

# ── Generic npm update with guard + rollback ─────────────────────────────────

update_npm_tool() {
  local tool_name="$1" pkg="$2" health_fn="$3"
  if ! command -v npm &>/dev/null; then
    log "${tool_name}: npm not installed — skipping"; record "$tool_name" "-" "-" "not-installed"; return
  fi
  local before after latest
  before=$(npm list -g "$pkg" --depth=0 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "not-installed")
  if [[ "$before" == "not-installed" ]]; then
    log "${tool_name}: not installed — skipping"; record "$tool_name" "-" "-" "not-installed"; return
  fi
  latest=$(npm view "$pkg" version 2>/dev/null || echo "unknown")
  if [[ "$latest" == "unknown" ]]; then
    log "WARN" "${tool_name}: npm registry unreachable — skipping"
    record "$tool_name" "$before" "?" "registry-unreachable" "healthy"
    write_transaction "$tool_name" "$before" "unknown" "$before" "registry-unreachable" "false" "healthy"
    return
  fi
  if is_major_bump "$before" "$latest"; then
    log "WARN" "${tool_name}: major bump ${before} -> ${latest} — skipping"
    record "$tool_name" "$before" "$latest" "major-bump-skipped"
    write_transaction "$tool_name" "$before" "$latest" "$before" "major-bump-skipped" "false" "healthy"
    return
  fi
  if [[ "$before" == "$latest" ]]; then
    log "${tool_name}: already at latest (${before})"
    record "$tool_name" "$before" "$latest" "up-to-date" "healthy"
    write_transaction "$tool_name" "$before" "$latest" "$before" "up-to-date" "false" "healthy"
    return
  fi
  if [[ "$DRY_RUN" == "true" ]]; then
    log "${tool_name}: [dry-run] ${before} -> ${latest}"
    record "$tool_name" "$before" "(dry-run: ${latest})" "dry-run"
    return
  fi
  log "${tool_name}: updating ${before} -> ${latest}"
  if npm install -g "${pkg}@latest" 2>&1 | tee -a "$LOG_FILE"; then
    after=$(npm list -g "$pkg" --depth=0 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
    if $health_fn; then
      log "${tool_name}: updated to ${after} — healthy"
      record "$tool_name" "$before" "$after" "updated" "healthy"
      write_transaction "$tool_name" "$before" "$latest" "$after" "updated" "false" "healthy"
    else
      log "CRITICAL" "${tool_name}: BROKEN — rolling back to ${before}"
      local rb=false; rollback_npm "$pkg" "$before" && rb=true
      after=$(npm list -g "$pkg" --depth=0 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
      if [[ "$rb" == "true" ]]; then
        record "$tool_name" "$before" "$after" "BROKEN-rollback" "broken"
        write_transaction "$tool_name" "$before" "$latest" "$after" "rollback" "true" "broken"
      else
        record "$tool_name" "$before" "$after" "BROKEN-no-rollback" "broken"
        write_transaction "$tool_name" "$before" "$latest" "$after" "rollback-failed" "true" "broken"
      fi
    fi
  else
    after=$(npm list -g "$pkg" --depth=0 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
    log "${tool_name}: npm install failed"
    record "$tool_name" "$before" "$after" "failed" "unknown"
    write_transaction "$tool_name" "$before" "$latest" "$after" "failed" "false" "unknown"
  fi
}

update_gsd() { update_npm_tool "GSD" "get-shit-done-cc" health_check_gsd; }
update_claude_code() { update_npm_tool "Claude Code" "@anthropic-ai/claude-code" health_check_claude; }
update_codex() { update_npm_tool "Codex" "@openai/codex" health_check_codex; }
update_gemini() { update_npm_tool "Gemini CLI" "@google/gemini-cli" health_check_gemini; }

# ── Summary + Notification ───────────────────────────────────────────────────

print_summary() {
  local sep="+-----------------+----------------------+----------------------+---------------------+----------+"
  log ""
  log "═══ Harness Update Summary (${HOSTNAME_SHORT}) ═══"
  log "$sep"
  printf "| %-15s | %-20s | %-20s | %-19s | %-8s |\n" "Tool" "Before" "After" "Status" "Health" | tee -a "$LOG_FILE"
  log "$sep"
  for i in "${!SUMMARY_TOOL[@]}"; do
    printf "| %-15s | %-20s | %-20s | %-19s | %-8s |\n" \
      "${SUMMARY_TOOL[$i]}" "${SUMMARY_BEFORE[$i]}" "${SUMMARY_AFTER[$i]}" \
      "${SUMMARY_STATUS[$i]}" "${SUMMARY_HEALTH[$i]:-ok}" | tee -a "$LOG_FILE"
  done
  log "$sep"
}

send_notification() {
  local fail_count=0 broken_count=0 tool_details=""
  for i in "${!SUMMARY_STATUS[@]}"; do
    local s="${SUMMARY_STATUS[$i]}" h="${SUMMARY_HEALTH[$i]:-ok}"
    [[ "$s" == "failed" ]] && ((fail_count++)) || true
    [[ "$h" == "broken" ]] && ((broken_count++)) || true
    [[ "$s" == "failed" || "$h" == "broken" || "$s" == *"BROKEN"* ]] && tool_details="${tool_details}${SUMMARY_TOOL[$i]}:${s}, "
  done
  local overall_status="pass"
  [[ "$broken_count" -gt 0 ]] && overall_status="fail"
  [[ "$fail_count" -gt 0 && "$overall_status" == "pass" ]] && overall_status="warn"
  local details="machine=${HOSTNAME_SHORT},tools=${#SUMMARY_TOOL[@]},failed=${fail_count},broken=${broken_count}"
  [[ -n "$tool_details" ]] && details="${details},failures=${tool_details%, }"
  if [[ "$DRY_RUN" != "true" && -f "${WORKSPACE_HUB}/scripts/notify.sh" ]]; then
    bash "${WORKSPACE_HUB}/scripts/notify.sh" cron harness-update "$overall_status" "$details" 2>/dev/null || true
  fi
  if [[ "$broken_count" -gt 0 ]]; then
    log ""; log "╔══════════════════════════════════════════════════════════╗"
    log "║  ⚠  BROKEN TOOLS DETECTED — MANUAL INTERVENTION NEEDED ║"
    log "║  Machine: ${HOSTNAME_SHORT}"; log "║  Broken: ${tool_details%, }"
    log "╚══════════════════════════════════════════════════════════╝"
    command -v logger &>/dev/null && logger -t harness-update -p user.err "BROKEN on ${HOSTNAME_SHORT}: ${tool_details%, }" 2>/dev/null || true
  fi
}

# ── Main ─────────────────────────────────────────────────────────────────────

log "==========================================="
log "Harness Update — ${TIMESTAMP} (${HOSTNAME_SHORT})"
[[ "$DRY_RUN" == "true" ]] && log "MODE: dry-run (no changes)"
log "==========================================="
log "Runtime: node=$(node --version 2>/dev/null || echo N/A) npm=$(npm --version 2>/dev/null || echo N/A) python=$(python3 --version 2>/dev/null | awk '{print $2}' || echo N/A)"

update_gstack
update_hermes
update_superpowers
update_gsd
update_claude_code
update_codex
update_gemini

print_summary
send_notification

log ""; log "Completed at $(date '+%Y-%m-%dT%H:%M:%S')"
find "$LOG_DIR" -name "harness-update-*.log" -mtime +30 -delete 2>/dev/null || true
find "$LOG_DIR" -name "harness-update-transactions*.yaml" -mtime +90 -delete 2>/dev/null || true
exit 0
