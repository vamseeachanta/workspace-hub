# Plan for #3403: Repair Linux Voice Dictation Rollout and VNC Consistency Contract

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-07-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3403
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Review artifacts:** scripts/review/results/2026-07-08-plan-3403-claude-r1.md | scripts/review/results/2026-07-08-plan-3403-codex-r1.md | scripts/review/results/2026-07-08-plan-3403-gemini-r1.md | scripts/review/results/2026-07-08-plan-3403-disagreement-r1.md | scripts/review/results/2026-07-08-plan-3403-claude-r2.md | scripts/review/results/2026-07-08-plan-3403-codex-r2.md | scripts/review/results/2026-07-08-plan-3403-gemini-r2.md | scripts/review/results/2026-07-08-plan-3403-disagreement-r2.md | scripts/review/results/2026-07-08-plan-3403-claude-r3.md | scripts/review/results/2026-07-08-plan-3403-codex-r3.md | scripts/review/results/2026-07-08-plan-3403-gemini-r3.md | scripts/review/results/2026-07-08-plan-3403-disagreement-r3.md | scripts/review/results/2026-07-08-plan-3403-claude-r4.md | scripts/review/results/2026-07-08-plan-3403-codex-r4.md | scripts/review/results/2026-07-08-plan-3403-gemini-r4.md | scripts/review/results/2026-07-08-plan-3403-disagreement-r4.md | scripts/review/results/2026-07-08-plan-3403-claude-r5.md | scripts/review/results/2026-07-08-plan-3403-codex-r5.md | scripts/review/results/2026-07-08-plan-3403-gemini-r5.md | scripts/review/results/2026-07-08-plan-3403-disagreement-r5.md | scripts/review/results/2026-07-08-plan-3403-claude-r6.md | scripts/review/results/2026-07-08-plan-3403-codex-r6.md | scripts/review/results/2026-07-08-plan-3403-gemini-r6.md | scripts/review/results/2026-07-08-plan-3403-disagreement-r6.md | scripts/review/results/2026-07-08-plan-3403-claude-r7.md | scripts/review/results/2026-07-08-plan-3403-codex-r7.md | scripts/review/results/2026-07-08-plan-3403-gemini-r7.md | scripts/review/results/2026-07-08-plan-3403-disagreement-r7.md | scripts/review/results/2026-07-08-plan-3403-claude-r8.md | scripts/review/results/2026-07-08-plan-3403-codex-r8.md | scripts/review/results/2026-07-08-plan-3403-gemini-r8.md | scripts/review/results/2026-07-08-plan-3403-disagreement-r8.md
> **Review artifacts (final r9):** scripts/review/results/2026-07-08-plan-3403-claude-r9.md | scripts/review/results/2026-07-08-plan-3403-codex-r9.md | scripts/review/results/2026-07-08-plan-3403-gemini-r9.md | scripts/review/results/2026-07-08-plan-3403-disagreement-r9.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: local branch `feat/voice-dictation-ecosystem` contains the previous implementation source:
  `tools/voice-dictation/README.md`, `tools/voice-dictation/codex-dictate.sh`,
  `tools/voice-dictation/dictate-test.sh`, `tools/voice-dictation/transcribe.py`, and
  `scripts/agents/install-voice-dictation.sh`.
- Found: local branch commit `97a5e4b86` added the original free/local stack:
  `arecord` -> `faster-whisper` -> `xdotool`/`wtype`, plus a bootstrap hook.
- Found: local branch commit `1ee68f767` added a soundcard-less skip, but it checks for
  any sound card via `/proc/asound/cards`; live evidence shows this is insufficient because
  ace-linux-1 can have an HDMI sound card while `arecord default` still fails.
- Found: current `main` has no tracked voice-dictation source files. The ace-linux-1 working
  tree also has an ignored local `tools/voice-dictation/__pycache__/transcribe.cpython-313.pyc`
  residue, so the user-level symlink currently points at a source directory without the launcher.
- Found: `scripts/memory/bootstrap-machine.sh` currently stops at section 2.10
  (`set-antigravity-default-model.sh`) before the Hermes memory reminder; the prior voice branch
  inserted the voice installer as section 2.11 there.
- Test-pattern fit: shell harness tests already exist under `scripts/agents/tests/` and
  `tests/setup/`; use that pattern for deterministic Bash tests of capture-device selection.
- Review finding incorporated: the implementation should not test these behaviors only through
  the full installer. It should put pure capture-device parsing/selection helpers in a small
  sourced shell library so tests can stub `arecord`, `gsettings`, `HOME`, and repo paths without
  recording audio or mutating the real user environment.
- Review finding incorporated: the helper should be dual-use. When sourced, it should define
  functions only. When executed with `--choose`, it should print a usable selected device to stdout
  and exit 0, or print a reason to stderr and exit non-zero when inactive.

### Standards

