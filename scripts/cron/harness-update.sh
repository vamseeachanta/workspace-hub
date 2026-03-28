#!/usr/bin/env bash
# harness-update.sh — Daily best-effort update of AI harness tools.
# Runs each tool's native update command, logs before/after versions.
# Exit 0 always (individual tool failures are non-fatal).
#
# Usage: bash scripts/cron/harness-update.sh [--dry-run]
# Cron:  15 1 * * *  (before main nightly pipeline)
set -uo pipefail

# ── Environment ──────────────────────────────────────────────────────────────
export PATH="${HOME}/.local/bin:${HOME}/.npm-global/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_DIR="${WORKSPACE_HUB}/logs/maintenance"
LOG_FILE="${LOG_DIR}/harness-update-$(date +%Y-%m-%d).log"
TIMESTAMP="$(date '+%Y-%m-%dT%H:%M:%S')"

DRY_RUN=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

mkdir -p "$LOG_DIR"

# ── Summary accumulators ────────────────────────────────────────────────────
declare -a SUMMARY_TOOL=()
declare -a SUMMARY_BEFORE=()
declare -a SUMMARY_AFTER=()
declare -a SUMMARY_STATUS=()

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

record() {
  local tool="$1" before="$2" after="$3" status="$4"
  SUMMARY_TOOL+=("$tool")
  SUMMARY_BEFORE+=("$before")
  SUMMARY_AFTER+=("$after")
  SUMMARY_STATUS+=("$status")
}

# ── Per-tool update functions ───────────────────────────────────────────────

update_gstack() {
  local dir="${HOME}/.claude/skills/gstack"
  if [[ ! -d "$dir/.git" ]]; then
    log "GStack: not installed at ${dir} — skipping"
    record "GStack" "-" "-" "not-installed"
    return
  fi
  local before after
  before=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
  if [[ "$DRY_RUN" == "true" ]]; then
    log "GStack: [dry-run] would git pull --rebase --autostash in ${dir}"
    record "GStack" "$before" "(dry-run)" "dry-run"
    return
  fi
  log "GStack: updating via git pull --rebase --autostash"
  if git -C "$dir" pull --rebase --autostash 2>&1 | tee -a "$LOG_FILE"; then
    after=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
    if [[ "$before" == "$after" ]]; then
      log "GStack: already up-to-date (${before})"
      record "GStack" "$before" "$after" "up-to-date"
    else
      log "GStack: updated ${before} -> ${after}"
      record "GStack" "$before" "$after" "updated"
    fi
  else
    after=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
    log "GStack: git pull failed"
    record "GStack" "$before" "$after" "failed"
  fi
}

update_hermes() {
  if ! command -v hermes &>/dev/null; then
    log "Hermes: not installed — skipping"
    record "Hermes" "-" "-" "not-installed"
    return
  fi
  local before after
  before=$(hermes --version 2>/dev/null | head -1 || hermes version 2>/dev/null | head -1 || echo "installed")
  if [[ "$DRY_RUN" == "true" ]]; then
    log "Hermes: [dry-run] would run hermes update"
    record "Hermes" "$before" "(dry-run)" "dry-run"
    return
  fi
  log "Hermes: updating via hermes update"
  if hermes update 2>&1 | tee -a "$LOG_FILE"; then
    after=$(hermes --version 2>/dev/null | head -1 || echo "unknown")
    if [[ "$before" == "$after" ]]; then
      log "Hermes: already up-to-date (${before})"
      record "Hermes" "$before" "$after" "up-to-date"
    else
      log "Hermes: updated ${before} -> ${after}"
      record "Hermes" "$before" "$after" "updated"
    fi
  else
    after=$(hermes --version 2>/dev/null | head -1 || echo "unknown")
    log "Hermes: update failed"
    record "Hermes" "$before" "$after" "failed"
  fi
}

