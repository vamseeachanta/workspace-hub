---
name: crossprovider hermes iterative-adversarial-review-find-fix-re-verify-
description: Iterative adversarial review (find → fix → re-verify) catches issues single-pass review misses
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [adversarial-review, qa-pattern, iterative-verification]
---

Adversarial review on llm-wiki #76 found MAJOR issues (broken links, weak validator coverage) in first pass. Fixes were targeted and narrow, then re-review confirmed all MAJOR findings resolved with no regressions. This two-pass pattern is more effective than trying to hunt every defect in one exhaustive pass; initial findings guide targeted fixes, reducing re-review scope.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
