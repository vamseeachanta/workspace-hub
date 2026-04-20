# Ecosystem Sync — Invocation Path Blocker (Post-Integration Validation)

Date: 2026-04-20
Context: clean integration worktree validation after landing Waves A/B/C into:
- `/mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration`
- branch `integration/ecosystem-sync-stage1-stage2-handoff`

## Summary
A real production-path blocker remains after successful Stage 1 integration: `run.py` succeeds when invoked as a module, but fails when invoked via the current script-path form used by the direct doctor command and cron wrapper design.

## Why this matters
Stage 1 code integration and test validation are green, but Stage 2 readiness cannot be called green while the production-style invocation path is broken.

The current mismatch is:
- invocation path used in docs/wrapper: `uv run scripts/ecosystem-sync/run.py ...`
- imports inside `run.py`: `from scripts.ecosystem_sync...`

That combination fails in the integrated checkout with `ModuleNotFoundError: No module named 'scripts'`.

## Evidence gathered
### 1. Integrated Stage 1 code is otherwise healthy
After fixture bootstrap in the clean integration worktree:
- `uv run pytest tests/ecosystem-sync -q` → `34 passed`
- `bash tests/hooks/test-require-plan-approval.sh` → pass

This isolates the remaining blocker to runtime invocation topology, not to broad Stage 1 feature correctness.

### 2. Direct script-path doctor fails
Command:
```bash
uv run scripts/ecosystem-sync/run.py --doctor
```

Observed result:
```text
Traceback (most recent call last):
  File ".../scripts/ecosystem-sync/run.py", line 10, in <module>
    from scripts.ecosystem_sync.config import SyncConfig, load_config
ModuleNotFoundError: No module named 'scripts'
```

### 3. Equivalent module invocation succeeds
Command:
```bash
uv run python -m scripts.ecosystem_sync.run --doctor
```

Observed result:
```text
2026-04-20 ... INFO doctor: PASS
module_doctor_rc=0
```

### 4. Wrapper currently uses the failing invocation style
Current wrapper file:
- `.claude/cron/ecosystem-sync.sh`

Relevant line:
```bash
if uv run scripts/ecosystem-sync/run.py "${EXTRA_ARGS[@]}" >> "$LOG" 2>&1; then
```

### 5. Wrapper validation in the integration worktree still fails early on expected topology
The integration worktree wrapper also fails at:
```bash
git pull --ff-only origin main
```

with log evidence:
```text
fatal: Not possible to fast-forward, aborting.
ecosystem-sync: git pull failed
```

That topology-specific wrapper failure is expected in the integration worktree, but it does not remove the direct proof above that the script-path invocation itself is broken.

## Root cause hypothesis
`run.py` assumes importable package context (`scripts.ecosystem_sync...`) but the current operational entrypoint invokes it as a file path under `scripts/ecosystem-sync/run.py`. Module-based execution sets up import resolution correctly; file-path execution here does not.

## Proposed fix direction
Primary recommendation:
- change operational invocation to module-based execution:
  - from: `uv run scripts/ecosystem-sync/run.py ...`
  - to: `uv run python -m scripts.ecosystem_sync.run ...`

Likely surfaces to update together:
- `.claude/cron/ecosystem-sync.sh`
- any docs/runbooks/command bundles still using script-path invocation
- possibly tests that should lock in the supported invocation style

## Acceptance criteria
- `uv run python -m scripts.ecosystem_sync.run --doctor` remains green
- the supported direct/operator invocation is documented consistently
- wrapper uses the same supported invocation form
- post-fix validation distinguishes invocation correctness from expected topology-specific `git pull --ff-only` behavior in non-main worktrees

## Recommended follow-up issue title
`fix(ecosystem-sync): invoke orchestrator as module so doctor/wrapper imports resolve`

## Recommended next action
Open a concrete GitHub issue for this blocker before calling Stage 2 readiness green, then implement the fix with TDD in the clean integration worktree.