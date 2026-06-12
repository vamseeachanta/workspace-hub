---
name: crossprovider codex machine-readable-output-must-not-be-contaminated
description: Machine-readable output must not be contaminated with human text on stdout
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [output-formatting, csv, robustness]
---

When emitting both human-readable and machine-readable formats (CSV, JSON), human annotations like "skipped 5 records" must go to stderr or be suppressed entirely in machine mode. If human text lands on stdout alongside CSV, downstream tools will fail to parse the output. This applies to all utility scripts that produce structured output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
