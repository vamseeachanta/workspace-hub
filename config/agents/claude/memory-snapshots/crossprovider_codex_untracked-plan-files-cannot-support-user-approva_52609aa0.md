---
name: crossprovider codex untracked-plan-files-cannot-support-user-approva
description: Untracked plan files cannot support user approval gates reliably
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, git-durability, approval-gates]
---

Plan files and governance-index updates that exist only in the working tree (not committed/pushed) cannot be audited by users or linked to GitHub review evidence. Approval gates require durable artifacts. Commit/push plans and link review evidence as GitHub issue comments before requesting user approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
