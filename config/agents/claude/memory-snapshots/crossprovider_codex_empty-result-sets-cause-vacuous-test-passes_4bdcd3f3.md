---
name: crossprovider codex empty-result-sets-cause-vacuous-test-passes
description: Empty result sets cause vacuous test passes
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [test-design, parser-validation, fail-closed]
---

Validation assertions like 'every parsed row contains field X' pass vacuously if the parser returns zero rows. Guard against malformed or missing input with explicit 'table found' or 'N rows parsed' checks before content validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
