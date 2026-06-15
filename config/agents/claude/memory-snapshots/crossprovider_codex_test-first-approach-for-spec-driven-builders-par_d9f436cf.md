---
name: crossprovider codex test-first-approach-for-spec-driven-builders-par
description: Test-first approach for spec-driven builders: parse spec before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, builder, spec-driven]
---

Write a test harness that parses the spec, validates key outputs (slide count, total duration, codec), and checks basic file existence *before* implementing the builder logic. This catches spec ambiguities early and provides regression coverage for future runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
