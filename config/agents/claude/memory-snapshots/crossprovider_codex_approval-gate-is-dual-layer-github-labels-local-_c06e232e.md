---
name: crossprovider codex approval-gate-is-dual-layer-github-labels-local-
description: Approval gate is dual-layer: GitHub labels + local markers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [issue-gates, approval, governance]
---

An issue is truly plan-approved only with both GitHub status:plan-approved label AND corresponding .planning/plan-approved/<issue>.md local marker. Tests checking single-layer (GitHub only, or marker only) miss unsafe deviations between them. Current worldenergydata has 48 approved labels but only 13 markers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
