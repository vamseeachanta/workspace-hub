### Verdict: APPROVE

### Summary
Well-engineered Linux voice-dictation installer with graceful degradation at every failure point (non-Linux, no mic, no gsettings, no faster-whisper, linked worktree) and unusually thorough shell test coverage, including hotkey-command round-trip execution, apostrophe quoting, stale-PID safety, and lock contention. All identified issues are minor edge cases; nothing blocks merge. Complies with repo conventions (no hardcoded absolute paths, repo-root derivation, guarded nonfatal bootstrap hook).

### Issues Found
- [P3] scripts/agents/lib/voice-dictation-detect.sh:276 — DICTATE_PROBE_SECONDS=0 passes `-d 0` to real arecord, which records unbounded; the `timeout 4` then kills it with a nonzero exit, so every device is wrongly classified unusable. Only affects a user who explicitly sets 0 (tests use a stub), but a guard (treat 0 as skip-probe or clamp to 1) would be safer.
- [P3] scripts/agents/install-voice-dictation.sh:98 — detect_helper resolves from repo_root (possibly a linked worktree) while tool_src/launcher resolve from install_root (primary checkout). Works at install time, but is inconsistent: if the worktree is later deleted, a re-run from a stale environment references a helper path that no longer exists. Prefer install_root for both.
- [P3] scripts/agents/install-voice-dictation.sh:132-150 — an explicitly set but broken DICTATE_PYTHON (import fails) is silently superseded by a conda/system python that can import faster_whisper. Explicit user config being quietly overridden deserves at least an informational message.
- [P3] scripts/agents/tests/test_voice_dictation_detection.sh:419-447 — the arecord stub loops forever when invoked without -d; several tests reap it via pidfile reads with `|| true` fallbacks, so an assertion failure mid-test can leak orphaned stub processes beyond tmpdir cleanup (the EXIT trap removes dirs but does not kill children).
- [P3] scripts/agents/install-voice-dictation.sh:94 — no collision check on the default `<Super><Shift>v` binding; if the user (or another custom keybinding) already owns that combo, GNOME will silently keep the pre-existing one and the freshly installed hotkey never fires, with no diagnostic.
- [P3] scripts/agents/tests/test_voice_dictation_static_contracts.sh:824 — test asserts `tools/voice-dictation/__pycache__/*.pyc` is git-ignored, but the diff adds no .gitignore entry; this passes only if a pre-existing repo-wide `__pycache__/` pattern exists. If it does not, the static suite fails on a fresh checkout.

### Suggestions
- Add a small uninstall/disable path (remove symlinks + gsettings binding); the installer is idempotent forward but there is no reverse operation, and orphaned hotkeys pointing at removed checkouts will surface as confusing notify-send failures.
- In ensure_hotkey, when appending to a non-empty custom-keybindings list, consider deduplicating any pre-existing entry containing `codex-dictate` under a different path form before appending, to avoid accumulating stale entries across naming changes.
- Kill lingering stub arecord children in the test cleanup trap (e.g., `pkill -f` scoped to the tmpdir, or track started PIDs) so failed assertions don't leak processes in CI.
- The inert-hotkey message and README both instruct `uv pip install --python <py> faster-whisper`; per the repo's environment quirk (uv broken for several repos, memory reference_digitalmodel_python_env_venv), consider also documenting the plain `pip install faster-whisper` fallback.

### Questions for Author
- Does the repository already carry a global `__pycache__/` .gitignore pattern that makes the check-ignore static test pass, or should this commit add `tools/voice-dictation/__pycache__/` explicitly?
- Is the silent fallback from a broken explicit DICTATE_PYTHON to another interpreter intended behavior, or should the installer fail-inactive with the explicit-config error the way the detect helper does for an explicit unusable ALSA device?
- The inert hotkey is only written when a codex-dictate binding already exists — intentional that a first-time inactive install leaves no hotkey at all (user must re-run the installer after fixing prerequisites)?
