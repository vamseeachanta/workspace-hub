#!/usr/bin/env bash
# setup-codex-sandbox.sh — enable OpenAI Codex's bwrap sandbox to run nested
# under Claude Code on Ubuntu 24.04+ (#2804).
#
# Codex's sandbox needs unprivileged user namespaces, which Ubuntu 24.04 blocks
# by default (kernel.apparmor_restrict_unprivileged_userns=1). This installs a
# surgical AppArmor profile granting `userns` to /usr/bin/bwrap, and (optionally)
# enables network access for Codex's workspace-write mode.
#
# DEFAULT MODE IS --check (no mutation). Writing requires --accept-userns-lpe-risk.
#
# Usage:
#   setup-codex-sandbox.sh                         # --check (report state, no changes)
#   setup-codex-sandbox.sh --dry-run               # print exact actions, no changes
#   setup-codex-sandbox.sh --accept-userns-lpe-risk [--with-network]
#   setup-codex-sandbox.sh --help
#
# SECURITY: granting userns to /usr/bin/bwrap re-enables unprivileged user
# namespaces for ALL system-bwrap consumers (Codex, VSCode, Firefox, Flatpak),
# not Codex alone. This is a deliberate host-security tradeoff. Reverse with
# teardown-codex-sandbox.sh. See scripts/install/codex-bwrap.aa header.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_SRC="${SCRIPT_DIR}/codex-bwrap.aa"
PROFILE_DST="/etc/apparmor.d/codex-bwrap"
SENTINEL="MANAGED-BY: workspace-hub scripts/install/setup-codex-sandbox.sh"
RESTRICT_SYSCTL="/proc/sys/kernel/apparmor_restrict_unprivileged_userns"
CODEX_CONFIG="${CODEX_HOME:-$HOME/.codex}/config.toml"

MODE="check"          # check | dry-run | install
WITH_NETWORK=0

while (( $# > 0 )); do
  case "$1" in
    --check) MODE="check" ;;
    --dry-run) MODE="dry-run" ;;
    --accept-userns-lpe-risk) MODE="install" ;;
    --with-network) WITH_NETWORK=1 ;;
    --help|-h) sed -n '2,30p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "ERROR: unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

log() { printf '%s\n' "$*" >&2; }
fail() { log "FAIL: $*"; exit 1; }

# ── Preconditions: fail fast on unsupported OS / mechanism ──────────────────
preflight() {
  command -v apparmor_parser >/dev/null 2>&1 || fail "apparmor_parser not found — this host does not use AppArmor (Debian/Fedora/Arch use a different userns mechanism). Not supported by this installer."
  [[ -r "$RESTRICT_SYSCTL" ]] || fail "$RESTRICT_SYSCTL absent — kernel lacks the AppArmor unprivileged-userns restriction; nothing to grant (or different mechanism). Not supported."
  [[ -e /usr/bin/bwrap ]] || fail "/usr/bin/bwrap not present — install bubblewrap first."
  [[ -r "$PROFILE_SRC" ]] || fail "profile source missing: $PROFILE_SRC"
  if command -v lsb_release >/dev/null 2>&1; then
    local distro; distro="$(lsb_release -is 2>/dev/null || true)"
    [[ "$distro" == "Ubuntu" ]] || log "WARN: distro='$distro' (expected Ubuntu); proceeding because AppArmor + restriction sysctl are present."
  fi
}

restriction_active() { [[ "$(cat "$RESTRICT_SYSCTL" 2>/dev/null || echo 0)" == "1" ]]; }

profile_loaded() {
  # aa-status needs root; fall back to checking the dst file's sentinel.
  if [[ -r "$PROFILE_DST" ]] && grep -q "$SENTINEL" "$PROFILE_DST" 2>/dev/null; then return 0; fi
  return 1
}

report_state() {
  log "── Codex sandbox state ──"
  log "restriction active (userns blocked): $(restriction_active && echo yes || echo no)"
  # Distinguish: a profile FILE present (possibly hand-installed) vs OUR managed profile (has sentinel).
  local prof_file="no" prof_managed="no"
  [[ -e "$PROFILE_DST" ]] && prof_file="yes"
  profile_loaded && prof_managed="yes"
  log "profile file at dst:                 $prof_file (managed-by-us: $prof_managed)"
  log "codex version:                       $(command -v codex >/dev/null 2>&1 && codex --version 2>/dev/null | head -1 || echo '(codex not found)')"
  if [[ -r "$CODEX_CONFIG" ]]; then
    # network_access may sit several comment lines below the table header; scan the whole file.
    log "config network_access:               $(grep -Eq '^[[:space:]]*network_access[[:space:]]*=[[:space:]]*true' "$CODEX_CONFIG" 2>/dev/null && echo true || echo 'false/unset')"
  else
    log "config:                              (no $CODEX_CONFIG)"
  fi
}

actions_preview() {
  log "Would perform:"
  log "  sudo install -m 0644 $PROFILE_SRC $PROFILE_DST"
  log "  sudo apparmor_parser -r -W $PROFILE_DST"
  (( WITH_NETWORK )) && log "  ensure [sandbox_workspace_write] network_access=true in $CODEX_CONFIG (full host egress for workspace-write Codex)"
}

preflight
report_state

case "$MODE" in
  check)
    restriction_active && ! profile_loaded && log "NEXT: run with --accept-userns-lpe-risk to install the profile."
    exit 0 ;;
  dry-run)
    actions_preview; exit 0 ;;
  install)
    # Refuse to overwrite unmanaged local content (no sentinel) — avoid clobbering a hand-rolled profile.
    if [[ -e "$PROFILE_DST" ]] && ! grep -q "$SENTINEL" "$PROFILE_DST" 2>/dev/null; then
      fail "$PROFILE_DST exists WITHOUT our sentinel — refusing to overwrite unmanaged content. Inspect/remove it manually first."
    fi
    log "Installing managed profile (requires sudo)…"
    sudo install -m 0644 "$PROFILE_SRC" "$PROFILE_DST"
    sudo apparmor_parser -r -W "$PROFILE_DST"
    log "Profile loaded."
    # Verify with a fresh bwrap userns attempt (proves the grant took effect).
    if /usr/bin/bwrap --unshare-user --unshare-pid --ro-bind / / --proc /proc /bin/true 2>/dev/null; then
      log "VERIFIED: /usr/bin/bwrap can now create a user namespace."
    else
      fail "profile installed but /usr/bin/bwrap still cannot create a userns — investigate AppArmor logs (dmesg | grep DENIED)."
    fi
    if (( WITH_NETWORK )); then
      if [[ -r "$CODEX_CONFIG" ]] && grep -q 'network_access = true' "$CODEX_CONFIG"; then
        log "network_access already true in $CODEX_CONFIG."
      else
        log "NOTE: add to $CODEX_CONFIG manually (full host egress for workspace-write Codex):"
        log "  [sandbox_workspace_write]"
        log "  network_access = true"
      fi
    fi
    log "Done. Reverse with: scripts/install/teardown-codex-sandbox.sh"
    ;;
esac
