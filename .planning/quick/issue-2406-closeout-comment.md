## #2406 closed — Codex dispatch stdin-hang fixed

**Fix landed.** Implementation matches the approved v3-final plan.

**Root cause confirmed during implementation:** `scripts/review/submit-to-codex.sh`'s `run_codex_exec()` dispatched the prompt as a positional argv to `codex exec`. When the script's stdin was an unconsumed non-tty pipe inherited from an orchestrator caller, `codex` blocked waiting for stdin that would never arrive — producing the observed "Reading additional input from stdin..." hang (exit 124 at 300s and 600s).

**Fix:**
- `printf '%s' "$prompt" | codex exec - …` — uses the CLI's documented stdin contract.
- One-time version probe cached in `_CODEX_STDIN_SUPPORTED`. On older codex CLIs without documented stdin support, script hard-fails with new exit code 7 and a stderr upgrade instruction. **No argv fallback** (that path is the bug).
- `return "${PIPESTATUS[1]}"` preserves codex's exit code across the new pipe under `set -euo pipefail`.
- All three dispatch branches (timeout / perl alarm / bare) fixed with identical semantics.
- Privacy side-benefit: prompt content no longer exposed via `ps -ef` argv.

**Tests:** 59/59 pass.
- 22 existing tests (T01–T13, T17–T25) — regression-clean.
- 8 new test blocks (T26–T33) covering argv-vs-stdin transport, compact-retry parity, pipefail exit-3 fidelity, version-probe hard-fail, probe-cache single-invocation, exit-5 NO_OUTPUT, exit-6 renderer-fail.
- Deterministic 24 000-char fixture at `tests/review/fixtures/codex-large-prompt.txt`.

**Live repro (release-gate check):** __LIVE_REPRO_PLACEHOLDER__

**Commits:**
- Plan v1→v3-final: `a73ec66f6`, `e5446f6d6`, `5d7552c4d`, + auto-sync cleanups `c47f57a20` / `94950ba88`.
- Implementation + tests + fixture: __IMPL_COMMIT_PLACEHOLDER__.

**Sources consumed** (per #2208 retrieval contract):
- `scripts/review/submit-to-codex.sh` — buggy `run_codex_exec` at lines 162–180, guards at 215–227, retry at 229–247.
- `codex exec --help` CLI contract (verified via `codex exec --help`).
- `tests/review/test-submit-scripts.sh` pattern — `make_mock` + assertion helpers.
- Memory: `feedback_codex_needs_pushed_artifact.md`, `feedback_cross_provider_review_payoff.md`.
- `.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md` — identified this as Action 1 leverage point.

**Promotion candidates:** none — this is harness infrastructure, not doc-intel knowledge. The argv-vs-stdin transport pattern is already covered by T26/T27 regression tests and does not require promotion from L5 transient to L3 durable knowledge per #2209.

**Deferred follow-ups** (from iter-3 Codex P2 findings):
- Expand threat model with malicious `CODEX_BIN` / `PATH` trust / help-text spoofing analysis.
- Formalize `PIPESTATUS[1]` shell-structure specification beyond the current inline note.

These are not blocking and can be filed as separate issues if desired.

**Plan of record:** [`docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md`](https://github.com/vamseeachanta/workspace-hub/blob/main/docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md)

Closing as delivered.
