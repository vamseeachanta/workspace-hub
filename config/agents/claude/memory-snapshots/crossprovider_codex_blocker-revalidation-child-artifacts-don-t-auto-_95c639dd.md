---
name: crossprovider codex blocker-revalidation-child-artifacts-don-t-auto-
description: Blocker revalidation: child artifacts don't auto-unblock parents
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [blocking-patterns, issue-gates, prerequisite-vs-completion]
---

Closing governance-artifact child issues (#43-48) does not unblock parent issues (#14, #19, #25, #26). Parents remain blocked until: (1) checklist fields are explicitly populated with evidence/approval values, not just artifact existence, and (2) a separate, approved implementation issue is created. The artifact is a prerequisite, not a completion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
