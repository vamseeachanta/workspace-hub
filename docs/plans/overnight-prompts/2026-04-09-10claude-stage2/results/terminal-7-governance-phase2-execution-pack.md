# Execution Pack: Session Governance Phase 2 — Runtime Hook Enforcement

## 1. Issue Metadata

| Field          | Value |
|----------------|-------|
| Issue          | [#2056](https://github.com/vamseeachanta/workspace-hub/issues/2056) |
| Title          | Session governance Phase 2: wire runtime enforcement into hooks |
| Labels         | enhancement, priority:high, cat:ai-orchestration, agent:claude |
| Parent         | #1839 (Phase 1 — completed 2026-04-09) |
| Plan status    | **NOT APPROVED** — needs `status:plan-approved` label before implementation |
| Stage-1 source | `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md` |
| Execution pack | 2026-04-09 |

---

## 2. Fresh Status Check (Since Stage-1 Dossier)

The stage-1 dossier identified 4 gaps. Significant implementation occurred AFTER the dossier was written (same day, later commits). The gap status has changed materially.

| Check | Stage-1 Assessment | Stage-2 Verification (live repo) | Delta |
|-------|-------------------|----------------------------------|-------|
| **Gap 1**: Tool-call ceiling at 200 | Hook uses 500 default, no integration with governor | **PreToolUse `session-governor-check.sh` (200-ceiling) is live and registered.** Old `tool-call-ceiling.sh` (500) removed from settings.json. | RESOLVED (but see bug below) |
| **Gap 2**: Error loop breaker | Zero implementation | **`error-loop-tracker.sh` (PostToolUse) + `session-governor-check.sh` (PreToolUse) fully wired.** 10 new tests. State files in `.claude/state/session-governor/`. | RESOLVED |
| **Gap 3**: Pre-push review gate strict default | Defaults to warn (exit 0) | **`require-review-on-push.sh:255` now `${REVIEW_GATE_STRICT:-1}`.** `REVIEW_GATE_STRICT=1` in settings.json env. `governance-checkpoints.yaml:73` `enforced: true`. | RESOLVED |
| **Gap 4**: Missing tests | 25 tests total | **55 tests** in `tests/work-queue/test_session_governor.py` + 15 in `tests/hooks/` | RESOLVED |
| `session-governor-check.sh` hook exists | Not mentioned (didn't exist) | **99 lines, PreToolUse, first hook, matches all tools** | NEW since dossier |
| `error-loop-tracker.sh` hook exists | Not mentioned | **130 lines, PostToolUse, first hook, matches all tools** | NEW since dossier |
| Old `tool-call-ceiling.sh` in settings.json | Listed as wired | **Removed from settings.json** — file still exists as dead code | Changed since dossier |
| `plan-approval-gate.sh` | Not in scope | **Exists (Phase 2c), 75 lines, PreToolUse** — enforcement for plan-approval hard-stop | NEW (out of #2056 scope, from #1839) |
| `SESSION-GOVERNANCE.md` | 105 lines | **475 lines** — documents Phases 2, 2b, 2c, 2d, 3, 3b, 3d, 4 | Massively expanded |
| GitHub issue comment | None | **Implementation comment posted** (2026-04-09T22:58:14Z) documenting Phase 2d completion | NEW |

### BUG FOUND: YAML Threshold Regression

**Critical**: `scripts/workflow/governance-checkpoints.yaml:54` has `threshold: 5000` but should be `200`.

- **Root cause**: Commit `d4f46c770` (Phase 2c) changed the value from 200 to 5000 — likely accidental during the multi-file commit that also flipped `enforced: true` and review gate defaults.
- **Impact**: `session_governor.py` reads the threshold from YAML. At runtime, the governor won't issue STOP until 5000 tool calls instead of 200. The PreToolUse hook's fast-path constant (`FAST_PATH_CEILING=160`) is correct for a 200-ceiling, but the governor it delegates to uses the YAML value of 5000.
- **Effective behavior**: Below 160 = fast path (no governor call). At 160-3999 = governor says CONTINUE. At 4000+ = PAUSE. At 5000+ = STOP. The documented 200-call ceiling is NOT enforced.
- **Tests don't catch it**: `test_session_governor.py` uses inline YAML fixtures with `threshold: 200`, not the production YAML file.
- **Fix**: One-line change: `threshold: 5000` -> `threshold: 200` in `governance-checkpoints.yaml:54`.

### Doc Staleness

| File | Issue |
|------|-------|
| `docs/standards/REVIEW_GATE_BYPASS_POLICY.md:10` | Says "Default interactive behavior may remain warning-based unless `REVIEW_GATE_STRICT=1` is explicitly enabled" — contradicts the new strict default |
| `.claude/hooks/tool-call-ceiling.sh:20` | Dead code (not wired in settings.json) still shows `CEILING="${TOOL_CALL_CEILING:-500}"` — confusing to readers |

**Staleness verdict**: Stage-1 dossier is **materially stale**. 3 of 4 gaps resolved by subsequent implementation. One threshold regression bug discovered. Two doc files are stale.

---

## 3. Minimal Plan-Review Packet

### 3.1 Remaining Scope

**1 config fix + 1 doc update + 1 optional test + 1 optional cleanup. Zero new hooks.**

The original #2056 scope (3 hooks + config + tests) is ~90% complete. The remaining work is small.

| File | Change Type | Lines |
|------|------------|-------|
| `scripts/workflow/governance-checkpoints.yaml` | Fix threshold 5000 -> 200 | 1 LOC |
| `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` | Update default policy text | ~3 LOC |
| `tests/work-queue/test_session_governor.py` | Add test reading production YAML, asserting threshold==200 | +10 LOC |
| `.claude/hooks/tool-call-ceiling.sh` | OPTIONAL: add "DEPRECATED" header or delete | 0-2 LOC |

### 3.2 Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Missing `status:plan-approved` label | **BLOCKING** | Operator must apply label |
| Threshold fix could surface latent governor STOP events | LOW | 200 was the original value; governor already tested at 200 |
| Bypass policy doc update could confuse existing operators | LOW | The code already defaults to strict; doc is just catching up |

### 3.3 Acceptance Criteria (Updated from Issue Body)

| AC | Status | Evidence |
|----|--------|----------|
| Tool-call ceiling fires at 200 with progress summary | **PARTIAL** — hook fires at 200 but YAML threshold says 5000 | `session-governor-check.sh:30` hardcodes 160 fast-path; `governance-checkpoints.yaml:54` says 5000 |
| Error-loop-breaker detects 3x consecutive identical errors | **DONE** | `error-loop-tracker.sh` + `session-governor-check.sh:59-77` |
| Pre-push review gate defaults to strict mode | **DONE** | `require-review-on-push.sh:255` `${REVIEW_GATE_STRICT:-1}` |
| SKIP_REVIEW_GATE=1 bypass is logged/audited | **DONE** | `require-review-on-push.sh` logs to `logs/hooks/review-gate-bypass.jsonl` |
| All new tests pass; existing tests still pass | **DONE** (55 tests) | `tests/work-queue/test_session_governor.py` |
| Governance doc updated | **DONE** | `docs/governance/SESSION-GOVERNANCE.md` — 475 lines, all phases documented |

---

## 4. Issue Refinement Recommendations

### 4.1 Threshold Bug Fix (Add to Issue)

The issue body should be updated to note the regression found in this execution pack:

> **Discovered regression**: `governance-checkpoints.yaml:54` has `threshold: 5000` (should be `200`). Changed in `d4f46c770` during Phase 2c. The 200-call ceiling is not enforced at the governor level — only the hook's hardcoded fast-path at 160 provides partial coverage. Fix: one-line revert of threshold value.

### 4.2 Production YAML Integration Test

The test suite uses inline YAML fixtures, not the production config file. Recommend adding one test that reads the actual `governance-checkpoints.yaml` and asserts `tool-call-ceiling.threshold == 200`.

### 4.3 Dead Code Cleanup

`tool-call-ceiling.sh` is 59 lines of dead code (removed from settings.json in Phase 2c). Recommend either:
- (a) Delete the file, or
- (b) Add a `# DEPRECATED: replaced by session-governor-check.sh (Phase 2c, #1839)` header

### 4.4 Label Update

Issue should be relabeled from the current state to reflect completion:
- Add `status:plan-review` to signal plan readiness
- After operator review: add `status:plan-approved` to unblock implementation

---

## 5. Operator Command Pack

### 5.1 Verify Current State

```bash
# Confirm threshold bug exists
grep 'threshold:' scripts/workflow/governance-checkpoints.yaml
# Expected: threshold: 5000 (line 54, should be 200), threshold: 3 (line 64, correct)

# Confirm old hook not wired
grep 'tool-call-ceiling' .claude/settings.json
# Expected: no output (removed from settings.json)

# Confirm new hooks ARE wired
grep -E 'session-governor-check|error-loop-tracker' .claude/settings.json
# Expected: both present

# Confirm strict review gate default
grep 'REVIEW_GATE_STRICT' scripts/enforcement/require-review-on-push.sh | head -3
# Expected: line 255 shows ${REVIEW_GATE_STRICT:-1}

# Run existing tests
uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v --tb=short
# Expected: 55 tests pass
```

### 5.2 Issue Label Commands

```bash
# Add plan-review label (signal readiness for operator review)
gh issue edit 2056 --add-label "status:plan-review"

# After reviewing this pack, approve:
gh issue edit 2056 --add-label "status:plan-approved"

# Comment with threshold regression finding
gh issue comment 2056 --body "$(cat <<'EOF'
## Stage-2 Execution Pack Finding: Threshold Regression

**Bug**: `governance-checkpoints.yaml:54` has `threshold: 5000` — should be `200`.
Introduced in `d4f46c770` (Phase 2c). The 200-call ceiling is not enforced by the
governor; only the hook's hardcoded fast-path at 160 provides partial coverage.

**Fix**: One-line change.
**Impact**: Tool-call ceiling effectively non-functional at the documented 200 limit.

Remaining scope: threshold fix + bypass policy doc update + optional cleanup.
Stage-1 dossier: 3 of 4 gaps already resolved by overnight implementation.
EOF
)"
```

### 5.3 Close Issue (After Implementation)

```bash
# After the threshold fix is implemented and verified:
gh issue close 2056 --comment "Completed. All 4 gaps resolved: tool-call ceiling (200), error-loop-breaker (3x), strict review gate, threshold regression fixed."
```

---

## 6. Implementation Prompt (Self-Contained, for Claude)

```markdown
## Implementation Prompt — Issue #2056 Cleanup

You are closing out the remaining work for GitHub issue #2056:
"Session governance Phase 2: wire runtime enforcement into hooks"
in /mnt/local-analysis/workspace-hub.

### Context

3 of 4 original gaps have been resolved by prior implementation:
- Error-loop-breaker: `.claude/hooks/error-loop-tracker.sh` + `session-governor-check.sh`
- Tool-call ceiling: `.claude/hooks/session-governor-check.sh` (PreToolUse, 200-ceiling)
- Strict review gate: `scripts/enforcement/require-review-on-push.sh` defaults to strict

One threshold regression bug was found. Two doc files are stale.

### Prerequisite

- Issue #2056 must have label `status:plan-approved`

### Step 1: Fix Threshold Regression (BUG)

File: `scripts/workflow/governance-checkpoints.yaml`
Line 54: change `threshold: 5000` to `threshold: 200`

This was the original value (commit e69473081) and matches:
- The description on the same checkpoint ("Auto-pause at 200 tool calls")
- The hook fast-path constant (`FAST_PATH_CEILING=160` = 80% of 200)
- All tests that use `threshold: 200` in fixtures
- The documentation in SESSION-GOVERNANCE.md

### Step 2: Update Bypass Policy Doc

File: `docs/standards/REVIEW_GATE_BYPASS_POLICY.md`
Line 10: Replace:
  "Default interactive behavior may remain warning-based unless
   REVIEW_GATE_STRICT=1 is explicitly enabled."
With:
  "Default behavior is strict mode (blocks unreviewed pushes).
   Override with REVIEW_GATE_STRICT=0 for a single push."
Line 11: Replace:
  "Use strict mode for high-risk pushes..."
With:
  "Use REVIEW_GATE_STRICT=0 override only for the acceptable bypass
   cases listed below."

### Step 3: Add Production YAML Integration Test

File: `tests/work-queue/test_session_governor.py`
Add one test in the appropriate class:

```python
def test_production_yaml_tool_call_ceiling_threshold(self):
    """Verify production YAML has correct 200-call ceiling (not 5000 regression)."""
    import yaml
    yaml_path = Path(__file__).parent.parent.parent / "scripts" / "workflow" / "governance-checkpoints.yaml"
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    ceiling = next(c for c in data["checkpoints"] if c["id"] == "tool-call-ceiling")
    assert ceiling["threshold"] == 200, (
        f"Tool-call ceiling threshold is {ceiling['threshold']}, expected 200. "
        f"This was a regression from d4f46c770 — do not change to 5000."
    )
```

### Step 4: Optional Cleanup

File: `.claude/hooks/tool-call-ceiling.sh`
Add at line 2: `# DEPRECATED: replaced by session-governor-check.sh (Phase 2c, #1839). Not wired in settings.json.`

Or delete the file entirely if confirmed no external references.

### Step 5: Verify

```bash
# 1. Threshold fix
grep 'threshold: 200' scripts/workflow/governance-checkpoints.yaml

# 2. Governor verifies at 200
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 200 --consecutive-errors 0
# Expected exit code: 2 (STOP)

uv run scripts/workflow/session_governor.py --check-limits --tool-calls 150 --consecutive-errors 0
# Expected exit code: 0 (CONTINUE)

uv run scripts/workflow/session_governor.py --check-limits --tool-calls 0 --consecutive-errors 3
# Expected exit code: 2 (STOP)

# 3. All tests pass
uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v --tb=short

# 4. Bypass policy updated
grep -c 'strict mode' docs/standards/REVIEW_GATE_BYPASS_POLICY.md
# Expected: >= 1

# 5. Old hook not wired
grep 'tool-call-ceiling' .claude/settings.json
# Expected: no output
```

### Acceptance Criteria
- [ ] `governance-checkpoints.yaml` tool-call-ceiling threshold is 200
- [ ] Governor returns STOP (exit 2) at 200 tool calls
- [ ] Bypass policy doc reflects strict default
- [ ] New integration test reads production YAML and asserts threshold==200
- [ ] All 55+ existing tests still pass

### Cross-Review Requirements
- Single-file bug fix + doc update — lightweight review acceptable
- Run `/gsd:review` for cross-AI check if desired
```

---

## 7. Morning Handoff

### What Happened Overnight

The stage-1 dossier identified 4 gaps for #2056. A separate implementation session (same day) resolved 3 of 4 gaps:

1. **Tool-call ceiling enforcement** -> `session-governor-check.sh` (PreToolUse, 200-ceiling via governor)
2. **Error loop breaker** -> `error-loop-tracker.sh` (PostToolUse) + governor integration
3. **Strict review gate** -> `require-review-on-push.sh` flipped to strict default

Additionally, Phases 2c, 3, 3b, 3d, and 4 were implemented (plan-approval gate, CI enforcement, enforcement-env, artifact verification, worker discovery protocol) — all documented in `docs/governance/SESSION-GOVERNANCE.md`.

### What Remains

| Item | Priority | Effort |
|------|----------|--------|
| Fix `threshold: 5000` -> `200` in `governance-checkpoints.yaml:54` | **HIGH** (bug) | 1 line |
| Update `REVIEW_GATE_BYPASS_POLICY.md` default text | MEDIUM (doc staleness) | 3 lines |
| Add production YAML integration test | MEDIUM (test gap) | 10 lines |
| Annotate/remove dead `tool-call-ceiling.sh` | LOW (cleanup) | 1-2 lines |

### Key Files

| File | Role |
|------|------|
| `scripts/workflow/governance-checkpoints.yaml` | Checkpoint config — **has threshold bug** |
| `.claude/hooks/session-governor-check.sh` | PreToolUse hook — tool-call ceiling + error count enforcement |
| `.claude/hooks/error-loop-tracker.sh` | PostToolUse hook — consecutive error tracking |
| `scripts/enforcement/require-review-on-push.sh` | Pre-push review gate — strict default |
| `docs/governance/SESSION-GOVERNANCE.md` | Comprehensive governance documentation (475 lines) |
| `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` | Bypass policy — **stale default text** |
| `.claude/hooks/tool-call-ceiling.sh` | Dead code (not wired) — original #1428 hook |
| `tests/work-queue/test_session_governor.py` | 55 tests covering all governance features |

### Recommended Operator Action

1. Read this execution pack (5 min)
2. Run verification commands from section 5.1 to confirm current state
3. Apply `status:plan-review` label and post the threshold regression comment (section 5.2)
4. After review, apply `status:plan-approved` to unblock the small implementation
5. Dispatch Claude for the threshold fix + doc update (~15 min estimated implementation)

---

## 8. Final Recommendation

**FIX-AND-CLOSE**: Issue #2056 is ~90% complete. Three of four gaps are resolved. The one remaining item is a threshold regression bug (`5000` instead of `200` in `governance-checkpoints.yaml:54`) plus two stale doc lines. Apply `status:plan-approved`, dispatch the 4-step implementation prompt from section 6, and close the issue.
