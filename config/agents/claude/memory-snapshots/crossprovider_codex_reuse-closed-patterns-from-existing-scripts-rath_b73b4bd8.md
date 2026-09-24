---
name: crossprovider codex reuse-closed-patterns-from-existing-scripts-rath
description: Reuse closed patterns from existing scripts rather than creating shared infrastructure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [implementation-pattern, code-review, safety-validation]
---

When building new data-processing scripts (e.g., client_private_boundary_disposition.py), mirror the exact structure of existing analogous scripts (client_private_routing_queue.py) rather than extracting constants into shared modules. This keeps the blast radius small, makes unsafe-token validation locally verifiable per script, and avoids introducing new abstractions that future reviewers must track. Patterns like _assert_safe(), render_manifest(), and static corpus-walk guard tests are worth duplicating.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
