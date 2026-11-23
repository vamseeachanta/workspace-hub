# Terminal 7 — Session Governance Phase 2: Wire Runtime Enforcement into Hooks

## Issue Metadata

| Field | Value |
|-------|-------|
| Issue | #2056 |
| Parent | #1839 (Phase 1 — completed 2026-04-09) |
| Labels | enhancement, priority:high, cat:ai-orchestration, agent:claude |
| Type | Implementation dossier (planning-only, no production code) |
| Date | 2026-04-09 |

---

## 1. Current-State Findings

### Files/Modules Already Present

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `scripts/workflow/governance-checkpoints.yaml` | Checkpoint config (7 gates, thresholds) | 74 | Complete — defines tool-call-ceiling=200, error-loop-breaker=3 |
| `scripts/workflow/session_governor.py` | Verification utility + runtime enforcement | 351 | Complete — `check_session_limits()`, `SessionVerdict`, `LimitResult` classes, CLI with `--check-limits` |
| `.claude/hooks/tool-call-ceiling.sh` | PostToolUse hook for session runaway detection | 58 | **Misaligned** — uses 500 default, advisory-only (exit 0 always) |
| `.claude/hooks/cross-review-gate.sh` | PreToolUse hook blocking PR/ship without review | 82 | Complete — blocks `gh pr create`, `gsd-ship`, plan execution |
| `.claude/hooks/emit-session-quality-signals.sh` | Stop hook emitting tool-call summaries | 57 | Complete — emits `session_tool_summary` signal |
| `.claude/hooks/capture-corrections.sh` | PostToolUse capturing correction patterns | ~80 | Present but NO error tracking/deduplication |
| `scripts/enforcement/require-review-on-push.sh` | Pre-push gate script | 266 | Complete — supports WARN (default), STRICT, SKIP modes |
| `scripts/ai/review-routing-gate.sh` | Shell wrapper for review routing | 18 | Complete — delegates to Python |
| `scripts/ai/review_routing_gate.py` | PR diff analysis + reviewer recommendation | 346 | Complete — 5 Gemini triggers |
| `docs/governance/SESSION-GOVERNANCE.md` | Governance roadmap documentation | 105 | Complete — accurately documents Phase 2b gaps |
| `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` | Bypass policy documentation | 36 | Complete — documents SKIP_REVIEW_GATE rules |
| `.claude/settings.json` | Hook configuration (hooks, env, permissions) | ~292 | Complete — 28 hooks configured |

### Tests Already Present

| Test File | Coverage | Count |
|-----------|----------|-------|
| `tests/work-queue/test_session_governor.py` | Config loading, gate verification, runtime enforcement (check_session_limits) | 25 tests |
| `scripts/enforcement/tests/test_require_review_on_push.sh` | SKIP bypass+logging, STRICT mode exit 1, evidence checks | ~6 tests |
| `tests/hooks/test_config_protection_hook.py` | Config protection hook | 3 tests |
| `tests/hooks/test_pre_push.py` | Pre-push hook | 7 tests |
| `scripts/ai/tests/test_review_routing_gate.py` | Review routing logic, Gemini triggers | ~12 tests |
| `scripts/ai/tests/test_review_routing_hook.py` | Cross-review hook integration | ~4 tests |

### Latest Relevant Commits

- `e69473081` (2026-04-09): `feat(governance): session hard-stop checkpoint model and verifier (#1839)` — Phase 1+2
- `ea959f3e5` (2026-04-09): `feat(harness): add config protection pretool hook (#1801)`
- `541c74c63`: `feat(enforcement): pre-push review gate + daily review audit cron (#1668)`
- `10e3a3137`: `feat(ai): promote review routing to Level 3 — hook integration (#1515, #1538)`

---

## 2. Remaining Implementation Delta

### Gap 1: Tool-Call Ceiling — Threshold Mismatch + No Hard Stop

**Current behavior** (`.claude/hooks/tool-call-ceiling.sh:20`):
```bash
CEILING="${TOOL_CALL_CEILING:-500}"  # <-- governance-checkpoints.yaml says 200
```

- Hook default is **500**, governance config says **200**
- Hook always exits 0 (advisory) — cannot hard-stop sessions
- Hook counts from daily JSONL (`session_$(date +%Y%m%d).jsonl`) not per-session
- Hook does NOT call `session_governor.py --check-limits`
- No progress summary is presented at ceiling

