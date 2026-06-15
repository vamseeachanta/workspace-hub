---
name: crossprovider codex mark-chunks-done-only-after-successful-commit
description: Mark chunks done only after successful commit
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest, state-management, resilience]
---

In dispatcher state file, mark chunk done only if git commit succeeds. If quarantined or commit fails, leave undone so retries re-attempt. Enables safe recovery without manual state cleanup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
