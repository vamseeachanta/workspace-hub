---
name: crossprovider gemini spec-centralization-uses-wave-based-migration-wi
description: Spec centralization uses wave-based migration with dry-run/apply pattern
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [specs-migration, governance, idempotency]
---

Large-scale spec migrations (e.g., moving 5543 files from digitalmodel/specs to specs/repos/digitalmodel/) use a controlled two-phase pattern: dry-run with sha256sum verification and collision detection, followed by idempotent apply. A second apply on already-migrated state produces no content diff. Pointer README stubs replace original specs/ directories.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
