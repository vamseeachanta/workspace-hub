---
name: crossprovider gemini use-json-output-format-for-parsing-tool-output
description: Use JSON output format for parsing tool output
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tooling, robustness]
---

When parsing output from command-line tools (ruff, mypy, etc.), prefer structured formats like `--output-format json` over regex/text parsing. Text format is brittle and breaks when tools update their output; JSON is version-stable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
