# Plan: workspace-hub #2653 — WRK-694 Per-session log files in session-logger.sh

**Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2653
**Status:** plan-review
**Tier:** T2 (small hook edit + state file convention; the hook lives in workspace-hub `.claude/hooks/`)
**Transferred from:** digitalmodel#275 on 2026-05-06 (mis-filed; the `session-logger.sh` hook lives in workspace-hub, and the issue body itself designates `Repo: ['workspace-hub']`)

## Context

Issue #275 (WRK-694) modifies `.claude/hooks/session-logger.sh` so each Claude session gets its own log file (`session_YYYYMMDD_HHMMSS.jsonl`) instead of merging all activity for a calendar day into one file. Resumed sessions within a 2-hour idle window must continue writing to the same per-session file; idle-over-2h triggers a new file. The hook must remain <1 second per invocation (raw-write principle). Existing date-based fans-in (e.g., `analyze-sessions.sh`) must continue to work.

The actual hook is **not in digitalmodel** — verified via `find . -name "session-logger.sh"` (empty in digitalmodel). It lives at `/mnt/local-analysis/workspace-hub/.claude/hooks/session-logger.sh` (also `session-governor-check.sh`, `session-review.sh`, `emit-session-quality-signals.sh`). The issue body itself confirms `Repo: ['workspace-hub']`.

**Stale-flag (mis-filed):** This issue should be in `vamseeachanta/workspace-hub`, not `vamseeachanta/digitalmodel`. The plan below is written assuming the executor will work in workspace-hub regardless of where the tracking issue is finally hosted. Recommend transferring the issue to workspace-hub before execution.

The issue's Status field reads `Stage 18: Reclaim (n)` and acceptance bullets are unchecked, but the WRK ledger flow inside the issue body shows stages 1–17 as `done` — so the implementation may have already landed. Verify before assuming open work.

## Plan

### Task 1 — Pre-flight: verify whether the work has already shipped
On workspace-hub, run `git log --oneline -- .claude/hooks/session-logger.sh | head -20` and inspect the current contents. If a per-session implementation has already landed, this issue collapses to a close-as-done with verification (Task 5 only).

### Task 2 — Define the session-id state convention
Create (or extend) a state file at `.claude/state/session-logger.json` containing `{session_id, session_started_at, last_tool_call_at}`. The hook reads this file at start, decides "continue" vs. "new session" based on `now - last_tool_call_at > 7200` (2h idle), updates `last_tool_call_at`, and writes through. State file must be gitignored — confirm `.claude/state/` is already in `.gitignore` (per the issue body, it is).

### Task 3 — Edit the hook
Modify `.claude/hooks/session-logger.sh`:
- On invocation, read `.claude/state/session-logger.json` (or initialize if absent).
- Compute `session_id = session_started_at` formatted as `YYYYMMDD_HHMMSS`.
- Write the log line to `.claude/state/sessions/session_<session_id>.jsonl` AND to `logs/orchestrator/claude/session_<session_id>.jsonl` (the two paths called out in the acceptance list).
- Update `last_tool_call_at` in the state file.
Keep the hot path append-only (`echo >> file`) — no jq, no Python, no per-call file locks beyond `flock` if concurrent appends are a concern. Target: <0.1s typical.

### Task 4 — Backwards-compat for existing fans-in
Audit `scripts/sessions/analyze-sessions.sh` (and any sibling) for hardcoded `session_YYYYMMDD.jsonl` glob assumptions. Update to glob `session_YYYYMMDD*.jsonl` so per-session files are picked up. Add a regression fixture under `tests/sessions/` that sources two synthetic per-session files and confirms the analyzer aggregates them by date.

### Task 5 — Verification scenarios
Drive three end-to-end checks: (a) brand-new session creates a fresh file; (b) resumed session within 2h appends to the same file; (c) tool call after >2h idle starts a new file. Capture timing for each invocation; assert hook duration <1s.

## Acceptance Criteria

- [ ] `.claude/hooks/session-logger.sh` writes per-session files named `session_YYYYMMDD_HHMMSS.jsonl`.
- [ ] Resumed sessions within 2h continue the same file; >2h idle starts a new one.
- [ ] Both log surfaces (`.claude/state/sessions/` and `logs/orchestrator/claude/`) use the same session id.
- [ ] State file at `.claude/state/session-logger.json` is gitignored (verified by `git check-ignore`).
- [ ] Hook execution time <1s on cold and warm invocations (measured with `time`).
- [ ] `scripts/sessions/analyze-sessions.sh` (or current equivalent) handles per-session files via the new glob.
- [ ] Regression fixture covers continuation, new-session, and idle-rollover branches.

## Open questions

- Repo scope: confirm whether to transfer #275 to `vamseeachanta/workspace-hub` and close `digitalmodel#275` with a redirect, or leave the tracker here and execute in the other repo.
- Idle window: 2 hours is the figure in the issue. Should it be configurable via env var (`SESSION_IDLE_SECONDS`)? Cheap to add and useful for tests — recommend yes unless owner objects.
