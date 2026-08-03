#!/usr/bin/env bash
# deploy-tmux.sh — install the workspace-hub tmux setup on this machine.
#
# Usage: ./deploy-tmux.sh
#
# Called from scripts/setup/new-machine-setup.sh Step 8b, so this is one of the
# first things a fresh box runs. That is why almost everything here degrades
# with a MESSAGE rather than failing: a box with no network, no systemd, or no
# tmux should still finish onboarding.
#
# Extended for workspace-hub#3784. What it did before: symlink the config. The
# three defects that required more, each measured on the live fleet 2026-08-02:
#
#   * It never installed the resurrect/continuum plugins. That is the root
#     cause of the drift — ace-linux-2 and gpu-claw have none, and tmux.conf's
#     `if-shell` guard skips the plugin block SILENTLY, so both look configured
#     while having no reboot survival whatsoever.
#   * `ln -sf` overwrote a regular ~/.tmux.conf with no backup. gpu-claw has a
#     hand-rolled 26-line file that would have been destroyed without trace.
#   * Nothing put an interactive SSH login into the persistent session.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="${REPO_ROOT}/config/tmux/tmux.conf"
DEST="$HOME/.tmux.conf"
AUTOATTACH="${REPO_ROOT}/config/tmux/autoattach.sh"
TIMER_INSTALLER="${REPO_ROOT}/scripts/install/setup-tmux-autosave-timer.sh"
PLUGIN_DIR="$HOME/.tmux/plugins"

# Pinned so three machines deployed months apart receive the SAME executable
# plugin code. An unpinned clone tracks upstream HEAD and quietly defeats the
# convergence this whole change exists to deliver.
RESURRECT_REF="${WH_TMUX_RESURRECT_REF:-v4.0.0}"
CONTINUUM_REF="${WH_TMUX_CONTINUUM_REF:-v3.1.0}"

SENTINEL_OPEN="# >>> workspace-hub tmux auto-attach >>>"
SENTINEL_CLOSE="# <<< workspace-hub tmux auto-attach <<<"

warned=0
log()  { printf '%s\n' "$*"; }
warn() { warned=1; printf 'WARNING: %s\n' "$*" >&2; }

[ -f "$SRC" ] || { printf 'ERROR: tmux.conf not found at %s\n' "$SRC" >&2; exit 1; }

# ── 1. Config symlink, backing up anything real that is already there ────
if [ -L "$DEST" ] && [ "$(readlink -f "$DEST")" = "$(readlink -f "$SRC")" ]; then
  log "config: already linked"
else
  # A regular file here is someone's hand-rolled config. Replacing it without
  # a copy is unrecoverable, and `ln -sf` gives no warning before doing so.
  if [ -e "$DEST" ] && [ ! -L "$DEST" ]; then
    backup="${DEST}.bak-$(date -u +%Y%m%dT%H%M%SZ)"
    cp -p "$DEST" "$backup"
    log "config: backed up existing file -> $(basename "$backup")"
  fi
  ln -sfn "$SRC" "$DEST"
  log "config: linked $DEST -> $SRC"
fi

# ── 2. Plugins — the drift root cause ────────────────────────────────────
#
# tmux.conf loads these behind `if-shell [ -r ... ]`, which means a machine
# without them sources the config cleanly and simply has no reboot survival.
# Nothing surfaces that at attach time, so it has to be fixed at deploy time.
mkdir -p "$PLUGIN_DIR"

