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

2. Compare that file list against the files Claude claimed to have changed in its final summary
- look for any claimed files missing from the commit stat

3. Inspect current working tree for owned-path leftovers
```bash
git status --short
```
- look specifically for files owned by the executed issue
- ignore unrelated dirty files outside the issue's owned paths

4. If a claimed file is still modified after the run:
- read it and confirm whether the intended change is present only in the working tree
- decide whether to:
  - make a tiny fixup commit, or
  - reopen the issue and finish properly

5. Verify GitHub closeout state
- read the latest issue comments
- check whether the issue is open/closed
- if closed with residual owned-path changes still uncommitted, treat the closeout as incomplete

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

## Workspace-hub-specific lesson

In workspace-hub, this matters when:
- docs or generated files violate local repo conventions
- some wiki/domain files are already oversized or shaped in ways that trip repo expectations
- the run stages only a subset of the owned-path edits

A concrete example pattern:
- worker committed 10 files
- claimed 12 intended updates
- 2 wiki `CLAUDE.md` files were still modified in working tree
- issue was already closed
- correct response was to treat the issue as substantially complete but with a small residual follow-up

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
