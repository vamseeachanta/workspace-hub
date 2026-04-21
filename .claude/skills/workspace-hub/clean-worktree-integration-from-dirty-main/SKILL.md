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

6. Pre-landing already-landed check (critical)
Before you prepare push/closeout artifacts or cherry-pick into the integration worktree, explicitly verify the issue has not already landed elsewhere.

### Topology-aware validation after cherry-picks (critical)

After the integration worktree contains the intended commits, validate in layers instead of trusting the first failing command:

1. Run the targeted test suite for the landed surface.
2. If tests depend on generated/local fixture repos, explicitly bootstrap those fixtures before classifying failures as code defects.
3. Separate code/import validation from topology validation:
   - direct module invocation / package import health
   - wrapper/cron behavior in the intended runtime topology
4. Do not treat wrapper failures in a clean integration worktree as proof the feature code is broken if the wrapper begins with topology-sensitive commands like `git pull --ff-only origin main`.

Observed reusable pattern:
- In a clean integration worktree, ecosystem-sync tests initially failed because fixture repos under `tests/.../fixtures/repos/` had not been built yet.
- After running the fixture builder, the full targeted suite passed, proving the failure was a fixture-bootstrap gap rather than a regression in the integrated code.
- The cron wrapper still failed in the integration worktree because `git pull --ff-only origin main` is expected to fail in a diverged landing branch/worktree; that is a topology issue, not necessarily an implementation issue.
- A direct `uv run path/to/script.py ...` invocation may fail with `ModuleNotFoundError` even when `uv run python -m package.module ...` works. When the landed script imports from the repo package root, verify both invocation styles before declaring the integration broken.

Practical rule:
- classify failures as one of:
  - fixture/bootstrap gap
  - import/invocation-path bug
  - topology-specific wrapper failure
  - real functional regression
- only the last category should automatically block the landing set as broken code.

Documentation-update guardrail learned in live use:
- when adjusting operator/docs artifacts inside the integration worktree, do NOT reconstruct whole files from line-numbered `read_file` output and then `write_file` them back; that can accidentally persist the line-number prefixes into the file contents.
- prefer targeted `patch` edits for command swaps or narrow wording fixes, especially in markdown/shell handoff artifacts.
- after any scripted doc rewrite, immediately sanity-check the first few lines of the file before committing.

Check all of:
- `git fetch origin main --quiet`
- `git log --oneline origin/main -5`
- `gh issue view <issue> --json state,comments,labels,url`
- if useful, `git log --oneline --grep='#<issue>' origin/main`

Interpretation rules:
- If `origin/main` already contains an implementation commit for the issue, treat the issue as potentially already landed.
- If the GitHub issue is already CLOSED with a landed-summary comment, treat that as strong evidence the work is already upstream.
- If your local isolated worktree re-implemented the same issue independently, stop before push and switch from landing mode to verification/reconciliation mode.

What to do if already landed upstream:
- do NOT push a duplicate implementation branch
- do NOT post duplicate closeout comments
- compare your local worktree against `origin/main` and determine whether it contains any extra learnings or fixes not upstream
- if your work is fully superseded, keep it as local evidence only and clean up the redundant worktree after documenting the discovery
- if your work contains additional value beyond upstream, create a fresh follow-up issue/branch for just that delta instead of re-landing the full issue

Why this matters:
- parallel agent execution can cause an issue to land on `origin/main` while your isolated worktree is still implementing
- a late cherry-pick conflict in the clean integration worktree is often the first signal that the issue was already landed elsewhere
- checking issue state + origin/main before landing avoids duplicate pushes and misleading second closeouts

7. Prepare landing artifacts before push
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

8. Push/close only after user approval for side effects
- Pushing, posting GH comments, and closing issues are external side effects.
- If user approval for execution existed but not explicit approval for external landing side effects, stop and ask for final go-ahead.

## Multi-wave landing rule (important)

If the isolated worktree contains more than one class of change, split the landing into waves instead of blindly cherry-picking everything at once.

Recommended order:
1. narrow repo-wide governance/enforcement fix first
2. core feature/implementation commits in dependency order
3. docs / handoff / operator artifacts last

Why:
- a small governance fix often has value beyond the feature branch that discovered it
- validating the narrow fix first reduces blame surface if later feature integration fails
- docs bundles should not be allowed to obscure whether code integration itself is healthy

Example trigger:
- a feature worktree contains both a verified enforcement-hook fix and a larger feature implementation
- the main checkout is dirty, so you need a clean integration worktree anyway

Validation rule by wave:
- after wave 1, run the targeted regression for the governance fix before continuing
- after wave 2, run the feature-targeted test suite before adding doc commits
- after wave 3, do a final status + regression pass

Also explicitly exclude planning-marker / approval-marker commits unless they are intentional repo-tracked deliverables.

## Recommended command pattern

```bash
# from dirty main checkout
BASE=$(git rev-parse HEAD)

git worktree add -b integration-2151-2155 \
  /mnt/local-analysis/worktrees/workspace-hub-integration-2151-2155 \
  "$BASE"

# in integration worktree
# wave 1: narrow governance fix
# git cherry-pick <governance-fix-commit>
# run targeted validation

# wave 2: feature commits in dependency order
# git cherry-pick <issue1-commit-1> <issue1-commit-2> ... <issue2-commit-1>

# wave 3: docs / handoff commits
# git cherry-pick <docs-commit-1> <docs-commit-2>

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
- if the landing set includes CLI/wrapper entrypoints, validate the real invocation mode, not just imported/unit-tested behavior

Additional runtime-entrypoint check learned from ecosystem-sync integration:
- distinguish three layers of validation:
  1. unit/integration tests
  2. direct runtime entrypoint invocation
  3. wrapper/topology invocation
- a clean integration worktree can reveal a real entrypoint bug even when tests are green. Example pattern:
  - tests pass
  - `python -m package.module --doctor` passes
  - wrapper or documented `tool/path.py` invocation fails because imports assume module/package context
- when this happens, record it as a real blocker, fix the invocation contract, and re-run tests before push
- separately, do not misclassify expected topology failures (for example wrapper `git pull --ff-only origin main` failing in a non-main integration worktree) as code regressions. Isolate entrypoint correctness from topology-specific behavior.

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
