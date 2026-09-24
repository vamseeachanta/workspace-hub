---
name: crossprovider codex issue-authorization-without-github-labels
description: Issue authorization without GitHub labels
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [authorization, issue-workflow, process]
---

User-specified implementation scope in the prompt (branch name, commit boundary, exact task specification) serves as approval authority even when the GitHub issue lacks a `status:plan-approved` label. Treat prompt specification as approved scope and proceed without relabeling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
