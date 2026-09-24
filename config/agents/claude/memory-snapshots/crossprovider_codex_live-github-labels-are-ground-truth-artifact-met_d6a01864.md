---
name: crossprovider codex live-github-labels-are-ground-truth-artifact-met
description: Live GitHub labels are ground truth; artifact metadata can be stale
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [issue-tracking, approval-gates]
---

When artifact prose metadata (e.g., "Approved direction" in title) conflicts with live issue labels (e.g., `status:scoping`), trust the live label. Stale artifact metadata is a common source of approval confusion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
