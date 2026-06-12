---
name: crossprovider gemini structured-plan-sections-enable-defect-detection
description: Structured plan sections enable defect detection but don't replace evidence
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [plan-structure, adversarial-review, evidence]
---

Plans with Identity Contract, Tier Assignment, and Threat Model sections help organize thinking and catch logical contradictions, but they do not prevent 'unverified claims' findings. v2 plans added sections yet remained MAJOR on real defects; v3 fixed the bugs by embedding evidence and correcting contradictions. Pattern: sections + evidence blocks + adversarial review are three orthogonal gates, each necessary.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
