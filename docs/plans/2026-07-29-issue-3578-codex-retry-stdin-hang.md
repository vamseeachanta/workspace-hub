# Plan for #3578: fix(review) — submit-to-codex.sh compact retry hangs exit 124 'Reading additional input from stdin'

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3578
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-29-plan-3578-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/review/submit-to-codex.sh` — contains `run_codex_exec()` helper that adds `</dev/null` via all three dispatch paths (timeout/perl/bare). The compact retry block (lines ~195–210) calls `run_codex_exec "$COMPACT_PROMPT"` which inherits the `</dev/null` redirect. No standalone test exercises the retry invocation path end-to-end.
- EXISTS: `scripts/review/tests/test_codex_version_guard.sh` — 14 tests covering version guard, pin idempotency, and CLAUDECODE safety net, but **zero tests** exercise the `run_codex_exec` function's stdin-isolation or the compact retry call shape directly.
- EXISTS: `scripts/review/lib/codex-version-guard.sh` — version guard library; sourced by submit-to-codex.sh early; `codex_version_guard_check` may call `codex --version` which itself could inherit stdin under certain environments.
- Gap: No integration test that proves the compact retry path passes `</dev/null` through to the actual codex subprocess when invoked from an orchestrator with a live stdin pipe.

### Standards
| Standard | Status | Source |
|---|---|---|
| POSIX shell stdin inheritance rules | not applicable (bash-internal semantics) | — |

### LLM Wiki pages consulted
- No relevant wiki pages for bash script stdin inheritance patterns.

### Documents consulted

- `docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md` — prior plan for the original stdin-hang fix; documents that the approved fix was adding `</dev/null` to `run_codex_exec`. Notes a deviation: `codex exec - --output-schema … --output-last-message …` hangs even with small stdin input when the `-` positional is used — the workaround is argv delivery + `</dev/null`. Also documents that timeout behaviour is ~135s for a 28K-char plan under the 300s default.
- Issue body #3578 — "two consecutive dispatches hung (exit 124), stderr = 'Reading additional input from stdin'; compact retry (--output-schema/--output-last-message flags) hung. plan-review-fanout's codex leg (different invocation shape) works." Cross-review degraded T3→T2 twice.
- Issue #3294 — the `</dev/null` + CLAUDECODE self-strip mitigation for the original stdin-hang upstream bug (openai/codex#19945). Established that `unset CLAUDECODE` + `</dev/null` was the fix for that class of hang.
- `scripts/review/plan-review-fanout.sh` (implicit, mentioned in issue body) — the fanout invocation shape does NOT hang; its codex leg differs from submit-to-codex's retry path. Diff in invocation shape is the diagnostic lever.

### Gaps identified

- No test that verifies `run_codex_exec` receives `</dev/null` when called from within the compact retry block (the `: > "$raw_file"` + retry path).
- Unknown whether codex v-current (at time of issue, 2026-07-17) re-introduced openai/codex#19945 — the version guard ceiling may need updating if upstream reverted the fix.
- Unknown whether the `timeout` binary itself propagates the `</dev/null` correctly on the installed codex version (some wrapper binaries ignore fd-level redirects on the exec'd child).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-29T00:00:00Z via `gh issue view`):
- `#3578` — OPEN — fix(review): submit-to-codex.sh hangs — codex exec exit 124 'Reading stdin'
- `#3294` — CLOSED — original `</dev/null` mitigation (referenced in issue body as "in place")
- `#2406` — CLOSED — prior stdin hang fix plan (2026-04-20, deviation documented)

**File existence** (verified 2026-07-29 via live checkout at `/mnt/local-analysis/workspace-hub`):
- EXISTS: `scripts/review/submit-to-codex.sh`
- EXISTS: `scripts/review/tests/test_codex_version_guard.sh`
- EXISTS: `scripts/review/lib/codex-version-guard.sh`
- MISSING (new — this plan creates): `scripts/review/tests/test_submit_codex_retry.sh`

**Line excerpts** (`submit-to-codex.sh` compact retry block):
```bash
# One compact retry when full payload returns no usable output.
if [[ "$exec_exit" -ne 0 || ! -s "$raw_file" ]]; then
  compact_text="${CONTENT_TEXT:0:CODEX_COMPACT_RETRY_CHARS}"
  COMPACT_PROMPT="..."
  : > "$raw_file"
  exec_exit=0
  run_codex_exec "$COMPACT_PROMPT" || exec_exit=$?  # ← run_codex_exec has </dev/null
fi
```

**Gap proofs**:
- `grep -c "compact_retry\|run_codex_exec" scripts/review/tests/test_codex_version_guard.sh` → 0 → confirms no test covers the retry path.

**Reproduction proofs**:
N/A — this plan targets a test-coverage gap and a potential upstream version regression. The issue body provides the repro context; a live repro requires a specific codex version and orchestrator invocation shape that cannot be deterministically reproduced in a plan-drafting context. Plan-time reproduction of an environment-specific hang is out of scope; TDD approach covers the verifiable invariants (stdin isolation, retry argv shape).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-29-issue-3578-codex-retry-stdin-hang.md |
| New test file | `scripts/review/tests/test_submit_codex_retry.sh` |
| Modified: version guard test | `scripts/review/tests/test_codex_version_guard.sh` |
| Implementation | `scripts/review/submit-to-codex.sh` (if code fix needed post-diagnosis) |
| Plan review — Claude | scripts/review/results/2026-07-29-plan-3578-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-29-plan-3578-codex.md |
| Plan review — Agy | scripts/review/results/2026-07-29-plan-3578-agy.md |

---

## Deliverable

