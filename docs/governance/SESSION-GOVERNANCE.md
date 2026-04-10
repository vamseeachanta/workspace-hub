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

### Error Loop Tracking (wired in #2056)

The consecutive error tracking gap from Phase 2b has been resolved. A PostToolUse hook
(`error-loop-tracker.sh`) now tracks consecutive identical errors, and the PreToolUse
hook (`session-governor-check.sh`) reads the count and passes it to the governor.

See Phase 2d below for full details.

### Known Gaps (documented, not blocked)

| Gap | Status | Resolution Path |
|-----|--------|-----------------|
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

## What Was Implemented (Phase 2d) — 2026-04-09

### Error Loop Breaker: Consecutive Error Tracking (#2056)

Closes the last documented gap from Phase 2b: consecutive error tracking now
passes real values to the session governor instead of hardcoded 0.

#### PostToolUse Hook: `error-loop-tracker.sh`

**File**: `.claude/hooks/error-loop-tracker.sh`

A PostToolUse hook that detects errors in tool responses and tracks consecutive
identical errors. Registered in `.claude/settings.json` as the first PostToolUse
hook, matching all tool types.

**Error Detection** (multi-layer):
1. `tool_response.is_error` flag (most reliable, when available)
2. `tool_response.exit_code` non-zero (Bash tool failures)
3. Content pattern matching for common error signatures (Traceback, SyntaxError, etc.)

**Deduplication**: Errors are hashed (md5 of tool name + error content preview).
Only consecutive *identical* errors increment the counter. A different error or a
successful tool call resets the counter to 0.

**State files** (in `.claude/state/session-governor/`):
- `consecutive-error-count` — current consecutive identical error count
- `last-error-hash` — md5 hash of the last error signature
- `error-date` — date guard for daily reset

**Protocol**: Non-blocking PostToolUse hook. Never emits stdout JSON (no decision
influence). Diagnostic output goes to stderr only.

#### PreToolUse Integration

**File**: `.claude/hooks/session-governor-check.sh`

Updated to read `consecutive-error-count` from the state file and pass it to
`session_governor.py --check-limits --consecutive-errors $CONSEC_ERRORS`.

When the error loop breaker fires (3x consecutive identical error):
- **STOP** verdict emits a targeted block message: "Do NOT retry. Escalate to user."
- **PAUSE** at 2x emits a warning: "Consider a different approach before retrying."

#### End-to-End Flow

```
Tool call fails (PostToolUse) → error-loop-tracker.sh detects error
  → hashes error signature → compares with last-error-hash
  → same hash: increment consecutive-error-count
  → different hash: reset to 1, update hash
  → success: reset to 0

Next tool call (PreToolUse) → session-governor-check.sh
  → reads consecutive-error-count from state file
  → passes to session_governor.py --check-limits
  → at 3x: STOP verdict → {"decision":"block"} on stdout
```

