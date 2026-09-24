---
name: crossprovider gemini migrations-gate-apply-with-dry-run-review-post-a
description: Migrations gate apply with dry-run review + post-apply verification
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [migration-pattern, verification, process-gate]
---

Dry-run output must use fixed, machine-parseable format (e.g., `repo=X loc=Y files=Z target=T dry_run=true`) to enable automation. Post-apply verification includes content parity (sha256sum), no orphaned files, idempotence recheck, and case-fold collision detection. This workflow prevents silent data loss in large-scale migrations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
