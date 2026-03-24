# WRK-657 Plan Review Input

## Work Item
- ID: WRK-657
- Title: fix(review): harden submit-to-claude.sh timeout cleanup and liveness
- Route: B (medium)
- Repo: workspace-hub
- Related: WRK-642, WRK-647

## Problem

`scripts/review/submit-to-claude.sh` has two compounding bugs:

1. **Process leak**: `timeout` sends SIGTERM to the direct `claude` child only. Any sub-processes
   spawned by `claude` stay alive and leak resources between review runs.

2. **Silent exit-0 on timeout**: after the retry loop exhausts, the script falls off the end
   and exits 0 — not 1, not 124. The `|| {}` handler in `cross-review.sh` never fires on
   timeout. NO_OUTPUT classification is reached only accidentally via the "timed out" text
   regex in `validate-review-output.sh`.

## Proposed Changes (3 phases)

### Phase 1 — submit-to-claude.sh

- Add `CLAUDE_WATCHDOG_PGID=""` module-level variable.
- Add `cleanup_claude_watchdog()`: sends SIGTERM to the full process group
  (`kill -- -$pgid`), sleeps 1 s, then SIGKILL; logs both steps to stderr.
- Modify `run_claude_once()`: if `setsid` is available, launch
  `setsid timeout $N claude …` as a background job (`&`), record job PID as PGID,
  `wait $!`, call `cleanup_claude_watchdog` on exit 124.
- Fallback (no `setsid`): keep existing subshell path; log warning on exit 124.
- Add `LAST_EXIT_CODE` tracking in retry loop; replace fall-off-end with
  `exit "${LAST_EXIT_CODE:-1}"`.
- Exit codes: 0 = valid review, 124 = watchdog timeout, 1 = other failure.

### Phase 2 — tests/test-submit-to-claude-timeout.sh (new, written first)

- Uses a fake `claude` stub placed earlier in `$PATH` — no real Claude CLI required.
- Test 1: wrapper exits 124 when `CLAUDE_TIMEOUT_SECONDS=2` and stub sleeps forever.
- Test 2: no process from the stub's PGID remains after timeout.
- Test 3: result file contains `WATCHDOG` marker on timeout.
- Test 4: wrapper exits 0 when stub outputs a valid JSON review.
- Test 5: wrapper exits 1 when stub exits 1 immediately (non-timeout failure).

### Phase 3 — cross-review.sh

- Replace `|| { echo "# Claude review failed" > $result_file; }` with explicit exit-code
  capture: `claude_exit=0; … || claude_exit=$?`.
- If `claude_exit -eq 124`: call `preserve_raw_result` (keeps watchdog log), write
  `"# Claude returned NO_OUTPUT (watchdog timeout)"` — skip overwriting with generic stub.
- If `claude_exit -ne 0` and not 124: existing stub write behaviour.
- `validate-review-output.sh` already classifies `"timed out"` as NO_OUTPUT — no change needed.

## Files Changed

| File | Change | Phase |
|------|--------|-------|
| `scripts/review/submit-to-claude.sh` | setsid path, watchdog cleanup, exit codes | 1 |
| `scripts/review/tests/test-submit-to-claude-timeout.sh` | New — 5 regression tests | 2 (first) |
| `scripts/review/cross-review.sh` | Capture claude_exit; map 124 → NO_OUTPUT | 3 |

Not changed: `validate-review-output.sh`, `submit-to-codex.sh`, `submit-to-gemini.sh`.

## Acceptance Criteria

- [ ] `submit-to-claude.sh` kills the child process group on timeout and logs teardown
- [ ] Exit codes: 0 = success, 124 = timeout, 1 = other failure
- [ ] 5 regression tests pass (timeout exit, no orphans, WATCHDOG log, success, failure)
- [ ] `cross-review.sh` maps exit 124 → NO_OUTPUT explicitly; preserves watchdog log
- [ ] Legal scan passes

## Key Design Decisions

- Use `setsid` to isolate the process group; fall back to subshell if unavailable.
- PGID == background job PID when started with `setsid` — this is the kill target.
- `sleep 1` between SIGTERM and SIGKILL is intentional; real claude runs don't need
  graceful shutdown here so SIGKILL after 1 s is safe.
- `validate-review-output.sh` intentionally unchanged — its regex handles `"timed out"` already.
- Codex/Gemini wrappers not in scope for this WRK — separate item if needed.

## Risks

1. `setsid` not available → fallback path with warning (tested separately).
2. PGID from background job differs from expected → verified with `ps -o pgid= -p $!` in tests.
3. `sleep 1` too short for slow claude shutdown → SIGKILL is hard kill, acceptable here.
4. `cross-review.sh` claude_exit capture touches active code path → minimal structural change.
