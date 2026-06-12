---
name: crossprovider hermes generated-reports-with-stale-snapshots-become-ac
description: Generated reports with stale snapshots become accidental source of truth
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-lifecycle, atomic-writes, source-of-truth]
---

When a report artifact is reused across runs with stale data (old timestamp, partial write, prior revision), downstream operators cannot distinguish 'old report' from 'current state'. Use atomic writes, explicit `generated_at` timestamps, and SHA binding to plan/commit. Invalidate stale snapshots before reuse or face inadvertent double-execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
