# Issue #1839 — Phase 2b Implementation Review

## Commit
`76c7af5ce` — `feat(governance): wire runtime enforcement into hooks (#1839)`

## What was implemented
Wire `check_session_limits()` from `session_governor.py` into Claude Code's PreToolUse hook system, making the 200-call tool ceiling an active enforcement gate rather than a standalone utility.

## Files changed (4 files, +222/-8)

| File | Change |
|------|--------|
| `.claude/hooks/session-governor-check.sh` | **New** — PreToolUse hook with fast-path counter + governor delegation |
| `.claude/settings.json` | Registered hook as first PreToolUse entry, broad tool matcher |
| `docs/governance/SESSION-GOVERNANCE.md` | Documented Phase 2b, known gaps, updated remaining phases |
| `tests/work-queue/test_session_governor.py` | 8 new tests (33 total), all pass |

## Architecture decisions

1. **PreToolUse over PostToolUse**: PreToolUse can block tool calls via `{"decision":"block"}` stdout protocol. PostToolUse can only warn.
2. **Fast-path optimization**: Below 160 calls (80% of 200), pure bash counter — zero Python overhead. Only 40 tool calls in a session ever invoke `uv run`.
3. **Daily counter reset**: No reliable session ID in hook env, so counter resets on date change. Conservative but workable.
4. **Error tracking gap**: Passes 0 for `--consecutive-errors` since no signal pipeline exists yet. Documented.
5. **Repo hook protocol**: Uses `{"decision":"block"}` on stdout (not non-zero exit), matching `cross-review-gate.sh` convention.

## Test coverage

- Hook file existence and executable bit
- Hook registration in settings.json  
- Governor exit code mapping (CONTINUE=0, PAUSE=1, STOP=2)
- Fast-path ceiling alignment with governance config (160 = 80% of 200)
- JSON output format validation
- CLI exit code verification via subprocess (all three verdicts)

## Known gaps

| Gap | Impact | Resolution |
|-----|--------|------------|
| Consecutive error tracking | Passes 0 always | Wire into session signal pipeline (Phase 3) |
| Daily vs per-session counter | May undercount across multi-session days | Awaits Claude Code session ID |
| Existing `tool-call-ceiling.sh` at 500 | Redundant safety net | Align or remove in future cleanup |
| `session-close` gate advisory | Not yet promoted to enforced | Awaits Phase 3 testing |

## Verification

- 33/33 pytest pass (1.04s)
- Governor CLI exits correctly: 0 (CONTINUE at 50), 1 (PAUSE at 170), 2 (STOP at 200)
- Hook script exists, is executable, and is registered in settings.json
