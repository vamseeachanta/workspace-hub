# Gated issue batch parallel recon

## Current task authority

The originating task request or established standing authority authorizes implementation within scope, including substantial work, after proportionate planning, TDD and adversarial review. No separate plan approval, approval label or local marker is required. Honor planning-only requests and unresolved domain decisions. Publication, deployment, access changes, destructive actions and outreach retain their action-specific authority. Preserve historical approval records; do not self-label owner approval.


Use when the user asks to “tackle all of them with subagents” but the work is not yet authorized for implementation because live issues do not exist, task authority is missing or review/domain decisions block execution, or a repo guard blocks `git`/`gh`.

## Pattern

1. State the gate plainly: subagents can run **read-only recon**, not implementation.
2. Split the batch into 2–3 independent analysis lanes by domain or write surface.
3. Give each subagent:
   - repo path and issue packet path,
   - exact issue subset,
   - explicit read-only constraint,
   - required output: existing files/tests/docs, likely files to change, TDD tests to write first, blockers, duplicate/prior-work signals, sequencing.
4. Keep durable writes in the main session only:
   - write one synthesis artifact under the issue packet or reports directory,
   - link it from the packet README,
   - verify file existence and script syntax if an issue-creation script exists.
5. Do not call the batch “implemented.” Report it as `parallel-readonly recon complete` and name the remaining gate.

## Good final artifact shape

- Gate state and exact blocker.
- Lanes run and issue coverage.
- Revised execution order.
- Likely new files and edits per issue.
- TDD-first test list per issue.
- Cross-cutting blockers/dependencies.
- Safe future parallelization plan after the task/review prerequisites are satisfied.

## Pitfalls

- Do not let subagents write source files, create GitHub issues, or commit; their writes may not persist and may exceed verified task scope or runtime capabilities.
- Do not treat a user request to “tackle all” as permission to bypass Issue → Plan → Review → Approval when the repo policy requires it.
- If `gh`/`git` is blocked by a scope guard, draft or verify the issue packet and tell the user the exact scope/creation command instead of bypassing the guard.