**What needs to change**:
1. Change default ceiling from 500 to 200 in `tool-call-ceiling.sh:20`
2. Integrate with `session_governor.py --check-limits --tool-calls N` for verdict
3. At STOP verdict (>=200): inject `additionalContext` via hook JSON stdout with progress summary and require user confirmation
4. At PAUSE verdict (>=160): inject warning context
5. Log ceiling events to session-signals JSONL (partially done already)

**Files to modify**:
- `.claude/hooks/tool-call-ceiling.sh` — threshold change, verdict integration, context injection
- `.claude/settings.json` line 4 env block — add `TOOL_CALL_CEILING=200` as explicit default

### Gap 2: Error Loop Breaker — No Hook Exists

**Current state**: Zero implementation at hook level. The `session_governor.py` has `check_session_limits(..., consecutive_error_count=N)` with verdict logic, but no hook tracks errors.

**What needs to be built**:
1. New hook script: `.claude/hooks/error-loop-breaker.sh` (or `.js`)
   - PostToolUse hook on `Bash` tool (errors come from Bash execution)
   - Read tool output from stdin JSON (`tool_input`, `tool_output` or exit code)
   - Hash/fingerprint error messages (strip timestamps, paths, line numbers)
   - Track consecutive identical errors in a temp file (`/tmp/claude-error-loop-${SESSION_ID}.json`)
   - After 3 consecutive identical errors: call `session_governor.py --check-limits --consecutive-errors 3`
   - On STOP verdict: emit `additionalContext` JSON with error details + escalation suggestion
   - Reset counter on any non-error result or different error
2. Register in `.claude/settings.json` PostToolUse section
3. State file cleanup in Stop hook or SessionStart hook

**Files to create**:
- `.claude/hooks/error-loop-breaker.sh` (new)

**Files to modify**:
- `.claude/settings.json` — add PostToolUse matcher for error-loop-breaker

### Gap 3: Pre-Push Review Gate — Default Still Warning Mode

**Current behavior** (`scripts/enforcement/require-review-on-push.sh:254`):
```bash
if [[ "${REVIEW_GATE_STRICT:-}" == "1" ]]; then
    # ... blocks push
    exit 1
fi
# Default warn mode — allow push
exit 0
```

- Default is warn (exit 0) — unreviewed pushes proceed
- `REVIEW_GATE_STRICT=1` must be explicitly set to block
- `SKIP_REVIEW_GATE=1` bypass already logs to `logs/hooks/review-gate-bypass.jsonl` (audit exists)
- Bypass logging IS present but only prints to stdout — no stderr warning about the audit

**What needs to change**:
1. Change default in `require-review-on-push.sh` from warn to strict: `REVIEW_GATE_STRICT="${REVIEW_GATE_STRICT:-1}"` (line 254 area)
2. Add `REVIEW_GATE_MODE=strict` to `.claude/settings.json` env block (or `.claude/.env` if it exists)
3. Enhance bypass logging: when `SKIP_REVIEW_GATE=1`, emit a visible stderr warning + log entry (currently just stdout)
4. Update `governance-checkpoints.yaml` line 73: change `enforced: false` to `enforced: true`
5. Update `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` to reflect new default

**Files to modify**:
- `scripts/enforcement/require-review-on-push.sh` — default strict mode
- `.claude/settings.json` env block — `REVIEW_GATE_STRICT=1`
- `scripts/workflow/governance-checkpoints.yaml` line 73 — `enforced: true`
- `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` — update default policy
- `docs/governance/SESSION-GOVERNANCE.md` — mark Phase 2b pre-push-review as completed

### Gap 4: Missing Tests

**Tests needed for hook-level enforcement**:

| Test | Target | Type |
|------|--------|------|
| Tool-call ceiling at 200 threshold | `.claude/hooks/tool-call-ceiling.sh` | Shell integration |
| Tool-call ceiling STOP verdict injection | Hook stdout JSON format | Shell integration |
| Error dedup/hashing produces stable fingerprint | Error-loop-breaker hash function | Unit (bash or Python) |
| 3 consecutive errors triggers STOP | Error-loop-breaker state tracking | Shell integration |
| Different error resets counter | Error-loop-breaker reset logic | Shell integration |
| Gate mode switching (warn→strict default) | `require-review-on-push.sh` | Shell integration (partially exists) |
| SKIP_REVIEW_GATE=1 audit trail visible | Bypass logging | Shell integration (partially exists) |

---

## 3. TDD-First Execution Plan

