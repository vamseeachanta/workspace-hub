---
name: crossprovider codex test-self-repair-trap-hides-staleness
description: Test self-repair trap hides staleness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, antipattern, artifact-verification]
---

Tests that regenerate tracked artifacts and then assert against the regenerated outputs will silently repair stale or incorrect artifacts instead of failing. Verify artifacts independently of test execution to avoid masking staleness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
