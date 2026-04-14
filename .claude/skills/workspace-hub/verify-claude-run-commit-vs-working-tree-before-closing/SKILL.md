---
name: verify-claude-run-commit-vs-working-tree-before-closing
description: After a Claude implementation run, verify the claimed file set against the actual commit and working tree before treating the issue as fully complete.
version: 1.0.0
author: Hermes Agent
category: workspace-hub
tags: [claude-code, verification, git, issue-closeout, workspace-hub, learned]
---

# Verify Claude run commit vs working tree before closing

## When to use

Use this after a Claude Code implementation run that claims:
- files were changed and committed
- a GitHub issue was commented/closed
- verification passed

Especially important when:
- the repo has many unrelated dirty files
- pre-commit or repo-specific hooks may reject some paths
- Claude reports that some changes were applied but not committed
- the issue was closed automatically by the worker

## Why this skill exists

A Claude implementation run can successfully commit and close an issue while still leaving intended edits in the working tree.
Observed failure mode:
- Claude edited the target files
- some files were blocked from commit by repo rules / hooks / file policies
- Claude still posted a success comment and closed the issue
- the uncommitted delta remained in the working tree

This means "issue closed" is not sufficient evidence that all intended changes landed.

## Required checks

After the run finishes, do all of these before declaring success:

1. Inspect the commit Claude claims landed
```bash
git show --stat --name-only <commit>
```

2. Verify the commit landed in the intended checkout / branch, not just somewhere in the repo ecosystem
```bash
git rev-parse --show-toplevel
git branch --show-current
git branch --contains <commit>
```
- if you launched Claude from an isolated worktree, confirm the commit is actually on that worktree branch
- do not assume `workdir=` or prompt text was sufficient protection
- if the commit landed on another local branch / checkout (for example dirty `main`) treat the worker result as only partially integrated

3. Compare that file list against the files Claude claimed to have changed in its final summary
- look for any claimed files missing from the commit stat

4. Inspect current working tree for owned-path leftovers
```bash
git status --short
```
- look specifically for files owned by the executed issue
- ignore unrelated dirty files outside the issue's owned paths

5. If a claimed file is still modified after the run:
- read it and confirm whether the intended change is present only in the working tree
- decide whether to:
  - make a tiny fixup commit, or
  - reopen the issue and finish properly

6. Verify GitHub closeout state
- read the latest issue comments
- check whether the issue is open/closed
- if closed with residual owned-path changes still uncommitted, treat the closeout as incomplete
- if the issue comment says work landed in the isolated branch but the commit actually landed on another checkout, post a correction/update before closeout

## Recovery pattern when commit lands in the wrong checkout

Observed failure mode:
- Claude was launched from an isolated worktree
- Claude reported success and produced a valid commit
- the commit actually landed on local `main` instead of the intended issue worktree branch
- the intended worktree remained unchanged

Safe recovery:
1. identify the real landed commit hash
2. verify the diff and tests in the checkout where it actually landed
3. cherry-pick that exact commit into the intended clean worktree/branch
4. re-run the targeted validation in the intended worktree
5. treat the clean worktree commit as the authoritative execution result for push/closeout

This is distinct from the older “residual dirty files” failure mode: the code may be correct, but it is landed in the wrong branch context and must be re-homed before integration/closeout.
## Decision rules

### Case A — clean success
Criteria:
- all claimed files appear in the commit
- no owned-path files remain dirty
- issue comment matches actual commit
Action:
- accept the run as complete

### Case B — partial landing with residual owned-path edits
Criteria:
- some claimed files are not in the commit
- those files remain modified in the working tree
- issue may already be closed
Action:
- do NOT assume full completion
- create a tiny follow-up commit for the missing owned-path files, OR reopen the issue if the gap is material
- document the discrepancy in the next GitHub comment

### Case C — false success comment
Criteria:
- worker claimed success but commit does not contain the core deliverable
Action:
- reopen or continue the issue immediately
- do not treat the run as landed

## Recommended workflow

1. Capture Claude’s reported outputs:
- commit hash
- changed file list
- GitHub comment URL
- issue closed/open status

2. Run:
```bash
git show --stat --name-only <commit>
git status --short
gh issue view <issue> --json state,comments
```

3. Compare three surfaces:
- Claude summary
- actual commit contents
- residual working tree state

4. Only then decide whether the implementation is truly done.

## Workspace-hub-specific lessons

In workspace-hub, this matters when:
- docs or generated files violate local repo conventions
- some wiki/domain files are already oversized or shaped in ways that trip repo expectations
- the run stages only a subset of the owned-path edits
- a Claude run launched from an isolated worktree may still create the commit on an unexpected local branch / checkout, even when the orchestrator passed the intended worktree as cwd

Concrete example pattern A:
- worker committed 10 files
- claimed 12 intended updates
- 2 wiki `CLAUDE.md` files were still modified in working tree
- issue was already closed
- correct response was to treat the issue as substantially complete but with a small residual follow-up

Concrete example pattern B:
- orchestrator launched `claude -p` from a clean issue worktree
- Claude reported success and a commit hash
- the intended issue worktree branch did **not** move
- the reported commit actually landed on the dirty local `main` checkout instead
- correct response was:
  1. verify the reported commit hash really contains the claimed file set
  2. confirm which branch/worktree actually contains that commit
  3. cherry-pick the validated commit into the clean execution worktree
  4. re-run the targeted tests in the clean worktree
  5. treat the clean worktree commit as the authoritative execution artifact for push/closeout

Add these checks when the worker was supposed to run in an isolated worktree:
- `git branch --contains <commit>` from the parent repo
- `git log --oneline -3` in both the intended worktree and the default/main checkout
- verify the expected issue branch tip actually advanced

If the commit landed on the wrong local branch but the diff/tests are valid, prefer cherry-picking into the clean worktree over trying to salvage closeout directly from the dirty checkout.

## Output template for post-run review

Use this structure when reporting your verification:

- Commit landed: `<hash>`
- Issue state: open/closed
- Claimed changed files: N
- Actually committed files: N
- Residual owned-path files still dirty: list or none
- Verdict: complete / substantially complete with follow-up / incomplete
- Next action: none / tiny fixup commit / reopen and continue

## Pitfalls

- Trusting the worker’s final summary without checking `git show`
- Looking only at `git status` and not the actual commit
- Missing residual issue-owned files because the repo has lots of unrelated dirt
- Treating an auto-closed issue as authoritative proof of completeness

## Minimal command set

```bash
git show --stat --name-only <commit>
git status --short
gh issue view <issue> --json state,comments
```

Use this every time a Claude run claims success on a dirty repo.
