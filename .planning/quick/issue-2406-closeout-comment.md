## #2406 closed — Codex dispatch stdin-inheritance hang fixed

**Fix landed on `main`.** Implementation deviates from the approved v3-final plan per user-approved Option 1 during live testing.

**Root cause (confirmed via live repro):** `scripts/review/submit-to-codex.sh`'s `run_codex_exec` invoked `codex exec "$PROMPT" ...` without redirecting stdin. When the script ran under an orchestrator (cross-review.sh or another agent harness), it inherited the caller's unconsumed non-tty stdin pipe. `codex` then blocked reading that pipe forever — the reported "Reading additional input from stdin..." hang (exit 124 at 300s and 600s).

**Fix:** add `</dev/null` to each of the three dispatch branches (`timeout` / `perl alarm` / bare) in `run_codex_exec`. codex now sees an immediate EOF on stdin instead of blocking on the caller's pipe. All other behavior — error classification, exit-code map, compact-retry logic, renderer pipeline, `CODEX_MAX_PROMPT_CHARS` guards — is preserved verbatim.

**Plan deviation (documented in the plan's "Post-implementation deviation" section):** the approved v3 plan proposed piping the prompt via stdin with the `-` sentinel and adding a runtime version probe. Live testing revealed codex v0.121.0 has a separate bug where `exec -` combined with `--output-schema` + `--output-last-message` hangs even with small stdin input — the planned approach does not work against the real CLI. The `</dev/null` + argv variant is the minimal change that actually fixes the hang. User approved this deviation mid-session (message "1" selecting Option 1 from three options presented after live repro failure).

**Live repro verification** (28 KB #2405 v3 plan against real codex CLI):
- **Pre-fix:** exit 124 at both 300s and 600s (the original bug)
- **Post-fix:** exit 0 in **2m15s**, producing **6870 bytes of valid structured-JSON MAJOR review**

**Tests: 59/59 pass.**
- 22 existing tests (T01–T13, T17–T25) unchanged — regression-clean.
- New coverage:
  - **T26:** caller's unconsumed stdin pipe is not inherited by codex (codex sees 0 bytes; caller sentinel is not forwarded).
  - **T27:** dispatch completes exit 0 even when the caller provides a dangling stdin pipe (the original hang scenario).
  - **T28:** compact-retry path also isolates stdin from caller on both call-1 and call-2.
  - **T29:** codex exit 3 (quota) propagates as script exit 3 — unchanged.
  - **T30:** timeout classification keeps exit 124 and emits guidance (added by linter sweep).
  - **T31:** transport classification keeps exit and emits guidance (added by linter sweep).
  - **T32:** NO_OUTPUT path → exit 5 — unchanged.
  - **T33:** renderer-fail path → exit 6 — unchanged.
- Deterministic fixture: `tests/review/fixtures/codex-large-prompt.txt` (24 400 chars).

**Commits:**
- Plan v1 → v3-final + adversarial review artifacts: `a73ec66f6`, `e5446f6d6`, `5d7552c4d` + auto-sync cleanup sweeps.
- Implementation + tests + fixture + plan amendment: landed via `d77e106a3` (auto-sync) + `691a34556` (explicit fix commit).

**Sources consumed** (per #2208 retrieval contract):
- `scripts/review/submit-to-codex.sh:162-180` — the buggy `run_codex_exec` function.
- `codex exec --help` CLI contract (verified live during diagnosis).
- `tests/review/test-submit-scripts.sh` pattern — `make_mock` harness + assertion helpers.
- Memory: `feedback_codex_needs_pushed_artifact.md`, `feedback_cross_provider_review_payoff.md`.
- `.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md` — identified this as Action 1 leverage point.

**Promotion candidates:** none — this is harness infrastructure, not doc-intel knowledge. The stdin-inheritance pattern is covered by T26/T27/T28 regression tests and does not require promotion from L5 transient to L3 durable knowledge per #2209.

**Key lesson surfaced** (candidate memory entry for future sessions): mock-based tests for external-CLI fixes can pass while live invocation fails when the mock is more permissive than reality. Always run a live repro against the actual external tool before closing such bugs — this is what exposed the `-` + `--output-schema` codex bug that invalidated the approved plan.

**Deferred follow-ups** (from iter-3 P2 findings, not blocking):
- Expand threat model with malicious `CODEX_BIN` / `PATH` trust / help-text spoofing analysis.
- The codex `exec -` + `--output-schema` hang could be filed upstream with openai/codex.

Plan of record: [`docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md`](https://github.com/vamseeachanta/workspace-hub/blob/main/docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md) — status `implemented-with-deviation`.

Closing as delivered.
