# Plans Index

This directory stores git-tracked issue plans used as the source of truth before implementation.

Workflow summary:
- Every issue gets a plan in `docs/plans/`
- Every plan goes through adversarial review before user review
- GitHub issue receives the plan as a comment
- `status:plan-review` means waiting for user approval
- `status:plan-approved` means safe for batch/scheduled execution

## Status meanings

| Status | Meaning |
|---|---|
| draft | Plan file exists locally but has not yet completed adversarial review |
| adversarial-reviewed | Frontier-model review passed; ready to post for user review |
| plan-review | Posted to GitHub; waiting for user approval |
| plan-approved | User approved; ready for implementation or batch execution |
| superseded | Replaced by a newer version of the plan |
| completed | Issue implemented and closed |

## Index

| Issue # | Title / Slug | Plan File | Date | Status | Complexity | Notes |
|---|---|---|---|---|---|---|
| TBD | Add entries here as new issue plans are created | `docs/plans/YYYY-MM-DD-issue-NNN-slug.md` | YYYY-MM-DD | draft | T1/T2/T3 | Link GitHub issue + review artifacts |

## Entry format

Add one row per plan using this pattern:

| 1234 | short-issue-slug | `docs/plans/2026-04-08-issue-1234-short-issue-slug.md` | 2026-04-08 | plan-review | T2 | GH comment posted; waiting for approval |

## Required contents for each plan file

Each plan should include:
- Resource intelligence summary
- Artifact map
- Deliverable
- Pseudocode
- Files to change
- TDD test list
- Acceptance criteria
- Risks and open questions
- Complexity classification
- Adversarial review summary or links to review artifacts

## Notes for agents

- All plans go in `docs/plans/` — not `.hermes/plans/`
- Keep this README updated whenever a new plan is created or status changes
- Batch execution agents should only act on issues marked `plan-approved`
- If a plan is revised materially, update the row and mark the older version `superseded`
