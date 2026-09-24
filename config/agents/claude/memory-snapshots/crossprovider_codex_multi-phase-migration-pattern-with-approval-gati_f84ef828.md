---
name: crossprovider codex multi-phase-migration-pattern-with-approval-gati
description: Multi-phase migration pattern with approval gating and compliance tracking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, migration, patterns]
---

Controlled migrations use distinct approval stages (APPROVED_FOR_DRYRUN, APPROVED_FOR_SIMULATION, APPROVED) with compliance artifact tracking for each phase. Compliance artifact matrix distinguishes tracked-required, tracked-optional, and transient-generated; each phase gates the next.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
