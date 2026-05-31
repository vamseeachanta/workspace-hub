### Verdict: REJECT

### Summary
Multiple major fail-closed regressions identified. The gate blocks all PRs that don't follow strict branch naming conventions, breaks approval freshness if the issue body is edited, and permanently blocks follow-up PRs that don't directly modify the plan file.

### Issues Found
- [MAJOR] Editing the issue body revokes plan approval (Freshness Error): `load_issue_binding_sources` sets `updatedAt` to GraphQL's `lastEditedAt`. `extract_plan_binding` uses this as `recorded_at`. If a user fixes a typo in the issue description after approval, `recorded_at` becomes newer than `label_applied_at`, causing `label_is_fresh` to fail and requiring re-approval.
- [MAJOR] Unconditional blocking of PRs without branch-linked issues: `evaluate_plan_approval` fails closed if `resolve_linked_issues` returns empty. Since it only checks `_BRANCH_ISSUE_RE`, any PR from branches like `main`, `patch-1`, or `dependabot/*` will be unconditionally blocked, even if they don't require plans.
- [MAJOR] Requires PRs to modify the plan file: `_evaluate_binding` checks `if binding.plan_path not in touched`. This permanently blocks follow-up PRs that implement code for an already-merged plan, as they won't touch the plan markdown file.
- [MINOR] API/Web UI commits permanently block approvals: `fetch_commit_pushed_at` relies on GraphQL `pushedDate`, which is often `null` for commits made via the GitHub Web UI or API. `fetch_plan_revision_anchor` returns `None, False` if `pushedDate` is null, causing a fail-closed.
- [MINOR] Mismatched regex extraction: `extract_plan_binding` uses `re.search` which finds the *first* occurrence in the body. If an issue body mentions an old plan path and then a new plan path and revision, the script extracts the old plan path and pairs it with the new revision, breaking validation.

### Suggestions
- Do not use `lastEditedAt` to determine the binding's `recorded_at`. Only invalidate if the binding text itself changes, or fallback to using the `createdAt` timestamp of the comment.
- If no linked issues are found, return `GateDecision(True, "No linked issues")` or skip the check, rather than failing closed unconditionally for all non-conforming branches.
- Remove the `if binding.plan_path not in touched` check. Verifying that `revision_reaches_head` is true is sufficient to ensure the plan revision is part of the PR's ancestry.
- Fallback to `committedDate` if `pushedDate` is null in `fetch_commit_pushed_at` to support Web UI/API commits.
- Enforce a stricter format for extracting plan bindings (e.g., line-anchored regex or reading from inside a specific code block) to avoid parsing mismatched paths and SHAs.

### Questions for Author
- How should the gate handle PRs (like Dependabot updates or hotfixes) that do not have an associated issue and don't match the branch naming regex?
- Is it strictly required that every PR linked to an issue modifies the plan file, or should follow-up implementation PRs be allowed to pass if the plan is already in the base branch?
