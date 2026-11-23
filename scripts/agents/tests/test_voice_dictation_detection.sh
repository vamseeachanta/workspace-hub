#!/usr/bin/env bash
# TDD -- #3403 voice dictation rollout, capture-device selection, and VNC text-injection contract.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel)"
BASH_BIN="$(command -v bash)"
HELPER="${REPO_ROOT}/scripts/agents/lib/voice-dictation-detect.sh"
INSTALLER="${REPO_ROOT}/scripts/agents/install-voice-dictation.sh"
LAUNCHER="${REPO_ROOT}/tools/voice-dictation/codex-dictate.sh"
DICTATE_TEST="${REPO_ROOT}/tools/voice-dictation/dictate-test.sh"
TRANSCRIBE="${REPO_ROOT}/tools/voice-dictation/transcribe.py"
BOOTSTRAP="${REPO_ROOT}/scripts/memory/bootstrap-machine.sh"

fail=0
tmpdirs=()

record_fail() {
    echo "  FAIL: $1"
    fail=$((fail + 1))
}

pass() {
    echo "  PASS: $1"
}

assert_eq() {
    local name="$1" actual="$2" expected="$3"
    if [[ "${actual}" == "${expected}" ]]; then pass "${name}"; else record_fail "${name} (got '${actual}', expected '${expected}')"; fi
}

assert_contains() {
    local name="$1" haystack="$2" needle="$3"
    if [[ "${haystack}" == *"${needle}"* ]]; then pass "${name}"; else record_fail "${name} (missing '${needle}')"; fi
}

assert_file_contains() {
    local name="$1" file="$2" needle="$3"
    if [[ -f "${file}" ]] && grep -Fq -- "${needle}" "${file}"; then pass "${name}"; else record_fail "${name} (missing '${needle}' in ${file})"; fi
}

assert_file_not_contains() {
    local name="$1" file="$2" needle="$3"
    if [[ -f "${file}" ]] && ! grep -Fq -- "${needle}" "${file}"; then pass "${name}"; else record_fail "${name} (unexpected '${needle}' in ${file})"; fi
}

make_tmp() {
    local out_var="$1" d
    d="$(mktemp -d)"
    tmpdirs+=("${d}")
    printf -v "${out_var}" '%s' "${d}"
}

cleanup() {
    local d
    for d in "${tmpdirs[@]}"; do
        rm -rf "${d}"
    done
}
trap cleanup EXIT

write_plantronics_fixture() {
    cat > "$1" <<'EOF'
card 0: NVidia [HDA NVidia], device 3: HDMI 0 [HDMI 0]
card 1: Seri [Plantronics Blackwire 3220 Seri], device 0: USB Audio [USB Audio]
EOF
}

write_no_capture_fixture() {
    cat > "$1" <<'EOF'
arecord: device_list:274: no soundcards found...
EOF
}

install_stubs() {
    local bin="$1"
    mkdir -p "${bin}"
    ln -s "${BASH_BIN}" "${bin}/bash"
    ln -s "$(command -v cat)" "${bin}/cat"
    ln -s "$(command -v mktemp)" "${bin}/mktemp"
    ln -s "$(command -v rm)" "${bin}/rm"
    ln -s "$(command -v sed)" "${bin}/sed"
    cat > "${bin}/arecord" <<'EOF'
#!/usr/bin/env bash
set -u
if [[ "${1:-}" == "-l" ]]; then
    cat "${ARECORD_LIST_FILE:?}"
    exit 0
fi
device=""
duration=""
out=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        -D) device="$2"; shift 2 ;;
        -d) duration="$2"; shift 2 ;;
        -q|-f|-r|-c) shift; [[ $# -gt 0 && "$1" != -* ]] && shift ;;
        *) out="$1"; shift ;;
    esac
done
printf '%s\n' "${device}" >> "${ARECORD_LOG:?}"
case " ${ARECORD_FAIL_DEVICES:-} " in
    *" ${device} "*) echo "audio open error" >&2; exit 1 ;;
