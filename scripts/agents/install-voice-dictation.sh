#!/usr/bin/env bash
# Idempotent Linux voice-dictation installer.
set -euo pipefail

script_dir="${BASH_SOURCE[0]%/*}"
script_dir="$(cd "${script_dir}" && pwd -P)"
repo_root="$(cd "${script_dir}/../.." && pwd -P)"
source "${repo_root}/scripts/setup/lib/detect-os.sh"
resolve_install_root_error=""

resolve_install_root() {
    local root="$1" out_var="$2" git_dir common_dir primary resolved
    if [[ -n "${VOICE_DICTATION_INSTALL_ROOT:-}" ]]; then
        if [[ ! -d "${VOICE_DICTATION_INSTALL_ROOT}" ]]; then
            resolve_install_root_error="VOICE_DICTATION_INSTALL_ROOT does not exist: ${VOICE_DICTATION_INSTALL_ROOT}"
            return 1
        fi
        resolved="$(cd "${VOICE_DICTATION_INSTALL_ROOT}" && pwd -P)"
        printf -v "${out_var}" '%s' "${resolved}"
        return 0
    fi
    command -v git >/dev/null 2>&1 || {
        printf -v "${out_var}" '%s' "${root}"
        return 0
    }
    git_dir="$(git -C "${root}" rev-parse --path-format=absolute --git-dir 2>/dev/null || true)"
    common_dir="$(git -C "${root}" rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
    if [[ -n "${git_dir}" && -n "${common_dir}" && "${git_dir}" != "${common_dir}" ]]; then
        primary="$(git -C "${root}" worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p' | sed -n '1p')"
        if [[ -n "${primary}" && -f "${primary}/tools/voice-dictation/codex-dictate.sh" ]]; then
            resolved="$(cd "${primary}" && pwd -P)"
            printf -v "${out_var}" '%s' "${resolved}"
            return 0
        fi
        resolve_install_root_error="installer is running from a linked worktree; rerun from the primary checkout after this change is on main"
        return 1
    fi
    printf -v "${out_var}" '%s' "${root}"
}

os="$(detect_os)" || os="unknown"
if [[ "${os}" != "linux" ]]; then
    echo "voice-dictation: Linux-only installer; skipping on ${os}."
    exit 0
fi

install_root=""
if ! resolve_install_root "${repo_root}" install_root; then
    echo "voice-dictation inactive: ${resolve_install_root_error:-unable to resolve persistent install root}."
    exit 0
fi
if [[ "${install_root}" != "${repo_root}" ]]; then
    echo "voice-dictation: linked worktree detected; binding hotkey to primary checkout: ${install_root}"
fi

tool_src="${install_root}/tools/voice-dictation"
share_dir="${HOME}/.local/share/voice-dictation"
bin_link="${HOME}/.local/bin/codex-dictate"
launcher="${share_dir}/codex-dictate.sh"
hotkey="${DICTATE_HOTKEY:-<Super><Shift>v}"
binding_path="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/"
base_schema="org.gnome.settings-daemon.plugins.media-keys"
binding_schema="${base_schema}.custom-keybinding:${binding_path}"
detect_helper="${repo_root}/scripts/agents/lib/voice-dictation-detect.sh"

