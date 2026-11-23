### Verdict: MAJOR

### Summary
High-quality, defensively written shell work with an unusually thorough test suite (12 test groups covering device selection, inert-hotkey fallback, lock contention, stale-PID safety, and committed file modes). No security or logic-critical defects found in the core toggle/record/transcribe flow. Requesting changes for a small set of robustness gaps: a missing existence guard on the symlink source (real risk given documented sparse-overlay checkouts), a misleading diagnostic on a bad VOICE_DICTATION_INSTALL_ROOT, and injector-argument/warning inconsistencies.

### Issues Found
- [P2] scripts/agents/install-voice-dictation.sh:81,158 — ensure_share_links symlinks share_dir -> ${install_root}/tools/voice-dictation without verifying the source exists. The worktree branch validates -f primary/tools/voice-dictation/codex-dictate.sh, but the default (non-worktree) path does not. On a sparse/partial checkout (the user's ~/workspace-hub is documented as a possible sparse overlay) this creates a dangling symlink and a hotkey bound to a nonexistent launcher, while still printing 'voice-dictation active'. Add [[ -x "${tool_src}/codex-dictate.sh" ]] guard before ensure_share_links/ensure_hotkey.
- [P3] scripts/agents/install-voice-dictation.sh:46-48 — when VOICE_DICTATION_INSTALL_ROOT points at a nonexistent path, cd fails, resolve_install_root returns non-zero, and the caller prints the unrelated 'running from a linked worktree' message. Validate the override path and emit an accurate error.
- [P3] scripts/agents/install-voice-dictation.sh:184-188 vs tools/voice-dictation/codex-dictate.sh:912-924 — installer warns 'no text injector' on Wayland when only xdotool is present, but inject_text will happily fall through to xdotool (works for XWayland apps). The warning and runtime behavior disagree; align the checks.
- [P3] tools/voice-dictation/codex-dictate.sh:915,919 — wtype "${text}" and ydotool type "${text}" pass the transcript as a bare first argument; a transcript beginning with '-' can be parsed as an option flag. xdotool already uses '--'; add the same guard (wtype -- "${text}", ydotool type -- "${text}" where supported).
- [P3] tools/voice-dictation/codex-dictate.sh:1015-1032 — is_owned_recording check followed by kill in stop_and_type is a TOCTOU window (PID reuse between /proc cmdline check and kill). Largely mitigated by the cmdline+wav match and short window; acceptable, but worth a comment noting the residual race.
- [P3] tools/voice-dictation/codex-dictate.sh:956 — empty-transcript check [[ -z "${text// /}" ]] strips only spaces; a transcript of tabs/newlines would be 'injected'. Use ${text//[[:space:]]/} for consistency with transcribe.py's whitespace collapsing (low likelihood in practice since transcribe.py already collapses).

### Suggestions
- Add a behavioral test for the linked-worktree resolution path in resolve_install_root — it is currently only grep-asserted in test_static_contracts ('installer resolves linked worktree root'), and every functional test bypasses it via VOICE_DICTATION_INSTALL_ROOT=${REPO_ROOT}. A fake git-worktree fixture (git init + git worktree add in a tmp dir) would cover both the resolves-to-primary and rerun-from-primary branches.
- Cover the DICTATE_BOOTSTRAP_INSTALL=1 uv-install branch (install-voice-dictation.sh:206-214) with a stubbed uv — it is currently untested.
- In ensure_hotkey's list-append ("${current%]}, '${binding_path}']") consider guarding against a malformed/empty gsettings response that lacks a trailing ']' — currently it would silently write a broken list literal.
- test_static_contracts asserts git check-ignore on tools/voice-dictation/__pycache__/…pyc, but the diff includes no .gitignore change — confirm the repo-level ignore already covers __pycache__ or this test fails on a clean clone.
- Wire the new test into whatever CI/enforcement entry point runs scripts/agents/tests/ — a 427-line TDD suite that only runs when invoked by hand loses most of its regression value.

### Questions for Author
- Is tools/voice-dictation guaranteed present in every checkout that runs bootstrap-machine.sh (i.e., are sparse overlays excluded from tools/)? If not, the P2 dangling-symlink guard is required before merge.
- The inert hotkey (write_inert_hotkey) only rewrites an existing codex-dictate binding and never creates one on first-time inactive installs — intentional, so that mic-less machines never gain a hotkey at all? A one-line comment stating this would prevent a future 'fix'.
- Does __pycache__ get git-ignored by an existing repo-root .gitignore rule, given the static-contract test asserts check-ignore succeeds but this commit adds no ignore entry?