esac
[[ -n "${out}" && "${out}" != "/dev/null" ]] && printf 'RIFFstub' > "${out}"
if [[ -n "${duration}" ]]; then
    exit 0
fi
trap 'exit 0' TERM INT
while :; do sleep 1; done
EOF
    chmod +x "${bin}/arecord"

    cat > "${bin}/uname" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' Linux
EOF
    chmod +x "${bin}/uname"

    cat > "${bin}/timeout" <<'EOF'
#!/usr/bin/env bash
shift
exec "$@"
EOF
    chmod +x "${bin}/timeout"

    cat > "${bin}/gsettings" <<'EOF'
#!/usr/bin/env bash
set -u
printf '%s\n' "$*" >> "${GSETTINGS_LOG:?}"
cmd="${1:-}"; schema="${2:-}"; key="${3:-}"; value="${4:-}"
case "${cmd}" in
    writable)
        printf '%s\n' "${GSETTINGS_WRITABLE:-true}"
        exit 0
        ;;
    get)
        if [[ "${key}" == "custom-keybindings" ]]; then
            printf '%s\n' "${GSETTINGS_CUSTOM_LIST:-@as []}"
        elif [[ "${key}" == "command" ]]; then
            printf "'%s'\n" "${GSETTINGS_EXISTING_COMMAND:-}"
        elif [[ "${key}" == "name" ]]; then
            printf "'%s'\n" "${GSETTINGS_EXISTING_NAME:-}"
        else
            printf "''\n"
        fi
        ;;
    set)
        printf 'set|%s|%s|%s\n' "${schema}" "${key}" "${value}" >> "${GSETTINGS_SET_LOG:?}"
        ;;
esac
EOF
    chmod +x "${bin}/gsettings"

    cat > "${bin}/python-fast" <<'EOF'
#!/usr/bin/env bash
if [[ "${1:-}" == "-c" ]]; then
    case "${PYTHON_IMPORT_FAIL:-0}" in 1) exit 1 ;; *) exit 0 ;; esac
fi
echo "stub transcript"
EOF
    chmod +x "${bin}/python-fast"

    for tool in notify-send logger xdotool wtype ydotool; do
        cat > "${bin}/${tool}" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$0 $*" >> "${TOOL_LOG:?}"
EOF
        chmod +x "${bin}/${tool}"
    done
}

run_helper_choose() {
    local tmp="$1"
    PATH="${tmp}/bin:${PATH}" \
    ARECORD_LIST_FILE="${tmp}/arecord-l.txt" \
    ARECORD_LOG="${tmp}/arecord.log" \
    ARECORD_FAIL_DEVICES="${ARECORD_FAIL_DEVICES:-}" \
    DICTATE_PROBE_SECONDS=0 \
    "${BASH_BIN}" "${HELPER}" --choose 2>"${tmp}/choose.err"
}

test_detects_plantronics_capture_device() {
    local tmp out
    make_tmp tmp; install_stubs "${tmp}/bin"; write_plantronics_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"
    # shellcheck source=/dev/null
    source "${HELPER}"
    out="$(voice_dictation_capture_devices_from_arecord < "${tmp}/arecord-l.txt")"
    assert_contains "detects Plantronics capture device" "${out}" "plughw:1,0"
}

test_missing_arecord_returns_inactive() {
    local tmp out rc
    make_tmp tmp; mkdir -p "${tmp}/bin"; : > "${tmp}/arecord-l.txt"
    out="$(PATH="${tmp}/bin" "${BASH_BIN}" "${HELPER}" --choose 2>"${tmp}/err")"; rc=$?
    [[ "${rc}" -eq 3 && -z "${out}" ]] && pass "missing arecord exits inactive" || record_fail "missing arecord exits inactive"
    assert_file_contains "missing arecord reason" "${tmp}/err" "missing alsa-utils"
}

