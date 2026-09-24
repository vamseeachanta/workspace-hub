---
name: crossprovider codex negative-test-false-greens-mask-unimplemented-re
description: Negative test false-greens mask unimplemented rejection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, negative-tests, adversarial-testing]
---

Tests claiming 'rejects X' while only exercising happy/prefix paths pass even when rejection logic is missing. Require explicit adversarial cases (boundary conditions, hostile inputs, malformed state) for negative coverage, not just basic scenarios.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