| Standard | Status | Source |
|---|---|---|
| Control-plane contract | applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md` says provider adapters must not contradict `AGENTS.md` and identifies `AGENTS.md` plus provider adapters as the canonical context surface. The voice tool should remain in repo-tracked harness code, with user-home symlinks as runtime adapters. |
| Legal/security scan | applicable | `AGENTS.md` requires `scripts/legal/legal-sanity-scan.sh`; this issue should run it because it adds shell/Python harness code. |
| TDD gate | applicable | `AGENTS.md` and `superpowers:test-driven-development` require tests before implementation. |

### LLM Wiki pages consulted

- No relevant LLM wiki pages. This is a workspace-hub harness/agent-UX issue, not domain knowledge.

### Documents consulted

- GitHub issue [#3403](https://github.com/vamseeachanta/workspace-hub/issues/3403) -- new implementation issue; carries `status:needs-plan`, `cat:harness`, `domain:agent-ux`, `machine:dev-primary`, and `lane:codex`.
- GitHub issue [#140](https://github.com/vamseeachanta/workspace-hub/issues/140) -- prior research issue; closed after Claude Code `/voice`, but comments identified `whisper.cpp`, `nerd-dictation`, and `faster-whisper`/WhisperLive options. This plan does not reopen that research track because the current gap is Codex/VNC/system-wide dictation.
- Branch handoff `docs/session-handoffs/2026-06-30-handoff-voice-dictation-ecosystem.md` on `feat/voice-dictation-ecosystem` -- records the working user model: dictate on ace-linux-1 and send text/keystrokes into focused VNC or SSH/tmux targets; do not bolt PipeWire-over-SSH onto TigerVNC for this workflow. Because this source is branch-only today, implementation should restore the handoff as a historical trace artifact so the cited evidence remains reachable after the branch is deleted.
- `docs/document-intelligence/README.md` -- consulted as the required intelligence entry point; no domain document intelligence applies beyond noting the drive-file index route.
- Drive-file index query `voice dictation VNC speech to text` -- returned unrelated CAD/text drawing hits and stale-index warnings for `og_standards_inventory` and `master_document_index`; no relevant drive files were identified for this harness issue.

### Gaps identified

- Current `main` lacks tracked source files for the installed voice-dictation symlink target.
- Current branch implementation does not distinguish "capture device exists but ALSA default is broken" from a healthy `default` device.
- Current branch implementation does not handle missing `arecord` before device detection; fresh Linux machines without `alsa-utils` need inactive/manual guidance instead of a bootstrap abort.
- Current branch implementation removes a pre-existing real `~/.local/share/voice-dictation` directory with `rm -rf`; the landed installer needs a non-destructive backup/skip contract instead.
- Current live GNOME state already has a `Super+Shift+V` binding. If a machine is inactive because no capture path is available, the installer must not leave that binding pointing at a failing launcher.
- The ace-linux-1 working tree has stale ignored `tools/voice-dictation/__pycache__/` residue; restoring source files should explicitly delete that local generated bytecode directory, while deterministic tests should rely on `.gitignore` coverage instead of machine-local residue.
- The installer needs deterministic tests for capture-device detection and inactive-machine behavior.
- The VNC contract needs to be stated in the repo-tracked README/installer output so future sessions do not reattempt microphone forwarding through TigerVNC.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-09T02:31:00Z via `gh issue view`):

- [#3403](https://github.com/vamseeachanta/workspace-hub/issues/3403) -- OPEN -- Repair Linux voice dictation rollout and VNC consistency contract; labels include `status:needs-plan`, `cat:harness`, `domain:agent-ux`, `machine:dev-primary`, `lane:codex`.
- [#140](https://github.com/vamseeachanta/workspace-hub/issues/140) -- CLOSED -- WRK-5030: Research speech-to-text tool similar to Whisper-flow for Linux.

**File existence** (`find`/`git ls-tree`, 2026-07-09T02:31:00Z):

```
current working-tree voice dir files:
tools/voice-dictation/__pycache__/transcribe.cpython-313.pyc 2665 bytes

current tracked voice files: none

branch voice files:
docs/session-handoffs/2026-06-30-handoff-voice-dictation-ecosystem.md
scripts/agents/install-voice-dictation.sh
tools/voice-dictation/README.md
tools/voice-dictation/codex-dictate.sh
tools/voice-dictation/dictate-test.sh
tools/voice-dictation/transcribe.py
```

**Hotkey and symlink state** (`ls`, `readlink`, `gsettings`, 2026-07-09T02:31:00Z):

```
/home/vamsee/.local/bin/codex-dictate -> /home/vamsee/.local/share/voice-dictation/codex-dictate.sh
/home/vamsee/.local/share/voice-dictation -> /mnt/local-analysis/workspace-hub/tools/voice-dictation
launcher target /mnt/local-analysis/workspace-hub/tools/voice-dictation/codex-dictate.sh: missing on current main
custom-keybindings ['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/']
keybinding path '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/'
binding '<Super><Shift>v'
command 'env DICTATE_PYTHON=/home/vamsee/miniforge3/bin/python3 bash /home/vamsee/.local/share/voice-dictation/codex-dictate.sh'
name 'Codex Voice Dictation'
```

**Audio reproduction proofs** (2026-07-09T02:31:00Z to 2026-07-09T02:34:00Z):

```
$ cat /proc/asound/cards
0 [NVidia         ]: HDA-Intel - HDA NVidia
1 [Seri           ]: USB-Audio - Plantronics Blackwire 3220 Seri

$ arecord -l
card 1: Seri [Plantronics Blackwire 3220 Seri], device 0: USB Audio [USB Audio]

$ timeout 3 arecord -q -D default -f S16_LE -r 16000 -c 1 -d 1 /tmp/plan3403_probe.wav
arecord default rc=1
arecord: main:834: audio open error: Host is down