### Wave 1: Failing Tests (write first)

1. **`tests/hooks/test_tool_call_ceiling.py`** — Test that:
   - Default ceiling is 200 (not 500)
   - At 200 calls, hook outputs JSON with `additionalContext` containing progress summary
   - At 160 calls (80%), hook outputs warning context
   - Below 160, hook is silent
   - `TOOL_CALL_CEILING` env var overrides threshold

2. **`tests/hooks/test_error_loop_breaker.py`** — Test that:
   - Error message hashing produces stable fingerprints (strip timestamps/paths)
   - 3 consecutive identical errors produce STOP verdict
   - Different error resets counter to 1
   - Non-error output resets counter to 0
   - State file is created/updated in expected location
   - Hook outputs JSON with `additionalContext` on STOP

3. **`tests/hooks/test_review_gate_strict_default.sh`** — Test that:
   - Default mode (no env vars) blocks push on unreviewed feature commits (exit 1)
   - `REVIEW_GATE_STRICT=0` allows push with warning (exit 0)
   - `SKIP_REVIEW_GATE=1` bypasses with visible audit log entry

### Wave 2: Implementation

1. **Modify `.claude/hooks/tool-call-ceiling.sh`**:
   - Change `CEILING="${TOOL_CALL_CEILING:-500}"` → `CEILING="${TOOL_CALL_CEILING:-200}"`
   - Add JSON stdout output for hook protocol (`additionalContext`)
   - Integrate `session_governor.py --check-limits` call for verdict
   - Emit progress summary at ceiling: tools used, edits made, time elapsed

2. **Create `.claude/hooks/error-loop-breaker.sh`**:
   - Read Bash tool output from stdin JSON
   - Detect non-zero exit codes or error patterns in output
   - Hash error message (md5sum or sha256, strip volatile parts)
   - Track in `/tmp/claude-error-loop-${SESSION_ID:-default}.json`
   - Call `session_governor.py --check-limits --consecutive-errors N` when threshold hit
   - Output `additionalContext` JSON on STOP verdict

3. **Register error-loop-breaker in `.claude/settings.json`**:
   - Add PostToolUse matcher for `Bash` → `error-loop-breaker.sh`

4. **Modify `scripts/enforcement/require-review-on-push.sh`**:
   - Change default: `REVIEW_GATE_STRICT="${REVIEW_GATE_STRICT:-1}"`
   - Enhance bypass stderr warning

5. **Update `.claude/settings.json` env block**:
   - Add `"REVIEW_GATE_STRICT": "1"`, `"TOOL_CALL_CEILING": "200"`

6. **Update config/docs**:
   - `governance-checkpoints.yaml:73` → `enforced: true`
   - `SESSION-GOVERNANCE.md` — mark Phase 2b items complete
   - `REVIEW_GATE_BYPASS_POLICY.md` — update default

### Wave 3: Verification

Run all tests and verification commands (see section below).

### Verification Commands

```bash
# 1. Run Python-level governance tests
uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v

# 2. Run new hook tests
uv run --no-project python -m pytest tests/hooks/test_tool_call_ceiling.py -v
uv run --no-project python -m pytest tests/hooks/test_error_loop_breaker.py -v

# 3. Run review gate shell tests
bash scripts/enforcement/tests/test_require_review_on_push.sh

# 4. Verify tool-call-ceiling default is 200
grep -n 'TOOL_CALL_CEILING:-' .claude/hooks/tool-call-ceiling.sh | grep -q '200'

# 5. Verify error-loop-breaker hook exists and is registered
test -f .claude/hooks/error-loop-breaker.sh && echo "PASS: hook exists"
jq '.hooks.PostToolUse[] | select(.hooks[].command | contains("error-loop"))' .claude/settings.json

# 6. Verify strict mode is default
grep -n 'REVIEW_GATE_STRICT:-' scripts/enforcement/require-review-on-push.sh | grep -q '1'

# 7. Verify governance checkpoint marks pre-push as enforced
uv run --no-project python -c "
import yaml
with open('scripts/workflow/governance-checkpoints.yaml') as f:
    data = yaml.safe_load(f)
cp = next(c for c in data['checkpoints'] if c['id'] == 'pre-push-review')
assert cp['enforced'] == True, f'Expected enforced=true, got {cp[\"enforced\"]}'
print('PASS: pre-push-review enforced=true')
"

# 8. End-to-end: session governor check-limits with threshold values
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 200 --consecutive-errors 0
# Should exit 2 (STOP)

uv run scripts/workflow/session_governor.py --check-limits --tool-calls 150 --consecutive-errors 0
# Should exit 0 (CONTINUE)

uv run scripts/workflow/session_governor.py --check-limits --tool-calls 0 --consecutive-errors 3
# Should exit 2 (STOP)
```

