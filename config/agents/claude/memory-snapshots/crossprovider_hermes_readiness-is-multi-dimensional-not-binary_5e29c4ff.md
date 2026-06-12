---
name: crossprovider hermes readiness-is-multi-dimensional-not-binary
description: Readiness is multi-dimensional, not binary
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [engineering-planning, readiness-assessment, risk-ranking]
---

Issues #2059 and #2062 both said 'READY AFTER LABEL UPDATE', but #2059 was truly ready (mostly test-only), while #2062 had significant hidden modeling blockers: draft estimation heuristics, sparse DRAFT_M fields, only ~138/2210 usable records. Rank issues by implementation confidence (data completeness, modeling assumptions, upstream dependency maturity), not just the label.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