$ timeout 4 arecord -q -D plughw:1,0 -f S16_LE -r 16000 -c 1 -d 1 /tmp/plan3403_usb_probe.wav
arecord plughw:1,0 rc=0
/tmp/plan3403_usb_probe.wav: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 16000 Hz
```

- Reproduced at: 2026-07-09T02:34:00Z
- Failure mode observed matches issue claim: PARTIAL -- the issue body captured an earlier no-visible-capture-device state, while this later live probe captured the second failure mode: Plantronics visible and concrete `plughw:1,0` working, but ALSA `default` broken. The implementation must cover both states.
- Refreshed at 2026-07-08T22:32:21-05:00 / 2026-07-09T03:32:21Z: `/proc/asound/cards` and `arecord -l` again showed Plantronics as card 1 device 0; `arecord -D default` again failed with `Host is down`; `arecord -D plughw:1,0` exited 0. The launcher file remained missing on current `main`, matching the tracked-source gap above.

**Drive-file index**:

```
$ scripts/data/drive-index-search/search.py "voice dictation VNC speech to text" --json --caller plan-resource-intel
WARNING: index og_standards_inventory is 193 days stale (threshold 90)
WARNING: index master_document_index is 83 days stale (threshold 60)
results: unrelated CAD/text drawing hits; no relevant harness/voice/VNC file.
```

Distinct source count: 7 (`#3403`, `#140`, branch handoff, branch source tree, live hotkey/audio probes, `docs/standards/CONTROL_PLANE_CONTRACT.md`, drive-file index).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md` |
| Plan index | `docs/plans/README.md` |
| Voice README | `tools/voice-dictation/README.md` |
| Push-to-talk launcher | `tools/voice-dictation/codex-dictate.sh` |
| Fixed-duration test launcher | `tools/voice-dictation/dictate-test.sh` |
| STT bridge | `tools/voice-dictation/transcribe.py` |
| Installer | `scripts/agents/install-voice-dictation.sh` |
| Capture-device helper library | `scripts/agents/lib/voice-dictation-detect.sh` |
| Bootstrap hook | `scripts/memory/bootstrap-machine.sh` |
| Detection tests | `scripts/agents/tests/test_voice_dictation_detection.sh` |
| Syntax/import verification | command-only, no persistent artifact |
| Historical handoff trace | `docs/session-handoffs/2026-06-30-handoff-voice-dictation-ecosystem.md` |
| Plan review -- Claude r1 | `scripts/review/results/2026-07-08-plan-3403-claude-r1.md` |
| Plan review -- Codex r1 | `scripts/review/results/2026-07-08-plan-3403-codex-r1.md` |
| Plan review -- Gemini r1 | `scripts/review/results/2026-07-08-plan-3403-gemini-r1.md` |
| Plan review -- disagreement r1 | `scripts/review/results/2026-07-08-plan-3403-disagreement-r1.md` |
| Plan review -- Claude r2 | `scripts/review/results/2026-07-08-plan-3403-claude-r2.md` |
| Plan review -- Codex r2 | `scripts/review/results/2026-07-08-plan-3403-codex-r2.md` |
| Plan review -- Gemini r2 | `scripts/review/results/2026-07-08-plan-3403-gemini-r2.md` |
| Plan review -- disagreement r2 | `scripts/review/results/2026-07-08-plan-3403-disagreement-r2.md` |
| Plan review -- Claude r3 | `scripts/review/results/2026-07-08-plan-3403-claude-r3.md` |
| Plan review -- Codex r3 | `scripts/review/results/2026-07-08-plan-3403-codex-r3.md` |
| Plan review -- Gemini r3 | `scripts/review/results/2026-07-08-plan-3403-gemini-r3.md` |
| Plan review -- disagreement r3 | `scripts/review/results/2026-07-08-plan-3403-disagreement-r3.md` |
| Plan review -- Claude r4 | `scripts/review/results/2026-07-08-plan-3403-claude-r4.md` |
| Plan review -- Codex r4 | `scripts/review/results/2026-07-08-plan-3403-codex-r4.md` |
| Plan review -- Gemini r4 | `scripts/review/results/2026-07-08-plan-3403-gemini-r4.md` |
| Plan review -- disagreement r4 | `scripts/review/results/2026-07-08-plan-3403-disagreement-r4.md` |
| Plan review -- Claude r5 | `scripts/review/results/2026-07-08-plan-3403-claude-r5.md` |
| Plan review -- Codex r5 | `scripts/review/results/2026-07-08-plan-3403-codex-r5.md` |
| Plan review -- Gemini r5 | `scripts/review/results/2026-07-08-plan-3403-gemini-r5.md` |
| Plan review -- disagreement r5 | `scripts/review/results/2026-07-08-plan-3403-disagreement-r5.md` |
| Plan review -- Claude r6 | `scripts/review/results/2026-07-08-plan-3403-claude-r6.md` |
| Plan review -- Codex r6 | `scripts/review/results/2026-07-08-plan-3403-codex-r6.md` |
| Plan review -- Gemini r6 | `scripts/review/results/2026-07-08-plan-3403-gemini-r6.md` |
| Plan review -- disagreement r6 | `scripts/review/results/2026-07-08-plan-3403-disagreement-r6.md` |
| Plan review -- Claude r7 | `scripts/review/results/2026-07-08-plan-3403-claude-r7.md` |
| Plan review -- Codex r7 | `scripts/review/results/2026-07-08-plan-3403-codex-r7.md` |
| Plan review -- Gemini r7 | `scripts/review/results/2026-07-08-plan-3403-gemini-r7.md` |
| Plan review -- disagreement r7 | `scripts/review/results/2026-07-08-plan-3403-disagreement-r7.md` |
| Plan review -- Claude r8 | `scripts/review/results/2026-07-08-plan-3403-claude-r8.md` |
| Plan review -- Codex r8 | `scripts/review/results/2026-07-08-plan-3403-codex-r8.md` |
| Plan review -- Gemini r8 | `scripts/review/results/2026-07-08-plan-3403-gemini-r8.md` |
| Plan review -- disagreement r8 | `scripts/review/results/2026-07-08-plan-3403-disagreement-r8.md` |
| Plan review -- Claude r9 | `scripts/review/results/2026-07-08-plan-3403-claude-r9.md` |
| Plan review -- Codex r9 | `scripts/review/results/2026-07-08-plan-3403-codex-r9.md` |
| Plan review -- Gemini r9 | `scripts/review/results/2026-07-08-plan-3403-gemini-r9.md` |
| Plan review -- disagreement r9 | `scripts/review/results/2026-07-08-plan-3403-disagreement-r9.md` |

---

## Deliverable

A repo-tracked, tested Linux voice-dictation rollout that restores `Super+Shift+V` dictation on ace-linux-1 when a usable capture device is available from a writable desktop user session, fails closed with explicit inactive guidance when hardware/session prerequisites are unavailable, and documents the VNC text-injection contract.

---

## Pseudocode

