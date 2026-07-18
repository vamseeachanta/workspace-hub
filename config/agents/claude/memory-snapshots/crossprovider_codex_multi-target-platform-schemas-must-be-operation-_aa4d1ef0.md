---
name: crossprovider codex multi-target-platform-schemas-must-be-operation-
description: Multi-target platform schemas must be operation-level, not path-level
metadata:
  type: reference
  source: codex
  bridged: 2026-07-13
  tags: [schema-design, platform-abstraction, completeness]
---

Code targeting multiple scheduler backends (systemd-user vs crontab, or Task Scheduler variants) should represent targets at the operation level, not dispersed across path-based logic. Enumerate the complete target set and validate completeness in enforcement/tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
