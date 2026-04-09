# Execution Pack: Issue #2056 — Session Governance Phase 2: Wire Runtime Enforcement into Hooks

| Field | Value |
|-------|-------|
| Issue | [#2056](https://github.com/vamseeachanta/workspace-hub/issues/2056) |
| Parent | #1839 (Phase 1 — completed 2026-04-09) |
| Labels | enhancement, priority:high, cat:ai-orchestration, agent:claude |
| Current status | OPEN — **missing** `status:plan-review` and `status:plan-approved` labels |
| Prepared | 2026-04-09 |
| Sources | `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md`, `docs/plans/2026-04-09-agent-team-followup-summary.md` |

---

## 1. Executive Summary

Issue #2056 wires the runtime enforcement layer that Phase 1 (#1839) left as data-only into live Claude Code hooks. The implementation delta is well-scoped (~150 lines new + ~30 lines modified): fix the tool-call ceiling threshold mismatch (500 -> 200) and add hard-stop context injection, create a new error-loop-breaker hook that detects 3x consecutive identical errors via message fingerprinting, flip the pre-push review gate default from warning to strict mode, and cover all three gaps with TDD-first test files. All prerequisite infrastructure — `session_governor.py` verdict logic, `governance-checkpoints.yaml` thresholds, hook JSON protocol (`additionalContext`) — is already in place and tested; this issue is the last-mile wiring.

---

## 2. Exact Scope Approved for Implementation

### Gap 1: Tool-Call Ceiling — Verify Current State, Then Complete Hard Stop Wiring
- First verify the current live value in `tool-call-ceiling.sh`; recent governance work may already have changed the default from 500 to 200
- If the file still defaults to 500, change it to 200; if it already defaults to 200, skip the threshold edit and only complete the remaining hard-stop wiring
- Integrate `session_governor.py --check-limits` for STOP/PAUSE verdicts
- At STOP (>=200): inject `additionalContext` JSON with progress summary, require user confirmation
- At PAUSE (>=160): inject warning context
- Add `TOOL_CALL_CEILING=200` to `.claude/settings.json` env block if not already present

### Gap 2: Error Loop Breaker — New Hook
- Create PostToolUse hook for Bash tool that reads stdin JSON
- Hash error messages (strip timestamps, paths, line numbers, PIDs) via md5sum
- Track consecutive identical errors in `/tmp/claude-error-loop-${SESSION_ID:-default}.json`
- After 3 consecutive identical errors: call `session_governor.py --check-limits --consecutive-errors N`
- On STOP verdict: output `additionalContext` JSON with error details and escalation suggestion
- Reset counter on non-error or different error
- Register hook in `.claude/settings.json` PostToolUse section

### Gap 3: Pre-Push Review Gate — Default Strict Mode
- Change default from warn (exit 0) to strict (exit 1) in `require-review-on-push.sh`
- Add `REVIEW_GATE_STRICT=1` to `.claude/settings.json` env block
- Enhance `SKIP_REVIEW_GATE=1` bypass to emit visible stderr warning in addition to existing stdout log
- Update `governance-checkpoints.yaml`: `enforced: false` -> `enforced: true`
- Update `REVIEW_GATE_BYPASS_POLICY.md` to reflect new default
- Update `SESSION-GOVERNANCE.md` to mark Phase 2b items complete

### Gap 4: Tests (TDD-first)
- `tests/hooks/test_tool_call_ceiling.py` — ceiling threshold, JSON output, warning at 80%
- `tests/hooks/test_error_loop_breaker.py` — hashing, 3x detection, counter reset, JSON output
- `tests/hooks/test_review_gate_strict_default.sh` (extend existing) — default blocks, override allows

---

## 3. Explicit Out-of-Scope List

| Item | Reason |
|------|--------|
| Phase 3 work (#2057 — session infrastructure restoration) | Separate issue; depends on #2056 stabilizing first |
| Hermes/CI integration of session governor | Programmatic consumers use exit codes already; hook protocol is Claude-only |
| Hook-level hard-kill of sessions | Architectural limitation — Claude Code hooks cannot kill sessions; enforcement is via `additionalContext` injection (documented design constraint) |
| Changes to `session_governor.py` core logic | Already complete and tested (25 tests); this issue only wires hooks to it |
| Changes to `review_routing_gate.py` or `review-routing-gate.sh` | Review routing logic is correct; only the default-mode flag in `require-review-on-push.sh` changes |
| New governance checkpoints or threshold changes | Thresholds (200 calls, 3 errors) are already defined in `governance-checkpoints.yaml`; this issue only enforces them |
| `capture-corrections.sh` error tracking/deduplication | Noted as misaligned in dossier but not part of #2056 scope |
| Any `digitalmodel/` repository changes | #2056 is governance-only, workspace-hub scope |

---

## 4. TDD-First Task Sequence

### Wave 1: Write Failing Tests (Red Phase)

| # | Task | Output file |
|---|------|-------------|
| 1.1 | Create tool-call ceiling tests: default=200, JSON output at STOP, warning at PAUSE, silent below 160, env var override | `tests/hooks/test_tool_call_ceiling.py` |
| 1.2 | Create error-loop-breaker tests: stable fingerprinting, 3x identical -> STOP, different-error reset, non-error reset, state file location, JSON output | `tests/hooks/test_error_loop_breaker.py` |
| 1.3 | Extend review gate tests: default blocks (exit 1), `REVIEW_GATE_STRICT=0` allows (exit 0), `SKIP_REVIEW_GATE=1` logs audit entry | `scripts/enforcement/tests/test_require_review_on_push.sh` |
| 1.4 | Run all new tests — confirm they FAIL | Verification checkpoint |

### Wave 2: Implementation (Green Phase)

| # | Task | Target file |
|---|------|-------------|
| 2.1 | Verify current ceiling value in `.claude/hooks/tool-call-ceiling.sh`; if it is still 500, change it to 200, otherwise skip the threshold edit | `.claude/hooks/tool-call-ceiling.sh` |
| 2.2 | Add verdict integration + `additionalContext` JSON output to ceiling hook | `.claude/hooks/tool-call-ceiling.sh` |
| 2.3 | Create error-loop-breaker hook (stdin JSON parsing, error hashing, state tracking, verdict call) | `.claude/hooks/error-loop-breaker.sh` (new) |
| 2.4 | Register error-loop-breaker in PostToolUse for Bash tool | `.claude/settings.json` |
| 2.5 | Add env vars: `TOOL_CALL_CEILING=200`, `REVIEW_GATE_STRICT=1` | `.claude/settings.json` |
| 2.6 | Flip review gate default: `"${REVIEW_GATE_STRICT:-}"` -> `"${REVIEW_GATE_STRICT:-1}"` | `scripts/enforcement/require-review-on-push.sh` |
| 2.7 | Enhance bypass stderr warning in review gate | `scripts/enforcement/require-review-on-push.sh` |
| 2.8 | Update `enforced: false` -> `enforced: true` | `scripts/workflow/governance-checkpoints.yaml` |
| 2.9 | Update governance docs to mark Phase 2b complete | `docs/governance/SESSION-GOVERNANCE.md` |
| 2.10 | Update bypass policy default | `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` |

### Wave 3: Verification (All Green)

| # | Task | Command |
|---|------|---------|
| 3.1 | Existing governor tests pass | `uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v` |
| 3.2 | New ceiling tests pass | `uv run --no-project python -m pytest tests/hooks/test_tool_call_ceiling.py -v` |
| 3.3 | New error-loop tests pass | `uv run --no-project python -m pytest tests/hooks/test_error_loop_breaker.py -v` |
| 3.4 | Review gate shell tests pass | `bash scripts/enforcement/tests/test_require_review_on_push.sh` |
| 3.5 | Grep-verify ceiling default is 200 | `grep 'TOOL_CALL_CEILING:-' .claude/hooks/tool-call-ceiling.sh` |
| 3.6 | Grep-verify strict default is 1 | `grep 'REVIEW_GATE_STRICT:-' scripts/enforcement/require-review-on-push.sh` |
| 3.7 | E2E: governor STOP at 200 calls | `uv run scripts/workflow/session_governor.py --check-limits --tool-calls 200` (exit 2) |
| 3.8 | E2E: governor CONTINUE at 150 calls | `uv run scripts/workflow/session_governor.py --check-limits --tool-calls 150` (exit 0) |
| 3.9 | E2E: governor STOP at 3 errors | `uv run scripts/workflow/session_governor.py --check-limits --consecutive-errors 3` (exit 2) |
| 3.10 | Verify error-loop-breaker hook exists and registered | `test -f .claude/hooks/error-loop-breaker.sh && jq '.hooks.PostToolUse[]' .claude/settings.json` |
| 3.11 | Cross-review: `/gsd:review --codex` (2-provider minimum) | Manual after commit |

---

## 5. Exact Files Expected to Change

### New Files

| File | Purpose |
|------|---------|
| `.claude/hooks/error-loop-breaker.sh` | PostToolUse hook: error fingerprinting + consecutive-error detection |
| `tests/hooks/test_tool_call_ceiling.py` | Test suite for ceiling hook |
| `tests/hooks/test_error_loop_breaker.py` | Test suite for error-loop hook |

### Modified Files

| File | Change |
|------|--------|
| `.claude/hooks/tool-call-ceiling.sh` | Threshold 500->200, add `additionalContext` JSON output, integrate `session_governor.py` verdict |
| `.claude/settings.json` | Add env vars (`TOOL_CALL_CEILING`, `REVIEW_GATE_STRICT`), add PostToolUse entry for error-loop-breaker |
| `scripts/enforcement/require-review-on-push.sh` | Default strict mode, enhance bypass stderr warning |
| `scripts/workflow/governance-checkpoints.yaml` | Line 73: `enforced: false` -> `enforced: true` |
| `docs/governance/SESSION-GOVERNANCE.md` | Mark Phase 2b items as completed |
| `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` | Update default policy to strict |
| `scripts/enforcement/tests/test_require_review_on_push.sh` | Extend with strict-default and bypass-audit tests |

### Files NOT Touched (explicit)

- `scripts/workflow/session_governor.py` — no changes (already correct)
- `scripts/ai/review_routing_gate.py` — no changes
- `scripts/ai/review-routing-gate.sh` — no changes
- `.claude/hooks/cross-review-gate.sh` — no changes
- `.claude/hooks/capture-corrections.sh` — out of scope

---

## 6. Git Contention Notes

| File | Contention risk | Mitigation |
|------|----------------|------------|
| `.claude/settings.json` | **HIGH** — most-contended file in repo (~292 lines, 28 hooks, modified by multiple overnight terminals) | Keep edits minimal: add 2 env vars + 1 PostToolUse entry. Coordinate with terminal-6 (#2057 Phase 3) if running in parallel. Rebase immediately before commit. |
| `scripts/enforcement/require-review-on-push.sh` | Low — last modified in #1668, rarely touched | No special handling needed |
| `.claude/hooks/tool-call-ceiling.sh` | Low — rarely modified | No special handling needed |
| `scripts/workflow/governance-checkpoints.yaml` | Low — stable config file | No special handling needed |
| `docs/governance/SESSION-GOVERNANCE.md` | Low | No special handling needed |
| `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` | Low | No special handling needed |

**Pre-implementation git hygiene**: Pull latest `main`, check for in-flight sessions touching `.claude/settings.json` with `git log --since="6 hours ago" -- .claude/settings.json`.

---

## 7. Self-Contained Claude Implementation Prompt

```markdown
## Implementation Prompt — Issue #2056: Session Governance Phase 2

You are implementing GitHub issue #2056: "Session governance Phase 2: wire runtime enforcement into hooks"
in /mnt/local-analysis/workspace-hub.

### Prerequisites
- Verify issue #2056 has label `status:plan-approved`
- Read the full dossier: docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md
- Read the execution pack: docs/plans/claude-followup-2026-04-09/results/issue-2056-execution-pack.md
- Run `git pull && git log --oneline -5` to confirm you are on latest main

### Strict TDD Order

**Step 1 — Red: Write failing tests FIRST (do not write implementation code yet)**

1. Create `tests/hooks/test_tool_call_ceiling.py`:
   - Test default ceiling is 200 (grep the hook script for `TOOL_CALL_CEILING:-200`)
   - Test that at 200 calls, hook outputs JSON with `additionalContext` containing progress summary
   - Test that at 160 calls (80%), hook outputs warning context
   - Test that below 160, hook exits 0 with no stdout
   - Test that `TOOL_CALL_CEILING` env var overrides the threshold

2. Create `tests/hooks/test_error_loop_breaker.py`:
   - Test error message hashing: strip timestamps (`YYYY-MM-DD`), absolute paths, `line N` patterns, then md5sum
   - Test 3 consecutive identical errors produce STOP verdict (exit 2 from governor)
   - Test different error resets counter to 1
   - Test non-error output resets counter to 0
   - Test state file at `/tmp/claude-error-loop-${SESSION_ID:-default}.json`
   - Test hook outputs `additionalContext` JSON on STOP

3. Extend `scripts/enforcement/tests/test_require_review_on_push.sh`:
   - Test default mode (no env vars set) blocks push (exit 1)
   - Test `REVIEW_GATE_STRICT=0` overrides to warn mode (exit 0)
   - Test `SKIP_REVIEW_GATE=1` logs audit entry and emits stderr warning

4. Run all new tests — confirm they FAIL:
   ```bash
   uv run --no-project python -m pytest tests/hooks/test_tool_call_ceiling.py -v
   uv run --no-project python -m pytest tests/hooks/test_error_loop_breaker.py -v
   bash scripts/enforcement/tests/test_require_review_on_push.sh
   ```

**Step 2 — Green: Implement (make tests pass)**

2. `.claude/hooks/tool-call-ceiling.sh`:
   - First grep the current file state and confirm whether it still contains `TOOL_CALL_CEILING:-500` or already uses `TOOL_CALL_CEILING:-200`
   - If still at 500, change it to 200; if already at 200, leave the threshold unchanged
   - Add JSON stdout: `{"hookSpecificOutput": {"additionalContext": "...progress summary..."}}`
   - At STOP (>=200): include tool counts, session duration, "User confirmation required to continue"
   - At PAUSE (>=160): include "Approaching session tool-call limit" warning
   - Integrate: call `uv run scripts/workflow/session_governor.py --check-limits --tool-calls $COUNT` for verdict

2. `.claude/hooks/error-loop-breaker.sh` (new file):
   - PostToolUse hook for Bash tool
   - Read stdin JSON, extract tool output and exit code
   - If non-zero exit or error pattern detected:
     - Hash: `echo "$ERROR_MSG" | sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}//g; s|/[^ ]*/||g; s/line [0-9]*//g' | md5sum | cut -d' ' -f1`
     - State: read/write `/tmp/claude-error-loop-${SESSION_ID:-default}.json` (`{"hash":"...","count":N}`)
     - If same hash: increment count; if different hash: reset to 1
     - If count >= 3: call `uv run scripts/workflow/session_governor.py --check-limits --consecutive-errors $COUNT`
     - On STOP (exit 2): output `{"hookSpecificOutput": {"additionalContext": "ERROR LOOP DETECTED: ..."}}`
   - If success (exit 0, no error): reset state file count to 0

3. `.claude/settings.json`:
   - Add to env block: `"TOOL_CALL_CEILING": "200"`, `"REVIEW_GATE_STRICT": "1"`
   - Add PostToolUse entry: `{"matcher": "Bash", "hooks": [{"type": "command", "command": "bash .claude/hooks/error-loop-breaker.sh", "timeout": 5}]}`

4. `scripts/enforcement/require-review-on-push.sh`:
   - Change `"${REVIEW_GATE_STRICT:-}"` to `"${REVIEW_GATE_STRICT:-1}"`
   - Add `>&2 echo "WARNING: Review gate bypassed via SKIP_REVIEW_GATE=1 — audit logged"` in bypass path

5. `scripts/workflow/governance-checkpoints.yaml`:
   - Line 73: change `enforced: false` to `enforced: true`

6. Documentation:
   - `docs/governance/SESSION-GOVERNANCE.md`: mark Phase 2b items (tool-call ceiling, error-loop breaker, pre-push strict) as completed
   - `docs/standards/REVIEW_GATE_BYPASS_POLICY.md`: update default policy from warn to strict

**Step 3 — Verify (all must pass)**

```bash
# Existing tests still pass
uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v
# New tests pass
uv run --no-project python -m pytest tests/hooks/test_tool_call_ceiling.py -v
uv run --no-project python -m pytest tests/hooks/test_error_loop_breaker.py -v
bash scripts/enforcement/tests/test_require_review_on_push.sh
# Grep verifications
grep 'TOOL_CALL_CEILING:-' .claude/hooks/tool-call-ceiling.sh  # must show 200
grep 'REVIEW_GATE_STRICT:-' scripts/enforcement/require-review-on-push.sh  # must show 1
# E2E governor verdicts
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 200 --consecutive-errors 0  # exit 2 (STOP)
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 150 --consecutive-errors 0  # exit 0 (CONTINUE)
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 0 --consecutive-errors 3    # exit 2 (STOP)
# Hook registration check
test -f .claude/hooks/error-loop-breaker.sh && echo "PASS"
jq '.hooks.PostToolUse[] | select(.hooks[].command | contains("error-loop"))' .claude/settings.json
```

**Step 4 — Commit and cross-review**

```bash
git add .claude/hooks/tool-call-ceiling.sh .claude/hooks/error-loop-breaker.sh \
  .claude/settings.json scripts/enforcement/require-review-on-push.sh \
  scripts/workflow/governance-checkpoints.yaml \
  docs/governance/SESSION-GOVERNANCE.md docs/standards/REVIEW_GATE_BYPASS_POLICY.md \
  tests/hooks/test_tool_call_ceiling.py tests/hooks/test_error_loop_breaker.py \
  scripts/enforcement/tests/test_require_review_on_push.sh
git commit -m "feat(governance): wire Phase 2 runtime enforcement into hooks (#2056)"
```

Then run cross-review: `/gsd:review --codex` (2-provider minimum per cross-review policy).

### Acceptance Criteria
- [ ] Tool-call ceiling fires at 200 (not 500) with user-facing progress summary via `additionalContext`
- [ ] Error-loop-breaker detects 3x consecutive identical errors and injects hard-stop context
- [ ] Pre-push review gate defaults to strict mode (exit 1 on unreviewed feature pushes)
- [ ] `SKIP_REVIEW_GATE=1` bypass emits visible stderr warning + logged audit entry
- [ ] All new tests pass; all existing governance tests still pass
- [ ] `governance-checkpoints.yaml` marks `pre-push-review` as `enforced: true`
- [ ] Governance docs updated to reflect Phase 2b completion
```

---

## 8. Approval Checklist

- [ ] Executive summary accurately reflects #2056 scope and motivation
- [ ] Scope is limited to the 4 gaps identified (ceiling fix, error-loop hook, strict gate, tests)
- [ ] Out-of-scope items are explicitly listed and acceptable
- [ ] TDD-first task sequence is correct (tests before implementation)
- [ ] File change list is complete and no unexpected files are touched
- [ ] `.claude/settings.json` contention risk is acknowledged with mitigation plan
- [ ] Implementation prompt is self-contained and executable by a fresh Claude session
- [ ] Cross-review policy (2-provider minimum) is included in the prompt
- [ ] No code implementation is included in this pack (planning-only artifact)
- [ ] Issue #2056 currently has labels: `enhancement`, `priority:high`, `cat:ai-orchestration`, `agent:claude`
- [ ] Ready to add `status:plan-review` label to issue #2056

---

## 9. Suggested Issue Comment Text

### For `status:plan-review` transition

```
## Plan Review: Execution Pack Ready

An execution pack has been prepared for #2056 (Session Governance Phase 2: Wire Runtime Enforcement into Hooks).

**Artifact**: `docs/plans/claude-followup-2026-04-09/results/issue-2056-execution-pack.md`

**Scope summary**:
- Fix tool-call ceiling threshold (500 → 200) + add hard-stop context injection
- Create error-loop-breaker hook (3x consecutive identical errors → STOP)
- Flip pre-push review gate default to strict mode
- TDD-first: 3 new test files before any implementation code

**Implementation delta**: ~150 lines new code + ~30 lines modified across 7 modified files and 3 new files.

**Contention note**: `.claude/settings.json` is high-contention; edits are minimal (2 env vars + 1 PostToolUse entry).

**Prerequisite**: #1839 Phase 1 is complete (verified via commit `e69473081`).

Please review and apply `status:plan-approved` when ready to proceed with implementation.

Labels: `status:plan-review`
```

### For `status:plan-approved` transition

```
## Plan Approved: Cleared for Implementation

Execution pack reviewed and approved. Implementation may proceed following the TDD-first task sequence defined in the pack.

**Reminder**: Pull latest main and check `.claude/settings.json` for recent changes before starting. Cross-review required after implementation (2-provider minimum).

Labels: remove `status:plan-review`, add `status:plan-approved`
```

---

RECOMMENDATION: READY FOR PLAN-APPROVAL LABEL
