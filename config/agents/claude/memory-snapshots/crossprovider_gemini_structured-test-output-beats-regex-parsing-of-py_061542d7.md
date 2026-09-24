---
name: crossprovider gemini structured-test-output-beats-regex-parsing-of-py
description: Structured test output beats regex parsing of pytest stdout
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, bash, pytest, fragility]
---

Parsing pytest's verbose stdout with regex is brittle across versions, terminal environments, and plugins. Instead, use `--junitxml=output.xml` for machine-readable results or pytest's native `@pytest.mark.xfail(strict=True)` decorator to handle expected failures directly in code without external files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
