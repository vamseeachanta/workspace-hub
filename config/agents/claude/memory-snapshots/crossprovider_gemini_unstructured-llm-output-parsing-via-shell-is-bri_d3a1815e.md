---
name: crossprovider gemini unstructured-llm-output-parsing-via-shell-is-bri
description: Unstructured LLM output parsing via shell is brittle
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [parsing, lvm-output, shell]
---

Parsing markdown verdicts, findings, and structured data from LLM output using shell regex is fragile and prone to silent failures. Require JSON or strict-block structured output (`<output format: json>`, `<output format: markdown-blocks>`). Parse in Python or jq, not sh.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