test_selection_policy() {
    local tmp out rc
    make_tmp tmp; install_stubs "${tmp}/bin"; write_plantronics_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"
    out="$(run_helper_choose "${tmp}")"; rc=$?
    [[ "${rc}" -eq 0 ]] && assert_eq "helper choose prints usable device" "${out}" "plughw:1,0" || record_fail "helper choose exits 0"

    out="$(ARECORD_FAIL_DEVICES="plughw:1,0" run_helper_choose "${tmp}")"; rc=$?
    [[ "${rc}" -eq 3 ]] && pass "unusable listed device is inactive" || record_fail "unusable listed device is inactive"

    out="$(PATH="${tmp}/bin:${PATH}" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" DICTATE_DEVICE_ALSA=hw:2,0 "${BASH_BIN}" "${HELPER}" --choose 2>"${tmp}/explicit.err")"; rc=$?
    [[ "${rc}" -eq 0 ]] && assert_eq "explicit usable device wins" "${out}" "hw:2,0" || record_fail "explicit usable device wins"

    out="$(PATH="${tmp}/bin:${PATH}" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" ARECORD_FAIL_DEVICES="hw:9,9" DICTATE_DEVICE_ALSA=hw:9,9 "${BASH_BIN}" "${HELPER}" --choose 2>"${tmp}/bad-explicit.err")"; rc=$?
    [[ "${rc}" -eq 3 ]] && pass "explicit unusable device inactive" || record_fail "explicit unusable device inactive"
    assert_file_contains "explicit unusable reason" "${tmp}/bad-explicit.err" "explicit device unusable"
}

test_no_capture_device_returns_inactive() {
    local tmp rc
    make_tmp tmp; install_stubs "${tmp}/bin"; write_no_capture_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"
    run_helper_choose "${tmp}" >/dev/null; rc=$?
    [[ "${rc}" -eq 3 ]] && pass "no capture device inactive" || record_fail "no capture device inactive"
    assert_file_contains "no capture reason" "${tmp}/choose.err" "no usable capture device"
}

run_installer() {
    local tmp="$1"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" \
    GSETTINGS_LOG="${tmp}/gsettings.log" GSETTINGS_SET_LOG="${tmp}/gsettings-set.log" TOOL_LOG="${tmp}/tool.log" \
    DBUS_SESSION_BUS_ADDRESS="unix:path=${tmp}/bus" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_PROBE_SECONDS=0 \
    VOICE_DICTATION_INSTALL_ROOT="${REPO_ROOT}" "${BASH_BIN}" "${INSTALLER}" >"${tmp}/installer.out" 2>"${tmp}/installer.err"
}

run_stored_hotkey_command() {
    local tmp="$1" command_line="$2"
    env -i HOME="${tmp}/home" PATH="${tmp}/bin:/usr/bin:/bin" XDG_RUNTIME_DIR="${tmp}/runtime" \
        ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" \
        "${BASH_BIN}" -c "${command_line}"
}

