---
name: crossprovider hermes greek-letter-javascript-variable-names-cause-run
description: Greek-letter JavaScript variable names cause runtime errors
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [javascript, syntax, variables, runtime-errors]
---

Use ASCII-compatible identifiers (alpha, theta) not Unicode Greek (α, θ) in JS variable declarations; reserve display-friendly Greek for output strings only. Undefined variable references bypass test assertions but surface at runtime.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
