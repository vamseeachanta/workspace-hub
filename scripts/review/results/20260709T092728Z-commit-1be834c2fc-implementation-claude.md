### Verdict: APPROVE

### Summary
Well-engineered Linux voice-dictation installer with defensive shell practices (strict mode, proper quoting via shell_quote_word, symlink/ownership checks on state dirs, PID-ownership verification before kill) and an unusually thorough test harness. All 60 test assertions pass when executed in the worktree, the __pycache__ gitignore assertion and detect-os.sh dependency were verified against the live repo, and every failure path degrades to a non-fatal inactive state so bootstrap stays green. Only minor (P3) issues found; none block merge.

### Issues Found
- [P3] scripts/agents/lib/voice-dictation-detect.sh:276 — probe wraps arecord in a hardcoded `timeout 4` while DICTATE_PROBE_SECONDS is user-configurable; any probe duration >~4s always fails, and `timeout` availability is never checked (a missing coreutils timeout yields exit 127, misreported as 'no usable capture device' instead of a missing-dependency message).
- [P3] scripts/agents/install-voice-dictation.sh:98 — detect_helper resolves from repo_root (the linked worktree) while tool_src resolves from install_root (primary checkout); in the worktree case the install-time device probe and the runtime launcher use different copies of the detection helper. Functionally benign today but an inconsistency waiting to skew if the helper diverges between checkouts.
- [P3] scripts/agents/install-voice-dictation.sh:191 — the GNOME hotkey command permanently executes a repo-tracked script through the ~/.local/share symlink chain, making the primary checkout a persistence/execution surface: any commit landing in tools/voice-dictation/ changes what Super+Shift+V runs with no reinstall step. Inherent to the design, but worth an explicit note in the README security posture.
- [P3] scripts/agents/install-voice-dictation.sh:193 — ensure_hotkey sets the binding without checking whether another GNOME custom keybinding already claims the same accelerator (<Super><Shift>v); a silent conflict leaves whichever binding GNOME prefers winning with no diagnostic.
- [P3] tools/voice-dictation/transcribe.py:33 — WhisperModel is instantiated on every hotkey press, so each dictation pays full model load (seconds on CPU for base.en) before transcription starts; acceptable for v1 but the dominant latency cost.
- [P3] tools/voice-dictation/codex-dictate.sh:901-913 — ensure_private_state_dir has a narrow TOCTOU window between the symlink check and mkdir -p in the world-writable ${TMPDIR:-/tmp} fallback path; largely mitigated by the post-mkdir `-O` ownership check and by XDG_RUNTIME_DIR being the primary path, but mkdir with an explicit mode plus a post-hoc lstat would close it fully.

### Suggestions
- Clamp or derive the probe timeout from DICTATE_PROBE_SECONDS (e.g. timeout $((seconds+3))) and emit a distinct reason when `timeout` itself is absent, so misdiagnosis of 'no usable capture device' can't mask a missing dependency.
- Point detect_helper at ${install_root} rather than ${repo_root} in the installer so install-time and runtime detection always execute the same file.
- In ensure_hotkey, scan existing custom-keybindings for a duplicate `binding` value and warn when Super+Shift+V is already taken.
- Consider a small persistent-daemon or model-cache mode for transcribe.py later to cut per-dictation latency; document expected first-press latency in the README meanwhile.
- The test harness patterns here (stub-bin PATH injection, executing the actual stored gsettings command, static mode/parse contracts) are strong and reusable — worth promoting into a shared shell-test skill or lib per the promote-generalizable-findings rule.

### Questions for Author
- Is the DICTATE_BOOTSTRAP_INSTALL=1 path (uv pip install into the first discovered interpreter, likely a conda base env) intentional as opt-in only, and should it prefer a dedicated venv instead of mutating miniforge/miniconda base?
- The hardcoded python candidate list (~/miniforge3, ~/miniconda3, ~/anaconda3) encodes one machine's conventions — should this be externalized to config per the externalize-config-to-YAML rule, or is the DICTATE_PYTHON override considered sufficient?
- resolve_install_root exits inactive (without writing the inert hotkey) when run from a linked worktree whose primary checkout lacks the tool — is silent no-hotkey the intended UX there, versus printing the primary-checkout rerun instruction it prints in the error string only?
