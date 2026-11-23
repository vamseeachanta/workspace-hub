# Disagreement report — plan #3403 (2026-07-08)

## Verdicts

| Provider | Verdict |
|---|---|
| claude-r1 | MINOR |
| claude | MINOR |
| codex-r1 | MAJOR |
| codex | MAJOR |
| disagreement-r1 | | Provider | Verdict | |
| gemini-r1 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude-r1

(no findings unique to this provider)

### claude

- **Artifact Map cites two zero-byte review files, contradicting the plan's own AC #11.** Rows at plan lines 156–157 point at `scripts/review/results/2026-07-08-plan-3403-claude.md` and `…-codex.md` — both are 0 bytes on disk. The real reviews are the `-r1.md` files cited in the header (line 10). The plan's acceptance criterion requires "non-empty artifacts or explicit UNAVAILABLE artifacts"; as written, the Artifact Map fails its own gate. Fix the map to the `-r1` names (and delete or fill the empty stubs), and note that the fullest Claude artifact is actually `2026-07-09-plan-3403-claude.md`, which neither header nor map references.
- **The r1 gate is failed by the plan's own account and no r2 artifact exists yet.** §Adversarial Review Summary states "Overall result: FAIL — r1 MAJOR from Codex; revised plan requires re-review before `status:plan-review`" (line 282). `scripts/review/results/` contains no r2 for the revised plan text. Until a re-review round exists (this review can serve as the Claude leg), the plan cannot be advanced to `status:plan-review` — the status header (`draft`) is currently correct and must stay that way.
- **AC #5 invokes the helper as a CLI, but the plan specifies it only as a sourced library.** Resource Intel (lines 36–38) mandates "a small sourced shell library so tests can stub `arecord`…"; AC #5 (line 263) runs `bash scripts/agents/lib/voice-dictation-detect.sh --choose`. The Pseudocode (lines 171–183) defines functions only — no argv dispatch, no `--choose` flag, no output contract (stdout = device string? exit code on inactive?). The dual-mode (source-vs-execute) entrypoint must be specified or the acceptance command is untestable as written. Related edge: if `--choose` returns empty with rc 0 (the pseudocode's inactive contract), the `&&` chain still runs `dictate-test.sh 5 ""`, which degrades to a confusing `arecord -D ""` failure instead of a clear inactive message.
- **The "inert notifier command" is named but never defined** (Pseudocode line 199; test at line 246). On a hotkey press there is no terminal — an `echo` is invisible, and `notify-send` may be absent or fail in headless/non-GNOME sessions the plan itself flags as a risk (line 300). Specify the concrete inert command and its fallback, otherwise the test `test_inactive_install_replaces_stale_hotkey_with_inert_warning` has no defined expected value to assert against.
- **Python-selection policy for the runtime binding is unspecified.** The live binding hardcodes `DICTATE_PYTHON=/home/vamsee/miniforge3/bin/python3`; Pseudocode line 201 says only "ensure faster-whisper exists in a selected Python." Selected how — miniforge, `uv run`, system python3? The Codex r1 bare-`python3` finding was fixed only for the *acceptance* `py_compile` command, not for the installer's runtime interpreter choice, and the TDD list has no test covering interpreter selection or the faster-whisper presence check.
- **Stale `__pycache__` residue has no disposition.** The plan documents `tools/voice-dictation/__pycache__/transcribe.cpython-313.pyc` as evidence (line 81) but Files to Change (lines 218–231) contains no row to delete or gitignore it. Restoring `transcribe.py` next to a stale 3.13 bytecode file is harmless functionally but is exactly the residue class the pre-completion cleanup audit gate blocks on — plan for its removal explicitly.
- **New test is not wired into any runner or CI.** `grep -rln "agents/tests" .github/workflows/` returns nothing, and there is no `run-all` script in `scripts/agents/tests/`. The plan's acceptance runs the test file directly, which matches existing repo practice, but nothing prevents the test from silently rotting; at minimum state that manual invocation is the intended (and only) execution path.

### codex-r1

(no findings unique to this provider)

### codex

- Plan promises a “usable” ALSA device but only specifies “first listed device” selection. `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:164` says the rollout “chooses a usable ALSA capture device”; `:180-183` only parses `arecord -l` and returns the first concrete device; `:242` explicitly tests that no `arecord -D default` probe is invoked, but there is no replacement test proving the selected concrete `plughw:N,M` can actually open/record before the installer binds it. This can still bind `Super+Shift+V` to a failing capture device, which is the core failure class the plan is supposed to eliminate.
- Review artifact references are internally inconsistent and point partly at empty files. The plan header names `scripts/review/results/2026-07-08-plan-3403-claude-r1.md`, `codex-r1.md`, `gemini-r1.md`, and `disagreement-r1.md` at `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:10`, but the Artifact Map names non-r1 paths at `:156-158`. The non-r1 Claude and Codex files exist and are 0 bytes (`scripts/review/results/2026-07-08-plan-3403-claude.md`, `scripts/review/results/2026-07-08-plan-3403-codex.md`). A gate or reviewer following the Artifact Map can mistake empty files for review evidence.
- The plan still self-declares a failed review state. `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:282` says `Overall result: FAIL -- r1 MAJOR from Codex; revised plan requires re-review before status:plan-review`. That may have been true before this rerun, but if left in the plan it remains a stale blocker embedded in the artifact itself and conflicts with moving the same artifact to plan-review/approval.
- The helper is specified as both a sourced library and an executable CLI without an explicit contract. `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md:35-37` calls for a “small sourced shell library,” while acceptance criterion `:262-263` executes `bash scripts/agents/lib/voice-dictation-detect.sh --choose`. The plan needs to specify the dual-use entrypoint behavior; otherwise an implementation can satisfy the library design while failing the live smoke command.

### disagreement-r1

- A finding is 'unique to X' if its text appears in X's artifact but not
- verbatim in any other provider's artifact.
- ### claude
- ### codex
- ### gemini

### gemini-r1

(no findings unique to this provider)

### gemini

(no findings unique to this provider)
