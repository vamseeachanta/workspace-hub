---
name: crossprovider codex substring-assertions-in-artifact-tests-won-t-cat
description: Substring assertions in artifact tests won't catch drift
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, artifact-validation, precision]
---

Testing that JSON keys exist or HTML contains substrings is insufficient for acceptance. Use exact byte/line comparisons (e.g., JSON equality, HTML diff) when artifact completeness or output shape is part of acceptance criteria. Exact tests are more noise-resistant.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
