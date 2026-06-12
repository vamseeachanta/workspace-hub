---
name: crossprovider hermes stale-artifact-paths-in-gtm-plan-narrative-secti
description: Stale artifact paths in GTM plan narrative sections break validation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gtm, plan-review, documentation, narrative-drift]
---

When plans have both narrative (summary/blocker language) and evidence sections, contradictions between them—e.g., narrative saying 'X hasn't shipped' while evidence lists shipped artifacts—confuse external reviewers and indicate the plan wasn't re-reviewed after related issue closure. After dependent issues land, re-run narrative edits and adversarial review before promotion to plan-review.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
