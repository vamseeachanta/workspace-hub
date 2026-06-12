---
name: crossprovider codex workflow-retry-loops-must-classify-failures-not-
description: Workflow retry loops must classify failures, not retry all equally
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [workflow, ci, error-handling, git]
---

Distinguish retryable (non-fast-forward, fetch-first) from non-retryable (auth, permission, hook, protected-branch) errors. Fail-fast on non-retryable to avoid wasting slots; only retry transient/contentious failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
