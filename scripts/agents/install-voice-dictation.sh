#!/usr/bin/env bash
# install-voice-dictation.sh — install the free/local push-to-talk dictation
# tool on this machine, or point at the OS-native equivalent. Idempotent;
# called from scripts/memory/bootstrap-machine.sh so every machine converges.
#
# Per-OS strategy (RSI relief "across many OS" — use the best tool each has):
#   linux   -> install tools/voice-dictation/ (no built-in dictation exists)
#   macos   -> native: press Fn/Globe twice. Print reminder, no install.
#   windows -> native: Win + H (voice typing). Print reminder, no install.
#
# On Linux it: symlinks the repo tool into ~/.local/{share,bin}, ensures a
# Python with faster-whisper, reports missing system deps (never sudo-installs
# silently), and binds the GNOME hotkey (X11/Wayland) when available.
#
# Tunables (env): DICTATE_HOTKEY (default '<Super><Shift>v'),
#                 DICTATE_PYTHON (force a specific interpreter).
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
source "${REPO_ROOT}/scripts/setup/lib/detect-os.sh"
OS="$(detect_os)" || { echo "voice-dictation: unsupported OS — skipping." >&2; exit 0; }

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
TOOL_SRC="${REPO_ROOT}/tools/voice-dictation"
SHARE_DIR="${HOME}/.local/share/voice-dictation"
LAUNCH="${SHARE_DIR}/codex-dictate.sh"
BIN_LINK="${HOME}/.local/bin/codex-dictate"
BINDING="${DICTATE_HOTKEY:-<Super><Shift>v}"

echo -e "${CYAN}=== voice-dictation install (${OS}) ===${NC}"

# --- macOS / Windows: native dictation is better than our tool. Just remind. ---
if [[ "${OS}" == "macos" ]]; then
  echo -e "${GREEN}macOS has built-in dictation — press the Fn (Globe) key twice to start/stop.${NC}"
  echo "  Enable once: System Settings → Keyboard → Dictation → On."
  exit 0
fi
if [[ "${OS}" == "windows" ]]; then
  echo -e "${GREEN}Windows has built-in voice typing — press  Win + H  in any text field.${NC}"
  echo "  No install needed; works offline after the first language-pack download."
  exit 0
fi

# ----------------------------- Linux from here -----------------------------

# 1) Symlink the repo tool to stable runtime locations (git pull = auto-update).
mkdir -p "${SHARE_DIR%/*}" "${HOME}/.local/bin"
# Replace a pre-existing REAL directory (e.g. an older copy-install) so that
# ln -sfn creates the link AT the path rather than nesting it inside.
[[ -e "${SHARE_DIR}" && ! -L "${SHARE_DIR}" ]] && rm -rf "${SHARE_DIR}"
ln -sfn "${TOOL_SRC}" "${SHARE_DIR}"
ln -sfn "${LAUNCH}" "${BIN_LINK}"
echo -e "${GREEN}✅ linked ${SHARE_DIR} → tools/voice-dictation; codex-dictate on PATH${NC}"

# 1.5) No sound card / mic? (e.g. a headless VNC *target* like ace-linux-2.)
# Such a machine can't dictate locally — and doesn't need to: dictate on the
# machine that HAS the mic and let VNC/ssh forward the typed TEXT into this
# one's focused window. Use /proc/asound/cards so this works even before
# alsa-utils is installed. Keep the symlink so a later USB mic + re-run just
# works; skip the model download + hotkey (which would bind to a failing tool).
if [[ ! -r /proc/asound/cards ]] || ! grep -qE '^[[:space:]]*[0-9]+[[:space:]]' /proc/asound/cards; then
  echo -e "${YELLOW}No sound card / capture device on this machine.${NC}"
  echo "  Dictate on a machine that HAS a mic; let VNC/ssh forward the typed text"
  echo "  into this one's focused window. Skipping faster-whisper + hotkey here."
  echo -e "${GREEN}voice-dictation: tool linked (inactive without a mic).${NC}"
  exit 0
