---
name: crossprovider gemini safe-content-migration-dry-run-collision-detecti
description: Safe content migration: dry-run, collision detection, idempotent apply
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [migration, data-integrity, validation]
---

For multi-file migrations: 1) generate dry-run with fixed format and summary line count, 2) pre-check target collisions (fail-fast if any exist), 3) validate idempotency (second apply produces no diff), 4) use sha256sum for content integrity. Applicable to spec centralization, filesystem consolidation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
