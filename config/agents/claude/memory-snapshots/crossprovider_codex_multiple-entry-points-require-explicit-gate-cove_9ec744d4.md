---
name: crossprovider codex multiple-entry-points-require-explicit-gate-cove
description: Multiple entry points require explicit gate coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-gates, threat-model, bypass-vectors]
---

Workflow transitions often have multiple code paths: official entrypoints (`plan.sh`, `cross-review.sh`), downstream validators (`verify-gate-evidence.py`), and out-of-band mutations (manual frontmatter edits). Gate enforcement must cover all paths or the gate is ineffective.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
