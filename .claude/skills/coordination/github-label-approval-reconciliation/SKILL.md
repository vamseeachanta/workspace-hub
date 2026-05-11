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

## Pitfalls

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
