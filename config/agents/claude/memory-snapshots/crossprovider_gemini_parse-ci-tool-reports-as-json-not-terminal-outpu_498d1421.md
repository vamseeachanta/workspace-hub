---
name: crossprovider gemini parse-ci-tool-reports-as-json-not-terminal-outpu
description: Parse CI tool reports as JSON, not terminal output
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci, testing, parsing]
---

Scraping terminal output with grep+awk is brittle and breaks on format changes. For pytest-cov, use `--cov-report=json` and parse the JSON file; for any tool, prefer structured output over stdout scraping (WRK-1067).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
