---
name: crossprovider codex compliance-audits-require-chronological-evidence
description: Compliance audits require chronological evidence over artifact snapshots
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit, evidence, verification]
---

Plans for workflow compliance (e.g., review→approval→implementation) must establish temporal ordering via GitHub timeline data (gh issue view --json timelineItems), not just presence of marker files (.planning/plan-approved/). Artifact existence alone does not prove chronology.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
