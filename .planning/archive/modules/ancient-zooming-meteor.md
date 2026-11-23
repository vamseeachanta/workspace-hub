# WRK-1172: Session Startup E2E Health Check

## Context

Agents inherit broken state from prior sessions and waste time debugging carry-over issues. Anthropic's "Effective Harnesses for Long-Running Agents" recommends running a basic e2e test at startup. Per user direction: **nightly batch** (not inline session-start) to keep session-start lightweight.

## Design

**Two components:**
1. **Nightly cron script** — runs smoke tests for tier-1 repos, caches results
2. **Session-start reader** — reads cached results, surfaces failures as warnings

### Component 1: `scripts/cron/nightly-smoke-tests.sh`

Follows `test-health-check.sh` pattern (best-effort, JSONL signals + YAML report).

**Flow:**
1. For each tier-1 repo (assetutilities, digitalmodel, worldenergydata, assethold), run `uv run python -m pytest -m smoke -q --tb=line --timeout=15` with per-repo PYTHONPATH
2. Capture exit code, pass/fail counts, duration per repo
3. Write YAML report to `.claude/state/session-health.yaml`
4. Append JSONL records to `.claude/state/session-signals/smoke-tests.jsonl`
5. Total budget: <60s (15s timeout per repo × 4 repos)

**Output format** (`.claude/state/session-health.yaml`):
```yaml
run_at: "2026-03-14T01:00:00Z"
total_duration_s: 23
all_healthy: false
repos:
  assetutilities: { status: pass, passed: 12, failed: 0, duration_s: 4 }
  digitalmodel: { status: pass, passed: 8, failed: 0, duration_s: 6 }
  worldenergydata: { status: fail, passed: 5, failed: 2, duration_s: 8 }
  assethold: { status: pass, passed: 10, failed: 0, duration_s: 5 }
```

**Cron integration:**
- Add as new check (R12) in `scripts/readiness/nightly-readiness.sh`
- Called from `comprehensive-learning-nightly.sh` Step 5 (existing readiness slot)
- Schedule: runs with existing nightly pipeline at 02:00 — no separate cron entry needed

### Component 2: Session-start integration

Add to `session-start/SKILL.md` as Step 1b (after Readiness Report, before Session Snapshot):
- Read `.claude/state/session-health.yaml`
- If `all_healthy: true` and age < 36h → display "All repos healthy" (one line)
- If any repo failed → display warning with repo names
- If file missing or stale (>36h) → display "Health check stale — consider running manually"

### Component 3: TDD tests

`scripts/cron/tests/test_nightly_smoke_tests.sh` — shell-based tests:
1. Test YAML output format (valid YAML, required fields present)
2. Test with mock repo that passes → `all_healthy: true`
3. Test with mock repo that fails → `all_healthy: false`, failed repo listed
4. Test JSONL signal emission (valid JSON per line)

### Files to create/modify

| Action | File | Purpose |
|--------|------|---------|
| Create | `scripts/cron/nightly-smoke-tests.sh` | Core health check script |
| Create | `scripts/cron/tests/test_nightly_smoke_tests.sh` | TDD tests |
| Modify | `scripts/readiness/nightly-readiness.sh` | Add R12 smoke test check |
| Modify | `scripts/cron/crontab-template.sh` | Document new check in template comments |
| Modify | `.claude/skills/workspace-hub/session-start/SKILL.md` | Add Step 1b health reader |

### Existing code to reuse

- `test-health-check.sh` (`scripts/readiness/test-health-check.sh`): JSONL emit pattern, `_json_str()` helper, `log()`/`warn()` pattern
- `nightly-readiness.sh` (`scripts/readiness/nightly-readiness.sh`): `log_pass()`/`log_fail()` check pattern, issues accumulator
- `repo-map.yaml` (`config/onboarding/repo-map.yaml`): tier-1 repo list + test commands

## Verification

1. Run `bash scripts/cron/nightly-smoke-tests.sh` manually — confirm YAML + JSONL output
2. Run TDD tests: `bash scripts/cron/tests/test_nightly_smoke_tests.sh`
3. Verify `.claude/state/session-health.yaml` has correct format
4. Verify session-start skill reads and surfaces results correctly
5. Confirm total runtime < 60s
