---
name: crossprovider codex deny-catalog-enforcement-lists-diverge-from-appr
description: Deny-catalog enforcement lists diverge from approved plans without validation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [deny-catalog, safety-gates, plan-compliance, code-review]
---

Plan-stage self-checks and implementation constants drifted across review rounds (e.g., omitted `formula`, `excerpt`, `quote`, `regulator acceptance`). Must validate that every term in the approved plan's deny catalog is actually checked in implementation constants and safe-text guards.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
