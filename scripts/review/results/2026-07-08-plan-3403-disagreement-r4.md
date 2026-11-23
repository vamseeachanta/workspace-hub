# Disagreement report — plan #3403 (2026-07-08)

## Verdicts

| Provider | Verdict |
|---|---|
| claude-r1 | MINOR |
| claude-r2 | MINOR |
| claude-r3 | **MINOR** |
| claude | **MAJOR** |
| codex-r1 | MAJOR |
| codex-r2 | MAJOR |
| codex-r3 | MAJOR |
| codex | MAJOR |
| disagreement-r1 | | Provider | Verdict | |
| disagreement-r2 | | Provider | Verdict | |
| disagreement-r3 | | Provider | Verdict | |
| gemini-r1 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r2 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini-r3 | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude-r1

(no findings unique to this provider)

### claude-r2

(no findings unique to this provider)

### claude-r3

(no findings unique to this provider)

### claude

- **Acceptance criterion hardcodes the wrong GNOME keybinding slot.** Plan AC (line 319) verifies `...custom-keybindings/custom0/ command`, but the live machine's binding lives at slot `codex-dictate/`, not `custom0/` — `gsettings get ... custom-keybindings` returns `['.../custom-keybindings/codex-dictate/']`. As written, the AC command queries a nonexistent slot and fails even against a correct installer. Worse, the pseudocode (`bind GNOME hotkey with env ...`, line 235) never specifies which slot the installer writes or whether it reuses/migrates the existing `codex-dictate` slot — if it creates `custom0` fresh, it leaves a duplicate stale `codex-dictate` binding on `Super+Shift+V`, the exact failure mode the plan claims to fix (line 69).
- **`test_stale_pycache_removed` (line 301) tests machine-local untracked state, not repo state.** The `.pyc` is untracked (`git ls-files` empty), so "main has stale `__pycache__` residue" (line 70) and evidence line 85 mischaracterize working-tree residue as repo state. The test's precondition ("Current `tools/voice-dictation/__pycache__/` exists") holds only on ace-linux-1; on any fresh checkout it fails or vacuously passes. This contradicts the plan's own "deterministic tests" goal (line 71). Deleting the residue is local cleanup, and the real repo-level fix — ensuring `__pycache__/` can't recur (`.gitignore` coverage) — is absent from Files to Change.
- **Headless/non-GNOME guard exists only in Risks, not in the contract.** Risk (line 375) acknowledges GNOME binding can fail on headless sessions and prescribes graceful skip + manual command, but the pseudocode happy path (line 235) binds unconditionally, and no TDD test covers "mic + Python ready, `gsettings` absent." Every gsettings test stubs it as present. An untested prescribed behavior on a repo whose bootstrap runs on headless machines (ace-linux-2 is headless per memory) is a gap in the test list, not just a risk note.
- **The uv fallback install path is underspecified.** Pseudocode line 227: "attempt user-space faster-whisper install into the first eligible interpreter with uv" — "first eligible" is undefined when no candidate imports `faster_whisper`, and `uv pip install --python <non-venv interpreter>` (e.g., miniforge base) has known-fragile semantics in this ecosystem (memory: uv is broken for several repos; digitalmodel policy is `.venv/bin/python` not `uv run`). The tests stub the install outcome (lines 298–299) so the actual invocation form is never pinned; implementation can satisfy the tests with a command that fails on the live machine.
- **Untracked review-artifact state contradicts the plan's own revision claim.** The plan's header and Artifact Map cite 12 r1–r3 artifacts, and revision note line 363 says stale canonical rows were "replaced" — but the dead zero-byte canonical files (`2026-07-08-plan-3403-{claude,codex,gemini,disagreement}.md`, `...codex.md.err`, plus orphan `2026-07-09-plan-3403-claude.md`) still sit in `scripts/review/results/`, and none of the 3403 artifacts (dead or live) are git-tracked. If the plan lands without committing the r-stamped artifacts and disposing of the zero-byte residue, the header's "Review artifacts" row cites files unreachable from any other machine — the same defect class as the branch-only handoff the plan itself fixes (line 59). No Files-to-Change row covers this.
- Checks run with **no** finding: branch/commit existence and file inventory; `rm -rf` and `/proc/asound/cards` claims against the branch installer; bootstrap section-2.10 claim; issue #3403 state/labels; #140 closed; `dictate-test.sh` arg order vs AC; handoff branch-only status; r1–r3 verdict table vs actual artifact contents; plan-index row; cited standards/scripts existence; helper `--choose` exit-code contract consistency between pseudocode (line 247) and test (line 293).

### codex-r1

(no findings unique to this provider)

### codex-r2

(no findings unique to this provider)

### codex-r3

(no findings unique to this provider)

### codex

- Plan acceptance criterion lines 317-320 hardcode the GNOME binding path `.../custom-keybindings/custom0/`, but live retrieval shows the configured binding list is `['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/']`; `custom0` name/command/binding are all empty, while `codex-dictate` contains `Codex Voice Dictation`, the launcher command, and `<Super><Shift>v`. The prior branch installer also uses `kpath="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/"`. This acceptance check will fail against the intended implementation path and does not verify the actual live binding.

### disagreement-r1

(no findings unique to this provider)

### disagreement-r2

(no findings unique to this provider)

### disagreement-r3

- ### claude-r2
- ### codex-r2
- ### disagreement-r2
- ### gemini-r2

### gemini-r1

(no findings unique to this provider)

### gemini-r2

(no findings unique to this provider)

### gemini-r3

(no findings unique to this provider)

### gemini

(no findings unique to this provider)
