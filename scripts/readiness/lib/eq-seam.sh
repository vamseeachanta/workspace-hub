#!/usr/bin/env bash
# eq-seam.sh — single source of truth for the equality GENERATION seam (#3702).
#
# WHY: collect-equality.sh and build-equality-matrix.py used to write their generated
# artifacts (.claude/state/equality-<machine>.yaml, docs/reports/*machine-equality-matrix.html)
# straight into the TRACKED working tree. Every peer publish advances those same paths on
# origin/main, so `git pull --ff-only` aborted with "local changes would be overwritten",
# behind_main ratcheted monotonically, and is_stale() stamped STALE-CHECKOUT across all
# dimensions of that machine. Relocating GENERATION out of the tree removes the blocker.
# The PUBLISHED surface on origin/main is unchanged: publish-equality.sh has written
# through a disposable sparse worktree since #3571.
#
# Resolution order (identical for every entry point, so the rollback below always holds):
#   1. explicit flag value passed by the caller (--state-dir / --out-dir)
#   2. $EQ_STATE_DIR / $EQ_REPORT_DIR
#   3. ${XDG_STATE_HOME:-$HOME/.local/state}/workspace-hub/equality[/reports]
# It NEVER falls back to a path inside the checkout.
#
# ROLLBACK: exporting EQ_STATE_DIR="$WORKSPACE_HUB/.claude/state" and
# EQ_REPORT_DIR="$WORKSPACE_HUB/docs/reports" in the cron environment restores the
# pre-#3702 behaviour exactly, with no revert commit. Windows Phase 1 uses precisely
# this seam to stay pinned in place (see scripts/windows/equality-report.ps1).
#
# NOTE: the seam directory is local, regenerable state — it is not backed up and not
# synced. The canonical copy of every machine's evidence lives on origin/main.

# `set -u` safe: an unset HOME must produce a bad path the caller reports loudly (the
# mkdir fails with the resolved directory named), not an "unbound variable" abort whose
# message says nothing about the seam.
eq_seam_root() {
  local base="${XDG_STATE_HOME:-}"
  [[ -n "$base" ]] || base="${HOME:-}/.local/state"
  printf '%s/workspace-hub/equality' "$base"
}

# eq_state_dir [explicit-flag-value] — where equality-<machine>.yaml is WRITTEN.
eq_state_dir() {
  if [[ -n "${1:-}" ]]; then printf '%s' "$1"; return 0; fi
  if [[ -n "${EQ_STATE_DIR:-}" ]]; then printf '%s' "${EQ_STATE_DIR}"; return 0; fi
  eq_seam_root
}

# eq_report_dir [explicit-flag-value] — where the matrix HTML is WRITTEN.
eq_report_dir() {
  if [[ -n "${1:-}" ]]; then printf '%s' "$1"; return 0; fi
  if [[ -n "${EQ_REPORT_DIR:-}" ]]; then printf '%s' "${EQ_REPORT_DIR}"; return 0; fi
  printf '%s/reports' "$(eq_seam_root)"
}
