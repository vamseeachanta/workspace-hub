---
name: crossprovider hermes prove-validation-gaps-via-construction-not-theor
description: Prove validation gaps via construction, not theory
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, validation, debugging]
---

When suspicious of a validator bypass, construct a case designed to fail (e.g., artifact with `summary["run_date"]` mismatched from report heading date, or `external:~` path in public graph). Run it through the validator. If it passes, the gap is real and reproducible, enabling targeted fix. This shifts from theory to evidence-based defect finding.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
