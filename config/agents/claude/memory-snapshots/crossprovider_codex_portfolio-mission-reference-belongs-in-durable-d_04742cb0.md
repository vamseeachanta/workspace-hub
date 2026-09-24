---
name: crossprovider codex portfolio-mission-reference-belongs-in-durable-d
description: Portfolio/mission reference belongs in durable docs, not review artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [documentation, architecture, governance]
---

Reusable reference material (mission tables, routing rules, portfolio index) lives in `docs/` under version control as single-source-of-truth. Transient execution artifacts (review findings, plan working docs) belong in `scripts/review/results/` or `docs/plans/`. This distinction preserves discoverability and canonical authority across sessions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
