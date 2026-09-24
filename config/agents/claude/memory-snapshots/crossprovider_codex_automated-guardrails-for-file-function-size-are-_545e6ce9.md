---
name: crossprovider codex automated-guardrails-for-file-function-size-are-
description: Automated guardrails for file/function size are more effective than manual review
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [guardrails, linting, automation]
---

Line-count (400-line file, 50-line function) and size guardrails should be enforced by linting scripts, not manual review. Sessions 4-7 repeatedly checked these limits during verification; a linter would catch violations at commit/CI time rather than requiring adversarial review cycles. Manual verification is slow and misses edge cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
