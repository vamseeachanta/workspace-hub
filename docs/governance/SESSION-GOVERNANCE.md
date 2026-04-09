# Session Governance — Hard-Stop Checkpoints

> Phase 1 implementation of #1839. Provides the checkpoint model and verification utility.
> Subsequent phases add runtime enforcement via hooks and Hermes orchestration.

## What Was Implemented (Phase 1)

### 1. Machine-Readable Checkpoint Config

**File**: `scripts/workflow/governance-checkpoints.yaml`

Defines 7 session lifecycle checkpoints with:
- `type`: `hard-stop` (user must approve) or `auto-gate` (system-enforced)
- `enforced`: whether failure blocks the session (`true`) or is advisory (`false`)
- `threshold`: numeric limits for runtime gates (tool-call ceiling, error loop)

### 2. Session Governor Utility

**File**: `scripts/workflow/session_governor.py`

A verification utility that checks which gates have been satisfied:

```bash
# List all checkpoints
uv run scripts/workflow/session_governor.py --list

# Check session with specific gates passed
uv run scripts/workflow/session_governor.py --passed plan-approval tdd-red

# Check with no gates (worst case)
uv run scripts/workflow/session_governor.py
```

Exit code: `0` = all enforced gates pass, `1` = at least one enforced gate fails.

### 3. Tests

**File**: `tests/work-queue/test_session_governor.py` — 14 tests covering config loading, gate verification logic, and edge cases.

## Current Checkpoints

