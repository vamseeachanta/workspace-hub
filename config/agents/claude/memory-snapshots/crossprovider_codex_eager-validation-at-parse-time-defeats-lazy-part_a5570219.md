---
name: crossprovider codex eager-validation-at-parse-time-defeats-lazy-part
description: Eager validation at parse time defeats lazy/partial-load patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation-strategy, lazy-loading, api-contracts]
---

Code that validates all required fields at parse time (e.g., DiffractionSpec.from_yaml validates environment, frequencies, wave_headings immediately) cannot support the partial-template + CLI-override pattern. Plans must verify whether the actual implementation uses eager or lazy validation before assuming lazy behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