fi

# 2) Report missing system deps (sudo apt is the user's call, never silent here).
missing_apt=()
command -v arecord  >/dev/null 2>&1 || missing_apt+=("alsa-utils")
if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
  command -v wtype >/dev/null 2>&1 || command -v ydotool >/dev/null 2>&1 || missing_apt+=("wtype")
else
  command -v xdotool >/dev/null 2>&1 || missing_apt+=("xdotool")
fi
if (( ${#missing_apt[@]} )); then
  echo -e "${YELLOW}⚠️  install system deps:  sudo apt install -y ${missing_apt[*]}${NC}"
fi

# 3) Ensure a Python that has faster-whisper; remember which one for the hotkey.
find_py() {
  local c=()
  [[ -n "${DICTATE_PYTHON:-}" ]] && c+=("${DICTATE_PYTHON}")
  c+=("$(command -v python3 || true)" \
     "${HOME}/miniforge3/bin/python3" "${HOME}/miniconda3/bin/python3" "${HOME}/anaconda3/bin/python3")
  local p
  for p in "${c[@]}"; do
    [[ -n "${p}" && -x "${p}" ]] || continue
    if "${p}" -c 'import faster_whisper' >/dev/null 2>&1; then echo "${p}"; return 0; fi
  done
  return 1
}
PYBIN="$(find_py || true)"
if [[ -z "${PYBIN}" ]]; then
  PYBIN="${DICTATE_PYTHON:-$(command -v python3 || true)}"
  if [[ -n "${PYBIN}" ]]; then
    echo -e "${CYAN}Installing faster-whisper into ${PYBIN}...${NC}"
    if command -v uv >/dev/null 2>&1; then
      uv pip install --python "${PYBIN}" faster-whisper || echo -e "${YELLOW}faster-whisper install failed — run manually.${NC}"
    else
      "${PYBIN}" -m pip install --user faster-whisper || echo -e "${YELLOW}faster-whisper install failed — run manually.${NC}"
    fi
  else
    echo -e "${YELLOW}⚠️  no python3 found — install Python 3, then re-run bootstrap.${NC}"
  fi
fi
[[ -n "${PYBIN}" ]] && echo -e "${GREEN}✅ STT python: ${PYBIN}${NC}"

# 4) Bind the GNOME hotkey (X11 or Wayland GNOME). Idempotent. Skip elsewhere.
bind_gnome_hotkey() {
  command -v gsettings >/dev/null 2>&1 || { echo -e "${YELLOW}no gsettings — bind a hotkey manually to: ${LAUNCH}${NC}"; return 0; }
  local base="org.gnome.settings-daemon.plugins.media-keys"
  gsettings writable "${base}" custom-keybindings >/dev/null 2>&1 || {
    echo -e "${YELLOW}GNOME media-keys schema unavailable (non-GNOME?) — bind manually to: ${LAUNCH}${NC}"; return 0; }
  local kpath="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/"
  local schema="${base}.custom-keybinding:${kpath}"
  local cur; cur="$(gsettings get "${base}" custom-keybindings 2>/dev/null || echo '@as []')"
  if [[ "${cur}" != *"${kpath}"* ]]; then
    if [[ "${cur}" == "@as []" || "${cur}" == "[]" ]]; then
      gsettings set "${base}" custom-keybindings "['${kpath}']"
    else
      gsettings set "${base}" custom-keybindings "${cur%]}, '${kpath}']"
    fi
  fi
  gsettings set "${schema}" name 'Codex Voice Dictation'
  gsettings set "${schema}" command "env DICTATE_PYTHON=${PYBIN:-python3} bash ${LAUNCH}"
  gsettings set "${schema}" binding "${BINDING}"
  echo -e "${GREEN}✅ hotkey bound: ${BINDING} → Codex Voice Dictation${NC}"
}
bind_gnome_hotkey

echo -e "${GREEN}voice-dictation: done. Test:  ${SHARE_DIR}/dictate-test.sh${NC}"
