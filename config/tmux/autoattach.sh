# autoattach.sh — put interactive SSH logins into the persistent tmux session.
#
# SOURCED from ~/.bashrc (see scripts/setup/deploy-tmux.sh, which installs the
# sourcing line between sentinels). Not executable on its own — it uses
# `return`, which is only valid in a sourced file.
#
# workspace-hub#3784.
#
# ── Why every guard below is load-bearing ────────────────────────────────
#
# ace-linux-1 is the fleet dispatch surface. This file runs in the startup
# path of every login shell on it, so the dangerous failure is not "tmux did
# not start" — it is tmux starting on a path that must stay clean:
#
#   * BatchMode SSH, which carries scripted dispatch
#   * `ssh host '<cmd>'`
#   * scp / rsync — these break on ANY byte written to stdout
#
# All of those are NON-INTERACTIVE, which is why the `$-` test comes first and
# why nothing above it may print. Note that sshd does NOT set
# SSH_ORIGINAL_COMMAND for a plain `ssh host '<cmd>'` — it sets it only under
# ForceCommand or an authorized_keys `command=` restriction. So the
# interactivity test, not SSH_ORIGINAL_COMMAND, is what actually protects file
# transfer; the latter is defence in depth.

# Interactive only. Silence and non-firing on this path are both contractual.
case $- in
  *i*) ;;
  *) return 0 ;;
esac

# An SSH session, not a local console login.
[ -n "${SSH_CONNECTION:-}" ] || return 0

# Not already inside tmux — never nest.
[ -z "${TMUX:-}" ] || return 0

# Defence in depth: a forced command is never an interactive login.
[ -z "${SSH_ORIGINAL_COMMAND:-}" ] || return 0

# Operator escape hatch. Set this to log in without tmux — the documented way
# out if the session or tmux itself is misbehaving.
[ -z "${NO_TMUX_AUTOATTACH:-}" ] || return 0

# A box without tmux gets a normal shell, not an error.
command -v tmux >/dev/null 2>&1 || return 0

# A literal default is required. A bare "$WH_TMUX_SESSION" would pass an EMPTY
# session name when unset and fail every interactive login.
_wh_tmux_session="${WH_TMUX_SESSION:-main}"

# Attach-or-create, deliberately WITHOUT `exec`.
#
# `exec tmux ...` is the more common idiom and gives identical behaviour while
# tmux is healthy — detaching ends the login either way, because we `exit`
# below. The difference is the failure case: with `exec`, a tmux that cannot
# start takes the login shell with it and closes the connection, so the
# operator cannot get in to repair it. Here a failure falls through to a
# working shell instead. On the dispatch surface that difference is the whole
# argument. tests/tmux/test_tmux_autoattach.py pins it.
# SSH forwards the CLIENT's TERM, and a modern terminal (Ghostty, WezTerm,
# kitty) sends a name most servers' terminfo databases do not carry. tmux then
# refuses with "missing or unsuitable terminal" and auto-attach is dead for
# every login from that terminal. Measured on gpu-claw 2026-08-03:
#   xterm-ghostty  MISSING
#   xterm-256color present
# Scoped to the tmux invocation, never exported, so a detached session leaves
# the operator's real TERM untouched.
_wh_term="${TERM:-}"
if [ -n "$_wh_term" ] && ! infocmp "$_wh_term" >/dev/null 2>&1; then
  _wh_term=xterm-256color
fi

if TERM="${_wh_term:-xterm-256color}" tmux new -A -s "$_wh_tmux_session"; then
  unset _wh_tmux_session _wh_term
  exit
fi

echo "warning: tmux auto-attach failed; continuing with a plain shell." >&2
echo "         set NO_TMUX_AUTOATTACH=1 to skip this next time." >&2
unset _wh_tmux_session _wh_term
