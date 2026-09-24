---
name: crossprovider codex drift-detection-requires-exact-byte-verification
description: Drift detection requires exact-byte verification, not heuristics
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [drift-detection, testing-pattern, artifact-verification]
---

When checking generated artifacts for drift (HTML pages, CSS, JSON), regenerate all outputs and compare byte-for-byte rather than using heuristic diffs or manual inspection. This approach caught 51 divergent pages that naive checkers would miss. Deterministic generation + byte comparison is the reliable pattern for artifact lifecycle verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
