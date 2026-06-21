---
name: crossprovider codex substring-testing-in-generated-artifacts-misses-
description: Substring testing in generated artifacts misses future drift — use exact comparison when consistency is critical
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [testing-gaps, artifact-verification, regression-detection]
---

Tests that check HTML with `in html_str` pass if the expected content is present, but miss additions or reorderings. For reports where exact structure matters (e.g., bucket ordering, field presence guarantees), compare the generated artifact exactly against the builder output or use a canonical text diff.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
