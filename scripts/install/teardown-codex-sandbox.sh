#!/usr/bin/env bash
# teardown-codex-sandbox.sh — reverse setup-codex-sandbox.sh (#2804).
# Removes the codex-bwrap AppArmor profile, restoring Ubuntu's default
# unprivileged-userns restriction for system bwrap. Does NOT touch config.toml
# network_access (leave/remove that manually). Default --check; --yes to apply.
set -euo pipefail

PROFILE_DST="/etc/apparmor.d/codex-bwrap"
SENTINEL="MANAGED-BY: workspace-hub scripts/install/setup-codex-sandbox.sh"
MODE="check"
while (( $# > 0 )); do
  case "$1" in
    --check) MODE="check" ;;
    --yes) MODE="apply" ;;
    --help|-h) sed -n '2,7p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "ERROR: unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done
log() { printf '%s\n' "$*" >&2; }

if [[ ! -e "$PROFILE_DST" ]]; then
  log "Nothing to do: $PROFILE_DST not present."
  exit 0
fi
if ! grep -q "$SENTINEL" "$PROFILE_DST" 2>/dev/null; then
  log "REFUSING: $PROFILE_DST exists but lacks our sentinel — not managed by us. Remove manually if intended."
  exit 1
fi
if [[ "$MODE" == "check" ]]; then
  log "Would run: sudo apparmor_parser -R $PROFILE_DST && sudo rm $PROFILE_DST"
  log "Re-run with --yes to apply."
  exit 0
fi
log "Unloading + removing managed profile (requires sudo)…"
sudo apparmor_parser -R "$PROFILE_DST" || true
sudo rm -f "$PROFILE_DST"
log "Removed. Ubuntu's unprivileged-userns restriction is back in force for /usr/bin/bwrap."
log "If you set config.toml [sandbox_workspace_write] network_access=true, remove it manually if desired."