```
function capture_devices_from_arecord(output):
    for each line matching "card N: ..., device M:":
        emit "plughw:N,M"

function choose_alsa_device():
    if arecord command is missing:
        return empty/inactive with reason "missing alsa-utils"
    if DICTATE_DEVICE_ALSA is set:
        if probe_capture_device(DICTATE_DEVICE_ALSA) succeeds:
            return that explicit value
        return empty/inactive with reason "explicit device unusable"
    devices = capture_devices_from_arecord(arecord -l)
    for device in devices:
        if probe_capture_device(device) succeeds:
            return device
    return empty/inactive with reason "no usable capture device"

function probe_capture_device(device):
    run timeout 3 arecord -q -D "$device" -f S16_LE -r 16000 -c 1 -d 1 /dev/null
    treat rc 0 as usable
    treat non-zero or timeout as unusable
    note: this opens the local capture stream for one second and discards audio to /dev/null

function prepare_share_dir():
    if ~/.local/share/voice-dictation is a symlink or missing:
        replace it with symlink to repo tools/voice-dictation
    else:
        move it to ~/.local/share/voice-dictation.backup-<timestamp>
        then create symlink to repo tools/voice-dictation

function install_voice_dictation():
    if uname -s is not Linux:
        print "voice dictation installer is Linux-only; skipping on this OS"
        return 0
    gnome_binding_path = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/"
    gnome_hotkey_available = command -v gsettings succeeds and the custom-keybindings list can be read
    selected_device = choose_alsa_device()
    if selected_device is empty:
        print inactive guidance with exact reason
        if gnome_hotkey_available and an existing GNOME custom keybinding already points at codex-dictate:
            rewrite_existing_codex_hotkey_to_inert_warning()
        otherwise do not create a new inactive hotkey binding
        return 0
    selected_python = choose_python_with_faster_whisper()
    if no selected_python:
        if DICTATE_BOOTSTRAP_INSTALL=1:
            install_target_python = first executable candidate from python_candidates()
            if install_target_python exists and command -v uv succeeds:
                run uv pip install --python "$install_target_python" faster-whisper
                selected_python = choose_python_with_faster_whisper()
            if command -v uv fails:
                print manual guidance that uv is missing and no package install was attempted
        if still no selected_python:
            if an executable Python candidate exists:
                print manual guidance with the exact uv pip install --python command for that candidate
            otherwise print manual guidance to install Python plus faster-whisper
            if gnome_hotkey_available and an existing GNOME custom keybinding already points at codex-dictate:
                rewrite_existing_codex_hotkey_to_inert_warning()
            return 0
    prepare_share_dir()
    link ~/.local/bin/codex-dictate to the launcher
    if no gnome_hotkey_available:
        print the manual launcher command with DICTATE_DEVICE_ALSA and DICTATE_PYTHON
        return 0
    ensure custom-keybindings includes gnome_binding_path
    remove stale duplicate custom-keybinding paths whose name or command points at codex-dictate unless they equal gnome_binding_path
    set gnome_binding_path name to "Codex Voice Dictation"
    set gnome_binding_path binding to "<Super><Shift>v"
    launcher_path = "$HOME/.local/share/voice-dictation/codex-dictate.sh" expanded to an absolute path before storing in gsettings
    set gnome_binding_path command to env DICTATE_DEVICE_ALSA=selected_device DICTATE_PYTHON=selected_python bash "$launcher_path"
    if no text injector exists for the active session (xdotool on X11, wtype or ydotool on Wayland):
        print warning "no text injector found; transcripts will print only"
        do not edit README during installer runtime; README warning is static repo content added during implementation
    return 0

function choose_python_with_faster_whisper():
    candidates = python_candidates()
    return first executable candidate where "$candidate" -c "import faster_whisper" exits 0
    if none import faster_whisper, return empty and let installer attempt opt-in user-space install/report

function python_candidates():
    emit DICTATE_PYTHON when set and executable
    emit ~/miniforge3/bin/python3, ~/miniconda3/bin/python3, ~/anaconda3/bin/python3 when executable
    emit command -v python3 when executable
    preserve this order so manual guidance and optional install target are deterministic

function rewrite_existing_codex_hotkey_to_inert_warning():
    set the existing codex-dictate GNOME binding command to:
      bash -lc 'msg="Voice dictation inactive: no usable microphone or STT runtime. Re-run scripts/agents/install-voice-dictation.sh after connecting a mic and installing faster-whisper."; if command -v notify-send >/dev/null 2>&1; then notify-send -t 4000 "dictate" "$msg"; else logger -t voice-dictation "$msg"; fi'
    keep the message text inside the bash -lc wrapper single-quote-free because it is stored through gsettings as a quoted command string

if script is executed directly:
    if argv[1] == "--choose":
        device = choose_alsa_device()
        if device is non-empty:
            print device to stdout and exit 0
        print inactive reason to stderr and exit 3
    otherwise print usage and exit 2

function codex_dictate_toggle():
    repo_root = cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../.." && pwd -P
    detect_helper = "$repo_root/scripts/agents/lib/voice-dictation-detect.sh"
    if recording pid exists:
        stop arecord, transcribe WAV, inject text into focused X11/Wayland window
        return 0
    device = DICTATE_DEVICE_ALSA
    explicit_device = true if DICTATE_DEVICE_ALSA is set, else false
    if device is empty:
        device = output of "$detect_helper" --choose
    if device is empty:
        notify/print "Voice dictation inactive: no usable capture device"
        return 0 without recording
    attempt to start arecord from device without a pre-speech one-second probe
    if start fails and explicit_device is true:
        notify/print "Configured microphone failed; trying auto-detected microphone. Re-run scripts/agents/install-voice-dictation.sh to refresh the saved hotkey device."
        fallback_device = output of "$detect_helper" --choose
        if fallback_device is non-empty:
            attempt to start arecord from fallback_device
    if start still fails:
        notify/print "Voice dictation inactive: no usable capture device"
        return 0

function docs_vnc_contract():
    explain that VNC receives typed text/keystrokes
    warn not to route microphone audio through TigerVNC for this workflow
    recommend SSH/tmux for remote terminal work and local dictation into focused window
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Restore/update | `tools/voice-dictation/README.md` | User-facing repo-tracked contract and OS strategy. |
| Restore/update | `tools/voice-dictation/codex-dictate.sh` | Push-to-talk launcher; should use selected ALSA device. |
| Restore/update | `tools/voice-dictation/dictate-test.sh` | Fixed-duration mic/STT verification path. |
| Restore/update | `tools/voice-dictation/transcribe.py` | Local faster-whisper transcription bridge. |
| Delete local residue | `tools/voice-dictation/__pycache__/` | Remove stale ignored generated bytecode from ace-linux-1 before closeout; do not rely on this path in deterministic tests. |
| Create | `scripts/agents/lib/voice-dictation-detect.sh` | Pure Bash helper for tested capture-device parsing, selected-device policy, and inactive reasons. |
| Create/update | `scripts/agents/install-voice-dictation.sh` | Idempotent installer with capture-device selection and GNOME binding. |
| Modify | `scripts/memory/bootstrap-machine.sh` | Add guarded voice-dictation install hook after section 2.10. |
| Create | `scripts/agents/tests/test_voice_dictation_detection.sh` | TDD coverage for capture-device parser/selection and inactive behavior. |
| Restore | `docs/session-handoffs/2026-06-30-handoff-voice-dictation-ecosystem.md` | Preserve the branch-only trace artifact cited by this plan. |
| Verify/update | `docs/plans/README.md` | The draft row for this plan already exists; implementation of the planning gate should commit that row without adding a duplicate. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_detects_plantronics_capture_device` | Parser extracts concrete capture target from `arecord -l` output. | Fixture with NVIDIA card 0 and Plantronics card 1 device 0. | `plughw:1,0`. |
| `test_missing_arecord_returns_inactive` | Fresh machine without `alsa-utils` does not abort bootstrap during device detection. | PATH without `arecord`. | No device selected; reason is `missing alsa-utils`; installer exits 0 after guidance. |
| `test_installer_non_linux_noops` | Cross-platform bootstrap remains safe when the hook runs on macOS/Windows. | Stubbed `uname -s` as `Darwin`, `MINGW64_NT`, and `CYGWIN_NT`. | Installer prints Linux-only skip guidance, exits 0, and does not touch ALSA/GNOME/user symlinks. |
| `test_explicit_device_with_missing_arecord_returns_missing_alsa_utils` | A stale `DICTATE_DEVICE_ALSA` override does not mask missing `alsa-utils`. | PATH without `arecord` and `DICTATE_DEVICE_ALSA=plughw:1,0`. | No device selected; reason is `missing alsa-utils`; no `set -e` abort. |
| `test_no_capture_device_returns_inactive` | Installer/detection path distinguishes no capture device from any sound card. | Fixture with no `arecord -l` capture devices. | No device selected; installer prints inactive/no-capture guidance and exits 0. |
| `test_concrete_capture_device_selected_after_successful_probe` | Selection proves the chosen concrete device can be opened before binding the launcher. | Fixture with one capture device and stubbed `arecord -D plughw:1,0` rc 0. | GNOME command/export path includes `DICTATE_DEVICE_ALSA=plughw:1,0`. |
| `test_unusable_first_device_skips_to_next_usable_device` | First listed device is not blindly treated as usable. | Fixture with `plughw:1,0` probe rc 1 and `plughw:2,0` probe rc 0. | Selected device is `plughw:2,0`. |
| `test_explicit_dictate_device_wins_only_when_probe_succeeds` | User override remains authoritative but still must be openable. | `DICTATE_DEVICE_ALSA=hw:2,0` and stubbed probe rc 0. | Selected device is `hw:2,0`; no auto-detection override. |
| `test_explicit_unusable_device_returns_inactive` | Bad override does not bind a failing launcher. | `DICTATE_DEVICE_ALSA=hw:9,9` and stubbed probe rc 1. | No device selected; inactive reason is `explicit device unusable`. |
| `test_helper_choose_cli_contract` | Helper works both as sourced library and executable CLI. | Stubbed `arecord -l` plus successful probe. | `bash scripts/agents/lib/voice-dictation-detect.sh --choose` prints selected device and exits 0; inactive path exits 3 with reason on stderr. |
| `test_codex_dictate_launcher_uses_selected_alsa_device` | Push-to-talk launcher honors the installer-selected device at recording time. | Stubbed `arecord`, `DICTATE_DEVICE_ALSA=plughw:2,0`, temp state dir. | Launcher invokes `arecord -D plughw:2,0` when starting recording. |
| `test_dictate_test_uses_selected_alsa_device_argument` | Fixed-duration smoke launcher exercises the same selected device path used by the hotkey. | Stubbed `arecord`; run `dictate-test.sh 5 plughw:2,0`. | Script invokes `arecord -D plughw:2,0` for the requested duration. |
| `test_codex_dictate_runtime_falls_back_when_bound_device_start_fails` | Hotkey self-heals after USB card renumbering without delaying every start with a probe. | `DICTATE_DEVICE_ALSA=plughw:1,0`; first start attempt fails immediately; helper `--choose` returns `plughw:2,0`. | Launcher notifies about override, retries, and records with `arecord -D plughw:2,0`. |
| `test_codex_dictate_stop_branch_runs_before_device_selection` | Second hotkey press can stop an in-progress recording even while ALSA device is busy. | Existing PID file and stubbed busy `arecord` device. | Launcher stops the recorded PID and does not call detection/probe before the stop branch. |
| `test_codex_dictate_resolves_helper_from_symlink_target` | Installed symlink layout can find the helper library at runtime. | Launcher executed through `~/.local/share/voice-dictation/codex-dictate.sh` symlink to repo file. | Launcher resolves repo root with `readlink -f`/`pwd -P` and invokes `$repo_root/scripts/agents/lib/voice-dictation-detect.sh`. |
| `test_installer_preserves_symlink_contract` | Installer links repo source to stable user paths without copy drift. | Temp `HOME`, temp repo root, stubbed `gsettings`. | `~/.local/share/voice-dictation` symlink points at repo `tools/voice-dictation`. |
| `test_existing_real_share_dir_is_backed_up_not_deleted` | Installer does not `rm -rf` a user-owned real directory. | Temp `HOME` with real `~/.local/share/voice-dictation/sentinel.txt`. | Sentinel remains in timestamped backup; new path is symlink. |
| `test_inactive_install_does_not_replace_real_share_dir` | Inactive no-mic installs avoid unrelated user-visible share-dir mutation. | Temp `HOME` with real `~/.local/share/voice-dictation/sentinel.txt`; no usable capture device. | Sentinel remains in place; no backup/symlink replacement occurs. |
| `test_inactive_install_replaces_stale_hotkey_with_inert_warning` | Inactive machines do not leave `Super+Shift+V` pointing at the failing launcher. | Stubbed no-capture fixture and existing `codex-dictate` GNOME keybinding. | Keybinding command is an inert warning command, not `codex-dictate.sh`. |
| `test_installer_uses_codex_dictate_binding_path` | Installer converges the semantic GNOME binding path used on the live machine and prior branch. | Stubbed `gsettings` with `/custom-keybindings/codex-dictate/`. | Command, name, and binding are written under `/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/`. |
| `test_installer_writes_absolute_active_hotkey_command` | Active GNOME command does not depend on shell tilde expansion. | Temp `HOME`, selected mic/Python, stubbed `gsettings`. | Stored command contains an absolute `$HOME/.local/share/voice-dictation/codex-dictate.sh` path and no literal `~`. |
| `test_active_hotkey_command_executes` | Active hotkey command string is executable, not just substring-correct. | Captured active command with stubbed `arecord`, state dir, and transcription path. | Running the captured command reaches the stubbed launcher without path-expansion failure. |
| `test_installer_removes_duplicate_codex_dictate_bindings` | Installer does not leave stale duplicate voice bindings in GNOME settings. | Stubbed custom-keybindings list with `codex-dictate/` plus another path whose command points at `codex-dictate.sh`. | Final list keeps only the `codex-dictate/` path for voice dictation. |
| `test_gsettings_absent_skips_hotkey_and_prints_manual_command` | Headless/non-GNOME bootstrap does not fail when mic and Python are otherwise ready. | PATH without `gsettings`, selected mic, selected Python. | Installer exits 0 and prints the manual launcher command instead of binding a hotkey. |
| `test_python_selection_prefers_dictate_python_with_faster_whisper` | Runtime binding uses the first interpreter that actually imports `faster_whisper`. | Stubbed candidate Python executables. | GNOME command includes the selected interpreter path. |
| `test_python_install_success_reselects_interpreter_before_binding` | Opt-in successful user-space install is followed by a fresh import probe before binding. | `DICTATE_BOOTSTRAP_INSTALL=1`; stubbed candidates initially missing `faster_whisper`, then succeeding after stubbed `uv pip install --python "$target" faster-whisper`. | GNOME command includes the reselected interpreter path, not an empty value. |
| `test_python_missing_keeps_hotkey_inactive_by_default` | Missing Python/STT support does not trigger an implicit package install or bind a failing launcher. | Stubbed candidates that cannot import `faster_whisper`; `DICTATE_BOOTSTRAP_INSTALL` unset. | Installer reports manual guidance with the exact opt-in install command and uses inactive warning behavior. |
| `test_python_install_command_pins_target_interpreter` | Optional install path is not left to ambiguous uv behavior. | `DICTATE_BOOTSTRAP_INSTALL=1` and first executable candidate `/tmp/python-ok`. | Stubbed uv receives `pip install --python /tmp/python-ok faster-whisper`. |
| `test_python_install_opt_in_without_uv_stays_inactive` | Opt-in dependency install does not abort bootstrap when `uv` is missing. | `DICTATE_BOOTSTRAP_INSTALL=1`, first executable Python candidate present, PATH without `uv`. | Installer exits 0, prints missing-uv manual guidance, and leaves/re-writes hotkey inert. |
| `test_missing_text_injector_warns_without_blocking` | Mic/Python-ready machines without xdotool/wtype/ydotool do not fail silently. | Stubbed selected mic and Python, PATH without text injector commands. | Installer exits 0 and prints a transcript-output-only warning. |
| `test_installer_missing_text_injector_does_not_mutate_readme` | Machine-specific installer warnings do not dirty repo-tracked docs. | Stubbed selected mic/Python, PATH without text injector commands, tracked README sentinel. | Installer prints the warning and leaves `tools/voice-dictation/README.md` unchanged. |
| `test_inert_warning_command_executes` | Inactive hotkey command survives gsettings quoting. | Captured inert command with stubbed `notify-send` and `logger`. | `bash -lc <captured-payload>` exits 0 and calls a notifier/logger stub. |
| `test_bootstrap_voice_hook_is_guarded_and_nonfatal` | Bootstrap hook cannot break fresh-machine setup if installer is absent or exits non-zero. | Stubbed missing installer and failing installer cases. | `bootstrap-machine.sh` checks executable presence and uses nonfatal `|| true`/equivalent guard. |
| `test_pycache_is_gitignored` | Bytecode residue stays out of repo state on fresh machines. | Existing `.gitignore` rules. | `git check-ignore -q tools/voice-dictation/__pycache__/transcribe.cpython-313.pyc` exits 0. |
| `test_voice_scripts_have_valid_syntax` | Restored shell scripts parse. | `bash -n` over launcher/test/installer/bootstrap. | All parse cleanly. |
| `test_transcribe_py_syntax_compiles` | Python bridge compiles syntactically under repo Python policy. | `uv run python -c 'from pathlib import Path; p=Path("tools/voice-dictation/transcribe.py"); compile(p.read_text(), str(p), "exec")'`. | Exit 0. |

