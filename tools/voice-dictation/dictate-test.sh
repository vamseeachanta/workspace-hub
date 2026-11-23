#!/usr/bin/env bash
# Fixed-duration mic/STT smoke test. Prints transcript; never injects text.
set -euo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
SCRIPT_DIR="$(cd "${SCRIPT_DIR}" && pwd -P)"

default_state_dir() {
    if [[ -n "${DICTATE_STATE_DIR:-}" ]]; then
        printf '%s\n' "${DICTATE_STATE_DIR}"
    elif [[ -n "${XDG_RUNTIME_DIR:-}" ]]; then
        printf '%s\n' "${XDG_RUNTIME_DIR}/codex-dictate"
    else
        printf '%s\n' "${TMPDIR:-/tmp}/codex-dictate-$(id -u)"
    fi
}

ensure_private_state_dir() {
    local dir="$1"
    if [[ -L "${dir}" || ( -e "${dir}" && ! -d "${dir}" ) ]]; then
        printf 'voice-dictation: unsafe state dir: %s\n' "${dir}" >&2
        exit 1
    fi
    mkdir -p "${dir}"
    if [[ ! -O "${dir}" ]]; then
        printf 'voice-dictation: state dir is not owned by current user: %s\n' "${dir}" >&2
        exit 1
    fi
    chmod 700 "${dir}"
}

seconds="${1:-5}"
device="${2:-${DICTATE_DEVICE_ALSA:-}}"
if [[ -z "${device}" ]]; then
    repo_root="$(cd "${SCRIPT_DIR}/../.." && pwd -P)"
    device="$("${BASH:-bash}" "${repo_root}/scripts/agents/lib/voice-dictation-detect.sh" --choose)"
fi

state_dir="$(default_state_dir)"
ensure_private_state_dir "${state_dir}"
wav="${state_dir}/dictate-test.wav"
err="${state_dir}/dictate-test.err"
trap 'rm -f "${wav}" "${err}"' EXIT
python_bin="${DICTATE_PYTHON:-$(command -v python3 || true)}"

if [[ -z "${python_bin}" ]]; then
    echo "no python3 found; set DICTATE_PYTHON" >&2
    exit 1
fi

echo "Recording ${seconds}s from ${device}; speak now..."
if ! arecord -q -D "${device}" -f S16_LE -r 16000 -c 1 -d "${seconds}" "${wav}" 2>"${err}"; then
    echo "arecord failed on ${device}:" >&2
    cat "${err}" >&2
    exit 1
fi

"${python_bin}" "${SCRIPT_DIR}/transcribe.py" "${wav}"
