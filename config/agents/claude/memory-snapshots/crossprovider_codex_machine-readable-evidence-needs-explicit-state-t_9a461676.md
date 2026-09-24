---
name: crossprovider codex machine-readable-evidence-needs-explicit-state-t
description: Machine-readable evidence needs explicit state taxonomy
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-modeling, state-machines, validation]
---

Enum values like 'LIVE' are ambiguous for downstream consumers. Require explicit machine-readable states: LIVE (verified), MISSING-EVIDENCE (probe incomplete), DIVERGES (origin mismatch), NOT-REACHABLE. Enforce relational invariants in validation, not just enum membership (e.g., REACHABLE + NOT-INSTALLED is invalid).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
