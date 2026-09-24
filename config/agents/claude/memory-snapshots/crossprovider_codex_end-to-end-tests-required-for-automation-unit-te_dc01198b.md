---
name: crossprovider codex end-to-end-tests-required-for-automation-unit-te
description: End-to-end tests required for automation; unit tests insufficient to catch deduplication and false positives
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, end-to-end, automation-discovery]
---

Testing individual functions (classify, priority_score, extract_checklist_lines) in isolation will not surface bugs in aggregation logic (duplicate items within same stage, cross-stage deduplication) or false positives that accumulate across the real dataset. Add at least one integration test that runs the full pipeline against real data and asserts absence of known failure modes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
