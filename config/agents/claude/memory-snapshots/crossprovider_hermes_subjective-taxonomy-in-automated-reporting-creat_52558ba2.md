---
name: crossprovider hermes subjective-taxonomy-in-automated-reporting-creat
description: Subjective taxonomy in automated reporting creates noise
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [automation, taxonomy, subjectivity, reporting]
---

When a weekly cron uses subjective classification buckets (e.g., 'adjacent-specialization' vs 'near-duplicate'), each run produces churn that *looks* like real repo changes. Prefer deterministic rules, or separate the governance-policy decision (who decides taxonomy?) from the reporting (what does the data show?). Otherwise, noise masks signal.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
