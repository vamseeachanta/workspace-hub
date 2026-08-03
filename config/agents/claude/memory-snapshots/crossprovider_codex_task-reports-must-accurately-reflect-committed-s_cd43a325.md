---
name: crossprovider codex task-reports-must-accurately-reflect-committed-s
description: Task reports must accurately reflect committed state, SHAs, and verification results
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [documentation, review-discipline, commit-metadata]
---

A task report is binding documentation, not aspirational: it must record actual commit SHAs, final HEAD, status transitions, and gate results. Stale reports that claim 'BLOCKED' and 'Commit SHA: none' while a SHA was actually committed create internal contradiction and block review. Update the report after every significant state change.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
