#!/usr/bin/env bash
# dictate-test.sh — fixed-duration mic check. Records N seconds (default 5),
# transcribes locally, and PRINTS what it heard (no typing) so the STT/mic path
# can be verified in isolation before the hotkey is bound.
#
#   ./dictate-test.sh [seconds] [alsa-device]
#   device examples:  default  |  plughw:1,0  (a specific USB headset)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECS="${1:-5}"
DEVICE="${2:-${DICTATE_DEVICE_ALSA:-default}}"
WAV="${XDG_RUNTIME_DIR:-/tmp}/dictate_test.wav"
ERR="${XDG_RUNTIME_DIR:-/tmp}/dictate_test.err"
PY="${DICTATE_PYTHON:-$(command -v python3 || true)}"

[[ -n "${PY}" ]] || { echo "!!! no python3 found (set DICTATE_PYTHON)"; exit 1; }

echo ">>> Recording ${SECS}s from device '${DEVICE}' — SPEAK NOW..."
if ! arecord -q -D "${DEVICE}" -f S16_LE -r 16000 -c 1 -d "${SECS}" "${WAV}" 2>"${ERR}"; then
  echo "!!! arecord failed on device '${DEVICE}':"; cat "${ERR}"
  echo "    Try a specific device:  $0 ${SECS} plughw:1,0   (see: arecord -l)"
  exit 1
fi
echo ">>> Recorded $(stat -c%s "${WAV}" 2>/dev/null || echo '?') bytes. Transcribing..."
text="$("${PY}" "${HERE}/transcribe.py" "${WAV}" 2>/dev/null || true)"
echo "================================================"
echo ">>> HEARD: '${text}'"
echo "================================================"
