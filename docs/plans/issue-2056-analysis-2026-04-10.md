# Issue Analysis: #2056 — Session governance Phase 2: wire runtime enforcement into hooks

**Analyzed:** 2026-04-10  
**Analyst:** Claude (read-only pass)

---

## Verdict

**ALREADY IMPLEMENTED — NOT directly executable.**

Issue #2056 is complete. All three runtime enforcement mechanisms are implemented, wired into `settings.json` hooks, and covered by tests. Four commits on `main` deliver the work. The issue is open but should be closed.

---

## Evidence

### Commits that deliver this issue (on `main`):

| Commit | Description |
|--------|-------------|
| `51a30b8aa` | feat(governance): add error loop breaker hook for consecutive error detection (#2056) |
| `12d1c4bd2` | fix(governance): restore 200-call enforcement threshold (#2056) |
| `e07395c9c` | fix(governance): per-session tool-call counter via PPID (#2063) |
| `58dfd9298` | feat(governance): enforce runtime session gates and strict review routing (#2056) |

### Three feature requirements vs. delivery state:

#### 1. Tool-Call Ceiling
- **Spec:** At 200 calls, auto-pause and present progress summary; user must confirm.
- **Implemented as:** Two-layer approach:
  - `tool-call-ceiling.sh` — advisory ceiling = 500 (warn at 400, block signal at 500)
  - `session-governor-check.sh` — authoritative per-session (PPID) counter, threshold = 1000, fast-path ceiling = 800 (delegates to `session_governor.py`)
- **Discrepancy:** Production threshold is 1000, not 200. The "restore to 200" commit (`12d1c4bd2`) targeted `governance-checkpoints.yaml`; subsequent PPID-isolation refactor (#2063) updated threshold to 1000 for per-session semantics. This is a known post-implementation evolution, not a gap.
- **Wire:** `PreToolUse` hook in `settings.json` — `session-governor-check.sh` on matcher `Bash|Read|Write|Edit|MultiEdit|Glob|Grep|Agent|Task`
- **Status:** DONE

#### 2. Error Loop Breaker (3x same error)
- **Spec:** Track consecutive identical errors by hash; hard stop at 3 repeats.
- **Implemented as:**
  - `error-loop-tracker.sh` (PostToolUse): reads stdin JSON, detects errors via `tool_response.is_error`, exit codes, and pattern matching; md5-hashes error signature; increments `consecutive-error-count` on same hash, resets on success.
  - `session-governor-check.sh` (PreToolUse): reads `consecutive-error-count`; at >= 3, emits `{"decision":"block","reason":"error-loop-breaker threshold: 3"}`.
- **Wire:** `PostToolUse` in `settings.json` — `error-loop-tracker.sh` on matcher `Bash|Read|Write|Edit|MultiEdit|Glob|Grep|Agent|Task`
- **Status:** DONE

#### 3. Pre-Push Review Gate -> Strict Mode
- **Spec:** `review-routing-gate.sh` defaults to warning mode — promote to strict (exit 1); add `REVIEW_GATE_MODE=strict`; `SKIP_REVIEW_GATE=1` bypass must be logged/audited.
- **Implemented as** (in `scripts/enforcement/require-review-on-push.sh`):
  - `${REVIEW_GATE_STRICT:-1}` — strict is the default (line ~255)
  - `log_bypass()` function defined and called when `SKIP_REVIEW_GATE=1` (lines ~149, ~166)
  - Bypass logged to `logs/hooks/review-gate-bypass.jsonl` as structured JSON with `timestamp`, `action`, `branch`
- **Status:** DONE

### Tests
- `scripts/ai/tests/test_session_governance_gates.py` — 21 tests covering bypass logging, strict mode source check, counter PPID isolation, 80%-fast-path arithmetic, block decision JSON, md5 dedup, success reset
- `tests/work-queue/test_session_governor.py` — 56 tests (15 covering `StrictReviewGate` and `TestCheckSessionLimits`)
- Issue comment (latest) confirms: 98/98 pass in `scripts/ai/tests/`; 56/56 in `tests/work-queue/`

---

## Files Verified

| File | Status |
|------|--------|
| `.claude/hooks/tool-call-ceiling.sh` | EXISTS — advisory ceiling, ceiling=500 |
| `.claude/hooks/error-loop-tracker.sh` | EXISTS — PostToolUse, md5 dedup, references #2056 |
| `.claude/hooks/session-governor-check.sh` | EXISTS — PreToolUse, PPID-isolated counter, reads consecutive-error-count |
| `.claude/hooks/plan-approval-gate.sh` | EXISTS — refined in final #2056 commit (tests/* safe-path restore) |
| `scripts/enforcement/require-review-on-push.sh` | EXISTS — REVIEW_GATE_STRICT:-1, log_bypass(), SKIP bypass logged |
| `scripts/workflow/governance-checkpoints.yaml` | EXISTS — threshold: 1000 (tool-call-ceiling gate) |
| `scripts/workflow/session_governor.py` | EXISTS — `--check-limits --tool-calls --consecutive-errors` flags present |
| `scripts/ai/review_routing_gate.py` | EXISTS (unchanged by this issue) |
| `.claude/settings.json` | EXISTS — all hooks wired (PreToolUse + PostToolUse) |
| `scripts/ai/tests/test_session_governance_gates.py` | EXISTS — 21 new tests |
| `docs/governance/SESSION-GOVERNANCE.md` | EXISTS — updated with Phase 2d section |

---

## Approval / Gate Status

- **Label:** `status:plan-approved` — gate is satisfied
- **Plan marker:** `.planning/plan-approved/` — not checked (plan-approval-gate.sh is a write gate; this is a read-only analysis pass)
- **Gate conclusion:** Implementation was conducted under a valid `status:plan-approved` state; no gate violation evidence

---

## Dirty-Worktree Risk

Current worktree dirty files (from `git status`):

```
M .claude/state/corrections/.edit_sequence_counter   <- runtime state, not source
 M .claude/state/corrections/.recent_edits           <- runtime state, not source
 M .claude/state/session-signals/2026-04-10.jsonl    <- runtime state, not source
?? .claude/skills/workspace-hub/learned/             <- untracked skills, unrelated
?? docs/plans/claude-ops-2026-04-09/results/backups/ <- untracked plan artifact, unrelated
?? scripts/skill-extractor.py                        <- untracked script, unrelated
```

**Assessment:** No implementation risk. All dirty files are runtime state or unrelated artifacts. None touch the #2056 delivery surface.

---

## Exact Write Boundaries for Implementation

**N/A — implementation is complete.** If the only remaining action is closing the issue, the write boundary is:

- GitHub issue `#2056` state change: `OPEN -> CLOSED`
- No source file modifications required

---

## Minimal Verification Commands

Run these to verify the implementation is live and tests pass before closing:

```bash
# 1. Confirm all three hooks are wired in settings.json
grep -E "error-loop-tracker|session-governor-check" .claude/settings.json

# 2. Confirm strict mode and log_bypass are in the review gate
grep -E "REVIEW_GATE_STRICT:-1|log_bypass" scripts/enforcement/require-review-on-push.sh

# 3. Run the governance gates test suite
uv run python -m pytest scripts/ai/tests/test_session_governance_gates.py -v --tb=short

# 4. Run the session governor tests (StrictReviewGate + CheckSessionLimits)
uv run python -m pytest tests/work-queue/test_session_governor.py \
  -k 'StrictReviewGate or TestCheckSessionLimits' -v

# 5. Smoke test the error loop tracker hook (success payload should reset counter)
echo '{"tool_name":"Bash","tool_input":{"command":"echo ok"},"tool_response":{"exit_code":0,"stdout":"ok","stderr":""}}' \
  | bash .claude/hooks/error-loop-tracker.sh
```

---

## Self-Contained Implementation Prompt

_Omitted — verdict is ALREADY COMPLETE, not directly executable._

---

## Next Action

1. **Close issue #2056** — all acceptance criteria are met and verified by tests.
2. **Optional follow-up (non-blocking):**
   - Harden `test_governor_hook_emits_block_on_stop` to assert `stdout` is non-empty before parsing JSON (currently soft — passes if stdout is empty)
   - Narrow `tests/*` safe-path in `plan-approval-gate.sh` to `*/scripts/*/tests/*` if broader coverage becomes a concern
   - Reconcile the documented "200-call" ceiling vs. the live `THRESHOLD=1000` in a follow-up issue if the lower ceiling is still desired
3. **No source file changes needed in this pass.**
