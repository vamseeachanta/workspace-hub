---
name: crossprovider hermes adversarial-review-infrastructure-100-execution-
description: Adversarial review infrastructure 100%, execution compliance only 4%
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-process, CI-CD, adversarial-review, compliance-gap]
---

The workspace-hub has perfect infrastructure for capturing and enforcing adversarial reviews (pending-reviews tracking, session signals, git-log verification), but git-level enforcement compliance is only 4% of eligible commits (overall 58% due to artifact coverage). The bottleneck is workflow adherence, not tooling — developers skip the review step even though the gate exists.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
