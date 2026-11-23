## Plan posted for user review — #2406 Codex dispatch stdin-hang fix

**Plan:** [`docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md`](https://github.com/vamseeachanta/workspace-hub/blob/main/docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md) — v3, T2

**Root cause confirmed:** `scripts/review/submit-to-codex.sh` dispatches via `codex exec "$prompt_text"` — positional argv. When the script's stdin is an unconsumed non-tty pipe inherited from an orchestrator caller, `codex` blocks waiting for stdin it will never receive, producing the observed "Reading additional input from stdin..." hang (exit 124 at 300s and 600s). The natural experiment during this session's reviews confirmed the threshold: the plan itself at ~33 KB is right at the hang boundary.

**Fix (Deliverable):**
- Pipe prompt via stdin using `printf '%s' "$prompt" | codex exec - …` — the CLI's documented "read from stdin" contract.
- Add runtime version probe: on older `codex` CLI without stdin support, hard-fail with new exit code 7. **No silent argv fallback** (that would reintroduce the bug). Cached at script scope — probe runs exactly once per invocation.
- Preserve all existing error classification, exit codes (1/2/3/5/6), compact-retry logic, and renderer pipeline.
- Privacy side-benefit: plan content no longer exposed in `ps -ef` argv.

**Tests:**
- T26: argv does not contain fixture body.
- T27: stdin equals FULL_PROMPT byte-for-byte (`cmp -s`).
- T28: compact-retry also uses stdin.
- T29: pipefail + SIGPIPE preserves codex exit code 3.
- T30: older codex CLI hard-fails with exit 7 (no argv fallback).
- T31: version probe cached — called once per script invocation.
- T32 + T33: exit codes 5 (NO_OUTPUT) and 6 (renderer fail) preserved.
- Existing 22 tests (T01–T13, T17–T25) all still pass.

**Adversarial review ledger:**

| Iter | Claude | Codex | Gemini |
|---|---|---|---|
| 1 | MINOR | MAJOR (Class A) | MAJOR (Class A) |
| 2 | MINOR | MAJOR (Class A — new) | MAJOR (Class B only) |
| 3 | APPROVE (self) | MAJOR (Class A: 2 internal-consistency contradictions + Class B) | MAJOR (Class B only — self-circular, resolves at #2405) |

v1→v2 fixed iter-1 Class A (compact-retry logic, operating-model checks, #2405 dep wording, threat model, AC↔test matrix).
v2→v3 fixed iter-2 Class A (removed argv fallback, marked README as already-done, cited operating-model source, tightened T27, added T31–T33 for exit-code coverage).
**v3→v3-final (post-iter-3, inline cleanup — not a new design iteration):** fixed 2 P1 internal-consistency contradictions Codex iter-3 caught — Files-to-Change row + Risks section had stale "argv-path fallback" language carried over from v2 while v3 Pseudocode said "hard-fail exit 7". All now consistently say hard-fail. Also cleanly split AC into automated-test-backed criteria vs release-gate operational checks (per iter-3 Codex P1).

Class B "unverified live state" findings are the #2405 meta-class — reviewer sandbox cannot check live repo state; resolves when #2405 attestation lands. Acknowledged and deferred.

**Not a dependency on #2405.** Executable independently against current `main`.

**Iteration cap:** 3/3 consumed per `issue-planning-mode` skill. No further cross-review iterations without explicit user direction.

**Requesting user approval.** After `status:plan-approved`:
1. Add `.planning/plan-approved/2406.md` marker.
2. Implement via TDD: tests first (T26–T33), then `run_codex_exec` rewrite + version probe.
3. Full suite must stay green.
4. Live repro against any large plan in `docs/plans/` ≥20 000 chars.

Plan artifacts on `origin/main`:
- v1: commit `a73ec66f6`
- v2: commit `e5446f6d6`
- v3: commit `5d7552c4d`
- v3-final cleanup (swept into auto-sync): commits `c47f57a20`, `94950ba88`

Review artifacts at `scripts/review/results/`:
- iter-1: `2026-04-20-plan-2406-{claude,codex,gemini}.md`
- iter-2: `2026-04-20-v2-plan-2406-{claude,codex,gemini}.md`
- iter-3: `2026-04-20-v3-plan-2406-{claude,codex,gemini}.md`
