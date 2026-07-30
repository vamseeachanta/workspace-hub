---
name: crossprovider codex split-unrelated-evidence-domains-into-separate-v
description: Split unrelated evidence domains into separate verification lanes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [issue-planning, testing, architecture]
---

When sources require different validation surfaces (e.g., benchmark methodology, OSS licensing, regulatory interpretation), split into child issues with independent tests, reviews, and commits. Shared verification gates block parallel progress and can make one defect category delay all others.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