---

## Acceptance Criteria

- [ ] Tests are written first and observed failing before implementation:
  `bash scripts/agents/tests/test_voice_dictation_detection.sh`
- [ ] After implementation, focused tests pass:
  `bash scripts/agents/tests/test_voice_dictation_detection.sh`
- [ ] Shell syntax passes:
  `bash -n scripts/agents/install-voice-dictation.sh tools/voice-dictation/codex-dictate.sh tools/voice-dictation/dictate-test.sh scripts/memory/bootstrap-machine.sh`
- [ ] Python syntax passes:
  `uv run python -c 'from pathlib import Path; p=Path("tools/voice-dictation/transcribe.py"); compile(p.read_text(), str(p), "exec")'`
- [ ] Live installer convergence is exercised on ace-linux-1:
  `bash scripts/agents/install-voice-dictation.sh`
- [ ] Live installer/hotkey convergence is run from a writable desktop user session. If the current agent sandbox cannot write the user dconf/home state, closeout records the sandbox error and uses an explicit user-run/manual verification command path instead of treating repo tests alone as live convergence.
- [ ] If `bash scripts/agents/lib/voice-dictation-detect.sh --choose` selects a usable device and GNOME settings are available, `gsettings get org.gnome.settings-daemon.plugins.media-keys custom-keybindings` includes `/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/`.
- [ ] The live `codex-dictate` binding command is verified with:
  `gsettings get org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/ command`
  and it includes `DICTATE_DEVICE_ALSA=<selected-device>`, `DICTATE_PYTHON=<selected-python>`, and `codex-dictate.sh`.
