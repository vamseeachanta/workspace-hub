# Voice dictation PipeWire exit handoff - 2026-07-09

## Active task

User asked to document and prepare to exit after validating Linux voice dictation on `ace-linux-1`.

## Completed actions

- Ran the voice-dictation installer and observed the initial inactive message: `no usable capture device`.
- User verified hardware is present:
  - `arecord -l` sees `Plantronics Blackwire 3220 Seri`, card 1, device 0.
  - `wpctl status` sees `Blackwire C3220 Headset` as source 124.
- Inspected `scripts/agents/install-voice-dictation.sh` and `scripts/agents/lib/voice-dictation-detect.sh`.
- Root cause found: auto-detection chose direct ALSA `plughw:1,0`; that direct path was busy, so the helper incorrectly concluded no usable capture device.
- User verified the PipeWire override works:
  - `DICTATE_DEVICE_ALSA=pipewire bash scripts/agents/lib/voice-dictation-detect.sh --choose` prints `pipewire`.
  - `DICTATE_DEVICE_ALSA=pipewire bash scripts/agents/install-voice-dictation.sh` activates dictation.
- Installer reported active hotkey binding: `Super+Shift+V`, using PipeWire capture and the miniforge Python runtime.

## Current verified state

- Voice dictation is installed and active for the user session.
- Bound capture device: `pipewire`.
- Bound Python runtime: `$HOME/miniforge3/bin/python3`.
- Hotkey behavior: press `Super+Shift+V` once to record, press it again to transcribe and type into the focused target.

## Suggested smoke test

Run:

```bash
DICTATE_DEVICE_ALSA=pipewire DICTATE_PYTHON="$HOME/miniforge3/bin/python3" tools/voice-dictation/dictate-test.sh 5
```

Then speak a short phrase. This test prints the transcript and does not inject text.

## Follow-up recommendation

File or implement a small issue for the installer detection path:

- Add `pipewire` as a first-class candidate before direct `plughw:*` devices when `arecord -L` exposes it.
- Preserve explicit `DICTATE_DEVICE_ALSA` behavior.
- Add a regression test showing that a busy direct ALSA device does not make detection fail when PipeWire is usable.
- Improve the inactive message to suggest `DICTATE_DEVICE_ALSA=pipewire` when direct ALSA probing fails with a busy device.

## Suggested skills

- `diagnose`
- `superpowers:test-driven-development`
- `coordination/pre-completion-cleanup-audit`

## Exit notes

- No repo code was changed for the installer in this session.
- This handoff records runtime diagnosis and the working operator command.
- Existing workspace-hub modified/generated files were present before this handoff and should not be swept into the handoff commit.
