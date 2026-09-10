#!/usr/bin/env bash
# tmux-autosave.sh — save the tmux session tree without needing an attached client.
#
# Invoked by the systemd user timer installed by
# scripts/install/setup-tmux-autosave-timer.sh. workspace-hub#3784.
#
# ── The defect this exists to fix ────────────────────────────────────────
#
# tmux-continuum performs its autosave by injecting continuum_save.sh into
# `status-right`. tmux evaluates the status line only for an ATTACHED client,
# so a DETACHED session — precisely the case persistence exists for — silently
# stops being saved. Measured on ace-linux-1: the last save was 75.8 hours old
# against a declared 15-minute interval, with zero attached clients. Nothing
# reported an error; the save simply never ran.
#
# ── Why this delegates instead of calling resurrect directly ─────────────
#
# It would be shorter to call ~/.tmux/plugins/tmux-resurrect/scripts/save.sh.
# That would be wrong. continuum_save.sh wraps that call with three things this
# script must not reimplement:
#
#   acquire_lock                      a PID-keyed, auto-expiring mkdir lock.
#                                     Its own comment: "Sometimes tmux starts
#                                     multiple saves in parallel. We want only
#                                     one save to be running, otherwise we can
#                                     get corrupted saved state." An attached
#                                     client can still trigger the status-line
#                                     save at any moment, so this timer is a
#                                     SECOND writer by construction.
#   enough_time_since_last_run_passed  honours @continuum-save-interval, so the
#                                     timer cadence and the tmux interval need
#                                     not agree; a fast timer simply no-ops.
#   set_last_save_timestamp           keeps @continuum-save-last-timestamp
#                                     coherent — the exact signal the original
#                                     defect was diagnosed from.
#
# An earlier draft of the plan instead guarded on a "restore in progress"
# marker. Adversarial review refuted it against the plugin source: no such
# durable marker exists (resurrect's restore.sh:19 RESTORING_FROM_SCRATCH is a
# process-local shell variable; continuum_restore.sh invokes restore directly).
# The boot-time restore race is handled by the TIMER instead — OnBootSec=5min,
# because @continuum-save-last-timestamp defaults to 0 on a fresh server and an
# early tick would otherwise save over an in-flight restore.
#
# ── Fail-soft ────────────────────────────────────────────────────────────
#
# Every absent precondition below is a normal resting state, not an error: a
# box without tmux, an idle box with no server, a box where the plugins were
# never installed. This runs every 15 minutes on every machine, and a unit that
# fails noisily on a healthy idle box trains people to ignore the one time it
# means something. Exit 0, say nothing.

set -uo pipefail

CONTINUUM_SAVE="${HOME}/.tmux/plugins/tmux-continuum/scripts/continuum_save.sh"

# No tmux on this machine.
command -v tmux >/dev/null 2>&1 || exit 0

# No server running — nothing to save.
tmux has-session >/dev/null 2>&1 || exit 0

# Plugins not installed here. scripts/setup/deploy-tmux.sh is what fixes this;
# staying silent keeps the timer from nagging until it has been run.
[ -x "$CONTINUUM_SAVE" ] || exit 0

exec "$CONTINUUM_SAVE"
