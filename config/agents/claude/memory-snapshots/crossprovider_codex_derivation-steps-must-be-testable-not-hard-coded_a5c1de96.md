---
name: crossprovider codex derivation-steps-must-be-testable-not-hard-coded
description: Derivation steps must be testable, not hard-coded
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [test-design, derivation, defensibility]
---

Combined factors derived from reserves/API must show the calculation (e.g., 1.2 MMbbl Montanazo + 2.9 MMbbl Lubina weighted by per-field API); tests asserting hard-coded derived values (32.584…) cannot catch formula or input errors. Separate source-stated values from derived proxies in test assertions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
