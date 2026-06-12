---
name: crossprovider hermes workbook-to-code-translation-requires-explicit-s
description: Workbook-to-code translation requires explicit sign and semantics contract
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [naval-architecture, workbook-translation, sign-convention, documentation]
---

Translating legacy workbook calculations (especially naval-architecture spreadsheets) to production code must explicitly document: (1) Ft vs Fn distinction (transverse vs normal force); (2) rudder angle sign convention (positive=port, negative=starboard); (3) moment-arm semantics distinguishing workbook geometry location from CG-based lever arm; (4) source-gap behavior when authoritative values unavailable. Omitting any of these creates downstream confusion and calculation errors.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
