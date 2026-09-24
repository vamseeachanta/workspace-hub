---
name: crossprovider gemini structured-output-over-text-parsing-for-tool-int
description: Structured output over text parsing for tool integration
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tooling-quirk, python-testing, bash-scripting]
---

When tools offer machine-readable output (JSON, XML, junitxml), use it instead of regex/grep on stdout. Text parsing of tool output is fragile and breaks easily when plugins, warnings, or error conditions change the format.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
