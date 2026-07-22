> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_required_check_must_not_skip.md

---
name: feedback_required_check_must_not_skip
description: Never make a conditionally-skipped GitHub job a required status check — a skipped required check deadlocks the PR at BLOCKED forever
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d8161c1f-2dbe-4020-9d3d-496ca0461f92
---

**A GitHub status check that is *required* by branch protection / a ruleset must NEVER be able to skip via a job-level `if:`.** A skipped job reports no success conclusion, and rulesets treat "not success" as unsatisfied → the PR is stuck `mergeStateStatus=BLOCKED` permanently, even though every other check passes.

**Why:** live incident 2026-07-04 (wed): `changelog-check` job had `if: !startsWith(title,'chore') && !startsWith(title,'ci')`, and "Changelog Check" was a required context. Every dependabot PR (`chore(deps):`) skipped the job → BLOCKED → the whole dependabot backlog was unmergeable since 2026-06-15. A rebase-and-merge sweep merged 0/6 before the cause was found.

**Diagnostic signature:** `gh pr view <n> --json mergeStateStatus` = `BLOCKED` while `gh pr checks <n> --required` shows all-but-one `pass` and one `skipping`. The skipping one is a required check with an `if:`. Confirm: compare `gh api repos/O/R/rules/branches/main --jq '...required_status_checks[].context'` against the reporting checks.

**How to apply:**
1. **Auditing:** any required check whose workflow job has a job-level `if:` is a latent deadlock. Either the job always runs (move the skip logic into a non-failing *step*), or the check is not required.
2. **Fixing:** remove the job-level `if:` so the job always runs and reports success. Safe when the step is advisory (only emits `::notice::`, never exits non-zero) — as `changelog-check` was.
3. **A fix PR is NOT self-blocked** if its title avoids the skip predicate (e.g., `fix(ci): ...` doesn't match a `chore`/`ci` prefix skip), so the required check runs normally on the fix itself.
4. Pairs with [[feedback_strict_uptodate_ruleset_no_admin_bypass]] — both are ruleset/required-check merge deadlocks; check for both when a green PR won't merge.

Fixed in wed PR #804 (closes #802).

Related: [[project_ecosystem_review_2026_07_04]], [[feedback_strict_uptodate_ruleset_no_admin_bypass]], [[feedback_ci_baseline_red_not_pr_broken]]
