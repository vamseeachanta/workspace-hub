---
name: crossprovider hermes licensed-data-must-fail-closed-and-never-committ
description: Licensed data must fail-closed and never committed
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [licensing, data-provenance, proj-a, hydrodynamics]
---

Licensed external files (e.g., OCIMF coefficients workbook) must reference by absolute path with fail-closed guards; never commit to repo. Implementation must error if source unavailable, and reports must explicitly cite provenance and state if data is generic reference vs. ship-specific.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