---

## 4. Risk/Blocker Analysis

### Plan-Gate Blockers

| Blocker | Severity | Mitigation |
|---------|----------|------------|
| Issue #2056 lacks `status:plan-approved` label | **BLOCKING** | User must review this dossier and add label before implementation |
| Strict-mode default could break existing workflows | Medium | Add `REVIEW_GATE_STRICT=0` override documentation; test with dry-run first |
| Hook exit codes are advisory-only (Claude hooks can't kill sessions) | Design limitation | Use `additionalContext` JSON injection to make Claude self-enforce; document this as architectural constraint |

### Data/Source Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| `session_governor.py` runtime enforcement | Complete | Low — fully tested, 11 tests |
| `governance-checkpoints.yaml` thresholds | Complete | Low — correct values already defined |
| Session JSONL logging (`session-logger.sh`) | Complete | Low — already writes pre/post hooks |
| Hook JSON protocol (`additionalContext`) | Established | Low — used by `gsd-context-monitor.js` as reference |
| Error message hashing | **Not started** | Medium — need to define which parts of error output to strip for stable fingerprints |

### Likely Merge/Contention Concerns

| Concern | Likelihood | Notes |
|---------|-----------|-------|
| `.claude/settings.json` conflicts | High | This file changes frequently; keep edits minimal (add env vars, add one PostToolUse entry) |
| `require-review-on-push.sh` conflicts | Low | Rarely modified; last change was #1668 |
| `tool-call-ceiling.sh` conflicts | Low | Rarely modified; simple threshold change |
| Other overnight terminals editing `.claude/settings.json` | Medium | Terminal-6 (governance Phase 3 infrastructure) may also touch settings.json |

---

## 5. Ready-to-Execute Implementation Prompt

```markdown
## Implementation Prompt — Issue #2056

You are implementing GitHub issue #2056: "Session governance Phase 2: wire runtime enforcement into hooks"
in /mnt/local-analysis/workspace-hub.

### Prerequisites
- Issue #2056 must have label `status:plan-approved`
- Read this dossier: docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md

### TDD Workflow (strict order)

**Step 1: Write failing tests FIRST**

Create `tests/hooks/test_tool_call_ceiling.py`:
- Test default ceiling is 200 (grep hook script)
- Test hook outputs JSON `additionalContext` at ceiling
- Test hook outputs warning at 80% (160 calls)
- Test below 160 is silent (exit 0, no stdout)

Create `tests/hooks/test_error_loop_breaker.py`:
- Test error hashing (strip timestamps/paths, md5)
- Test 3 consecutive identical errors → STOP verdict
- Test different error resets counter
- Test non-error resets counter
- Test hook JSON output on STOP

Extend `scripts/enforcement/tests/test_require_review_on_push.sh`:
- Test default mode (no env vars) now blocks (exit 1)
- Test REVIEW_GATE_STRICT=0 overrides to warn mode

Run tests — all new tests should FAIL (red phase).

**Step 2: Implement**

1. `.claude/hooks/tool-call-ceiling.sh`:
   - Line 20: change `CEILING="${TOOL_CALL_CEILING:-500}"` → `CEILING="${TOOL_CALL_CEILING:-200}"`
   - Add JSON stdout output: `{"hookSpecificOutput": {"additionalContext": "...progress summary..."}}`
   - At STOP: include tool counts, session duration, "User confirmation required to continue"
   - At PAUSE: include "Approaching limit" warning

2. `.claude/hooks/error-loop-breaker.sh` (new file):
   - PostToolUse hook for Bash tool
   - Read stdin JSON, extract exit code and output
   - Hash error output: `echo "$ERROR_MSG" | sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}//g; s|/[^ ]*/||g; s/line [0-9]*//g' | md5sum | cut -d' ' -f1`
   - State file: `/tmp/claude-error-loop-${SESSION_ID:-default}.json` with `{"hash":"...","count":N}`
   - When count >= 3: call `uv run scripts/workflow/session_governor.py --check-limits --consecutive-errors $COUNT`
   - On STOP (exit 2): output additionalContext JSON
   - On non-error or different error: reset state

