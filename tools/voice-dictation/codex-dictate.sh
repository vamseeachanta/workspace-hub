#!/usr/bin/env bash
# Toggle dictation: first press records, second press transcribes and types text.
set -euo pipefail

resolve_script() {
    if command -v readlink >/dev/null 2>&1; then
        readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || printf '%s\n' "${BASH_SOURCE[0]}"
    else
        printf '%s\n' "${BASH_SOURCE[0]}"
    fi
}

script_path="$(resolve_script)"
tool_dir="$(cd "${script_path%/*}" && pwd -P)"
repo_root="$(cd "${tool_dir}/../.." && pwd -P)"
detect_helper="${repo_root}/scripts/agents/lib/voice-dictation-detect.sh"

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

state_dir="$(default_state_dir)"
wav="${state_dir}/rec.wav"
pidfile="${state_dir}/arecord.pid"
metafile="${state_dir}/arecord.meta"
lockfile="${state_dir}/toggle.lock"
lockdir="${state_dir}/toggle.lock.d"
lockdir_acquired=""
ensure_private_state_dir "${state_dir}"

notify() {
    local msg="$1"
    if command -v notify-send >/dev/null 2>&1; then
        notify-send -t 2000 "dictate" "${msg}" || true
    else
        printf '%s\n' "${msg}" >&2
    fi
}

cleanup_lock_dir() {
    [[ -n "${lockdir_acquired}" ]] && rmdir "${lockdir}" 2>/dev/null || true
}

acquire_toggle_lock() {
    if command -v flock >/dev/null 2>&1; then
        exec 9>"${lockfile}"
        if ! flock -n 9; then
            notify "dictation busy"
            exit 0
        fi
        return 0
    fi
    if mkdir "${lockdir}" 2>/dev/null; then
        lockdir_acquired=1
        trap cleanup_lock_dir EXIT
        return 0
    fi
    notify "dictation busy"
    exit 0
}

inject_text() {
    local text="$1"
    if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
        if command -v wtype >/dev/null 2>&1; then
            wtype -- "${text}"
        elif command -v ydotool >/dev/null 2>&1; then
            ydotool type -- "${text}"
        elif command -v xdotool >/dev/null 2>&1; then
            xdotool type --clearmodifiers -- "${text}"
        else
            notify "no text injector found; transcript on stdout"
            printf '%s\n' "${text}"
        fi
    elif command -v xdotool >/dev/null 2>&1; then
        xdotool type --clearmodifiers -- "${text}"
    elif command -v wtype >/dev/null 2>&1; then
        wtype -- "${text}"
    elif command -v ydotool >/dev/null 2>&1; then
        ydotool type -- "${text}"
    else
        notify "no text injector found; transcript on stdout"
        printf '%s\n' "${text}"
    fi
}

stop_and_type() {
    local pid text python_bin transcribe_err error_text
    pid="$(cat "${pidfile}" 2>/dev/null || true)"
    rm -f "${pidfile}" "${metafile}"
    [[ -n "${pid}" ]] && kill "${pid}" 2>/dev/null || true
    if [[ -n "${pid}" ]]; then
        for _ in 1 2 3 4 5 6 7 8 9 10; do
            kill -0 "${pid}" 2>/dev/null || break
            sleep 0.05
        done
        if kill -0 "${pid}" 2>/dev/null; then
            kill -KILL "${pid}" 2>/dev/null || true
        fi
        wait "${pid}" 2>/dev/null || true
    fi
    notify "transcribing"
    python_bin="${DICTATE_PYTHON:-$(command -v python3 || true)}"
    if [[ -z "${python_bin}" ]]; then
        notify "Voice dictation inactive: no Python runtime"
        rm -f "${wav}"
        return 0
    fi
    transcribe_err="${state_dir}/transcribe.err"
    if ! text="$("${python_bin}" "${tool_dir}/transcribe.py" "${wav}" 2>"${transcribe_err}")"; then
        error_text="$(sed -n '1p' "${transcribe_err}" 2>/dev/null || true)"
        notify "dictation runtime broken: ${error_text:-transcription failed}"
        rm -f "${wav}"
        return 0
    fi
    rm -f "${wav}" "${transcribe_err}"
    if [[ -z "${text//[[:space:]]/}" ]]; then
        notify "no speech detected"
        return 0
    fi
    inject_text "${text}"
}

choose_auto_device() {
    DICTATE_DEVICE_ALSA= "${BASH:-bash}" "${detect_helper}" --choose 2>/dev/null || true
}

start_arecord() {
    local device="$1" pid grace
    rm -f "${pidfile}" "${metafile}"
    arecord -q -D "${device}" -f S16_LE -r 16000 -c 1 "${wav}" 9>&- &
    pid=$!
    grace="${DICTATE_START_GRACE_SECONDS:-0.15}"
    sleep "${grace}" 2>/dev/null || true
    if ! kill -0 "${pid}" 2>/dev/null; then
        wait "${pid}" 2>/dev/null || true
        return 1
    fi
    printf '%s\n' "${pid}" > "${pidfile}"
    {
        printf 'pid=%s\n' "${pid}"
        printf 'device=%s\n' "${device}"
        printf 'wav=%s\n' "${wav}"
    } > "${metafile}"
    return 0
}

start_recording() {
    local device fallback explicit=false
    device="${DICTATE_DEVICE_ALSA:-}"
    if [[ -n "${device}" ]]; then
        explicit=true
    else
        device="$(choose_auto_device)"
    fi
    if [[ -z "${device}" ]]; then
        notify "Voice dictation inactive: no usable capture device"
        return 0
    fi
    if start_arecord "${device}"; then
        notify "recording; press hotkey again to stop"
        return 0
    fi
    if [[ "${explicit}" == true ]]; then
        notify "Configured microphone failed; trying auto-detected microphone. Re-run scripts/agents/install-voice-dictation.sh to refresh the saved hotkey device."
        fallback="$(choose_auto_device)"
        if [[ -n "${fallback}" ]] && start_arecord "${fallback}"; then
            notify "recording with fallback microphone"
            return 0
        fi
    fi
    notify "Voice dictation inactive: no usable capture device"
    return 0
}

is_owned_recording() {
    local pid="$1" meta_pid cmdline
    [[ "${pid}" =~ ^[0-9]+$ ]] || return 1
    [[ -f "${metafile}" ]] || return 1
    meta_pid="$(sed -n 's/^pid=//p' "${metafile}" 2>/dev/null | head -1)"
    [[ "${meta_pid}" == "${pid}" ]] || return 1
    [[ -r "/proc/${pid}/cmdline" ]] || return 1
    cmdline="$(tr '\0' ' ' < "/proc/${pid}/cmdline" 2>/dev/null || true)"
    [[ "${cmdline}" == *arecord* && "${cmdline}" == *"${wav}"* ]]
}

acquire_toggle_lock

if [[ -f "${pidfile}" ]]; then
    existing_pid="$(cat "${pidfile}" 2>/dev/null || true)"
    if [[ -n "${existing_pid}" ]] && kill -0 "${existing_pid}" 2>/dev/null; then
        if is_owned_recording "${existing_pid}"; then
            stop_and_type
        else
            rm -f "${pidfile}" "${metafile}"
            start_recording
        fi
    else
        rm -f "${pidfile}" "${metafile}"
        start_recording
    fi
else
    start_recording
fi
