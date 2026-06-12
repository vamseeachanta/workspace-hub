---
name: crossprovider codex evidence-schema-consolidation-to-canonical-asset
description: Evidence schema consolidation to canonical assets/WRK-*/evidence/ path
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [refactoring, evidence-schema, process]
---

Governance migration: moving from scattered evidence files (claim-evidence.yaml, close-evidence.yaml, archive-evidence.yaml, etc.) to normalized `assets/WRK-*/evidence/{stage}.yaml` structure with per-stage canonical files (resource-intelligence.yaml, claim.yaml, execute.yaml, reclaim.yaml, future-work.yaml, close.yaml, archive.yaml). Reduces schema drift and improves validator validation coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