3. `.claude/settings.json`:
   - Add to env: `"TOOL_CALL_CEILING": "200"`, `"REVIEW_GATE_STRICT": "1"`
   - Add PostToolUse entry: `{"matcher": "Bash", "hooks": [{"type": "command", "command": "bash .claude/hooks/error-loop-breaker.sh", "timeout": 5}]}`

4. `scripts/enforcement/require-review-on-push.sh`:
   - Line 254: change `"${REVIEW_GATE_STRICT:-}"` → `"${REVIEW_GATE_STRICT:-1}"`

5. `scripts/workflow/governance-checkpoints.yaml`:
   - Line 73: change `enforced: false` → `enforced: true`

6. Documentation updates:
   - `docs/governance/SESSION-GOVERNANCE.md`: mark Phase 2b items complete
   - `docs/standards/REVIEW_GATE_BYPASS_POLICY.md`: update default to strict

**Step 3: Verify (all must pass)**

```bash
uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v
uv run --no-project python -m pytest tests/hooks/test_tool_call_ceiling.py -v
uv run --no-project python -m pytest tests/hooks/test_error_loop_breaker.py -v
bash scripts/enforcement/tests/test_require_review_on_push.sh
grep 'TOOL_CALL_CEILING:-' .claude/hooks/tool-call-ceiling.sh
grep 'REVIEW_GATE_STRICT:-' scripts/enforcement/require-review-on-push.sh
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 200
```

### Acceptance Criteria
- [ ] Tool-call ceiling fires at 200 (not 500) with user-facing progress summary
- [ ] Error-loop-breaker detects 3x consecutive identical errors and hard-stops
- [ ] Pre-push review gate defaults to strict mode (exit 1 on unreviewed pushes)
- [ ] SKIP_REVIEW_GATE=1 bypass is logged + audible (not silent)
- [ ] All new tests pass; all existing tests still pass
- [ ] Governance doc updated to reflect Phase 2b completion

### Cross-Review Requirements
- After implementation: run `/gsd:review --codex` for adversarial review
- Review routing policy applies: Claude + Codex minimum (2-provider)
- If `.claude/settings.json` changes trigger architecture-heavy detection → add Gemini review
```

---

## 6. Architectural Notes

### Hook Protocol Limitation

Claude Code hooks **cannot hard-kill a session** — they always return control to Claude. The "hard stop" is implemented via `additionalContext` injection: the hook outputs JSON that Claude reads as context, and Claude is expected to self-enforce the pause. This is documented in `tool-call-ceiling.sh:8`:

> "The ceiling is advisory — Claude hooks cannot hard-kill a session, but the warning is injected into the assistant context to trigger graceful shutdown."

This means the enforcement is advisory at the hook level but functionally a hard stop because Claude Code respects `additionalContext` instructions. The `session_governor.py` exit code (2=STOP) is used for programmatic consumers (CI, Hermes) but not by the hook protocol directly.

### Error Fingerprinting Strategy

The error-loop-breaker needs stable fingerprints across:
- Timestamps (strip date/time patterns)
- File paths (strip absolute path prefixes)
- Line numbers (strip `line N` patterns)
- Process IDs (strip PID-like numbers)

Recommended approach: pipe error through sed pattern to strip volatile parts, then md5sum. The `session_governor.py` already handles the verdict logic — the hook only needs to count and hash.

### Settings.json Contention

`.claude/settings.json` is the most-contended file in the repo. Changes should be:
- Minimal (add env vars, add one PostToolUse entry)
- Tested immediately after merge
- Coordinated with terminal-6 (governance Phase 3) if running in parallel

---

## 7. Final Recommendation

**READY AFTER LABEL UPDATE**

All prerequisite infrastructure is complete:
- `session_governor.py` has the correct threshold logic and verdict system (200 calls, 3 errors)
- The hook protocol (`additionalContext` JSON injection) is proven via `gsd-context-monitor.js`
- Review gate strict/bypass modes are fully implemented, just need default flip
- Test infrastructure exists and is well-established (pytest + shell tests)

The implementation delta is well-scoped (~150 lines of new code + ~30 lines of modifications):
- 1 new file (error-loop-breaker hook)
- 4 file modifications (ceiling threshold, settings.json, require-review-on-push, governance-checkpoints.yaml)
- 2 doc updates
- 3 new test files

**Action required**: Add `status:plan-approved` label to #2056 to unblock implementation.