install_plugin() {
  local name="$1" url="$2" ref="$3"
  local dir="${PLUGIN_DIR}/${name}"
  local entrypoint="${dir}/${name#tmux-}.tmux"

  # A DIRECTORY IS NOT A PLUGIN. A clone interrupted by a dropped network
  # leaves one behind, and an existence check would then treat the box as
  # healthy forever.
  if [ -d "$dir" ] && [ -r "$entrypoint" ]; then
    log "plugin ${name}: present"
    return 0
  fi

  if [ -d "$dir" ]; then
    warn "plugin ${name}: directory exists but ${name#tmux-}.tmux is missing — re-cloning"
    rm -rf "$dir"
  fi

  if git clone --depth 1 --branch "$ref" "$url" "$dir" >/dev/null 2>&1; then
    log "plugin ${name}: installed at ${ref}"
  else
    warn "plugin ${name}: clone failed (offline?) — reboot survival is NOT active on this box."
    warn "  re-run this script once the network is available."
    rm -rf "$dir"
  fi
}

install_plugin tmux-resurrect https://github.com/tmux-plugins/tmux-resurrect "$RESURRECT_REF"
install_plugin tmux-continuum https://github.com/tmux-plugins/tmux-continuum "$CONTINUUM_REF"

# ── 3. Auto-attach block in ~/.bashrc ────────────────────────────────────
BASHRC="$HOME/.bashrc"
[ -e "$BASHRC" ] || : > "$BASHRC"

# Rewrite between sentinels so re-running never duplicates or strands an old
# copy. Everything outside the markers is the user's and is preserved.
tmp="$(mktemp)"
# `close` is an awk BUILTIN, so `-v close=...` is a run-time error
# ("cannot command line assign to close"). Hence the s_ prefixes.
awk -v s_open="$SENTINEL_OPEN" -v s_close="$SENTINEL_CLOSE" '
  index($0, s_open)  { skip = 1; next }
  index($0, s_close) { skip = 0; next }
  !skip { print }
' "$BASHRC" > "$tmp"

{
  cat "$tmp"
  printf '%s\n' "$SENTINEL_OPEN"
  printf '# Managed by scripts/setup/deploy-tmux.sh (workspace-hub#3784).\n'
  printf '# Edits between these markers are overwritten on the next run.\n'
  printf '[ -r "%s" ] && . "%s"\n' "$AUTOATTACH" "$AUTOATTACH"
  printf '%s\n' "$SENTINEL_CLOSE"
} > "$BASHRC"
rm -f "$tmp"
log "auto-attach: block installed in ~/.bashrc"

# The block only runs if the login-shell chain actually reaches ~/.bashrc.
# bash reads the FIRST of ~/.bash_profile, ~/.bash_login, ~/.profile for a
# login shell; the stock ~/.profile sources ~/.bashrc, but a ~/.bash_profile
# added later shadows it and silently makes this block dead code.
for f in "$HOME/.bash_profile" "$HOME/.bash_login"; do
  if [ -r "$f" ] && ! grep -q 'bashrc' "$f"; then
    warn "$(basename "$f") exists and does not source ~/.bashrc — auto-attach will NOT run."
    warn "  add:  [ -f ~/.bashrc ] && . ~/.bashrc"
  fi
done

# ── 4. Autosave timer (governed surface — separate script) ───────────────
#
# Delegated rather than inlined so this onboarding script does not itself
# become a scheduler mutation surface under
# .claude/rules/scheduler-mutation-safety.md. A failure is a warning: the box
# still gets working tmux config, it just falls back to attach-only saves.
if [ -x "$TIMER_INSTALLER" ]; then
  if ! "$TIMER_INSTALLER"; then
    warn "autosave timer install failed — saves will only happen while ATTACHED."
  fi
else
  warn "timer installer missing at $TIMER_INSTALLER — saves will be attach-only."
fi

# ── 5. Reload a running server ───────────────────────────────────────────
if command -v tmux >/dev/null 2>&1 && tmux list-sessions >/dev/null 2>&1; then
  tmux source-file "$DEST" || warn "could not reload config in the running server"
  log "config: reloaded in the running tmux server"
fi

if [ "$warned" -eq 1 ]; then
  log "Done, WITH WARNINGS above — this box is not fully configured."
else
  log "Done. tmux configured."
fi
