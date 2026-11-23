# Resume handoff — Ecosystem CI queue (session 5, #2442 in-progress)

## Quick prompt for next session

```
Resume ecosystem CI queue from
docs/handoffs/2026-04-21-ecosystem-ci-queue-resume-1.md

Issue #2442 (assethold CI) plan is at v5, through 4 cross-review waves.
Plan needs one more review wave after v5 fixes (checkout path blocker + P3 scope).
See handoff for full state.
```

## Queue state

| Issue | Priority | Status | Plan | Reviews |
|-------|----------|--------|------|---------|
| #2442 | HIGH | `plan-review` | v5 at `069afceaa` | 4 waves complete; v5 not yet reviewed |
| #2433 | Medium | **`plan-approved`** | exists | approved by user |
| #2437 | Medium | **`plan-approved`** | exists | approved by user |
| #2441 | Medium | `plan-review` | exists | Wave 1 complete (parallel session) |
| #2443 | Low | `plan-review` | exists | Wave 1 complete (parallel session) |
| #2444 | Low | `plan-review` | exists | Wave 1 complete (parallel session) |

## #2442 review history

| Wave | Claude | Codex | Gemini | Key fixes applied |
|------|--------|-------|--------|-------------------|
| 1 | MAJOR | MAJOR | MAJOR | assetutilities sibling dep, codecov inclusion, YAML proof |
| 2 | MAJOR | MAJOR | APPROVE | stale uv-sync wording, precondition verification, ref:main risk |
| 3 | MAJOR | MAJOR | APPROVE | execution-strategy contradiction (feature-branch vs direct-to-main) |
| 4 | MAJOR | MAJOR | APPROVE | checkout path blocker (actions/checkout rejects ../), P3 scope |

**Pattern:** Gemini has APPROVED since Wave 2. Claude and Codex keep finding real issues but they're getting smaller (text contradictions, not architectural). Wave 4 had one real P1 (checkout path) which v5 fixes with `git clone --depth 1`.

## What v5 changed (not yet reviewed)

1. Replaced `actions/checkout@v4 with path: ../assetutilities` with `git clone --depth 1 https://github.com/vamseeachanta/assetutilities.git ../assetutilities` (checkout@v4 requires path under $GITHUB_WORKSPACE)
2. Updated Files to Change table to match
3. Annotated P3 quality-gate acceptance criterion as "FOLLOW-ON, not required to close #2442"

## Next steps for receiving session

1. Run Wave 5 cross-review: `bash scripts/review/cross-review.sh docs/plans/2026-04-21-issue-2442-assethold-python-tests.md all --type plan`
2. If no MAJOR: post summary comment on #2442, confirm `status:plan-review`, message user
3. If MAJOR: iterate (remaining issues likely minor text contradictions)
4. After #2442 approval + execution, proceed to #2433 (already plan-approved, execute)
5. Then #2437 (already plan-approved, execute)
6. Then #2441, #2443, #2444 (each needs review verdict check + user approval)

## Cross-cutting context

- #2433 and #2437 are already `status:plan-approved` — skip to execution when reached
- Parallel session was running Wave 4 reviews for #2441/#2443/#2444 (check results at `scripts/review/results/2026-04-21-plan-244{1,3,4}-*-r2.md`)
- assetutilities is PUBLIC, has no cascading sibling deps, test_smoke.py exists (all verified)
- Direct-to-main execution per assethold repo convention (no feature branch)
- Issue-close criterion for #2442: P2 smoke-green (one matrix cell passes)
- Do NOT self-approve any plan — user-in-loop gate is load-bearing

## Review artifacts location

Wave 1: `scripts/review/results/2026-04-21-plan-2442-{claude,codex,gemini}.md`
Wave 2: `scripts/review/results/20260421T185638Z-*-plan-claude.md` etc.
Wave 3: `scripts/review/results/20260421T191126Z-*-plan-claude.md` etc.
Wave 4: `scripts/review/results/20260421T192054Z-*-plan-claude.md` etc.

## Commits this session (chronological)

| SHA | Description |
|-----|-------------|
| `fe5f216e5` | plan v2 — fix uv sync->system install, add phase gate enforcement |
| `0c39f0605` | plan v3 — address Wave 2 findings (preconditions, ref:main, Unicode) |
| `333f2b4c6` | plan v4 — resolve execution-strategy contradiction |
| `069afceaa` | plan v5 — fix checkout path blocker, clarify P3 follow-on |
