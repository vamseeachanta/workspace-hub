---
name: crossprovider codex floor-rule-assertions-require-effective-enableme
description: Floor-rule assertions require effective enablement checks, not config-shape validation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [validation, ci-gates, test-falsifiability]
---

Plans asserting a lint floor (e.g., 20 rules minimum) can still be bypassed if the config uses a global `default: false` pattern while claiming the floor is enforced. The check must fail on `missing=floor & disabled`, not just `v is False`. This pattern appeared in markdown-lint gate design.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
