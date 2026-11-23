# Session Failures & Workflow Refactor Review

**Issue:** #1430 — Review recent session failures and workflow refactor history before adopting new patterns
**Date:** 2026-04-01
**Period analyzed:** 2026-03-01 to 2026-04-01

---

## Summary

1,433 commits in March. 37 fix/refactor commits in the last week alone (12% fix rate).
4,740 high-churn sessions (100+ tool calls). Dominant failure patterns are: runaway
tool-call loops, persistent smoke test failures, worktree merge conflicts, and
python runtime drift.

## 1. Session-Level Failures

### Runaway Tool-Call Sessions

The session-tool-summary data reveals extreme churn on three WRK items:

| WRK | Sessions | Total Calls | Max Single Session | Avg Calls/Session |
|-----|----------|------------|-------------------|-------------------|
| WRK-1022 | 2,665 | 3,876,520 | 7,429 | 1,454 |
| WRK-1012 | 466 | 1,384,075 | 6,264 | 2,970 |
| WRK-1005 | 548 | 910,923 | 5,970 | 1,662 |
| WRK-1011 | 47 | 100,113 | 5,342 | 2,130 |
| WRK-1021 | 11 | 52,336 | 4,829 | 4,757 |

**Finding:** WRK-1022 alone consumed 3.8M tool calls across 2,665 sessions with peaks
of 7,400+ calls per session. These are clearly runaway loops, not productive work.
This is the single largest source of wasted AI capacity.

**Root cause hypothesis:** Automated/cron-driven sessions without proper exit
conditions, or recursive task expansion without completion gates.

### 4,740 High-Churn Sessions Total

Any session with 100+ tool calls is likely either a complex legitimate task or
a runaway. At 4,740 such sessions, the system has a systemic loop problem.

## 2. Smoke Test Failures

| Repo | Failures | Date Range | Pattern |
|------|----------|------------|---------|
| worldenergydata | 12 | Mar 14-25 | **Persistent** — failed every day for 12 days |
| OGManufacturing | 3 | Mar 14 | Clustered single day |
| assetutilities | 2 | Mar 14 | Clustered single day |
| digitalmodel | 2 | Mar 14 | Clustered single day |
| assethold | 2 | Mar 14 | Clustered single day |

**Finding:** worldenergydata has been broken for 12+ consecutive days with no fix.
All failures show `passed=0 failed=0` — this is a test runner crash, not test failures.
The smoke test harness is likely failing to find or execute tests in these repos.

## 3. Drift Violations

| Date | Python Runtime | File Placement | Git Workflow |
|------|---------------|----------------|--------------|
| Mar 10 | 161 | 0 | 14 |
| Mar 24 | 25 | 0 | 3 |
| Mar 25 | 117 | 0 | 33 |

**Finding:** Python runtime violations swing wildly (25 → 117 → 161). These are
likely bare `python3`/`pip` invocations in scripts. The `uv run` convention is not
consistently enforced in automated scripts.

## 4. TDD Health

| Date | Repos Scanned | TDD Pairing % | At Risk |
|------|--------------|---------------|---------|
| Mar 28 | 1 | 3% | workspace-hub:3% |
| Mar 31 | 1 | 4% | workspace-hub:4% |
| Apr 1 | 1 | 3% | workspace-hub:3% |

**Finding:** TDD pairing sits at 3-4% despite being a "hard gate" in AGENTS.md.
Only workspace-hub is scanned. The gap between policy (TDD mandatory) and
reality (3% pairing) is the largest process integrity risk.

## 5. Worktree Merge Conflicts

15 merge-conflict resolution commits in March from worktree-based parallel work.
Primary conflict target: `STATE.md` and other shared state files.

**Finding:** The worktree pattern generates predictable merge conflicts on shared
state files. This is a known cost of parallel execution but suggests STATE.md
needs a conflict-resistant format (append-only log vs. edited document).

## 6. Refactor History (Last 30 Days)

8 refactor commits in March:
- Skills restructuring (#85): nested 24 orcaflex + 7 orcawave skills
- Specs → .planning/ path migration
- Settings deduplication (#1432)

No reverts of refactors — refactors have been stable.

3 reverts total (CDN links, archive/standalone, pre-phase log) — all small, all resolved.

## Recommendations Before Adopting New Patterns

### Must-Fix (blocks new pattern adoption)

1. **Kill runaway loops.** WRK-1022/1012/1005 consumed 6.1M tool calls. Add:
   - Hard tool-call ceiling per session (e.g., 500 calls → auto-abort)
   - Exit-condition checks in cron-driven sessions
   - Alert on sessions exceeding 200 calls

2. **Fix worldenergydata smoke tests.** 12 consecutive days of failure is unacceptable.
   The test runner itself is crashing (0 passed, 0 failed). Fix the harness, not the tests.

3. **Close the TDD gap.** 3% pairing vs. "TDD mandatory" policy. Either:
   - Enforce pairing (pre-commit hook that blocks commits without test changes), or
   - Downgrade the policy from "mandatory" to "recommended" and be honest about it

### Should-Fix (improves foundation)

4. **Enforce `uv run` in all scripts.** 117-161 python runtime violations persist.
   Add a pre-commit hook that greps for bare `python3`/`pip` in shell scripts.

5. **Make STATE.md append-only.** Eliminate merge conflicts from parallel worktrees
   by switching to an append-only log format.

6. **Expand smoke test coverage.** Only 1 repo scanned for TDD health. The system
   should cover at least tier-1 repos (workspace-hub, digitalmodel, assetutilities).

### Implication for #1427 and #1428

- **#1427 (subagent context isolation):** Safe to proceed — the worktree pattern
  already works, just needs STATE.md format fix for conflict reduction.
- **#1428 (automated verification gates):** **High priority** — the runaway loop
  problem and TDD gap both point to missing verification gates. This issue should
  be the next implementation target after fixing the runaway loops.
