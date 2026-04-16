You are working in /mnt/local-analysis/workspace-hub.

Planning-only overnight run. Do NOT implement code. Your job is to prepare 20 GitHub issues for tomorrow's Claude execution by drafting/tightening canonical plans and performing adversarial planning review.

Hard constraints:
- Planning and adversarial review only.
- No implementation, no source edits outside planning/review artifacts.
- Allowed write paths only:
  - docs/plans/
  - scripts/review/results/
  - docs/reports/
- Forbidden write paths:
  - src/
  - tests/
  - .planning/plan-approved/
  - production/runtime scripts outside scripts/review/results/
- Do not create approval markers.
- Do not add status:plan-approved.
- You may create or refresh docs/plans/README.md rows as needed.
- Follow workspace-hub issue-planning policy strictly.

Primary source document:
- docs/plans/2026-04-15-20-issue-adversarial-planning-review-pack.md

Execution mode:
- Process issues one by one in the listed order.
- After each issue, append a concise status line to docs/reports/2026-04-15-overnight-planning-review-results.md.
- Stop early only if you hit a hard blocker that prevents safe planning work across the whole queue.

For each issue:
1. Read the live GitHub issue body, comments, and labels.
2. Verify whether a canonical plan already exists.
3. If missing, draft the canonical plan using docs/plans/_template-issue-plan.md and update docs/plans/README.md.
4. Perform strengthened resource intelligence before finalizing the plan.
5. Run adversarial planning review and save review artifacts under scripts/review/results/ with clear provider/reviewer naming.
6. Update the plan's review summary and approval-readiness state based on the review findings.
7. Post a concise GitHub comment with planning/review status and blockers if any.
8. Keep the issue in planning state only. No execution approval.

Required final artifact:
- docs/reports/2026-04-15-overnight-planning-review-results.md

That final report must contain for each of the 20 issues:
- issue number and title
- whether canonical plan existed or was created
- review artifact paths
- verdict: approval-ready / needs-revision / blocked
- exact blocker if not approval-ready
- whether it should be considered for Claude execution tomorrow after user approval

Success condition:
- All 20 issues have an explicit planning status and repo-tracked artifact trail.
- Tomorrow morning, the user can quickly approve the approval-ready plans and launch execution only on those items.