has_gsettings() {
    local writable
    [[ -n "${DBUS_SESSION_BUS_ADDRESS:-}${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]] || return 1
    command -v gsettings >/dev/null 2>&1 || return 1
    writable="$(gsettings writable "${base_schema}" custom-keybindings 2>/dev/null || true)"
    [[ "${writable}" == "true" ]]
}

existing_voice_binding() {
    has_gsettings || return 1
    local current
    current="$(gsettings get "${base_schema}" custom-keybindings 2>/dev/null || printf '@as []\n')"
    [[ "${current}" == *"codex-dictate"* ]]
}

shell_quote_word() {
    local value="$1"
    printf "'%s'" "${value//\'/\'\\\'\'}"
}

write_inert_hotkey() {
    has_gsettings || return 0
    existing_voice_binding || return 0
    local msg inner_command command
    msg="Voice dictation inactive: no usable microphone or STT runtime. Re-run scripts/agents/install-voice-dictation.sh after connecting a mic and installing faster-whisper."
    inner_command="if command -v notify-send >/dev/null 2>&1; then notify-send -t 4000 dictate $(shell_quote_word "${msg}"); else logger -t voice-dictation $(shell_quote_word "${msg}"); fi"
    command="bash -c $(shell_quote_word "${inner_command}")"
    gsettings set "${binding_schema}" name "Codex Voice Dictation"
    gsettings set "${binding_schema}" binding "${hotkey}"
    gsettings set "${binding_schema}" command "${command}"
}

python_candidates() {
    [[ -n "${DICTATE_PYTHON:-}" ]] && printf '%s\n' "${DICTATE_PYTHON}"
    printf '%s\n' "${HOME}/miniforge3/bin/python3"
    printf '%s\n' "${HOME}/miniconda3/bin/python3"
    printf '%s\n' "${HOME}/anaconda3/bin/python3"
    command -v python3 2>/dev/null || true
}

choose_python_with_faster_whisper() {
    local py
    while IFS= read -r py; do
        [[ -n "${py}" && -x "${py}" ]] || continue
        if "${py}" -c "import faster_whisper" >/dev/null 2>&1; then
            printf '%s\n' "${py}"
            return 0
        fi
    done < <(python_candidates)
    return 1
}

first_python_candidate() {
    local py
    while IFS= read -r py; do
        [[ -n "${py}" && -x "${py}" ]] || continue
        printf '%s\n' "${py}"
        return 0
    done < <(python_candidates)
    return 1
}

ensure_share_links() {
    if [[ ! -x "${tool_src}/codex-dictate.sh" ]]; then
        echo "voice-dictation inactive: tool source missing executable ${tool_src}/codex-dictate.sh"
        write_inert_hotkey
        exit 0
    fi
    mkdir -p "${share_dir%/*}" "${bin_link%/*}"
    if [[ -e "${share_dir}" && ! -L "${share_dir}" ]]; then
        mv "${share_dir}" "${share_dir}.backup-$(date +%Y%m%d%H%M%S)"
    fi
    ln -sfn "${tool_src}" "${share_dir}"
    ln -sfn "${launcher}" "${bin_link}"
}

ensure_hotkey() {
    has_gsettings || {
        echo "voice-dictation: no gsettings; bind manually to: env DICTATE_DEVICE_ALSA=${selected_device} DICTATE_PYTHON=${selected_python} bash ${launcher}"
        return 0
    }
    local current
    current="$(gsettings get "${base_schema}" custom-keybindings 2>/dev/null || printf '@as []\n')"
    if [[ "${current}" != *"${binding_path}"* ]]; then
        if [[ "${current}" == "@as []" || "${current}" == "[]" ]]; then
            gsettings set "${base_schema}" custom-keybindings "['${binding_path}']"
        else
            gsettings set "${base_schema}" custom-keybindings "${current%]}, '${binding_path}']"
        fi
    fi
    local command
    command="env $(shell_quote_word "DICTATE_DEVICE_ALSA=${selected_device}") $(shell_quote_word "DICTATE_PYTHON=${selected_python}") bash $(shell_quote_word "${launcher}")"
    gsettings set "${binding_schema}" name "Codex Voice Dictation"
    gsettings set "${binding_schema}" binding "${hotkey}"
    gsettings set "${binding_schema}" command "${command}"
}

warn_missing_injector() {
    if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
        command -v wtype >/dev/null 2>&1 || command -v ydotool >/dev/null 2>&1 || echo "voice-dictation: no text injector found; install wtype or ydotool, transcripts will print only."
    else
        command -v xdotool >/dev/null 2>&1 || echo "voice-dictation: no text injector found; install xdotool, transcripts will print only."
    fi
}

selected_device=""
bash_bin="${BASH:-bash}"
detect_err="$(mktemp "${TMPDIR:-/tmp}/voice-dictation-detect.XXXXXX")"
trap 'rm -f "${detect_err}"' EXIT
if ! selected_device="$("${bash_bin}" "${detect_helper}" --choose 2>"${detect_err}")"; then
    reason="$(sed -n '1p' "${detect_err}" 2>/dev/null || true)"
    echo "voice-dictation inactive: ${reason:-no usable capture device}"
    echo "Dictate on a mic-bearing local desktop and type into the focused VNC/SSH/tmux target."
    write_inert_hotkey
    exit 0
fi

warn_missing_injector

selected_python="$(choose_python_with_faster_whisper || true)"
if [[ -z "${selected_python}" && "${DICTATE_BOOTSTRAP_INSTALL:-0}" == "1" ]]; then
    install_python="$(first_python_candidate || true)"
    if [[ -n "${install_python}" && -n "$(command -v uv 2>/dev/null || true)" ]]; then
        uv pip install --python "${install_python}" faster-whisper || true
        selected_python="$(choose_python_with_faster_whisper || true)"
    elif [[ -n "${install_python}" ]]; then
        echo "voice-dictation: uv missing; run: uv pip install --python ${install_python} faster-whisper"
    fi
fi

if [[ -z "${selected_python}" ]]; then
    install_python="$(first_python_candidate || true)"
    if [[ -n "${install_python}" ]]; then
        echo "voice-dictation inactive: faster-whisper missing. Run: uv pip install --python ${install_python} faster-whisper"
    else
        echo "voice-dictation inactive: install Python and faster-whisper."
    fi
    write_inert_hotkey
    exit 0
fi

ensure_share_links
ensure_hotkey
echo "voice-dictation active: ${hotkey} -> ${launcher} (${selected_device}, ${selected_python})"
