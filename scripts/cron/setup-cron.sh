#!/usr/bin/env bash
# setup-cron.sh — Hostname-aware crontab installer for workspace-hub.
# Reads task definitions from config/scheduled-tasks/schedule-tasks.yaml.
# Idempotent: skips entries already present in crontab.
# Safe: --dry-run prints what would be installed without modifying crontab.
#
# ── New Workstation Onboarding ────────────────────────────────────────────────
#  1. Clone workspace-hub
#       git clone git@github.com:<org>/workspace-hub.git
#       cd workspace-hub && git submodule update --init --recursive
#  2. Set up SSH key to dev-primary (for state file sync)
#       ssh-keygen -t ed25519 -C "$(hostname)" # if no key exists
#       ssh-copy-id vamsee@dev-primary
#  3. Install crontab
#       bash scripts/cron/setup-cron.sh
#  4. Smoke-test readiness
#       bash scripts/readiness/nightly-readiness.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
SCHEDULE_FILE="${WORKSPACE_HUB}/config/scheduled-tasks/schedule-tasks.yaml"
REGISTRY="${WORKSPACE_HUB}/config/workstations/registry.yaml"

DRY_RUN=false
REPLACE=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
  [[ "$arg" == "--replace" ]] && REPLACE=true
done

if [[ ! -f "$SCHEDULE_FILE" ]]; then
  echo "ERROR: ${SCHEDULE_FILE} not found"
  exit 1
fi

HOSTNAME_SHORT=$(hostname -s 2>/dev/null || hostname | cut -d. -f1)
HOSTNAME_SHORT=$(printf '%s' "$HOSTNAME_SHORT" | tr '[:upper:]' '[:lower:]')

# ── Determine cron_variant from registry ─────────────────────────────────────
if [[ -f "$REGISTRY" ]]; then
  CRON_VARIANT=$(uv run --no-project python -c "
import yaml
with open('${REGISTRY}') as f:
    data = yaml.safe_load(f)
host = '${HOSTNAME_SHORT}'
for name, m in data.get('machines', {}).items():
    candidates = [m['hostname']] + m.get('hostname_aliases', [])
    candidates = [c.lower() for c in candidates]
    if host in candidates:
        print(m.get('schedule_variant', 'contribute'))
        break
else:
    print('__unknown__')
" 2>/dev/null)
  if [[ "$CRON_VARIANT" == "__unknown__" ]]; then
    echo "INFO: hostname '${HOSTNAME_SHORT}' not in registry — defaulting to 'contribute'"
    echo "      Add this machine to: config/workstations/registry.yaml"
    CRON_VARIANT="contribute"
  fi
else
  echo "WARN: registry not found at ${REGISTRY} — falling back to hostname case match"
  case "$HOSTNAME_SHORT" in
    dev-primary|ace-linux-1)   CRON_VARIANT="full" ;;
    dev-secondary|ace-linux-2) CRON_VARIANT="contribute" ;;
    licensed-win-1|licensed-win-2) CRON_VARIANT="contribute-minimal" ;;
    *)
      echo "INFO: hostname '${HOSTNAME_SHORT}' not in registry — defaulting to 'contribute'"
      CRON_VARIANT="contribute"
      ;;
  esac
fi

echo "Host: ${HOSTNAME_SHORT} → cron_variant: ${CRON_VARIANT}"

# ── Windows / contribute-minimal: print Task Scheduler instructions from YAML ─
if [[ "$CRON_VARIANT" == "contribute-minimal" ]]; then
  echo ""
  echo "  This machine uses cron_variant: contribute-minimal (Windows)."
  echo "  Automated cron is not supported. Set up Windows Task Scheduler entries"
  echo "  as documented in: ${SCHEDULE_FILE}"
  echo "  (look for scheduler: windows-task-scheduler entries)"
  echo ""
  exit 0
fi

# ── Read cron entries from schedule-tasks.yaml for this hostname ─────────────
# Uses a small Python one-liner to parse YAML and emit cron lines.
ENTRIES=()
while IFS= read -r line; do
  [[ -n "$line" ]] && ENTRIES+=("$line")
