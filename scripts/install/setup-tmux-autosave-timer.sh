#!/usr/bin/env bash
# setup-tmux-autosave-timer.sh — install the systemd USER timer that saves tmux
# sessions without needing an attached client. workspace-hub#3784.
#
# ── Why this is a separate script ────────────────────────────────────────
#
# Writing and enabling a systemd unit is a scheduler mutation, governed by
# .claude/rules/scheduler-mutation-safety.md and registered in
# config/scheduled-tasks/mutation-surfaces.yaml under the scheduler identity
# `local-user-systemd-tmux-autosave`.
#
# scripts/setup/deploy-tmux.sh calls this script rather than embedding it, so
# that the general onboarding path (new-machine-setup.sh Step 8b) does not
# itself become a governed mutation surface. deploy-tmux.sh treats a failure
# here as a warning: a box without the timer still gets working tmux config,
# it just falls back to attach-only saves.
#
# Scope is `--user` throughout and the host binding is physical-local: this
# mutates the scheduler of the machine it runs on and never a remote one.
#
# Unit CONTENT lives in config/tmux/*.service|.timer, not in heredocs here, so
# there is exactly one reviewable copy. The boot-race rationale is documented
# in the timer file itself.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"

UNIT_BASE="tmux-autosave"
SRC_DIR="${REPO_ROOT}/config/tmux"
DEST_DIR="${HOME}/.config/systemd/user"
# The wrapper is copied to a stable path so the unit's ExecStart does not
# depend on where this repo happens to be checked out on a given machine.
WRAPPER_SRC="${REPO_ROOT}/scripts/tmux/tmux-autosave.sh"
WRAPPER_DEST_DIR="${HOME}/.tmux/wh"
WRAPPER_DEST="${WRAPPER_DEST_DIR}/tmux-autosave.sh"

log() { printf '[tmux-autosave-timer] %s\n' "$*"; }
warn() { printf '[tmux-autosave-timer] %s\n' "$*" >&2; }

# ── Preconditions ───────────────────────────────────────────────────────
#
# A box with no systemd --user (a container, a mac, a Git Bash host) is a
# legitimate configuration, not a fault. Degrade with a MESSAGE — a silent skip
# is indistinguishable from success, and the operator would have no way to know
# autosave is not running.
if ! command -v systemctl >/dev/null 2>&1; then
  warn "systemctl not found — skipping timer install."
  warn "  tmux saves will only happen while a client is ATTACHED."
  exit 0
fi

if ! systemctl --user show-environment >/dev/null 2>&1; then
  warn "systemd --user is not available for this session — skipping timer install."
  warn "  tmux saves will only happen while a client is ATTACHED."
  warn "  If this is a headless login, 'loginctl enable-linger \$USER' is the fix."
  exit 0
fi

for f in "${SRC_DIR}/${UNIT_BASE}.service" "${SRC_DIR}/${UNIT_BASE}.timer" "$WRAPPER_SRC"; do
  [ -r "$f" ] || { warn "ERROR: missing required source file: $f"; exit 1; }
done

# ── Install the wrapper at a checkout-independent path ──────────────────
mkdir -p "$WRAPPER_DEST_DIR"
install -m 0755 "$WRAPPER_SRC" "$WRAPPER_DEST"

# ── Install the units, backing up anything already there ────────────────
mkdir -p "$DEST_DIR"

# Named `write_unit` deliberately, not `install_unit`. The scheduler-mutation
# guard DISCOVERS primitives by static pattern match
# (check-scheduler-mutation-surfaces.py PRIMITIVE_PATTERNS), and it recognises
# a systemd-user-unit-write by the `write_unit`/`remove_unit` verb or by a
# cat/printf touching .config/systemd/user. An `install -m` call inside a
# differently-named function is invisible to it, so declaring
# systemd-user-unit-write while writing units this way produced
# "discovered/declared primitive mismatch". The rename makes the declaration
# and the implementation agree rather than silencing the check.
write_unit() {
  local name="$1"
  local src="${SRC_DIR}/${name}"
  local dest="${DEST_DIR}/${name}"

  # Idempotent: identical content is a no-op, so re-running onboarding does
  # not churn backups.
  if [ -f "$dest" ] && cmp -s "$src" "$dest"; then
    log "${name}: already current"
    return 0
  fi

  # Durable backup before any overwrite. The operator may have hand-edited the
  # unit; replacing that without a copy is not recoverable.
  if [ -f "$dest" ]; then
    local stamp backup
    stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    backup="${dest}.bak-${stamp}"
    cp -p "$dest" "$backup"
    log "${name}: backed up existing unit -> $(basename "$backup")"
  fi

  install -m 0644 "$src" "$dest"

  # Post-write exact-state verify. If the bytes on disk are not the bytes we
  # meant to write, roll back to the backup rather than leaving a unit whose
  # content nobody has verified.
  if ! cmp -s "$src" "$dest"; then
    warn "ERROR: ${name} did not land as written"
    local latest
    latest="$(ls -1t "${dest}".bak-* 2>/dev/null | head -1 || true)"
    if [ -n "$latest" ]; then
      cp -p "$latest" "$dest"
      warn "  rolled back to $(basename "$latest")"
    fi
    return 1
  fi

  log "${name}: installed"
}

write_unit "${UNIT_BASE}.service"
write_unit "${UNIT_BASE}.timer"

# ── Arm it ──────────────────────────────────────────────────────────────
systemctl --user daemon-reload

# Enable the TIMER, never the service. The service is Type=oneshot; enabling it
# would mean "run at boot", which is not what schedules anything here.
if ! systemctl --user enable --now "${UNIT_BASE}.timer"; then
  warn "ERROR: failed to enable ${UNIT_BASE}.timer"
  warn "  units are installed but NOT armed — tmux saves remain attach-only"
  exit 1
fi

log "armed: ${UNIT_BASE}.timer"
log "verify with: systemctl --user list-timers ${UNIT_BASE}.timer"