test_installer_active_contract() {
    local tmp command_line pid
    make_tmp tmp; mkdir -p "${tmp}/home/.local/share" "${tmp}/home/.local/bin"; install_stubs "${tmp}/bin"; write_plantronics_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"; : > "${tmp}/gsettings.log"; : > "${tmp}/gsettings-set.log"; : > "${tmp}/tool.log"
    mkdir -p "${tmp}/home/.local/share/voice-dictation"; echo sentinel > "${tmp}/home/.local/share/voice-dictation/sentinel.txt"
    run_installer "${tmp}"
    [[ -L "${tmp}/home/.local/share/voice-dictation" ]] && pass "installer creates share symlink" || record_fail "installer creates share symlink"
    compgen -G "${tmp}/home/.local/share/voice-dictation.backup-*/*" >/dev/null && pass "real share dir backed up" || record_fail "real share dir backed up"
    assert_file_contains "active binding path used" "${tmp}/gsettings-set.log" "/custom-keybindings/codex-dictate/"
    assert_file_contains "active command carries ALSA device" "${tmp}/gsettings-set.log" "DICTATE_DEVICE_ALSA=plughw:1,0"
    assert_file_contains "active command carries Python" "${tmp}/gsettings-set.log" "DICTATE_PYTHON=${tmp}/bin/python-fast"
    command_line="$(awk -F'|' '$3 == "command" {print $4}' "${tmp}/gsettings-set.log" | tail -1)"
    [[ "${command_line}" != *"~"* && "${command_line}" == *"${tmp}/home/.local/share/voice-dictation/codex-dictate.sh"* ]] && pass "active command stores absolute launcher path" || record_fail "active command stores absolute launcher path"
    mkdir -p "${tmp}/runtime"
    : > "${tmp}/arecord.log"
    run_stored_hotkey_command "${tmp}" "${command_line}" >/dev/null 2>&1
    assert_file_contains "active hotkey command executes" "${tmp}/arecord.log" "plughw:1,0"
    pid="$(cat "${tmp}/runtime/codex-dictate/arecord.pid" 2>/dev/null || true)"; [[ -n "${pid}" ]] && kill "${pid}" 2>/dev/null || true
}

test_inactive_install_preserves_real_share_and_inerts_existing_hotkey() {
    local tmp inert_command
    make_tmp tmp; mkdir -p "${tmp}/home/.local/share/voice-dictation" "${tmp}/home/.local/bin"; install_stubs "${tmp}/bin"; write_no_capture_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"; : > "${tmp}/gsettings.log"; : > "${tmp}/gsettings-set.log"; : > "${tmp}/tool.log"
    echo sentinel > "${tmp}/home/.local/share/voice-dictation/sentinel.txt"
    GSETTINGS_CUSTOM_LIST="['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/']" run_installer "${tmp}"
    [[ -f "${tmp}/home/.local/share/voice-dictation/sentinel.txt" && ! -L "${tmp}/home/.local/share/voice-dictation" ]] && pass "inactive install preserves real share dir" || record_fail "inactive install preserves real share dir"
    assert_file_contains "inactive hotkey writes warning command" "${tmp}/gsettings-set.log" "Voice dictation inactive"
    assert_file_contains "inactive hotkey avoids launcher" "${tmp}/gsettings-set.log" "notify-send"
    inert_command="$(awk -F'|' '$3 == "command" {print $4}' "${tmp}/gsettings-set.log" | tail -1)"
    mkdir -p "${tmp}/runtime"
    run_stored_hotkey_command "${tmp}" "${inert_command}" >/dev/null 2>&1
    assert_file_contains "inert warning command executes" "${tmp}/tool.log" "notify-send"
    assert_file_contains "inert warning body is unescaped" "${tmp}/tool.log" "dictate Voice dictation inactive"
    assert_file_not_contains "inert warning body lacks escape prefix" "${tmp}/tool.log" "\\Voice dictation inactive"
}

test_installer_skips_unwritable_gsettings() {
    local tmp
    make_tmp tmp; mkdir -p "${tmp}/home/.local/share" "${tmp}/home/.local/bin"; install_stubs "${tmp}/bin"; write_plantronics_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"; : > "${tmp}/gsettings.log"; : > "${tmp}/gsettings-set.log"; : > "${tmp}/tool.log"
    GSETTINGS_WRITABLE=false run_installer "${tmp}"
    [[ ! -s "${tmp}/gsettings-set.log" ]] && pass "unwritable gsettings skips hotkey mutation" || record_fail "unwritable gsettings skips hotkey mutation"
    assert_file_contains "unwritable gsettings prints manual binding" "${tmp}/installer.out" "bind manually"
}

