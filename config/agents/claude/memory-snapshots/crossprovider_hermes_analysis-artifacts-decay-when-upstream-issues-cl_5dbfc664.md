---
name: crossprovider hermes analysis-artifacts-decay-when-upstream-issues-cl
description: Analysis artifacts decay when upstream issues close or change
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifacts, issue-closure, stale-analysis]
---

Issue analysis PDFs/plans (docs/plans/*/results/*.md) become stale within hours as referenced issues close or are re-scoped. Artifacts claim executability or blocking status that no longer holds; no reconciliation sweep fires after issue closures. Need post-closure audit gate that invalidates or re-derives dependent artifacts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
