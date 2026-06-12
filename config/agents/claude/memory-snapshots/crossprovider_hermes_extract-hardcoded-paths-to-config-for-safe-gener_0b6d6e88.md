---
name: crossprovider hermes extract-hardcoded-paths-to-config-for-safe-gener
description: Extract hardcoded paths to config for safe generator re-execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [idempotence, configuration, generators]
---

Generators with embedded file paths cannot be safely re-run (path drift on subsequent executions). Extract to config constants so artifacts can be regenerated after classifier/logic changes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