test_launcher_and_dictate_test_use_selected_device() {
    local tmp pid fallback_state mode uid
    make_tmp tmp; mkdir -p "${tmp}/home" "${tmp}/runtime" "${tmp}/tmp-root"; install_stubs "${tmp}/bin"; write_plantronics_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"; : > "${tmp}/tool.log"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" XDG_RUNTIME_DIR="${tmp}/runtime" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_DEVICE_ALSA=plughw:2,0 "${BASH_BIN}" "${LAUNCHER}" >/dev/null 2>&1
    assert_file_contains "launcher uses selected ALSA device" "${tmp}/arecord.log" "plughw:2,0"
    pid="$(cat "${tmp}/runtime/codex-dictate/arecord.pid" 2>/dev/null || true)"; [[ -n "${pid}" ]] && kill "${pid}" 2>/dev/null || true

    uid="$(id -u)"
    : > "${tmp}/arecord.log"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" TMPDIR="${tmp}/tmp-root" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_DEVICE_ALSA=plughw:4,0 "${BASH_BIN}" "${LAUNCHER}" >/dev/null 2>&1
    fallback_state="${tmp}/tmp-root/codex-dictate-${uid}"
    mode="$(stat -c '%a' "${fallback_state}" 2>/dev/null || true)"
    assert_eq "launcher fallback state dir mode" "${mode}" "700"
    assert_file_contains "launcher fallback uses selected ALSA device" "${tmp}/arecord.log" "plughw:4,0"
    pid="$(cat "${fallback_state}/arecord.pid" 2>/dev/null || true)"; [[ -n "${pid}" ]] && kill "${pid}" 2>/dev/null || true

    : > "${tmp}/arecord.log"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" XDG_RUNTIME_DIR="${tmp}/runtime" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" DICTATE_PYTHON="${tmp}/bin/python-fast" "${BASH_BIN}" "${DICTATE_TEST}" 5 plughw:3,0 >/dev/null 2>&1
    assert_file_contains "dictate-test uses selected ALSA argument" "${tmp}/arecord.log" "plughw:3,0"

    rm -rf "${fallback_state}"
    : > "${tmp}/arecord.log"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" TMPDIR="${tmp}/tmp-root" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" DICTATE_PYTHON="${tmp}/bin/python-fast" "${BASH_BIN}" "${DICTATE_TEST}" 5 plughw:5,0 >/dev/null 2>&1
    mode="$(stat -c '%a' "${fallback_state}" 2>/dev/null || true)"
    assert_eq "dictate-test fallback state dir mode" "${mode}" "700"
    assert_file_contains "dictate-test fallback uses selected ALSA argument" "${tmp}/arecord.log" "plughw:5,0"
}

