---
name: feedback_check_issue_state_before_implementing_on_detached_head
description: "Before coding an issue, branch from origin/main and confirm it isn't already closed/PR-merged by a parallel session — detached-HEAD sessions silently produce stale-base work"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 97f5bdec-e4ac-46ef-9621-afbf4c40dc6c
  modified: 2026-08-02T11:41:52.672Z
---

On 2026-06-09 I created #2992 (statusline weekly-reset countdown), implemented it (TDD, 4 bats green), committed, and opened PR #3005 — only to discover a **parallel session had already implemented the identical feature, merged it via #3004 (11:35Z), and closed #2992** with a *better* version (Python `resets_at` parser, `source`-aware skip for unavailable AND estimated, more tests). All my implementation effort was wasted.

Two compounding root causes:
1. The session started on a **detached HEAD** (`git status` showed `Current branch: HEAD`). I ran `git checkout -b feat/... ` off it, so my branch base was 154–159 commits behind origin/main. The PR diff ballooned to 100 files / +500k lines (the drift between the ancient merge-base and current main), not my 2-file change — the classic stale-base hazard from [[feedback_recover_stale_branch_for_pr]].
2. I did NOT verify the issue's live state on the remote before implementing — violating [[feedback_check_parallel_work]]. A 10-second `gh pr list --search "<issue#> in:title" --state all` + `gh issue view <#> --json state` would have shown the merged PR and CLOSED issue before I wrote a line.

**Why:** the ecosystem runs multiple concurrent sessions/agents against the same GitHub-issue backlog; auto-sync keeps local main drifting. Detached-HEAD + no pre-flight state check = guaranteed duplicate or stale-base work.

**How to apply:** Before implementing ANY issue, FIRST: (a) `git fetch origin` and branch explicitly from `origin/main` (`git checkout -b <branch> origin/main`), never from a detached/ambient HEAD; (b) check the issue is still OPEN and has no merged/open PR (`gh issue view <#> --json state,stateReason`; `gh pr list --search "<#> in:title" --state all`). If closed/merged: stop, clean up, report — don't re-implement. When cleaning up redundant work, `git reset --hard` on cron-churn the agent didn't author is auto-denied — use targeted `git checkout --ours -- <files>` (stash is retained on pop-conflict, so data is safe).

---

## 2026-08-02: the same failure when FILING, not just implementing

Filed digitalmodel #1955 for a Gibbs-solver defect found by reading `physics.py`. It was a duplicate of **#1857**, open with `priority:high` and already routed `machine:licensed-win-1`. Wrote a full plan and burned a T2 two-provider adversarial review on it before the duplicate surfaced — and it surfaced only because a *reviewer* read the module docstring.

**The tell was in the file I was proposing to change.** `solver.py`'s class docstring said, inline:

> `'gibbs'` does not transform the load at all — it returns an affine rescale of the surface card **(issue #1857)** — so it cannot resolve pump condition.

Plus a measured comparison table showing `everitt_jennings` at 0.9% median nRMSE versus `gibbs` at 17.3%, and *"Neither should be used for diagnosis."* Everything needed to not file the issue, and to know the repair was not worth doing, was in the docstring of the class I was planning to modify.

**Why this variant is distinct:** the existing rule guards *implementing* an already-done issue. This is filing a duplicate *and* planning against it — the cost lands earlier and is larger, because a plan plus a two-provider review is far more expensive than a wasted branch.

**How to apply, extended:**
- **Before `gh issue create`, search the defect, not the title you're about to write:** `gh issue list --repo <r> --state all --search "<symptom keywords>"`. A duplicate rarely shares your phrasing — search the *behaviour* (`"affine rescale"`, `"does not transform load"`).
- **Grep the target module for issue references before planning against it** (`grep -nE '#[0-9]{3,}' <file>`). Code comments are where prior triage goes to be forgotten; a defect serious enough to plan around has usually already been annotated at the site.
- **Read the full class/module docstring of what you intend to change** — not just the function. Recommended alternatives, measured comparisons, and "do not use this" warnings live at class level, and skipping them is how you plan to repair something already labelled comparison-only.

Related: [[feedback_discovery_first_on_stale_plan_approved]], [[feedback_narrow_grep_false_dead_before_deletion]].
