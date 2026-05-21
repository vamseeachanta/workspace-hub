# Layered Kanban Flow Routing

Use this reference when the user asks to organize related GitHub issues into a workflow board around layers such as data → execution → results/output.

## Pattern

1. Discover the issue set from GitHub using titles, labels, parent/child links, and existing plan artifacts.
2. Classify every issue across two independent axes:
   - Flow layer: data foundation, execution backbone, output/results, or cross-cutting governance.
   - Workflow gate: backlog, plan, plan-review, approved/execution, closeout.
3. Build the Kanban from dependencies, not just labels:
   - Data contracts/inventories before execution orchestration.
   - Execution/provider/worktree lanes before reporting and result publication.
   - Provenance/result-schema work before downstream dashboards or demos.
4. Route agents by work shape:
   - Gemini: inventory, deduplication, research, broad gap scans, external/context-heavy review.
   - Claude: architecture, orchestration, complex planning, approved multi-file implementation.
   - Codex: bounded implementation, tests, refactors, CLI/reporting/provenance work.
5. Prefer project fields/status and a durable report artifact for board setup when issue lifecycle labels are governance-sensitive.

## Governance guardrails

- Do not add `status:plan-approved`; only the user can approve plans.
- Do not close issues during board preparation unless explicitly asked.
- Do not mutate lifecycle labels just to make a board look tidy; use GitHub Project fields or a report artifact when the task is planning/coordination.
- If implementation is requested, confirm each issue is `status:plan-approved` and apply TDD before edits.

## Recommended artifact

Create a concise report under `docs/reports/YYYY-MM-DD-<topic>-kanban.md` with:

- Board purpose and scope.
- Layered issue table: issue, title, layer, gate/stage, dependencies, recommended agent.
- Execution sequence from data → execution → output/results.
- Explicit non-actions: labels not changed, issues not closed, approvals not self-applied.
- Verification evidence: project URL, sample project-field checks, commit/remote SHA if committed.

## Delegated implementation review-fix loop

When a layered board moves from planning into delegated Claude/Codex implementation, keep the board honest about review outcomes instead of treating "tests pass" as done:

- Add an explicit **Blocked by code review** state/section for lanes where targeted tests pass but adversarial review returns MAJOR.
- Capture blocker bullets by issue with the exact class of defect, not a narrative transcript. Examples: fail-closed partial writes, unsafe duplicate classification, oversized test files, inaccessible-path handling.
- Do not advance downstream execution/result lanes until upstream data/provenance and cleanup/disposition contracts have cleared review.
- If a delegated worker claims completion, verify: local diff, targeted tests, unrelated artifact cleanup, branch push state, and adversarial review result.
- Treat ambiguous push/ref-lock output as a verification caveat: re-check remote branch SHA before reporting the branch as safely pushed.

## Closeout wording

Report:

- What was created/updated.
- Which GitHub Project board was used.
- Which issue comment/report artifact is canonical.
- Verification evidence.
- Next execution sequence by agent.
- Any blocked-by-review items and the specific review-fix loop required before downstream work.
- Any dirty-worktree or remote-push caveat, with unrelated dirt left untouched.