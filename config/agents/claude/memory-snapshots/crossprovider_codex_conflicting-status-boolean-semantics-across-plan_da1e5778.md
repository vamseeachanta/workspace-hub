---
name: crossprovider codex conflicting-status-boolean-semantics-across-plan
description: Conflicting status/boolean semantics across plan sections produce inconsistent output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [spec-consistency, specification-review, adversarial-review]
---

When different plan sections define the same concept differently (e.g., status FAIL rules, flag precedence, format acceptance), implementation teams pick one interpretation and the other code path goes untested. Adversarial review must verify all uses of the same concept are consistent across §Proposed Tasks, §Acceptance Criteria, and §Pseudocode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