| ID | Name | Type | Enforced | Stage |
|----|------|------|----------|-------|
| plan-approval | Plan Approval | hard-stop | Yes | pre-implement |
| review-verdict | Review Verdict | hard-stop | Yes | post-review |
| session-close | Session Close | hard-stop | No (Phase 2) | end |
| tdd-red | TDD Red Phase | auto-gate | Yes | pre-implement |
| tool-call-ceiling | Tool Call Ceiling (200) | auto-gate | Yes | runtime |
| error-loop-breaker | Error Loop Breaker (3x) | auto-gate | Yes | runtime |
| pre-push-review | Pre-Push Review Gate | auto-gate | Yes (#2028) | pre-push |

## What Was Implemented (Phase 2) — 2026-04-09

### Runtime Enforcement via `check_session_limits()`

**File**: `scripts/workflow/session_governor.py`

The session governor now supports runtime enforcement — checking live session metrics
against governance thresholds. Three-tier verdict system:
- **CONTINUE** (exit 0): below 80% of threshold
- **PAUSE** (exit 1): 80-99% of threshold — warning zone
- **STOP** (exit 2): at or above threshold — hard stop required

```bash
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 170 --consecutive-errors 2
```

Tests: 11 new tests in `tests/work-queue/test_session_governor.py` (25 total).

### Queue Staleness + Parity Check

**File**: `scripts/refresh-agent-work-queue.py`

- `--check-staleness`: reports if queue file is >7 days old
- `--parity-check`: compares file issue counts vs live GitHub

Tests: 7 new tests in `tests/work-queue/test_queue_refresh.py` (23 total).

## What Was Implemented (Phase 2b) — 2026-04-09

### Hook Integration: `session-governor-check.sh`

**File**: `.claude/hooks/session-governor-check.sh`

A PreToolUse hook that wires `check_session_limits()` into the Claude Code session lifecycle.
Registered in `.claude/settings.json` as the first PreToolUse hook, matching all tool types.

**Architecture:**
- Maintains a per-day tool call counter in `.claude/state/session-governor/tool-call-count`
- **Fast path** (< 160 calls): pure bash counter increment, exits silently (~0ms overhead)
- **Warning zone** (160-199 calls): delegates to `session_governor.py --check-limits`, emits stderr warning
- **Ceiling** (>= 200 calls): delegates to governor, emits `{"decision":"block"}` on stdout to block further tool calls

**Protocol:** follows the repo convention from `cross-review-gate.sh` — stdout JSON for Claude context, stderr for user terminal. Always exits 0; blocking is via `{"decision":"block"}`.

**Tests:** 8 new tests in `tests/work-queue/test_session_governor.py` (33 total), covering:
- Hook file existence and executable bit
- Hook registration in settings.json
- Governor exit code mapping (0=CONTINUE, 1=PAUSE, 2=STOP)
- Fast-path threshold alignment with governance config
- CLI exit code verification via subprocess

### Known Gaps (documented, not blocked)

| Gap | Status | Resolution Path |
|-----|--------|-----------------|
| Consecutive error tracking | Passes 0 to governor | Wire into session signal pipeline (Phase 3) |
| Counter resets daily, not per-session | No reliable session ID in hook env | Awaits Claude Code session ID exposure |

## What Was Implemented (Phase 2c) — 2026-04-09

### Plan-Approval Enforcement Hook

**File**: `.claude/hooks/plan-approval-gate.sh`

A PreToolUse hook that enforces the plan-approval hard-stop (AC #1). Blocks `Write|Edit|MultiEdit`
to implementation paths when no approval marker exists in `.planning/plan-approved/`.

**Approval marker convention:**
- After user approves a plan, create: `.planning/plan-approved/<issue-number>.md`
- For non-issue work: `.planning/plan-approved/session.md`
- Safe paths (always allowed without marker): `.planning/`, `docs/`, `tests/`, `.claude/`,
  `scripts/workflow/`, `scripts/enforcement/`, `*.md` files

**Also gates:** `git push` commands via Bash tool — requires approval marker.

**Bypass:** `SKIP_PLAN_APPROVAL_GATE=1` (emergency only, logged to stderr).

### Strict Review Gate Default

**Files**: `scripts/enforcement/require-review-on-push.sh`, `scripts/workflow/governance-checkpoints.yaml`, `.claude/settings.json`

The pre-push review gate now defaults to **strict mode** (AC #7):
- `REVIEW_GATE_STRICT=1` set in `.claude/settings.json` env block
- `require-review-on-push.sh` changed from `${REVIEW_GATE_STRICT:-}` (empty = warn) to `${REVIEW_GATE_STRICT:-1}` (default = block)
- `pre-push-review` checkpoint promoted to `enforced: true` in governance-checkpoints.yaml

**Override:** `REVIEW_GATE_STRICT=0 git push` reverts to warn mode for a single push.

### Old 500-Ceiling Hook Removed

**File**: `.claude/settings.json` (PostToolUse section)

The old `tool-call-ceiling.sh` PostToolUse hook (500-call ceiling from #1428) has been **removed
from settings.json**. The PreToolUse `session-governor-check.sh` (200-call ceiling) is now the
sole active ceiling mechanism. The script file remains for reference but is no longer wired.

**Tests:** 16 new tests in `tests/work-queue/test_session_governor.py` (49 total), covering:
- Plan-approval hook existence, registration, matcher, marker directory
- Hook blocking behavior (no marker → block, safe paths → allow, with marker → allow)
- Strict review gate env var, YAML enforcement flag, script default
- Old ceiling hook removal verification

## What Was Implemented (Phase 3) — 2026-04-09

### Stronger Planning Workflow Enforcement (#2047)

Triggered by compliance audit (#2046) which found **0% compliance** with the strict planning
workflow. The audit revealed 5 failure modes: workflow was DOA, governance work self-exempted,
safe-path exemptions negated enforcement, label workflow was ceremonial, and only Claude Code
was gated.

#### 3a. Narrowed Safe-Path Exemptions

**File**: `.claude/hooks/plan-approval-gate.sh`

The `is_safe_path()` function was narrowed significantly:

| Before (#2045) | After (#2047) | Rationale |
|---|---|---|
| `*.md` (all markdown) | Removed | Was allowing all implementation docs to bypass |
| `tests/*` | Removed | Test changes should require plan approval |
| `.claude/*` | Kept | Harness infrastructure, not implementation |
| `scripts/*` (all) | Only `scripts/workflow/`, `scripts/enforcement/` | General scripts are implementation code |
| `knowledge/*` | Removed | Knowledge changes should follow planning |
| `docs/*` (all) | Only `docs/plans/`, `docs/governance/`, `docs/reports/`, `docs/standards/`, `docs/handoffs/` | Targeted governance paths only |

New safe paths added: `.git/hooks/*` (hook maintenance).

#### 3b. Self-Approval Detection

**File**: `.claude/hooks/plan-approval-gate.sh`

New `is_self_approved()` function detects approval markers that were created by the implementing
agent rather than by a human operator:

- **Content check**: rejects markers containing "Worker session", "auto-approved", "self-approved"
- **Freshness check**: rejects markers created within 120 seconds that have never been committed to git
- **Iteration**: `has_approval()` now checks ALL markers in `.planning/plan-approved/`, accepting
  if ANY one passes the self-approval test (prevents one bad marker from blocking all work)

#### 3c. Pre-Commit Hook Integration

**File**: `.git/hooks/pre-commit`

The plan-approval gate is now wired into the git pre-commit hook via
`scripts/enforcement/require-plan-approval.sh --strict`. This fires for ALL git commits
regardless of which tool makes them (Claude Code, Codex CLI, Gemini CLI, manual `git commit`).

**Bypass**: `FORCE_PLAN_GATE=1 git commit` (logged by the script).

This addresses the audit finding that only Claude Code was gated (Failure Mode 5).

#### 3d. Fixed `issue-planning-mode` Skill

**File**: `.claude/skills/coordination/issue-planning-mode/SKILL.md`

The skill was a deprecated stub pointing to nonexistent `gh-work-planning`. It has been
replaced with a functional skill containing the full 5-step planning workflow:
1. Create plan file from template
2. Apply `status:plan-review` label
3. Get adversarial review
4. Get user approval (creates marker)
5. Implement (gate enforced)

### Remaining Gaps (Phase 3)

| Gap | Status | Resolution Path |
|-----|--------|-----------------|
| Consecutive error tracking | Not yet wired | Wire into session-governor-check.sh |
| GitHub label checking in hooks | Not implemented | Would require `gh` API calls in hooks (slow) |
| Cross-agent memory bridge | Partial | See `compound-extended` skill |

## What Was Implemented (Phase 3b) — 2026-04-09

### GitHub Actions CI Enforcement (#2028)

**File**: `.github/workflows/enforcement-gate.yml`

PR-level enforcement that mirrors local pre-push/pre-commit gates in CI, so reviewers
see compliance status on every pull request to `main`.

#### Jobs

| Job | Gate Type | Behavior |
|-----|-----------|----------|
| `review-evidence` | Blocking | Runs `require-review-on-push.sh` with `REVIEW_GATE_STRICT=1` against the PR commit range. Fails the PR if feature/fix commits lack review evidence. |
| `plan-approval` | Blocking | Runs `require-plan-approval.sh --strict` against staged files. Fails if implementation changes lack plan approval markers. |
| `compliance-dashboard` | Advisory | Runs `compliance-dashboard.sh` with a 168h window. Reports compliance rate in the PR summary but does not block merge (`continue-on-error: true`). |

#### Enforcement Layers (Complete)

| Layer | Mechanism | Scope | Blocking |
|-------|-----------|-------|----------|
| Pre-commit hook | `require-plan-approval.sh --strict` | All local commits | Yes |
| PreToolUse hook | `plan-approval-gate.sh` | Claude Code sessions | Yes |
| Pre-push hook | `require-review-on-push.sh` | All local pushes | Yes (strict default) |
| GitHub Actions CI | `enforcement-gate.yml` | All PRs to main | Yes (review + plan) |

This closes the gap where changes pushed via bypass (`SKIP_REVIEW_GATE=1`) would still
be flagged at the PR level before merge.

## What Remains (Phase 4)

### Phase 4: Hermes Orchestration
- Hermes manages gate transitions and hard-stop enforcement
- Hermes dispatches to Claude/Codex/Gemini per routing matrix
- Hermes tracks session metrics and generates session reports
- Inter-session continuity validation

## References

- Issue: #1839, #2028 (CI enforcement)
- Trust Architecture: `docs/governance/TRUST-ARCHITECTURE.md`
- Review Routing Policy: `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- Session failures analysis: `docs/reports/session-failures-and-refactor-review.md`
