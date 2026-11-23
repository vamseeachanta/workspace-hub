# 2026-04-20 Long Nightly Batch

## Reviewed candidates

Included tonight:
- #2206 — verify-close stale open issue; implementation commit `880720fdf` is already on `origin/main`
- #2207 — verify-close stale open issue; implementation commit `a7b0fd4fc5cbeee004bb0cde738e067a555af8e4` is already on `origin/main`
- #2209 — verify-close stale open issue; implementation commit `4fb05a4525e6ecc36ca364c94a78d2a92e165c9c` is already on `origin/main`
- #2320 / PR #2354 — repair failing checks on live implementation branch
- #2348 — execute approved ToS / robots / unpause-governance implementation in isolated worktree

Excluded tonight:
- #2408 — GitHub label says `status:plan-approved`, but issue comments say do not treat as approval-ready yet; excluded as stale/mislabeled
- #2403 — scaffold is landed, but real measurement phase is gated on model/runtime provisioning; not a good unattended batch candidate
- #2346 — multi-repo GTM + digitalmodel + website deployment scope is broader and riskier than tonight’s bounded wave

## Issue to terminal mapping

| Issue | Stream | Worktree |
|---:|---|---|
| #2206 | T1 verify-close | `/mnt/local-analysis/worktrees/workspace-hub-issue-2206-verify` |
| #2207 | T2 verify-close | `/mnt/local-analysis/worktrees/workspace-hub-issue-2207-verify` |
| #2209 | T3 verify-close | `/mnt/local-analysis/worktrees/workspace-hub-issue-2209-verify` |
| #2320 | T4 PR repair | `/mnt/local-analysis/worktrees/workspace-hub-issue-2320` |
| #2348 | T5 implementation | `/mnt/local-analysis/worktrees/workspace-hub-issue-2348-nightly` |

## Contention map

T1 writes:
- `.nightly-results/2026-04-20-issue-2206.md`
- GitHub comment/close only
- no product-code edits unless verification proves the issue is not actually done

T2 writes:
- `.nightly-results/2026-04-20-issue-2207.md`
- GitHub comment/close only
- no product-code edits unless verification proves the issue is not actually done

T3 writes:
- `.nightly-results/2026-04-20-issue-2209.md`
- GitHub comment/close only
- no product-code edits unless verification proves the issue is not actually done

T4 writes:
- `scripts/skills/`
- `tests/skills/`
- `docs/reports/skill-invocation-*`
- `.nightly-results/2026-04-20-issue-2320.md`

T5 writes:
- `scripts/gtm/job-market-scanner.py`
- `docs/strategy/gtm/job-market-scan/`
- `tests/gtm/`
- `config/scheduled-tasks/schedule-tasks.yaml` only if all unpause criteria are genuinely satisfied
- `.nightly-results/2026-04-20-issue-2348.md`
- `.planning/plan-approved/2348.md` already precommitted

Zero intended overlap.

## What should exist by morning

From T1:
- evidence bundle proving whether #2206 is already satisfied
- GitHub closeout comment and closure if satisfied

From T2:
- evidence bundle proving whether #2207 is already satisfied
- GitHub closeout comment and closure if satisfied

From T3:
- evidence bundle proving whether #2209 is already satisfied
- GitHub closeout comment and closure if satisfied

From T4:
- repaired PR #2354 branch or precise blocker report with reproduced failing checks

From T5:
- concrete #2348 implementation progress on the approved plan, or a bounded blocker report with tests/evidence