**Tests**: 10 new tests in `tests/work-queue/test_session_governor.py` (55+ total),
covering hook existence, registration, matcher, state directory, governor verdicts,
PreToolUse integration (reads state file, no hardcoded zero), and reset behavior.

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
| Consecutive error tracking | **Resolved** (Phase 2d) | Wired via `error-loop-tracker.sh` + `session-governor-check.sh` (#2056) |
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

## What Was Implemented (Phase 3d) — 2026-04-09

### Enforcement Environment + End-to-End Hook Chain (#2027)

Completes the enforcement wiring started in Phase 3 (#2047). Creates a git-tracked
enforcement-env template and wires the full hook chain end-to-end.

#### Enforcement Environment

**File**: `scripts/enforcement/enforcement-env.sh` (git-tracked template)

Central configuration for enforcement strictness. Controls all gates via environment variables:

| Variable | Default | Effect |
|----------|---------|--------|
| `FORCE_PLAN_GATE_STRICT` | `1` | Plan gate blocks commits without approval |
| `REVIEW_GATE_STRICT` | `1` | Review gate blocks pushes without review |
| `DISABLE_ENFORCEMENT` | `0` | Master kill switch for all gates |

Installed to `.git/hooks/enforcement-env` via `scripts/enforcement/install-hooks.sh`.

#### Post-Commit Learning Pipeline

**File**: `scripts/hooks/post-commit-learnings.sh`

Fixed dead code in `.git/hooks/post-commit` where `track-skill-patches.sh` (#1719) and
`extract-learnings.sh` were unreachable after `exit 0`. The post-commit hook now calls:

1. Auto-push (background, existing)
2. `post-commit-learnings.sh` which chains:
   - `track-skill-patches.sh` — skill modification tracking (#1719)
   - `extract-learnings.sh` — commit analysis and pattern detection (#1760 Phase 4)

Both learning pipeline steps run with `|| true` guards — they never block commits.

#### Hook Install Script

**File**: `scripts/enforcement/install-hooks.sh`

Idempotent installer that:
1. Copies `enforcement-env.sh` to `.git/hooks/enforcement-env`
2. Wires enforcement-env sourcing into pre-commit (after PATH export)
3. Fixes post-commit dead code and wires learning pipeline

Run: `bash scripts/enforcement/install-hooks.sh` (supports `--dry-run`).

#### End-to-End Chain (Verified)

```
pre-commit:
  source enforcement-env (FORCE_PLAN_GATE_STRICT=1, REVIEW_GATE_STRICT=1)
  -> encoding check
  -> claude-md-limits check
  -> skill content scan
  -> JS lockfile guard
  -> require-plan-approval.sh --strict (blocks without plan approval)

post-commit:
  -> auto-push (background)
  -> post-commit-learnings.sh
     -> track-skill-patches.sh
     -> extract-learnings.sh HEAD

pre-push:
  -> require-review-on-push.sh (blocks without review evidence)
```

## What Was Implemented (Phase 3e) — 2026-04-09

### Governance Skill Smoke Tests

Adds regression tests that verify governance coordination skills remain structurally
intact. Each test validates file existence, frontmatter presence, and key content markers.

#### Test Coverage

| Test file | Skill under test | Assertions |
|-----------|-----------------|------------|
| `test_session_start_routine_smoke.py` | `coordination/session-start-routine` | exists, frontmatter, body contains "pre-flight", "context", "environment" |
| `test_session_corpus_audit_smoke.py` | `coordination/session-corpus-audit` | exists, frontmatter |
| `test_comprehensive_learning_smoke.py` | `coordination/comprehensive-learning-wrapper` | wrapper exists, cron script `scripts/cron/comprehensive-learning-nightly.sh` exists |
| `test_cross_review_policy_smoke.py` | `coordination/cross-review-policy` | exists, body contains `AI_REVIEW_ROUTING_POLICY` |

Run: `uv run pytest tests/skills/test_*_smoke.py -v`

These smoke tests act as canaries — if a skill file is accidentally deleted, renamed,
or has its frontmatter corrupted during refactoring, CI catches it before session
workflows silently break.

## What Was Implemented (Phase 4) — 2026-04-09

### Artifact Verification + Knowledge Propagation (#2020)

Completes the orchestrator/worker context enforcement gap identified in #2020.
Phase 1 (plan gate enforcement) was done by #2047. This phase adds the remaining
two pieces: verification of worker outputs and propagation of worker discoveries.

#### 4a. Artifact Verification Skill

**File**: `.claude/skills/coordination/artifact-verification/SKILL.md`

A structured checklist for orchestrators to verify worker outputs against the
approved plan before accepting artifacts. Covers:

1. **Scope alignment** — files changed match plan's "Files to Change"
2. **Acceptance criteria** — each AC from the plan is satisfied with evidence
3. **Test coverage** — tests match the plan's TDD test list
4. **Artifact completeness** — all deliverables present
5. **No unplanned side effects** — no unrelated changes

**Verification markers**: After verification, the orchestrator creates a marker
in `.planning/verified/<issue>.md` with verdict (PASS/PARTIAL/FAIL), checklist
results, and notes. The `.planning/verified/` directory is now git-tracked.

**FAIL feedback protocol**: On rejection, the orchestrator provides specific
per-item feedback referencing the exact plan section, not generic rejection.
The worker is re-dispatched with targeted feedback.

**Integration point**: Fits between implementation and cross-review in the
issue-planning-mode workflow:
```
Plan Approved -> Worker Implements -> ARTIFACT VERIFICATION -> Cross-Review -> Close
```

#### 4b. Worker Discovery Protocol

**File**: `.claude/skills/coordination/worker-discovery-protocol/SKILL.md`

Defines how workers capture discoveries and how orchestrators propagate them.

**Worker side**: During execution, workers append JSONL entries to
`.planning/discoveries/YYYY-MM-DD-worker.jsonl` with structured fields:
timestamp, issue, category, summary, detail, severity, source.

Discovery categories: `bug`, `convention`, `dependency`, `quirk`, `performance`,
`security`, `pattern`.

At session end, workers include a `## Worker Discoveries` summary block.

**Orchestrator side**: After worker returns, the orchestrator triages each
discovery and routes to the appropriate target:

| Discovery type | Primary target | Action |
|---------------|---------------|--------|
| Bug | GitHub issue | `gh issue create` |
| Convention | Relevant SKILL.md | Edit skill |
| Dependency | Module docstring | Update docs |
| Quirk | KNOWLEDGE.md | Append entry |
| Performance | KNOWLEDGE.md | Append entry |
| Security | GitHub issue (priority:high) | `gh issue create` |
| Pattern | SKILL.md (new or existing) | Create/edit skill |

**Integration**: Discovery JSONL files are compatible with the comprehensive-learning
pipeline and are processed during nightly knowledge harvesting.

#### 4c. Planning Directory Structure

New git-tracked directories:
- `.planning/verified/` — verification markers from artifact verification
- `.planning/discoveries/` — worker discovery JSONL logs

## What Was Implemented (Phase 3f) — 2026-04-10

### Per-Session Tool-Call Counter

**Problem**: The `session-governor-check.sh` hook maintained a single counter file
(`tool-call-count`) reset only at midnight. On days with multiple Claude sessions,
tool calls accumulated across all sessions toward the 200-call ceiling, causing HARD
STOP blocks in session 2+ regardless of how many calls that individual session had made.

**Fix**:

| | Before | After |
|--|--------|-------|
| Counter file | `tool-call-count` (one per day) | `tool-call-count-$PPID` (one per Claude process) |
| Reset trigger | Midnight | New Claude session (new OS process = new PPID) |
| Threshold | 200 calls/day | 1000 calls/session |
| Fast-path ceiling | 160 (80% of 200) | 800 (80% of 1000) |

**Why `$PPID` works**: Every `claude` invocation is a new OS process. The bash hook's
`$PPID` is the PID of the spawning Claude process — constant within a session,
different across sessions. Old PID-based files are cleaned up after 7 days.

**Files changed**:
- `.claude/hooks/session-governor-check.sh` — PPID-based counter, updated messages
- `scripts/workflow/governance-checkpoints.yaml` — threshold 1000
- `tests/work-queue/test_session_governor.py` — test assertions aligned to new threshold

**Follow-up issues**:
- #2064 — fix pre-existing plan-approval-gate test path mismatches
- #2065 — derive `FAST_PATH_CEILING` dynamically from YAML threshold

## What Was Implemented (Phase 3g) — 2026-04-09

### Session Infrastructure Skills Restoration (#2057)

Restores four session skills lost during the GSD migration or never formalized as actionable
skills. Driven by #1839's Phase 3 scope.

| Skill | Path | Lines | Purpose |
|-------|------|-------|---------|
| session-start-routine | `.claude/skills/coordination/session-start-routine/SKILL.md` | 44 | Pre-flight checks at session start — load context, check prior state, validate env, check in-flight work |
| session-corpus-audit | `.claude/skills/coordination/session-corpus-audit/SKILL.md` | 58 | Session quality trend analysis from `.claude/state/session-signals/` |
| comprehensive-learning-wrapper | `.claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md` | 143 | Skill-tree discoverability wrapper for the nightly learning pipeline cron |
| cross-review-policy | `.claude/skills/coordination/cross-review-policy/SKILL.md` | 57 | Actionable three-agent review routing derived from `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |

**Commits**: e582d7e70..ef8e7826b (overnight batch 2026-04-09)

**Note**: `session-corpus-audit` also exists at `.claude/skills/workspace-hub/session-corpus-audit/SKILL.md`
(434 lines, Hermes-authored, comprehensive). The coordination version is a slim reference copy.
The workspace-hub version is canonical for detailed signal analysis.

## What Remains (Phase 5)

### Phase 5: Hermes Orchestration
- Hermes manages gate transitions and hard-stop enforcement
- Hermes dispatches to Claude/Codex/Gemini per routing matrix
- Hermes tracks session metrics and generates session reports
- Inter-session continuity validation

## References

- Issue: #1839, #2020, #2027, #2028 (CI enforcement)
- Trust Architecture: `docs/governance/TRUST-ARCHITECTURE.md`
- Review Routing Policy: `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- Session failures analysis: `docs/reports/session-failures-and-refactor-review.md`
