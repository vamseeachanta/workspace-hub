#!/usr/bin/env bash
# compare-harness-state.sh — diff harness readiness across workstations
# Checks dev-secondary via SSH; licensed-win-1 via stale-report detection.
# Usage: bash scripts/readiness/compare-harness-state.sh [--dry-run] [--force-ssh-fail]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
HARNESS_CONFIG="${HARNESS_CONFIG:-${SCRIPT_DIR}/harness-config.yaml}"
STATE_DIR="${WORKSPACE_HUB}/.claude/state"
DRY_RUN=0
FORCE_SSH_FAIL=0

for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=1
  [[ "$arg" == "--force-ssh-fail" ]] && FORCE_SSH_FAIL=1
done

DEGRADED=0
log_ok()   { echo "  OK  $1"; }
log_warn() { echo "  WARN $1"; }
log_deg()  { echo "  DEGRADED $1"; DEGRADED=1; }

echo "--- compare-harness-state: $(date +%Y-%m-%dT%H:%M:%S) ---"

# ── dev-secondary: SSH diff ──────────────────────────────────────────────────
check_ace2() {
  local ssh_target="ace2"
  local ace2_hub="/mnt/workspace-hub"
  local ace2_report="${STATE_DIR}/harness-readiness-dev-secondary.yaml"

  if [[ "$FORCE_SSH_FAIL" == "1" ]]; then
    log_deg "dev-secondary: SSH unreachable (--force-ssh-fail) — skipping diff"
    return
  fi

  if [[ "$DRY_RUN" == "1" ]]; then
    log_ok "dev-secondary: dry-run — would SSH to ${ssh_target}"
    return
  fi

  # Attempt to fetch remote report via SSH (5s timeout)
  local remote_report
  remote_report=$(ssh -o ConnectTimeout=5 -o BatchMode=yes "$ssh_target" \
    "cat ${ace2_hub}/.claude/state/harness-readiness-dev-secondary.yaml" 2>/dev/null || echo "")

  if [[ -z "$remote_report" ]]; then
    log_deg "dev-secondary: SSH unreachable or report absent — DEGRADED"
    return
  fi

  # Write a local copy for reference
  echo "$remote_report" > "$ace2_report" 2>/dev/null || true

  local ace2_overall
  ace2_overall=$(echo "$remote_report" | grep "^overall:" | awk '{print $2}' | head -1)
  local ace2_fails
  ace2_fails=$(echo "$remote_report" | grep "^fail_count:" | awk '{print $2}' | head -1)
  ace2_fails=${ace2_fails:-0}

  if [[ "$ace2_overall" == "pass" ]]; then
    log_ok "dev-secondary: overall=pass, fail_count=${ace2_fails}"
  else
    log_warn "dev-secondary: overall=${ace2_overall}, fail_count=${ace2_fails} — run remediate-harness.sh"
  fi
}
check_ace2

# ── licensed-win-1: stale-report detection (>25h) ───────────────────────────
check_acma() {
  local report="${STATE_DIR}/harness-readiness-licensed-win-1.yaml"
  if [[ ! -f "$report" ]]; then
    log_warn "licensed-win-1: no report found — Windows Task Scheduler may not have run yet"
    return
  fi

  local gen_at
  gen_at=$(grep "^generated_at:" "$report" | sed 's/generated_at:[[:space:]]*//' | tr -d '"' | head -1)
  if [[ -z "$gen_at" ]]; then
    log_deg "licensed-win-1: report missing generated_at field — DEGRADED (stale)"
    return
  fi

  local report_epoch now_epoch age_hours
  report_epoch=$(date -d "$gen_at" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$gen_at" +%s 2>/dev/null || echo 0)
  now_epoch=$(date +%s)
  age_hours=$(( (now_epoch - report_epoch) / 3600 ))

  if [[ "$age_hours" -gt 25 ]]; then
    log_deg "licensed-win-1: report is ${age_hours}h old (>25h threshold) — DEGRADED (stale)"
  else
    local overall
    overall=$(grep "^overall:" "$report" | awk '{print $2}' | head -1)
    log_ok "licensed-win-1: report ${age_hours}h old, overall=${overall}"
  fi
}
check_acma

echo ""
if [[ "$DEGRADED" -eq 0 ]]; then
  echo "compare-harness-state: all workstations reachable / reports fresh"
  exit 0
else
  echo "compare-harness-state: DEGRADED — one or more workstations unreachable or stale"
  exit 2
fi
