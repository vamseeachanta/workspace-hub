# 2026-04-21 nightly CI batch

## Objective
Run a Claude-only overnight batch to move the ecosystem CI queue forward with zero repo/file contention.

## Live eligibility pass
- #2442 OPEN + `status:plan-approved` in workspace-hub. Live repo state shows Phase 1 already landed in `vamseeachanta/assethold` at commit `457ea2d` (`fix(ci): unblock assethold python workflow startup (#2442)`). Latest `Python Tests` run `24756679196` lasted 58s and failed after startup, so the issue remains directly executable. Overnight goal is Phase 2 verification + fix + close if smoke green.
- #2433 OPEN + `status:plan-approved`. `worldenergydata` main is still red (`CI` run `24754590982`). Repo already contains some partial CI softening (`continue-on-error` appears in `.github/workflows/ci.yml`), so the worker must do an already-done precheck before editing and then execute only the missing remainder.
- #2437 OPEN + `status:plan-approved`. `workspace-hub` main still contains the orphan references in `.github/workflows/baseline-check.yml` and `.pre-commit-config.yaml`. Directly executable in an isolated worktree.
- #2441 / #2443 / #2444 are OPEN but only `status:plan-review`. These are NOT implementation-eligible. Overnight workstream is planning-only: revise plans against Wave-2 MAJOR findings, rerun adversarial review, post review-state comments, and stop.

## Terminal map
| Issue(s) | Terminal | Mode | Repo / worktree |
|---|---|---|---|
| #2442 | T1 | implementation | `/mnt/local-analysis/worktrees/assethold-2442` |
| #2433 | T2 | implementation | `/mnt/local-analysis/worktrees/worldenergydata-2433` |
| #2437 | T3 | implementation | `/mnt/local-analysis/worktrees/ws-2437` |
| #2441, #2443, #2444 | T4 | planning-only | `/mnt/local-analysis/worktrees/ws-plan-2441-2444` |

## Contention map
- T1 writes only in `assethold-2442`: `.github/workflows/python-tests.yml` plus optional tiny supporting repo files if required by validation; GitHub comments on workspace-hub issues `#2442` and `#2424`.
- T2 writes only in `worldenergydata-2433`: `tests/conftest.py`, `.github/workflows/ci.yml`, and the specific test files black/isort touches under `tests/`; GitHub comments on workspace-hub issue `#2433` and parent `#2424`.
- T3 writes only in `ws-2437`: `.github/workflows/baseline-check.yml`, `.pre-commit-config.yaml`, `scripts/work-queue/whats-next.sh`, `scripts/work-queue/verify-gate-evidence.py`, `.planning/plan-approved/2437.md`, and any follow-up issue body temp files it creates locally; GitHub comments/issues only for `#2437` and child issues under `#2424`.
- T4 writes only in `ws-plan-2441-2444`: `docs/plans/2026-04-21-issue-2441-digitalmodel-pylife.md`, `docs/plans/2026-04-21-issue-2443-achantas-data-ci.md`, `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`, matching `scripts/review/results/2026-04-21-plan-244{1,3,4}-*.md` artifacts, and `docs/plans/README.md` if needed.
- Zero overlap by repo/worktree and file ownership.

## Launch pattern
Use non-interactive Claude Code with prompt-as-argument and closed stdin:

```bash
PROMPT=$(< docs/plans/overnight-prompts/2026-04-21/terminal-N-*.md)
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-budget-usd 25 \
  "$PROMPT" </dev/null | tee /mnt/local-analysis/workspace-hub/logs/nightly-2026-04-21/terminal-N.log
```

## What you should have by morning
- T1: either `assethold` P2 fix landed on `main` with CI evidence and `#2442` closed, or a concrete blocker comment with exact failing step/log evidence.
- T2: `worldenergydata` CI narrowed toward green with evidence, issue comment posted, and ideally `#2433` closed if acceptance is met.
- T3: `workspace-hub` orphan refs pruned, follow-on issues filed under `#2424`, verification evidence posted, and `#2437` closed if all checks pass.
- T4: revised v3 plans plus fresh review artifacts for `#2441`, `#2443`, and `#2444`, with GitHub comments summarizing whether each is approval-ready or still blocked.