test_launcher_stop_and_fallback_contracts() {
    local tmp sleeper pid lock_holder
    make_tmp tmp; mkdir -p "${tmp}/home" "${tmp}/runtime/codex-dictate"; install_stubs "${tmp}/bin"; write_plantronics_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"; : > "${tmp}/tool.log"
    if command -v flock >/dev/null 2>&1; then
        (flock -n 200 && sleep 5) 200>"${tmp}/runtime/codex-dictate/toggle.lock" &
        lock_holder=$!
        sleep 0.1
        HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" XDG_RUNTIME_DIR="${tmp}/runtime" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_DEVICE_ALSA=plughw:2,0 "${BASH_BIN}" "${LAUNCHER}" >/dev/null 2>&1
        [[ ! -s "${tmp}/arecord.log" ]] && pass "held toggle lock prevents second recorder" || record_fail "held toggle lock prevents second recorder"
        assert_file_contains "held toggle lock notifies busy" "${tmp}/tool.log" "dictation busy"
        kill "${lock_holder}" 2>/dev/null || true
        wait "${lock_holder}" 2>/dev/null || true
        : > "${tmp}/tool.log"
    fi

    sleep 60 & sleeper=$!
    echo "${sleeper}" > "${tmp}/runtime/codex-dictate/arecord.pid"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" XDG_RUNTIME_DIR="${tmp}/runtime" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" ARECORD_FAIL_DEVICES="plughw:9,9 plughw:1,0" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_DEVICE_ALSA=plughw:9,9 "${BASH_BIN}" "${LAUNCHER}" >/dev/null 2>&1
    kill -0 "${sleeper}" 2>/dev/null && pass "stale unrelated pid is not killed" || record_fail "stale unrelated pid is not killed"
    kill "${sleeper}" 2>/dev/null || true

    sleep 60 & sleeper=$!
    echo "${sleeper}" > "${tmp}/runtime/codex-dictate/arecord.pid"
    {
        printf 'pid=%s\n' "${sleeper}"
        printf 'device=%s\n' "plughw:9,9"
        printf 'wav=%s\n' "${tmp}/runtime/codex-dictate/rec.wav"
    } > "${tmp}/runtime/codex-dictate/arecord.meta"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" XDG_RUNTIME_DIR="${tmp}/runtime" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" ARECORD_FAIL_DEVICES="plughw:9,9 plughw:1,0" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_DEVICE_ALSA=plughw:9,9 "${BASH_BIN}" "${LAUNCHER}" >/dev/null 2>&1
    kill -0 "${sleeper}" 2>/dev/null && pass "matching stale meta still does not kill non-arecord pid" || record_fail "matching stale meta still does not kill non-arecord pid"
    kill "${sleeper}" 2>/dev/null || true

    : > "${tmp}/arecord.log"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" XDG_RUNTIME_DIR="${tmp}/runtime" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_DEVICE_ALSA=plughw:2,0 "${BASH_BIN}" "${LAUNCHER}" >/dev/null 2>&1
    pid="$(cat "${tmp}/runtime/codex-dictate/arecord.pid" 2>/dev/null || true)"
    : > "${tmp}/arecord.log"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" XDG_RUNTIME_DIR="${tmp}/runtime" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_DEVICE_ALSA=plughw:9,9 "${BASH_BIN}" "${LAUNCHER}" >/dev/null 2>&1
    for _ in 1 2 3 4 5 6 7 8 9 10; do
        [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null || break
        sleep 0.05
    done
    [[ -n "${pid}" ]] && ! kill -0 "${pid}" 2>/dev/null && pass "owned recording is stopped" || record_fail "owned recording is stopped"
    [[ ! -s "${tmp}/arecord.log" ]] && pass "owned stop branch runs before device detection" || record_fail "owned stop branch runs before device detection"

    : > "${tmp}/arecord.log"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" XDG_RUNTIME_DIR="${tmp}/runtime" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" ARECORD_FAIL_DEVICES="plughw:9,9" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_DEVICE_ALSA=plughw:9,9 "${BASH_BIN}" "${LAUNCHER}" >/dev/null 2>&1
    assert_file_contains "launcher retries auto device after stale bound device" "${tmp}/arecord.log" "plughw:1,0"
    pid="$(cat "${tmp}/runtime/codex-dictate/arecord.pid" 2>/dev/null || true)"; [[ -n "${pid}" ]] && kill "${pid}" 2>/dev/null || true
}

if [[ "${VOICE_DICTATION_TEST_SOURCE_ONLY:-0}" == "1" ]]; then
    return 0 2>/dev/null || exit 0
fi

test_detects_plantronics_capture_device
test_missing_arecord_returns_inactive
test_selection_policy
test_no_capture_device_returns_inactive
test_installer_active_contract
test_inactive_install_preserves_real_share_and_inerts_existing_hotkey
test_installer_skips_unwritable_gsettings
test_launcher_and_dictate_test_use_selected_device
test_launcher_stop_and_fallback_contracts

companion="${SCRIPT_DIR}/test_voice_dictation_static_contracts.sh"
if [[ "${VOICE_DICTATION_RUN_COMPANION:-1}" == "1" && -x "${companion}" ]]; then
    "${BASH_BIN}" "${companion}" || record_fail "voice dictation companion tests"
fi

echo "---"
if [[ "${fail}" -gt 0 ]]; then
    echo "FAILED: ${fail} check(s)"
    exit 1
fi
echo "ALL PASS"
