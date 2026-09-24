---
name: crossprovider codex plan-contract-tripartition-narrative-vs-pseudoco
description: Plan contract tripartition: narrative vs. pseudocode vs. TDD tests must be reconciled explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, contract-design, correctness-critical]
---

Codex reviews of wiki-gap-detection and email-queue plans repeatedly surfaced conflicts where plan text, pseudocode, and test-list assertions diverged (e.g., bare-hex normalization rules, optional input handling, schema validation scope). Plans must reconcile these three surfaces in a single authoritative table or the pseudocode implementation satisfies one surface and fails the others invisibly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
