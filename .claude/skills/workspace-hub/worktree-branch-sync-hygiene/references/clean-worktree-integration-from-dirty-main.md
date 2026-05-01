# Archived Skill: `clean-worktree-integration-from-dirty-main`

Original path: `/home/vamsee/.hermes/skills/workspace-hub/clean-worktree-integration-from-dirty-main`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub/clean-worktree-integration-from-dirty-main`
Consolidation date: 2026-04-29

---

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

### Critical preflight: verify the landing set is still unlanded

Before you create an integration worktree, check the exact target file set you think needs landing.

Recommended pattern:
- `git status --short -- <target files...>`
- `git diff --stat -- <target files...>`

Interpretation rules:
- If both commands are empty for the target set, do **not** assume you still need a landing branch for those files. That often means the edits already landed on the current base via another session/commit.
- In that case, switch from landing mode to **reconciliation mode**:
  - identify which intended artifacts are already on `HEAD`
  - isolate any truly new files from this session (for example a new runbook or prompt pack)
  - create a worktree only for the still-unlanded residue, or skip the worktree entirely if nothing remains

Why this matters:
- in parallel agent sessions, plan/doc edits may be committed to `main` between drafting and integration
- creating a fresh worktree and copying files can reveal that the only remaining delta is a newly-created artifact, not the full landing set you expected
- this prevents duplicate commits for files that are already identical to the integration base

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

### Dirty/diverged main with a valid local commit

If the active main checkout already contains a valid local implementation commit but cannot push because `origin/main` advanced and the checkout also has unrelated dirty/untracked files:
1. Do **not** rebase/reset/stash the dirty main checkout just to land the issue.
2. Record both SHAs:
   - local equivalent implementation commit (`git rev-parse HEAD` or the specific commit SHA)
   - current remote base (`git ls-remote origin refs/heads/main` or `origin/main` after fetch)
3. Create a temporary clean worktree directly from `origin/main`:
   - `git worktree add /tmp/<repo>-<issue>-push origin/main`
4. Cherry-pick only the scoped implementation/review commit(s) into that clean worktree.
5. Validate in the clean worktree, then push `HEAD:main` from there.
6. Treat the new remote commit SHA as canonical; the dirty main commit is only an equivalent local patch unless/until reconciled later.
7. After successful remote verification, remove the temporary worktree and explicitly report that the original checkout may still be dirty/diverged with an equivalent local commit.

This avoids destructive cleanup of unrelated session state while still producing a clean, auditable landing commit on top of the current remote branch.

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
- Fresh integration worktrees may fail pre-push hooks for reasons unrelated to the landing commit. In workspace-hub, a clean worktree created outside the normal repo topology triggered repo-wide tier-1 checks that expected sibling repos at matching relative paths and failed before push. Practical recovery pattern:
  1. First try pushing from a topology-compatible checkout/worktree where the hook environment already matches the repo's assumptions.
  2. If the hook still fails only because of unrelated ecosystem debt (for example tier-1 quality failures in other repos) and the landing branch is a narrowly scoped docs-only or low-risk artifact change, consider an audited bypass push rather than mutating the clean worktree to satisfy unrelated checks.
  3. In this repo, `GIT_PRE_PUSH_SKIP=1 git push ...` is a soft bypass that logs to `logs/hooks/pre-push-bypass.jsonl`. Use it only when the branch scope is truly isolated and you can justify that the pre-push failures are unrelated to the landing artifact.
- Before bypassing, confirm the branch diff is exactly the intended scoped artifact set (for example a single docs runbook file) and preserve the clean non-bypass landing branch so you still have a normal-path provenance record.

## Pre-push topology mismatch on clean worktrees (important live lesson)

A fresh integration worktree can still fail at push time even when the landing diff is correct, because workspace-level pre-push hooks may assume the full repo ecosystem exists at paths relative to that checkout.

Observed failure mode:
- a clean worktree contained only `workspace-hub/`
- `git push` triggered the repo pre-push hook
- the hook tried to run tier-1 checks for sibling repos like `assetutilities`, `digitalmodel`, `worldenergydata`, and `assethold`
- those paths did not exist under the clean worktree root, so the push failed before evaluating the actual landing diff
- a later attempt from the topology-compatible main checkout got past the path-mismatch but still failed because the same hook enforces unrelated tier-1 quality debt across the ecosystem

### Practical rule

For docs-only or narrow governance landings in workspace-hub:
1. Validate the diff in the clean integration worktree first.
2. Before push, inspect the repo's pre-push hook assumptions:
   - does it expect sibling repos under the checkout root?
   - does it run ecosystem-wide tier-1 checks unrelated to the landing diff?
3. If yes, treat the clean worktree as a validation/integration room, not necessarily the final push location.
4. Recreate the landing commit in a topology-compatible checkout (for example the main workspace checkout where sibling repos exist) or cherry-pick it there.
5. If the push still fails only because of unrelated ecosystem-wide checks, consider an explicit audited bypass for the docs-only branch rather than mutating the clean worktree to fake the missing topology.

### Recommended sequence for this case

1. Create and validate the clean worktree landing commit.
2. Create a topology-compatible branch in the real workspace checkout.
3. Commit or cherry-pick the same narrow landing there.
4. Attempt a normal push once.
5. If the only remaining blocker is unrelated repo-wide pre-push debt, use the repo's audited bypass mechanism (for example `GIT_PRE_PUSH_SKIP=1`) for the narrow docs-only branch.
6. Record that the bypass was environmental/governance-driven, not required by the change itself.

This avoids wasting time debugging a perfectly good clean worktree that simply lacks the filesystem topology expected by repo hooks.
- In workspace-hub, a brand-new clean worktree may NOT be push-ready even for docs-only branches. Pre-push hooks can assume the full tier-1 repo topology exists relative to the current checkout (for example sibling dirs like `assetutilities/`, `digitalmodel/`, `worldenergydata/`, `assethold/`) and may also require local Python deps such as `yaml` for config-drift checks. A skeletal worktree containing only workspace-hub can therefore fail pre-push despite a clean, valid commit.
- The topology-compatible fallback can still fail for unrelated reasons: even in the real workspace checkout, pre-push may run cross-repo quality gates across tier-1 repos and block your docs-only branch on unrelated failures (observed: `assetutilities` ruff/mypy failures blocked a push for a one-file runbook branch).
- Practical rule: before planning to push from a fresh integration worktree, do a real push probe (with side-effect approval) or inspect the pre-push hook assumptions. If hooks expect multi-repo topology, prefer one of three paths: (1) cherry-pick the clean commit into a topology-compatible checkout/worktree where hooks already pass, (2) recreate the expected sibling-repo layout for that worktree, or (3) use an explicit user-approved bypass for the docs-only push.
- Workspace-hub's current pre-push hook supports an audited soft bypass via `GIT_PRE_PUSH_SKIP=1`. It logs a JSONL record to `logs/hooks/pre-push-bypass.jsonl` and exits 0 before running the heavy tier-1 checks. For isolated docs/plans branches that are clean and intentionally low-risk, this can be the fastest safe landing path once the user approves the bypass. Example:
  - `GIT_PRE_PUSH_SKIP=1 git push -u origin <branch>`
- When using that bypass, capture in your landing notes: the exact branch pushed, the exact commit SHA, and the bypass log path. This preserves auditability and keeps the bypass scoped to the already-validated low-risk branch rather than normalizing bypass use for broader implementation work.
- In workspace-hub, a brand-new clean worktree may NOT be push-ready even for docs-only branches. Pre-push hooks can assume the full tier-1 repo topology exists relative to the current checkout (for example sibling dirs like `assetutilities/`, `digitalmodel/`, `worldenergydata/`, `assethold/`) and may also require local Python deps such as `yaml` for config-drift checks. A skeletal worktree containing only workspace-hub can therefore fail pre-push despite a clean, valid commit.
- The topology-compatible fallback can still fail for unrelated reasons: even in the real workspace checkout, pre-push may run cross-repo quality gates across tier-1 repos and block your docs-only branch on unrelated failures (observed: `assetutilities` ruff/mypy failures blocked a push for a one-file runbook branch).
- Practical rule: before planning to push from a fresh integration worktree, do a real push probe (with side-effect approval) or inspect the pre-push hook assumptions. If hooks expect multi-repo topology, prefer one of three paths: (1) cherry-pick the clean commit into a topology-compatible checkout/worktree where hooks already pass, (2) recreate the expected sibling-repo layout for that worktree, or (3) use an explicit user-approved bypass for the docs-only push.
- Workspace-hub's current pre-push hook supports an audited soft bypass via `GIT_PRE_PUSH_SKIP=1`. It logs a JSONL record to `logs/hooks/pre-push-bypass.jsonl` and exits 0 before running the heavy tier-1 checks. For isolated docs/plans branches that are clean and intentionally low-risk, this can be the fastest safe landing path once the user approves the bypass. Example:
  - `GIT_PRE_PUSH_SKIP=1 git push -u origin <branch>`
- When using that bypass, capture in your landing notes: the exact branch pushed, the exact commit SHA, and the bypass log path. This preserves auditability and keeps the bypass scoped to the already-validated low-risk branch rather than normalizing bypass use for broader implementation work.
