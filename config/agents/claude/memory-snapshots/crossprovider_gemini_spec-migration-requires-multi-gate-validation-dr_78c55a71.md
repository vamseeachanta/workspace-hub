---
name: crossprovider gemini spec-migration-requires-multi-gate-validation-dr
description: Spec migration requires multi-gate validation: dry-run, checksums, collision detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [specs, migrations, governance]
---

Spec centralization (e.g., worldenergydata→specs/repos/) enforces: dry-run log gates, pre/post sha256sum parity, target collision detection, pointer README stubs. All gates must pass before apply; no exceptions for wave-1.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
