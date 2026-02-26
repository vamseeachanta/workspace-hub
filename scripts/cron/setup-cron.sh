#!/usr/bin/env bash
# setup-cron.sh — Hostname-aware crontab installer for workspace-hub.
# Maps hostname → cron_variant; installs the appropriate cron entries.
# Idempotent: skips entries already present in crontab.
# Safe: --dry-run prints what would be installed without modifying crontab.
#
# ── New Workstation Onboarding ────────────────────────────────────────────────
#  1. Clone workspace-hub
#       git clone git@github.com:<org>/workspace-hub.git
#       cd workspace-hub && git submodule update --init --recursive
#  2. Set up SSH key to ace-linux-1 (for state file sync)
#       ssh-keygen -t ed25519 -C "$(hostname)" # if no key exists
#       ssh-copy-id vamsee@ace-linux-1
#  3. Install crontab
#       bash scripts/cron/setup-cron.sh
#  4. Smoke-test readiness
#       bash scripts/readiness/nightly-readiness.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"

DRY_RUN=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

HOSTNAME_SHORT=$(hostname -s 2>/dev/null || hostname | cut -d. -f1)
HOSTNAME_SHORT=$(printf '%s' "$HOSTNAME_SHORT" | tr '[:upper:]' '[:lower:]')

# ── Determine cron_variant from hostname ─────────────────────────────────────
case "$HOSTNAME_SHORT" in
  ace-linux-1)             CRON_VARIANT="full" ;;
  ace-linux-2)             CRON_VARIANT="contribute" ;;
  acma-ansys05|acma-ws014) CRON_VARIANT="contribute-minimal" ;;
  *)
    echo "INFO: hostname '${HOSTNAME_SHORT}' not in registry — defaulting to 'contribute'"
    echo "      Update the case statement in this script if this is a new machine."
    CRON_VARIANT="contribute"
    ;;
esac

echo "Host: ${HOSTNAME_SHORT} → cron_variant: ${CRON_VARIANT}"

# ── Windows / contribute-minimal: print Task Scheduler instructions and exit ─
if [[ "$CRON_VARIANT" == "contribute-minimal" ]]; then
  cat <<'EOF'

  This machine uses cron_variant: contribute-minimal (Windows or isolated node).
  Automated cron is not supported. Instead, set up Windows Task Scheduler entries:

  Task 1 — Repository Sync (every 4 hours)
    Program: bash.exe (Git Bash or WSL)
    Arguments: -c "cd /path/to/workspace-hub && git pull --no-rebase origin main && git push"
    Trigger: Every 4 hours

  Task 2 — Commit derived state (daily at 03:00)
    Program: bash.exe (Git Bash or WSL)
    Arguments: -c "cd /path/to/workspace-hub && git add .claude/state/candidates/ .claude/state/corrections/ && git diff --staged --quiet || git commit -m 'chore: session learnings from %COMPUTERNAME%' && git push"
    Trigger: Daily at 03:00

  For WSL, replace paths accordingly. For SSH-based sync, ensure SSH key is
  authorized on ace-linux-1 (Step 2 of onboarding checklist above).

EOF
  exit 0
fi

# ── Build the list of cron entries for this variant ──────────────────────────
ENTRIES=()

# Quote the hub path so spaces in the path don't break cron command parsing
HUB_Q="\"${WORKSPACE_HUB}\""
LOG="${WORKSPACE_HUB}/.claude/state/learning-reports/cron.log"

if [[ "$CRON_VARIANT" == "full" ]]; then
  # ace-linux-1: full 10-phase pipeline + all maintenance crons
  ENTRIES+=(
    "0  2  * * *  cd ${HUB_Q} && bash scripts/cron/comprehensive-learning-nightly.sh >> \"${LOG}\" 2>&1"
    "0  3  * * *  cd ${HUB_Q} && bash scripts/cron/session-analysis-nightly.sh >> \"${LOG}\" 2>&1"
    "30 3  * * 0  cd ${HUB_Q} && bash scripts/cron/update-model-ids.sh >> \"${LOG}\" 2>&1"
    "0  4  * * 1  cd ${HUB_Q} && bash scripts/cron/skills-curation.sh >> \"${LOG}\" 2>&1"
    "0  */4 * * * cd ${HUB_Q} && bash scripts/repository-sync-auto >> \"${LOG}\" 2>&1"
  )
fi

if [[ "$CRON_VARIANT" == "contribute" ]]; then
  # ace-linux-2 and other Linux contributors: repository-sync only
  ENTRIES+=(
    "0  */4 * * * cd ${HUB_Q} && bash scripts/repository-sync-auto >> /tmp/workspace-hub-cron.log 2>&1"
  )
fi

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

# ── Install: idempotent — skip entries already present ───────────────────────
CURRENT_CRONTAB=$(crontab -l 2>/dev/null || true)
ADDED=0
SKIPPED=0
NEW_CRONTAB="$CURRENT_CRONTAB"

for entry in "${ENTRIES[@]}"; do
  # Use schedule + script basename as the unique key.
  # Schedule: first 5 fields; script: last path component of the scripts/... token.
  schedule=$(printf '%s' "$entry" | awk '{print $1,$2,$3,$4,$5}')
  script_base=$(printf '%s' "$entry" | grep -oE 'scripts/[^ "]+' | head -1 \
    | xargs -I{} basename {} 2>/dev/null || true)
  key="${schedule} ${script_base}"
  if printf '%s\n' "$CURRENT_CRONTAB" | grep -qF "$script_base" 2>/dev/null \
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