update_superpowers() {
  if ! command -v claude &>/dev/null; then
    log "Superpowers: claude CLI not installed — skipping"
    record "Superpowers" "-" "-" "not-installed"
    return
  fi
  # Check if superpowers plugin is installed — try plugin list, then directory fallback
  local before sp_installed=false
  if claude plugin list 2>/dev/null | grep -qi superpowers; then
    sp_installed=true
    # Extract just the plugin name (strip ansi/leading whitespace)
    before=$(claude plugin list 2>/dev/null | grep -i superpowers | sed 's/^[[:space:]]*[^a-zA-Z]*//' | head -1)
  fi
  if [[ "$sp_installed" == "false" ]]; then
    local sp_dir="${HOME}/.claude/plugins/superpowers"
    if [[ -d "$sp_dir/.git" ]]; then
      sp_installed=true
      before=$(git -C "$sp_dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
    else
      log "Superpowers: not installed — skipping"
      record "Superpowers" "-" "-" "not-installed"
      return
    fi
  fi
  if [[ "$DRY_RUN" == "true" ]]; then
    log "Superpowers: [dry-run] would run claude plugin update superpowers"
    record "Superpowers" "$before" "(dry-run)" "dry-run"
    return
  fi
  log "Superpowers: updating via claude plugin update superpowers"
  # claude plugin update may require TTY; timeout after 60s to avoid hanging
  local after
  if timeout 60 claude plugin update superpowers 2>&1 | tee -a "$LOG_FILE"; then
    after=$(claude plugin list 2>/dev/null | grep -i superpowers | head -1 || echo "unknown")
    log "Superpowers: update complete (${before} -> ${after})"
    record "Superpowers" "$before" "$after" "updated"
  else
    log "Superpowers: update failed or timed out (may require interactive TTY)"
    record "Superpowers" "$before" "-" "failed"
  fi
}

update_gsd() {
  if ! command -v npm &>/dev/null; then
    log "GSD: npm not installed — skipping"
    record "GSD" "-" "-" "not-installed"
    return
  fi
  local before after
  before=$(npm list -g get-shit-done-cc --depth=0 2>/dev/null | grep get-shit-done-cc | grep -oP '\d+\.\d+\.\d+' || echo "not-installed")
  if [[ "$before" == "not-installed" ]]; then
    log "GSD: not installed globally — skipping"
    record "GSD" "-" "-" "not-installed"
    return
  fi
  local latest
  latest=$(npm view get-shit-done-cc version 2>/dev/null || echo "unknown")
  if [[ "$before" == "$latest" ]]; then
    log "GSD: already at latest (${before})"
    record "GSD" "$before" "$latest" "up-to-date"
    return
  fi
  if [[ "$DRY_RUN" == "true" ]]; then
    log "GSD: [dry-run] would npm install -g get-shit-done-cc@latest (${before} -> ${latest})"
    record "GSD" "$before" "(dry-run: ${latest})" "dry-run"
    return
  fi
  log "GSD: updating ${before} -> ${latest}"
  if npm install -g get-shit-done-cc@latest 2>&1 | tee -a "$LOG_FILE"; then
    after=$(npm list -g get-shit-done-cc --depth=0 2>/dev/null | grep get-shit-done-cc | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
    log "GSD: updated to ${after}"
    record "GSD" "$before" "$after" "updated"
  else
    after=$(npm list -g get-shit-done-cc --depth=0 2>/dev/null | grep get-shit-done-cc | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
    log "GSD: npm install failed"
    record "GSD" "$before" "$after" "failed"
  fi
}

# ── Summary table ───────────────────────────────────────────────────────────

print_summary() {
  local sep="+-----------------+----------------------+----------------------+---------------+"
  log ""
  log "═══ Harness Update Summary ═══"
  log "$sep"
  printf "| %-15s | %-20s | %-20s | %-13s |\n" "Tool" "Before" "After" "Status" | tee -a "$LOG_FILE"
  log "$sep"
  for i in "${!SUMMARY_TOOL[@]}"; do
    printf "| %-15s | %-20s | %-20s | %-13s |\n" \
      "${SUMMARY_TOOL[$i]}" "${SUMMARY_BEFORE[$i]}" "${SUMMARY_AFTER[$i]}" "${SUMMARY_STATUS[$i]}" \
      | tee -a "$LOG_FILE"
  done
  log "$sep"
}

# ── Main ────────────────────────────────────────────────────────────────────

log "=========================================="
log "Harness Update — ${TIMESTAMP}"
[[ "$DRY_RUN" == "true" ]] && log "MODE: dry-run (no changes)"
log "=========================================="

update_gstack
update_hermes
update_superpowers
update_gsd

print_summary

# Notify (best-effort)
FAIL_COUNT=0
for s in "${SUMMARY_STATUS[@]}"; do
  [[ "$s" == "failed" ]] && ((FAIL_COUNT++)) || true
done
if [[ "$DRY_RUN" != "true" && -f "${WORKSPACE_HUB}/scripts/notify.sh" ]]; then
  STATUS=$( (( FAIL_COUNT == 0 )) && echo "pass" || echo "warn" )
  bash "${WORKSPACE_HUB}/scripts/notify.sh" cron harness-update "$STATUS" \
    "tools=${#SUMMARY_TOOL[@]},failed=${FAIL_COUNT}" 2>/dev/null || true
fi

log ""
log "Completed at $(date '+%Y-%m-%dT%H:%M:%S')"

# Retain 30 days of logs
find "$LOG_DIR" -name "harness-update-*.log" -mtime +30 -delete 2>/dev/null || true

exit 0
