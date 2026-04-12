---
name: clean-worktree-integration-from-dirty-main
description: Land validated issue work from isolated worktrees when the main checkout is dirty by creating a fresh integration worktree, cherry-picking only implementation commits, re-running combined validation, and preparing push/closeout artifacts.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [git, worktree, integration, workspace-hub, issue-execution, validation]
---

# Clean Worktree Integration from Dirty Main

## When to use

Use this when:
- the primary repo checkout on `main` has unrelated local changes
- one or more issues were implemented and validated in separate worktrees
- you need a clean landing path without disturbing the dirty main checkout
- you want a reproducible integration branch before push/closeout

Typical trigger:
- `git status` on the main checkout shows many unrelated modified/untracked files
- issue worktrees are clean and contain the validated commits you actually want to land

## Why this pattern exists

Trying to land work directly from a dirty main checkout risks:
- mixing unrelated files into the landing set
- accidental staging of local audit/docs/session artifacts
- difficult rollback if cherry-pick/integration validation fails

A fresh integration worktree gives you a clean room for landing only the approved commits.

## Workflow

1. Confirm issue worktrees are clean and validated
- In each issue worktree, ensure `git status --short` is clean.
- Record the exact implementation commits to land.
- If there are planning-marker commits in the issue worktree, do not include them in the final landing set unless they are intentionally repo-tracked deliverables.

2. Record the clean integration base
- Capture the intended base commit from the main repo:
  - `git rev-parse HEAD`
- Do this from the main checkout, not from an issue worktree.

3. Create a fresh integration worktree
- Example:
  - `git worktree add -b integration-<issue-set> /path/to/integration-worktree <base-commit>`
- This avoids interference from the dirty main checkout.

4. Cherry-pick only the implementation/fix commits
- Cherry-pick the validated issue commits into the integration worktree in dependency order.
- Example pattern:
  - schema feature commit
  - schema fix commit(s)
  - resolver feature commit
  - resolver fix commit(s)
- Exclude local-only approval-marker commits unless they must land.

5. Run combined validation in the integration worktree
- Re-run the exact targeted tests for each issue.
- Also run a nearby regression set that covers touched consumers.
- Do not assume per-worktree validation is enough; the combined landing set needs its own green run.

6. Prepare landing artifacts before push
Create:
- an integration runbook with:
  - issue links
  - commits included
  - validation commands/results
  - exact branch/worktree path
- closeout comment drafts with:
  - result
  - change summary
  - acceptance criteria mapping
  - validation evidence
  - git evidence
  - residual risk

7. Push/close only after user approval for side effects
- Pushing, posting GH comments, and closing issues are external side effects.
- If user approval for execution existed but not explicit approval for external landing side effects, stop and ask for final go-ahead.

## Recommended command pattern

```bash
# from dirty main checkout
BASE=$(git rev-parse HEAD)

git worktree add -b integration-2151-2155 \
  /mnt/local-analysis/worktrees/workspace-hub-integration-2151-2155 \
  "$BASE"

# in integration worktree
git cherry-pick <issue1-commit-1> <issue1-commit-2> ... <issue2-commit-1>

uv run pytest \
  tests/analysis/test_readiness_bundle_schema.py \
  tests/workstations/test_machine_path_resolver.py \
  tests/analysis/test_provider_session_ecosystem_audit.py \
  tests/analysis/test_claude_session_ecosystem_audit.py \
  tests/workstations/test_registry.py \
  tests/workstations/test_dispatch.py \
  tests/cron/test_provider_session_ecosystem_audit_wrapper.py \
  -q
```

## Selection rules for cherry-picks

Include:
- feature commits for the issue
- follow-up fix commits from adversarial review

Exclude by default:
- local approval-marker commits (`chore(planning): approve issue #...`) unless they are intentionally meant to be tracked in the final landing branch
- unrelated docs/planning/session artifacts

## Validation standard

Before declaring integration-ready, verify:
- integration worktree is clean after cherry-picks and tests
- all issue-targeted tests pass
- nearby regression tests pass
- no unrelated files were introduced

## Output checklist

Before final push, prepare:
- integration worktree path
- integration branch name
- exact included commits
- exact validation commands and results
- draft GH closeout comments for each landed issue
- explicit note for any still-blocked issue

## Example reusable outcome

This pattern worked well for landing two approved issues from isolated worktrees while the main checkout had many unrelated modified files:
- issue A: schema + contract fixes
- issue B: shared resolver + normalization fix
- integration branch created from clean base
- only implementation commits cherry-picked
- combined regression suite re-run successfully
- push/closeout artifacts prepared separately from the dirty main checkout

## Pitfalls

- Do not cherry-pick from the dirty main checkout itself.
- Do not assume worktree-local green tests imply combined landing-set green tests.
- Do not silently include approval-marker commits.
- Do not push or close issues without explicit side-effect approval.
- If a blocked issue depends on missing upstream foundations, keep it open and document the blocker rather than forcing fixture work against an invented contract.
