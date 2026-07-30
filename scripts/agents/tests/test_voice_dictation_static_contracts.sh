#!/usr/bin/env bash
# Edge-case and static-contract tests for #3403 voice dictation.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VOICE_DICTATION_TEST_SOURCE_ONLY=1 source "${SCRIPT_DIR}/test_voice_dictation_detection.sh"

test_installer_guards_install_root_and_tool_source() {
    local tmp
    make_tmp tmp; mkdir -p "${tmp}/home/.local/share" "${tmp}/home/.local/bin" "${tmp}/empty-root"; install_stubs "${tmp}/bin"; write_plantronics_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"; : > "${tmp}/gsettings.log"; : > "${tmp}/gsettings-set.log"; : > "${tmp}/tool.log"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" VOICE_DICTATION_INSTALL_ROOT="${tmp}/missing-root" "${BASH_BIN}" "${INSTALLER}" >"${tmp}/missing-root.out" 2>"${tmp}/missing-root.err"
    assert_file_contains "bad install root prints accurate reason" "${tmp}/missing-root.out" "VOICE_DICTATION_INSTALL_ROOT does not exist"

    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" \
    GSETTINGS_LOG="${tmp}/gsettings.log" GSETTINGS_SET_LOG="${tmp}/gsettings-set.log" TOOL_LOG="${tmp}/tool.log" \
    DBUS_SESSION_BUS_ADDRESS="unix:path=${tmp}/bus" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_PROBE_SECONDS=0 \
    VOICE_DICTATION_INSTALL_ROOT="${tmp}/empty-root" "${BASH_BIN}" "${INSTALLER}" >"${tmp}/missing-source.out" 2>"${tmp}/missing-source.err"
    [[ ! -L "${tmp}/home/.local/share/voice-dictation" ]] && pass "missing tool source does not create share symlink" || record_fail "missing tool source does not create share symlink"
    assert_file_contains "missing tool source prints inactive reason" "${tmp}/missing-source.out" "tool source missing executable"
}

test_installer_non_linux_noops() {
    local tmp
    make_tmp tmp; mkdir -p "${tmp}/home" "${tmp}/bin"; install_stubs "${tmp}/bin"
    cat > "${tmp}/bin/uname" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' Darwin
STUB
    chmod +x "${tmp}/bin/uname"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" "${BASH_BIN}" "${INSTALLER}" >"${tmp}/out" 2>"${tmp}/err"
    [[ ! -e "${tmp}/home/.local/share/voice-dictation" ]] && pass "non-Linux installer does not mutate home" || record_fail "non-Linux installer does not mutate home"
    assert_file_contains "non-Linux skip guidance" "${tmp}/out" "Linux-only"
}

test_missing_python_and_text_injector_guidance() {
    local tmp before after
    make_tmp tmp; mkdir -p "${tmp}/home" "${tmp}/bin"; install_stubs "${tmp}/bin"; write_plantronics_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"; : > "${tmp}/gsettings.log"; : > "${tmp}/gsettings-set.log"; : > "${tmp}/tool.log"
    rm -f "${tmp}/bin/python-fast" "${tmp}/bin/xdotool" "${tmp}/bin/wtype" "${tmp}/bin/ydotool"
    before="$(sha256sum "${REPO_ROOT}/tools/voice-dictation/README.md" 2>/dev/null || true)"
    HOME="${tmp}/home" PATH="${tmp}/bin" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" GSETTINGS_LOG="${tmp}/gsettings.log" GSETTINGS_SET_LOG="${tmp}/gsettings-set.log" "${BASH_BIN}" "${INSTALLER}" >"${tmp}/out" 2>"${tmp}/err"
    after="$(sha256sum "${REPO_ROOT}/tools/voice-dictation/README.md" 2>/dev/null || true)"
    assert_file_contains "missing Python guidance" "${tmp}/out" "faster-whisper"
    assert_file_contains "missing injector warning" "${tmp}/out" "no text injector"
    assert_eq "installer does not mutate README" "${after}" "${before}"
}

test_wayland_prefers_ydotool_over_xdotool() {
    local tmp pid
    make_tmp tmp; mkdir -p "${tmp}/home" "${tmp}/runtime"; install_stubs "${tmp}/bin"; write_plantronics_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"; : > "${tmp}/tool.log"; rm -f "${tmp}/bin/wtype"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" XDG_RUNTIME_DIR="${tmp}/runtime" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_DEVICE_ALSA=plughw:6,0 "${BASH_BIN}" "${LAUNCHER}" >/dev/null 2>&1
    pid="$(cat "${tmp}/runtime/codex-dictate/arecord.pid" 2>/dev/null || true)"
    HOME="${tmp}/home" PATH="${tmp}/bin:${PATH}" WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR="${tmp}/runtime" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" DICTATE_PYTHON="${tmp}/bin/python-fast" DICTATE_DEVICE_ALSA=plughw:6,0 "${BASH_BIN}" "${LAUNCHER}" >/dev/null 2>&1
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
        kill "${pid}" 2>/dev/null || true
    fi
    assert_file_contains "Wayland ydotool preferred over xdotool" "${tmp}/tool.log" "ydotool type -- stub transcript"
    assert_file_not_contains "Wayland does not choose xdotool before ydotool" "${tmp}/tool.log" "xdotool type"
}

