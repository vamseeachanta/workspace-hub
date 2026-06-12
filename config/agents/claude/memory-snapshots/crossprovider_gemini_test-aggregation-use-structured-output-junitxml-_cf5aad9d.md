---
name: crossprovider gemini test-aggregation-use-structured-output-junitxml-
description: Test aggregation: use structured output (--junitxml), not text parsing
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, orchestration, maintainability]
---

Parsing pytest text summary lines with bash is fragile (pytest version changes, plugins, edge cases). Instead, use --junitxml or --report-log and parse structured XML/JSON. Expected failures belong in test code (@pytest.mark.xfail), not external tracking lists.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