- [ ] The live custom-keybindings list has no duplicate voice-dictation binding paths whose name or command points at `codex-dictate` outside `/custom-keybindings/codex-dictate/`.
- [ ] If GNOME settings are unavailable, the installer exits 0 and prints the manual launcher command instead of failing bootstrap.
- [ ] If `bash scripts/agents/lib/voice-dictation-detect.sh --choose` returns inactive on the live machine, closeout records the reason; an existing stale `codex-dictate` GNOME binding is rewritten to the inert warning command, while a machine with no prior voice binding does not get a new inactive hotkey.
- [ ] If a usable device is selected, the live ace-linux-1 mic smoke test records 3-5 seconds from that device:
  `dev="$(bash scripts/agents/lib/voice-dictation-detect.sh --choose)" && ~/.local/share/voice-dictation/dictate-test.sh 5 "$dev"`
- [ ] If no usable device is selected, the live mic smoke test is recorded as `SKIP: no usable capture device` and inactive installer convergence evidence substitutes for hardware smoke.
- [ ] Live audio state is refreshed at implementation start and closeout. If `default` has healed, no special-case failure is required; the installer still selects an openable concrete device and the README records the observed state.
- [ ] Installer command binding includes a usable `DICTATE_DEVICE_ALSA` when `default` is broken.
- [ ] Installer missing-capture/missing-`arecord` paths leave the hotkey inert or warning-only, never pointing at a failing launcher.
- [ ] A pre-existing real `~/.local/share/voice-dictation` directory is backed up, not deleted.
- [ ] Local generated bytecode residue is removed from ace-linux-1:
  `rm -rf tools/voice-dictation/__pycache__ && test ! -e tools/voice-dictation/__pycache__`
