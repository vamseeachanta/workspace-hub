---
name: crossprovider codex evidence-schema-proliferation-across-work-queue-
description: Evidence schema proliferation across work-queue stages creates maintenance drift
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema, work-queue, maintenance]
---

claim-evidence.yaml, close-evidence.yaml, archive-evidence.yaml, gap-review-user.json, future-work-recommendations.md each have separate schema; normalize to evidence/ subdirectory with per-stage canonical files (resource-intelligence.yaml, claim.yaml, etc.) and explicit legacy aliases for migration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