A new integration test (`test_submit_codex_retry.sh`) that proves the compact retry path correctly passes `</dev/null` to the codex subprocess even when the caller holds a live stdin pipe, plus a version guard ceiling bump or code fix if the diagnosis reveals a regression.

---

## Pseudocode

```
# Phase 1 — Diagnose (T2 diagnostic step before deciding if code changes needed)

compare_invocation_shapes():
    # Read fanout.sh codex leg invocation (known-good)
    fanout_args = extract_argv_from(plan_review_fanout.sh, provider=codex)
    # Read submit-to-codex.sh compact retry invocation via run_codex_exec
    retry_args = extract_argv_from(submit-to-codex.sh, section=compact_retry)
    # Diff: if fanout uses a different flag order / missing </dev/null → root cause confirmed
    return diff(fanout_args, retry_args)

check_version_guard_ceiling():
    installed_version = codex --version
    if installed_version > CODEX_VERSION_GUARD_CEILING:
        return "ceiling needs bump — version may have re-introduced #19945"
    else:
        return "version within guard — bug is in retry path, not upstream"

# Phase 2 — Test-first coverage

test_retry_stdin_isolation():
    # Create a mock codex that:
    #   - prints "hanging" if it can read from stdin (stdin not /dev/null)
    #   - exits 0 with valid JSON output if stdin is /dev/null
    mock = create_mock_codex(stdin_sensitive=true)
    # Invoke submit-to-codex.sh with a content file that triggers compact retry
    #   (first invocation → NO_OUTPUT, retry fires)
    result = invoke_with_open_stdin_pipe(submit-to-codex.sh, mock, content_file)
    assert result.exit == 0                    # retry succeeded
    assert "hanging" not in result.stderr      # stdin was /dev/null

test_retry_fires_when_first_no_output():
    # Verify retry logic: first run exits 5 (NO_OUTPUT), retry should fire
    mock = create_mock_codex(first_invocation=exits_5, second_invocation=exits_0_with_json)
    result = invoke(submit-to-codex.sh, mock, content_file)
    assert mock.invocation_count == 2
    assert result.exit == 0

test_retry_prompt_is_truncated():
    # Verify COMPACT_PROMPT is ≤ CODEX_COMPACT_RETRY_CHARS chars
    # (ensures retry does not re-create an oversized payload)
    ...
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/review/tests/test_submit_codex_retry.sh` | TDD: stdin isolation + retry-fires test |
| Modify | `scripts/review/submit-to-codex.sh` | Code fix if diagnosis reveals hang in retry path |
| Modify | `scripts/review/lib/codex-version-guard.sh` | Bump ceiling if upstream regression confirmed |
| Update | docs/plans/README.md | Add plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_retry_stdin_not_inherited | stdin `/dev/null` reaches codex even with caller pipe open | open stdin pipe + NO_OUTPUT first run | exit 0, mock sees no stdin bytes |
| test_retry_fires_on_no_output | compact retry triggers when first invocation exits 5 | mock exits 5 first call, 0+JSON second | exit 0, mock called twice |
| test_retry_fires_on_nonzero_exit | compact retry triggers when first invocation exits non-0 | mock exits 124 first call, 0+JSON second | exit 0, mock called twice |
| test_retry_truncates_payload | COMPACT_PROMPT is at most CODEX_COMPACT_RETRY_CHARS chars | 50K-char content file | mock receives ≤ 24000 chars |
| test_no_retry_on_valid_first_output | retry does NOT fire when first invocation produces valid JSON | mock exits 0 with valid JSON | mock called exactly once |
| test_full_path_timeout_preserves_devnull | `timeout` wrapper passes `</dev/null` to child subprocess | mock that reads stdin + open caller pipe | mock sees EOF immediately |

---

## Acceptance Criteria

- [ ] All new tests pass: `bash scripts/review/tests/test_submit_codex_retry.sh`
- [ ] All existing tests still pass: `bash scripts/review/tests/test_codex_version_guard.sh`
- [ ] If version ceiling bump: ceiling updated in `scripts/review/lib/codex-version-guard.sh` + pin env aligned
- [ ] If code fix: `submit-to-codex.sh` passes shellcheck with no new warnings
- [ ] Cross-review no longer exits 124 on a 12KB plan file (verified by running fanout against a real plan file if codex is available; or documented as "pending live codex verification" if not)
- [ ] Review artifacts posted to `scripts/review/results/2026-07-29-plan-3578-*.md`

---

## Adversarial Review Summary

<!-- Filled in after adversarial review completes. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | — |
| Codex | TBD | — |
| Agy | TBD | — |

**Overall result:** TBD

---

## Risks and Open Questions

- **Risk:** The actual hang may be a codex v-current regression that requires a ceiling bump in the version guard, not a code fix in submit-to-codex.sh. If so, the plan pivots from "write test + fix code" to "write test + update ceiling" — scope is the same size.
- **Risk:** Mock-based tests for stdin isolation may pass even if the live codex binary does not honour `</dev/null` correctly on a specific kernel/libc version. Acceptance criterion requires a live codex run if available.
- **Open:** Should the retry path also `unset CLAUDECODE` before the second invocation? The first invocation does `unset CLAUDECODE` at script top, but a future refactor that re-exports it could resurrect the #2684 hang. Flag for user during approval — low priority but worth pinning.
- **Open:** The issue says "plan-review-fanout's codex leg (different invocation shape) works" — if the fanout shape is clean, should the retry path be refactored to match the fanout shape? Or is the minimum fix just confirming `</dev/null` is correct? User to decide scope.

---

## Complexity: T2

New test file (6 tests) + targeted code or version guard fix. Two files changed, tests required. No architecture changes.