done < <(
  uv run --no-project python -c "
import yaml, sys
with open('${SCHEDULE_FILE}') as f:
    data = yaml.safe_load(f)
hub = '${WORKSPACE_HUB}'
log_full = hub + '/logs/quality/cron-wrapper.log'
log_contrib = '/tmp/workspace-hub-cron.log'
hostname = '${HOSTNAME_SHORT}'
for task in data.get('tasks', []):
    if task.get('scheduler', 'cron') != 'cron':
        continue
    if hostname not in task.get('machines', []):
        continue
    # Support per-machine staggered schedules (#1668)
    sbm = task.get('schedule_by_machine', {})
    schedule = sbm.get(hostname, task.get('schedule', ''))
    if not schedule:
        continue
    command = task['command']
    # Expand \$WORKSPACE_HUB and \$LOG variables
    command = command.replace('\$WORKSPACE_HUB', hub)
    if '${CRON_VARIANT}' == 'full':
        command = command.replace('\$LOG', log_full)
    else:
        command = command.replace('\$LOG', log_contrib)
    print(f'{schedule}  {command}')
" 2>&1
)

echo "Found ${#ENTRIES[@]} task(s) for ${HOSTNAME_SHORT}"

# ── Dry-run: print and exit ───────────────────────────────────────────────────
if [[ "$DRY_RUN" == "true" ]]; then
  echo ""
  echo "DRY RUN — would install the following crontab entries:"
  for entry in "${ENTRIES[@]}"; do
    echo "  ${entry}"
  done
  echo ""
  echo "(no changes made)"
  exit 0
fi

# ── Install ──────────────────────────────────────────────────────────────────
if [[ "$REPLACE" == "true" ]]; then
  # --replace mode: overwrite entire crontab with YAML-derived entries
  NEW_CRONTAB="# workspace-hub crontab — generated by setup-cron.sh --replace"
  NEW_CRONTAB+=$'\n'"# Source of truth: config/scheduled-tasks/schedule-tasks.yaml"
  NEW_CRONTAB+=$'\n'"# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ) for ${HOSTNAME_SHORT}"
  NEW_CRONTAB+=$'\n'
  for entry in "${ENTRIES[@]}"; do
    NEW_CRONTAB+=$'\n'"${entry}"
  done
  echo "$NEW_CRONTAB" | crontab -
  echo ""
  echo "Replaced crontab with ${#ENTRIES[@]} entries from schedule-tasks.yaml."
  echo "Verify with: crontab -l"
else
  # Default: idempotent — skip entries already present
  CURRENT_CRONTAB=$(crontab -l 2>/dev/null || true)
  ADDED=0
  SKIPPED=0
  NEW_CRONTAB="$CURRENT_CRONTAB"

  for entry in "${ENTRIES[@]}"; do
    # Use schedule + script basename as the unique key.
    schedule=$(printf '%s' "$entry" | awk '{print $1,$2,$3,$4,$5}')
    script_base=$(printf '%s' "$entry" | grep -oE 'scripts/[^ "]+' | head -1 \
      | xargs -I{} basename {} 2>/dev/null || true)
    key="${schedule} ${script_base}"
    if [[ -n "$script_base" ]] \
       && printf '%s\n' "$CURRENT_CRONTAB" | grep -qF "$script_base" 2>/dev/null \
       && printf '%s\n' "$CURRENT_CRONTAB" | grep -qF "$schedule" 2>/dev/null; then
      echo "  SKIP (already present): ${key}"
      SKIPPED=$((SKIPPED + 1))
    else
      NEW_CRONTAB="${NEW_CRONTAB}"$'\n'"${entry}"
      echo "  ADD: ${entry}"
      ADDED=$((ADDED + 1))
    fi
  done

  if [[ "$ADDED" -gt 0 ]]; then
    echo "$NEW_CRONTAB" | crontab -
    echo ""
    echo "Installed ${ADDED} new crontab entry/entries (skipped ${SKIPPED} already present)."
    echo "Verify with: crontab -l"
  else
    echo ""
    echo "All ${SKIPPED} entries already present — no changes made."
  fi
fi
