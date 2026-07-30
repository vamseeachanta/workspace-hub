#!/usr/bin/env bash
# Shared capture-device detection for the Linux voice dictation tool.

voice_dictation_capture_devices_from_arecord() {
    local line card device
    while IFS= read -r line; do
        [[ "${line}" == *HDMI* ]] && continue
        if [[ "${line}" =~ card[[:space:]]+([0-9]+):.*device[[:space:]]+([0-9]+): ]]; then
            card="${BASH_REMATCH[1]}"
            device="${BASH_REMATCH[2]}"
            printf 'plughw:%s,%s\n' "${card}" "${device}"
        fi
    done
}

voice_dictation_inactive() {
    VOICE_DICTATION_INACTIVE_REASON="$1"
    if [[ "${VOICE_DICTATION_PRINT_REASON:-0}" == "1" ]]; then
        printf '%s\n' "${VOICE_DICTATION_INACTIVE_REASON}" >&2
    fi
}

voice_dictation_probe_capture_device() {
    local device="$1"
    local seconds="${DICTATE_PROBE_SECONDS:-1}"
    command -v arecord >/dev/null 2>&1 || return 127
    timeout 4 arecord -q -D "${device}" -f S16_LE -r 16000 -c 1 -d "${seconds}" /dev/null >/dev/null 2>&1
}

voice_dictation_choose_alsa_device() {
    VOICE_DICTATION_INACTIVE_REASON=""

    if ! command -v arecord >/dev/null 2>&1; then
        voice_dictation_inactive "missing alsa-utils"
        return 3
    fi

    if [[ -n "${DICTATE_DEVICE_ALSA:-}" ]]; then
        if voice_dictation_probe_capture_device "${DICTATE_DEVICE_ALSA}"; then
            printf '%s\n' "${DICTATE_DEVICE_ALSA}"
            return 0
        fi
        voice_dictation_inactive "explicit device unusable: ${DICTATE_DEVICE_ALSA}"
        return 3
    fi

    local list devices device
    list="$(arecord -l 2>/dev/null || true)"
    devices="$(voice_dictation_capture_devices_from_arecord <<< "${list}")"
    while IFS= read -r device; do
        [[ -n "${device}" ]] || continue
        if voice_dictation_probe_capture_device "${device}"; then
            printf '%s\n' "${device}"
            return 0
        fi
    done <<< "${devices}"

    voice_dictation_inactive "no usable capture device"
    return 3
}

voice_dictation_main() {
    case "${1:-}" in
        --choose)
            local device
            if device="$(VOICE_DICTATION_PRINT_REASON=1 voice_dictation_choose_alsa_device)"; then
                printf '%s\n' "${device}"
                return 0
            fi
            return 3
            ;;
        *)
            printf 'usage: %s --choose\n' "$0" >&2
            return 2
            ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    voice_dictation_main "$@"
fi