test_hotkey_command_round_trips_apostrophes() {
    local tmp home_q py_q command_line pid
    make_tmp tmp; install_stubs "${tmp}/bin"; write_plantronics_fixture "${tmp}/arecord-l.txt"; : > "${tmp}/arecord.log"; : > "${tmp}/gsettings.log"; : > "${tmp}/gsettings-set.log"; : > "${tmp}/tool.log"
    home_q="${tmp}/home with 'quote"
    py_q="${tmp}/py 'dir/python-fast"
    mkdir -p "${home_q}/.local/share" "${home_q}/.local/bin" "${py_q%/*}" "${tmp}/runtime"
    ln -s "${tmp}/bin/python-fast" "${py_q}"

    HOME="${home_q}" PATH="${tmp}/bin:${PATH}" ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" \
    GSETTINGS_LOG="${tmp}/gsettings.log" GSETTINGS_SET_LOG="${tmp}/gsettings-set.log" TOOL_LOG="${tmp}/tool.log" \
    DBUS_SESSION_BUS_ADDRESS="unix:path=${tmp}/bus" DICTATE_PYTHON="${py_q}" DICTATE_PROBE_SECONDS=0 \
    VOICE_DICTATION_INSTALL_ROOT="${REPO_ROOT}" "${BASH_BIN}" "${INSTALLER}" >"${tmp}/installer.out" 2>"${tmp}/installer.err"

    command_line="$(awk -F'|' '$3 == "command" {print $4}' "${tmp}/gsettings-set.log" | tail -1)"
    env -i HOME="${home_q}" PATH="${tmp}/bin:/usr/bin:/bin" XDG_RUNTIME_DIR="${tmp}/runtime" \
        ARECORD_LIST_FILE="${tmp}/arecord-l.txt" ARECORD_LOG="${tmp}/arecord.log" TOOL_LOG="${tmp}/tool.log" \
        "${BASH_BIN}" -c "${command_line}" >/dev/null 2>&1
    assert_file_contains "apostrophe hotkey command executes" "${tmp}/arecord.log" "plughw:1,0"
    pid="$(cat "${tmp}/runtime/codex-dictate/arecord.pid" 2>/dev/null || true)"
    [[ -n "${pid}" ]] && kill "${pid}" 2>/dev/null || true
}

test_static_contracts() {
    local mode path
    for path in \
        scripts/agents/lib/voice-dictation-detect.sh \
        scripts/agents/install-voice-dictation.sh \
        tools/voice-dictation/codex-dictate.sh \
        tools/voice-dictation/dictate-test.sh \
        tools/voice-dictation/transcribe.py \
        scripts/agents/tests/test_voice_dictation_detection.sh \
        scripts/agents/tests/test_voice_dictation_static_contracts.sh; do
        mode="$(git -C "${REPO_ROOT}" ls-files -s "${path}" | awk '{print $1}')"
        [[ "${mode}" == "100755" ]] && pass "committed executable mode for ${path}" || record_fail "committed executable mode for ${path}"
    done
    [[ -f "${BOOTSTRAP}" ]] && grep -Fq 'bash "${VOICE_DICTATION_INSTALLER}" || true' "${BOOTSTRAP}" && pass "bootstrap hook is guarded" || record_fail "bootstrap hook is guarded"
    grep -Fq "resolve_install_root" "${INSTALLER}" && grep -Fq "worktree list --porcelain" "${INSTALLER}" && pass "installer resolves linked worktree root" || record_fail "installer resolves linked worktree root"
    git -C "${REPO_ROOT}" check-ignore -q tools/voice-dictation/__pycache__/transcribe.cpython-313.pyc && pass "pycache is gitignored" || record_fail "pycache is gitignored"
    bash -n "${HELPER}" "${INSTALLER}" "${LAUNCHER}" "${DICTATE_TEST}" "${BOOTSTRAP}" "$0" >/dev/null 2>&1 && pass "voice shell scripts parse" || record_fail "voice shell scripts parse"
    python3 -c "from pathlib import Path; p=Path('${TRANSCRIBE}'); compile(p.read_text(), str(p), 'exec')" >/dev/null 2>&1 && pass "transcribe.py compiles" || record_fail "transcribe.py compiles"
}

test_installer_guards_install_root_and_tool_source
test_installer_non_linux_noops
test_missing_python_and_text_injector_guidance
test_wayland_prefers_ydotool_over_xdotool
test_hotkey_command_round_trips_apostrophes
test_static_contracts

echo "---"
if [[ "${fail}" -gt 0 ]]; then
    echo "FAILED: ${fail} check(s)"
    exit 1
fi
echo "ALL PASS"
