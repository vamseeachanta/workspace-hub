---
name: crossprovider hermes licensed-ocimf-source-must-replace-hardcoded-coe
description: Licensed OCIMF source must replace hardcoded coefficients
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [naval-architecture, source-control, licensing, fail-closed]
---

Naval architecture force calculations using OCIMF coefficients must derive from off-repo licensed workbook `/mnt/ace/mkt-a-codes/OCIMF/OCIMF Coef.xlsx`, not inline trig placeholders. Tests must fail closed on missing workbook, missing provenance README, or continued placeholder formulas (e.g., `ocimf_cx = 1.05 * abs(cos(psi))`). Acceptable source IDs are `ocimf-meg3-current-coefficients` and `ocimf-meg4-current-coefficients`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
