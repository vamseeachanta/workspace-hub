---
name: crossprovider hermes report-artifacts-must-use-deterministic-syntheti
description: Report artifacts must use deterministic synthetic fixtures, not live state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [fixtures, determinism, artifact-testing]
---

Reports derived from live machine state (dirty/ahead/behind, unknown repos) are non-reproducible. Fixture-backed tests require synthetic registry/repo fixtures; compare against synthetic fixtures, not live state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
