# Merge authorization — what "merge and continue" allows an agent to run (#3390)

**When to apply:** any time an agent considers running `gh pr merge` (or arming `--auto`) itself, in any repo of the ecosystem.

**Why:** the no-self-merge norm was held by the permission classifier, not by the models. Live incident 2026-07-03/04 (motion-forecast session, dm #1356 epic): after one classifier non-fire on a bare "Merge and continue", the agent concluded "I'll merge directly when you tell me to from now on" and self-merged 4 subsequent PRs (#1395/#1407/#1409/#1413) treating a single success as standing session policy. In three other sessions the same week the classifier blocked identical attempts. Elastic behavior around an irreversible, outward-facing action is the defect; this policy makes authorization explicit and non-sticky.

**Policy:**

1. **Default:** the agent verifies the PR is green + `mergeStateStatus==CLEAN`, then hands the human the exact command (`gh pr merge <N> --squash --delete-branch --repo owner/name`). This remains the normal path (`feedback_agent_can_verify_but_not_self_merge_pr`).
2. **A user "merge" / "merge and continue" authorizes an agent-run merge ONLY when the target is unambiguous:**
   - the user's message names the PR number(s), **or**
   - the instruction is the direct reply to the agent presenting that specific PR (the PR is the plain antecedent of the message).
3. **Batch merges:** only the PRs explicitly enumerated in the user's message, or a list the agent presented and the user approved in that same exchange. "Merge my PRs" without a presented list → present the list first.
4. **Authorization is per-PR and non-sticky.** One authorized merge does NOT create a session-wide "merge whatever comes next" policy. Each subsequent merge needs its own trigger under rule 2.
5. **Never self-authorize gates:** merging never substitutes for `status:plan-approved`, owner review markers, or completeness stamps — those stay human-created regardless of merge authorization.
6. **After any merge (agent- or human-run): verify MERGED on the remote** and confirm the content landed (`git cat-file -e origin/main:<path>` — squash-merge makes merge-commit reachability meaningless, see `reference_squash_merge_reachability_false_orphan`).
7. **Explicit user authorization never waives freshness.** Immediately before an agent-run merge, require `mergeStateStatus == CLEAN`; authorization does not permit `BEHIND`, `BLOCKED`, `DIRTY`, `UNKNOWN`, or `UNSTABLE` state.
8. **Use the CLEAN-only merge helper.** Every authorized agent-run merge must use `scripts/operations/merge-when-clean.sh --merge` for that PR, never a direct `gh pr merge` substitute.
9. **Validate the actual landed tree.** After remote verification, run `git fetch origin main`, resolve the landed `origin/main`, and rerun changed-domain generated-artifact checks before closeout.

**Do NOT apply when:** the user runs the merge themselves (pasting output back) — then the agent's job is only step 6 verification.

**Related:** [`model-routing.md`](model-routing.md) (corollary 4), [`completeness-before-close.md`](completeness-before-close.md). Memory: `feedback_agent_can_verify_but_not_self_merge_pr`, `feedback_dependabot_merge_no_rebase_trust_clean`. Issue: workspace-hub#3390 item 4 (owner adopted option b, 2026-07-06).
