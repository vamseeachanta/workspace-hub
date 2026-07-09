---
name: crossprovider codex split-brain-validator-coordination-multiple-scan
description: Split-brain validator coordination: multiple scanners over same surface cause silent divergence
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [validator-design, ci-ordering, integration-test]
---

When two validators (e.g., legal-scan.py and legacy ACE validator) scan overlapping public surfaces with different rules, they can accept/reject the same files silently. CI must include explicit integration tests between validators or unified scan ordering to catch divergence before commit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
