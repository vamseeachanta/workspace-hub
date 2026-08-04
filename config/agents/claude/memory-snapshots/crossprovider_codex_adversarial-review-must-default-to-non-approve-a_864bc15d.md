---
name: crossprovider codex adversarial-review-must-default-to-non-approve-a
description: Adversarial review must default to non-APPROVE and cite evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [code-review, adversarial-stance, evidence]
---

Adversarial review stance assumes the plan/code is wrong until affirmatively proven; findings must cite specific file paths, line numbers, or quoted claims. Silence (no findings after review) is a failure, not implicit approval—always state what was checked. Default verdict is MINOR or MAJOR; APPROVE is the exception.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