- [ ] Existing ignore coverage for future bytecode residue is verified:
  `git check-ignore -q tools/voice-dictation/__pycache__/transcribe.cpython-313.pyc`
- [ ] VNC contract is documented: local dictation types into focused VNC/SSH/tmux target; no TigerVNC microphone forwarding is required.
- [ ] Legal/security scan passes:
  `bash scripts/legal/legal-sanity-scan.sh`
- [ ] Code-stage adversarial review runs before closeout with non-MAJOR Claude and Codex artifacts required for this T2 issue; Gemini is attempted opportunistically and, if non-interactive auth remains unavailable, an explicit Gemini `UNAVAILABLE` artifact is recorded without blocking.
- [ ] `scripts/agents/tests/test_voice_dictation_detection.sh` is intentionally manual/direct-invoked for this issue; no CI wiring is added in this scope.
- [ ] Before moving [#3403](https://github.com/vamseeachanta/workspace-hub/issues/3403) to `status:plan-review`, refresh this plan's `Review artifacts` header and Artifact Map so they include the final no-MAJOR review round.
- [ ] Before moving [#3403](https://github.com/vamseeachanta/workspace-hub/issues/3403) to `status:plan-review`, inspect branch divergence with `git fetch origin`, `git status --short --branch`, and `git log --oneline --left-right HEAD...origin/main --`; if local and remote have diverged, reconcile with an explicit rebase or merge first, re-run pathspec status, and only then commit/push this plan, the existing `docs/plans/README.md` row, and the final revision-stamped no-MAJOR review artifacts using pathspec staging and `git add -f` for `scripts/review/results/` files because that directory is ignored.
- [ ] Before the plan-review commit, remove or explicitly exclude every non-cited [#3403](https://github.com/vamseeachanta/workspace-hub/issues/3403) review artifact matching `scripts/review/results/*plan-3403*` that is not listed in this plan's refreshed `Review artifacts` header. This cleanup is computed from the live filesystem after the final review archive is written; do not rely on a hand-maintained example list.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | MINOR | Mischaracterized reproduction, hardcoded `plughw:1,0`, underspecified default probe, stale inactive hotkey, branch-only handoff citation. |
| Codex r1 | MAJOR | Missing `arecord` path, ambiguous default probing, bare `python3` contrary to repo policy, destructive existing-directory behavior. |
| Claude r2 | MINOR | Artifact naming, helper CLI contract, inert notifier, runtime Python selection, stale pycache, manual test wiring. |
| Codex r2 | MAJOR | "First listed" was not proven usable, artifact paths stale/inconsistent, stale failed review state, helper CLI contract underspecified. |
| Claude r3 | MINOR | Dead canonical artifact rows, py_compile recreating bytecode, Python fallback fallthrough, inactive-hotkey overreach, missing text-injector warning. |
| Codex r3 | MAJOR | Dead canonical artifact rows, Python fallback fallthrough, inactive-hotkey overreach, missing live installer convergence, unconditional live mic smoke. |
| Claude r4 | MAJOR | GNOME binding path hardcoded to `custom0`, local pycache test, missing headless gsettings guard, underspecified uv fallback, untracked/dead review residue. |
| Codex r4 | MAJOR | GNOME binding path hardcoded to `custom0`; live binding is `/custom-keybindings/codex-dictate/`. |
| Claude r5 | MINOR | Stale-residue glob targeted wrong files, inactive install share-dir ordering, uncommitted plan/index exposure, dead bytecode assertion, Gemini repeat-unavailable note. |
| Codex r5 | MAJOR | Code-stage provider set underspecified, actual unstamped residue missed, ignored review artifacts need `git add -f`. |
| Claude r6 | MINOR | Artifact cleanup examples drifted, final-round artifacts not in header, existing README row/uncommitted exposure, no-Python inert rewrite ambiguity, inert command quote fragility. |
| Codex r6 | MAJOR | Launcher did not have tests proving `DICTATE_DEVICE_ALSA` reaches `arecord`, smoke test launcher device argument untested, explicit device plus missing `arecord` path untested. |
| Claude r7 | MINOR | Runtime stale-device fallback, missing `uv` guard, inert command executability, bootstrap hook guard, reproduction refresh note. |
| Codex r7 | MAJOR | Live desktop convergence may require writable user session/manual path, embedded audio evidence needed refresh, launcher missing needed explicit wording, final r7 artifacts not in header. |
| Claude r8 | MAJOR | Runtime fallback probed before stop branch, helper path unresolved from symlinked launcher, stop branch untested, start latency regression, explicit-device policy mismatch. |
| Codex r8 | MAJOR | Non-Linux installer guard missing, installer could mutate repo README at runtime, branch divergence not called out before plan-review push. |
| Claude r9 | MINOR | Active hotkey command used literal `~`, active command executability not tested, runtime stale-device notice, Gemini churn, inert quote wording. |
| Codex r9 | MINOR | Plan self-declared pending r9, deliverable overpromised when hardware unavailable, divergence reconciliation rule needed. |
| Gemini r1/r2/r3/r4/r5/r6/r7/r8/r9 | UNAVAILABLE | No non-interactive Gemini auth configured. |

**Overall result:** PLAN-REVIEW READY -- r9 returned no MAJOR findings from Claude or Codex; Gemini is UNAVAILABLE due missing non-interactive auth. r9 MINOR findings are incorporated inline in this revision. Implementation remains blocked until user approval applies `status:plan-approved`.

Revisions made based on review:
- Reclassified reproduction as partial: no-capture and default-broken-visible-capture are distinct states.
- Replaced install-time `default` probing with deterministic concrete capture-device selection from `arecord -l`.
- Added missing-`arecord` inactive path and test.
- Added existing real-directory backup contract and test; no `rm -rf` user data.
- Added inactive-hotkey warning/inert command contract and test.
- Replaced bare `python3` acceptance command with `uv run python`.
- Removed hardcoded smoke-test device from acceptance criteria.
- Added branch-only handoff disposition.
- Added one-second discarded open-probe for concrete capture devices before binding the launcher.
- Specified helper dual-use contract (`source` for functions, `--choose` for CLI smoke path).
- Defined the inert no-mic hotkey command using `notify-send` with `logger` fallback.
- Added runtime Python selection/faster-whisper tests.
- Added stale `__pycache__` deletion and manual-test-runner scope.
- Replaced dead canonical review artifact rows with revision-stamped r1/r2/r3 artifacts.
- Made Python dependency installation fail-closed: reselect the interpreter after install or return inactive.
- Scoped inactive hotkey rewrites to pre-existing `codex-dictate` bindings only.
- Added live installer convergence and conditional hardware smoke acceptance criteria.
- Added installer/README warning coverage for missing text injectors.
- Corrected GNOME convergence to the live/prior-branch `/custom-keybindings/codex-dictate/` slot and added duplicate-binding cleanup tests.
- Converted local `__pycache__` cleanup from deterministic TDD precondition to closeout evidence plus `.gitignore` verification.
- Added headless/non-GNOME `gsettings` skip behavior and test.
- Made user-space STT dependency installation opt-in via `DICTATE_BOOTSTRAP_INSTALL=1` and pinned the uv command to `uv pip install --python "$target" faster-whisper`.
- Added review-artifact closeout evidence requiring final revision-stamped artifacts to be committed and stale non-cited residue to be excluded or removed before label movement.
- Moved share-dir mutation after mic/Python readiness so inactive no-mic installs do not rewrite real user directories.
- Named Claude + Codex + Gemini as the required code-stage review provider set, with explicit Gemini-unavailable degradation.
- Added `git add -f` requirement for ignored `scripts/review/results/` artifacts.
- Replaced the stale-residue cleanup glob with an explicit "all non-cited `*plan-3403*` artifacts" rule and examples matching the live unstamped files.
- Removed the vacuous bytecode assertion from the Python syntax test.
- Added launcher tests proving both `codex-dictate.sh` and `dictate-test.sh` pass the selected ALSA device to `arecord -D`.
- Moved missing-`arecord` detection ahead of explicit device probing and added the combined override-plus-missing-arecord test.
- Required the final review round to be added to the header before computed artifact cleanup runs.
- Replaced stale artifact cleanup examples with a computed filesystem-minus-header rule.
- Acknowledged the existing `docs/plans/README.md` row and duplicate-row avoidance.
- Aligned no-Python inactive handling with no-mic handling by reusing the inert hotkey rewrite helper and documenting the single-quote constraint.
- Added runtime stale-device fallback in the launcher and test coverage for stale baked ALSA devices.
- Added missing-`uv` guard/test for opt-in dependency installation.
- Added inert warning command executability and guarded bootstrap-hook tests.
- Refreshed audio evidence and clarified that the current launcher target is missing on `main`.
- Added writable-desktop/manual-verification fallback for live GNOME convergence.
- Moved toggle stop branch before any device selection/probing and added stop-branch coverage.
- Resolved helper path from the symlink target with `readlink -f`/`pwd -P` and added symlink-layout coverage.
- Changed runtime stale-device handling to fallback after a failed start attempt instead of pre-speech probing.
- Added Linux-only installer no-op behavior and macOS/Windows tests to preserve cross-platform bootstrap.
- Removed installer-time README mutation; text-injector warning is printed at runtime and documented only by static repo changes.
- Added branch-divergence preflight before plan-review commit/push.
- Switched the active GNOME command to a stored absolute launcher path and added active-command executability coverage.
- Qualified the deliverable for hardware/session availability and stale-device rerun-installer guidance.
- Made Gemini code-stage review opportunistic for this T2 issue while requiring non-MAJOR Claude and Codex.
- Added explicit divergence reconciliation before the plan-review commit/push.

---

## Risks and Open Questions

- **Risk:** The Plantronics device can appear/disappear during a session; tests must not depend on live hardware except for the final smoke test.
- **Risk:** `faster-whisper` may download the selected model on first run; installer should report this but avoid doing uncontrolled sudo/system changes.
- **Risk:** GNOME hotkey binding in headless/non-GNOME sessions can fail; installer should skip gracefully and print the manual command. If a stale binding exists and `gsettings` is available, the installer should update it to an inert warning command or clearly report that it could not change it.
- **Risk:** The existing local branch is ahead/behind `main` and includes unrelated historical drift; implementation should cherry-pick/recreate only issue-scoped files, not merge the branch wholesale.
- **Risk:** If multiple capture devices are present, selecting the first openable `arecord -l` capture device may choose the wrong mic. The override remains `DICTATE_DEVICE_ALSA`; documenting the chosen device in installer output is required.

---

## Complexity: T2

**T2** -- multi-file harness repair with Bash and Python files, bootstrap integration, deterministic tests, live hardware smoke verification, and a cross-review gate before closeout.
