#!/usr/bin/env bash
# codex-dictate.sh — free/local push-to-talk dictation for any focused window.
#
# Bind to ONE hotkey (toggle model):
#   1st press -> start recording mic to a temp WAV (arecord, 16 kHz mono)
#   2nd press -> stop, transcribe locally (faster-whisper), type into the
#                focused window via xdotool (X11) / wtype|ydotool (Wayland).
#
# Agent-agnostic: types wherever the cursor is — Codex, Claude Code, a shell,
# or an ssh/tmux pane to another machine. Stack is 100% free + offline.
#
# Tunables (env): DICTATE_PYTHON (interpreter with faster-whisper),
#                 DICTATE_DEVICE_ALSA (arecord -D target, default 'default'),
#                 DICTATE_MODEL (whisper size, default base.en).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="${XDG_RUNTIME_DIR:-/tmp}/codex-dictate"
WAV="${STATE_DIR}/rec.wav"
PIDFILE="${STATE_DIR}/arecord.pid"
mkdir -p "${STATE_DIR}"

PY="${DICTATE_PYTHON:-$(command -v python3 || true)}"
ALSA_DEV="${DICTATE_DEVICE_ALSA:-default}"

notify() { command -v notify-send >/dev/null 2>&1 && notify-send -t 1500 "🎙 dictate" "$1" || true; }

# Inject text into the focused window, picking the tool that fits the session.
inject_text() {
  local text="$1"
  if [[ -n "${WAYLAND_DISPLAY:-}" ]] && command -v wtype >/dev/null 2>&1; then
    wtype "${text}"
  elif command -v xdotool >/dev/null 2>&1; then
    # --clearmodifiers so a still-held Super/Shift from the hotkey doesn't
    # turn the typed letters into shortcuts.
    xdotool type --clearmodifiers -- "${text}"
  elif command -v ydotool >/dev/null 2>&1; then
    ydotool type "${text}"
  else
    notify "no injector (install xdotool or wtype) — transcript on stdout"
    printf '%s\n' "${text}"
  fi
}

start_recording() {
  notify "recording… (press hotkey again to stop)"
  arecord -q -D "${ALSA_DEV}" -f S16_LE -r 16000 -c 1 "${WAV}" &
  echo $! > "${PIDFILE}"
}

stop_and_type() {
  local pid; pid="$(cat "${PIDFILE}")"
  rm -f "${PIDFILE}"
  kill "${pid}" 2>/dev/null || true
  wait "${pid}" 2>/dev/null || true   # let arecord flush a valid WAV header
  notify "transcribing…"
  [[ -n "${PY}" ]] || { notify "no python3 found"; return 1; }
  local text; text="$("${PY}" "${HERE}/transcribe.py" "${WAV}" 2>/dev/null || true)"
  if [[ -z "${text// /}" ]]; then
    notify "(no speech detected)"
    return 0
  fi
  inject_text "${text}"
}

# Toggle: a live PID file means "currently recording".
if [[ -f "${PIDFILE}" ]] && kill -0 "$(cat "${PIDFILE}")" 2>/dev/null; then
  stop_and_type
else
  start_recording
fi
