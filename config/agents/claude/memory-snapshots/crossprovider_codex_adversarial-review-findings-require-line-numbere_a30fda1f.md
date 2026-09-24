---
name: crossprovider codex adversarial-review-findings-require-line-numbere
description: Adversarial review findings require line-numbered evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-rigor, codex-standard, cross-provider]
---

Findings without specific file paths, plan section citations, or quoted line numbers are stripped during review. 'Looks good' or 'consider adding X' statements are not findings. Every defect must be anchored to concrete evidence: plan.md:L42-L48 or a grep result.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
