---
name: crossprovider hermes licensed-third-party-workbook-coefficients-must-
description: Licensed third-party workbook coefficients must use off-repo adapter pattern with TDD gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [licensed-sources, off-repo-routes, tdd-gates]
---

For licensed OCIMF coefficients: don't commit workbook/PDFs/extracted corpus; use off-repo route (`/mnt/ace/...`) at calculation time; implement workbook parser/interpolator; gate with tests proving actual interpolated values used, not hardcoded placeholders. Placeholder coefficient tests (e.g., `ocimf_cy = sin(psi)` formulas) pass but don't prove workbook accuracy—need TDD coverage of workbook lookup and interpolation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
