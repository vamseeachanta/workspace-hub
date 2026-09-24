---
name: crossprovider codex adversarial-review-requires-multiple-passes-to-c
description: Adversarial review requires multiple passes to catch different defect classes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-methodology, adversarial-review, multi-pass-review]
---

Single-pass adversarial reviews miss entire categories of defects. In #291, round 1 said PASS but round 2 found MAJOR implementation blockers (row-dropping semantics, backlog parity). Standards reviews catch gate/process violations; spec reviews catch scope contradictions. Complement adversarial review with standards and spec angles for comprehensive coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
