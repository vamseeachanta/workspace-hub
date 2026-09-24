---
name: crossprovider codex stale-approval-surfaces-block-plan-disambiguatio
description: Stale approval surfaces block plan disambiguation when new drafts diverge
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gates, revision-tracking, drift]
---

Issue #2460 had live GitHub `status:plan-approved` pointing to an older revision while draft lineage (r11-r14) was newer and not approval-ready. Status headers must distinguish 'latest approved' from 'current draft' and cite the exact revision snapshot that holds approval. Lack of immutable binding (file path + commit SHA + review artifacts) meant approval state was ambiguous.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
