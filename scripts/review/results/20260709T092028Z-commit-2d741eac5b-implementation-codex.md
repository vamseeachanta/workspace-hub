### Verdict: MAJOR

### Summary
REQUEST_CHANGES: The implementation is generally well-scoped and has substantial shell-level coverage, but the Wayland injector selection has a real runtime correctness bug. On Wayland systems with `ydotool` available and `xdotool` also installed, the installer will report the injector path as OK while the launcher can still choose `xdotool`, which is not a reliable Wayland injector.

### Issues Found
- [P2] Important: tools/voice-dictation/codex-dictate.sh:76 The injector precedence is inconsistent with the installer’s Wayland contract. `warn_missing_injector` treats `wtype` or `ydotool` as valid on Wayland, but `inject_text` tries `xdotool` before `ydotool` when `wtype` is absent. On Wayland desktops where `xdotool` is installed but ineffective for the focused Wayland app, dictation can silently fail even though `ydotool` is available. Prefer `wtype`, then `ydotool`, then optionally `xdotool` only for X11 or explicit fallback.

### Suggestions
- Add a test for Wayland with `WAYLAND_DISPLAY=1`, no `wtype`, both `xdotool` and `ydotool` present, asserting `ydotool` is used.
- Consider adding cleanup traps in `dictate-test.sh` so failed transcription does not leave stale WAV/error files behind.

### Questions for Author
- None.
