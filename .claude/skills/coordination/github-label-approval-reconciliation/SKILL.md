---
name: github-label-approval-reconciliation
description: Reconcile issue workflow state when the user approves plans by applying GitHub labels directly, then surface remaining user-input work without misclassifying approved issues.
version: 1.0.0
author: Hermes Agent
category: coordination
tags: [github, planning, approval, governance, issue-triage]
---

# GitHub Label Approval Reconciliation

## When to use

Use when the user says they approved one or more GitHub issues by applying labels directly, asks what still needs user action, or asks to continue after plan approvals may have happened outside the local checkout.

Class of task: live GitHub approval-state reconciliation across labels, local approval markers, plan-review queues, and needs-data queues.

## Procedure

1. **Verify live GitHub state first**
   - Do not trust a prior local audit or transcript summary.
   - Run live `gh issue view` for specifically mentioned issues.
   - Also list open `status:plan-review`, open `status:plan-approved`, and open `status:needs-data` issues as needed.

   ```bash
   gh issue view NNN --repo OWNER/REPO --json number,title,state,url,labels,updatedAt
   gh issue list --repo OWNER/REPO --state open --label 'status:plan-review' --limit 100 --json number,title,url,labels,updatedAt
   gh issue list --repo OWNER/REPO --state open --label 'status:needs-data' --limit 100 --json number,title,url,labels,updatedAt
   ```

2. **Apply status precedence**
   - Live GitHub `status:plan-approved` is authoritative evidence of user approval.
   - If local `.planning/plan-approved/NNN.md` is missing, treat that as execution-prep governance cleanup, not as more user input.
   - Do not resurface those issues as needing approval once the live label is verified.

3. **Separate queues in the response**
   - Remaining user approval needed: open issues still labeled `status:plan-review`.
   - User/data input needed: open issues labeled `status:needs-data`, even when already `status:plan-approved`.
   - Approved / execution-prep: issues now labeled `status:plan-approved` but missing local markers.

4. **Before implementing an approved issue**
   - Create or reconcile `.planning/plan-approved/NNN.md` from the verified live GitHub approval label.
   - Patch local repo status surfaces that still say `plan-review` (canonical plan header, planning index, and any approved storyboard/spec header) so GitHub approval, local approval marker, and durable docs agree.
   - Post a concise GitHub comment that approval was reconciled, explicitly preserving any boundary that the approval does not imply (for example: no external outreach, no send action, no sibling issue consumption until its gate clears).
   - Then execute only the approved plan scope with normal TDD gates.

5. **Umbrella + child approvals**
   - If the user approves an umbrella and child issues together, execute the child issues as the concrete units unless the umbrella plan has standalone deliverables.
   - Use the umbrella for coordination, rollup comments, and closing only after children are complete or explicitly scoped.

## Exit-closeout after approval

When the user approves issues and immediately asks to "document and prepare to exit":

1. Verify live `status:plan-approved` labels for the named issues with `gh issue view`.
2. Reconcile local governance surfaces before writing the handoff:
   - update plan frontmatter and gate text from `plan-review` to `plan-approved`;
   - update `docs/plans/README.md` status rows;
   - create `.planning/plan-approved/<issue>.md` markers that cite the live label/user approval;
   - remove stale `.planning/plan-review/<issue>.md` pointers.
3. Run the repo's targeted governance/plan validators and the narrow tests that cover planning artifacts.
4. Write a durable handoff under `docs/session-handoffs/` that states the issues are approved but not implemented, plus the public-safety/no-external-action boundary.
5. Commit, push, fetch, and prove `HEAD == origin/<branch>` in the same closeout window.
6. Post concise GitHub issue comments using `--body-file` to record the approval reconciliation and validation evidence.
7. Do not implement or close the issues during this exit-only pass unless the user explicitly asked for execution/closure.

This pattern prevents the next session from seeing contradictory live labels (`status:plan-approved`) and local files (`plan-review`) while preserving the implementation gate.

## Pitfalls

- Do not leave stale `.planning/plan-review/<issue>.md` files after creating `.planning/plan-approved/<issue>.md`; mixed local markers create approval drift for the next operator.
- Do not say an issue still needs user approval merely because its local approval marker is missing after the user applied the GitHub label.
- Do not treat `status:needs-data` as solved by `status:plan-approved`; data/assumption questions still need user input.
- Do not self-approve or create approval markers before verifying the live GitHub label or explicit user approval.
- Do not execute umbrella issues as if they were implementation tickets when child issues carry the concrete scopes.

## Output pattern

When the user asks for approval links, do a live `gh issue view`/`gh issue list` check immediately and return concise clickable GitHub URLs. Do not include implementation planning, review history, or extra narrative unless asked.

Use a short table:

| Bucket | Issue | State | Action |
|---|---|---|---|
| Approval needed | [`#NNN`](https://github.com/OWNER/REPO/issues/NNN) | `status:plan-review` | User may promote to `status:plan-approved` |
| Needs data | [`#NNN`](https://github.com/OWNER/REPO/issues/NNN) | `status:plan-approved`, `status:needs-data` | User/data decision still required |
| Approved / execution-prep | [`#NNN`](https://github.com/OWNER/REPO/issues/NNN) | `status:plan-approved`, marker missing | Create local marker before implementation |

For a narrow request like “show gh issue links for user approval,” a reduced table is preferred:

| Issue | Title | Link |
|---:|---|---|
| #NNN | <title> | https://github.com/OWNER/REPO/issues/NNN |

End with one sentence confirming the live labels/state checked (for example: “All listed issues are open and labeled `status:plan-review`.”).
