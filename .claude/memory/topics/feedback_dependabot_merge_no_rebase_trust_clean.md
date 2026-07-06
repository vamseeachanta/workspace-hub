> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-05
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_dependabot_merge_no_rebase_trust_clean.md

---
name: feedback_dependabot_merge_no_rebase_trust_clean
description: "When batch-merging PRs, don't rebase under non-strict rulesets (it cancels queued CI) and merge only on GitHub's mergeStateStatus==CLEAN, never by counting gh pr checks"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d8161c1f-2dbe-4020-9d3d-496ca0461f92
---

Two automation traps hit while batch-merging 6 dependabot PRs on wed 2026-07-04 (took 5 sweep attempts before both were fixed):

**1. Don't `gh pr update-branch` when strict-up-to-date is OFF.** Each rebase mints a new head SHA, which **cancels the in-flight CI run** and restarts it from scratch. On a repo with a heavy matrix (wed: ~80-job `domain-tests` + a `Test (PR gate)` job that `needs:` them all), the gate check NEVER completes because the next poll's rebase kills the run first → permanent BLOCKED livelock. When strict-up-to-date is off, the branch does NOT need to be current — rebasing is pure harm. Just WAIT for CI on the existing head.

**2. Merge only on `mergeStateStatus == CLEAN`, never on a hand-counted `gh pr checks` verdict.** `gh pr checks <n> --required` lists only checks that *reported*. A required context that never posts (skipped, or a `needs:`-gated job that hasn't run yet) is simply ABSENT — so counting "no pending, no fail" reads as all-green when a required check is actually missing → premature merge attempt → "the base branch policy prohibits the merge" (a 405, silently). GitHub's `mergeStateStatus` already encodes the full truth: CLEAN = every *required* context present AND success AND no blocking rule. Trust the platform's computed verdict over reconstructing it.

**3. Always verify the merge landed on the remote.** `gh pr merge` can print an error to stderr while a naive `grep 'Merged'` matches stale `/tmp` output from a prior loop iteration → false "merged". After every merge attempt, re-query `gh pr view <n> --json state` and believe `MERGED`, not the command's stdout. (Same discipline as verifying a push reached origin.)

**Canonical waiter shape:**
```bash
for pr in $LIST; do
  v=$(gh pr view $pr --json state,mergeStateStatus --jq '"\(.state)|\(.mergeStateStatus)"')
  [ "${v%%|*}" = MERGED ] && continue
  case "${v#*|}" in
    CLEAN|UNSTABLE) gh pr merge $pr --squash --delete-branch >/dev/null 2>&1
      [ "$(gh pr view $pr --json state --jq .state)" = MERGED ] && echo "$pr ok" ;;
    *) : ;;  # wait — do NOT rebase
  esac
done
```

Related: [[project_ecosystem_review_2026_07_04]], [[feedback_strict_uptodate_ruleset_no_admin_bypass]], [[feedback_required_check_must_not_skip]]
