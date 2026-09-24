---
name: crossprovider codex gate-verdict-severity-not-enforced-in-cross-revi
description: Gate verdict severity not enforced in cross-review
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, policy-implementation-gap, cross-review, governance]
---

Cross-review hard-gate logic accepts any structurally valid output without checking verdict severity (APPROVE/MINOR/MAJOR/REJECT). Documentation claims Codex REJECT/MAJOR hard-fails with no fallback, but actual implementation marks Codex as passed on any structurally valid output. Policy and implementation are misaligned.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
