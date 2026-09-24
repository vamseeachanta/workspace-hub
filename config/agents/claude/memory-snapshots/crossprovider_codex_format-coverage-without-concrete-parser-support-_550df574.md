---
name: crossprovider codex format-coverage-without-concrete-parser-support-
description: Format coverage without concrete parser support is overclaiming
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [spreadsheets, plan-defects, test-coverage, format-scope]
---

Don't assign success % or ingestion yield to unsupported file formats without a working parser, test fixture, and regression tests. Sessions showed `.xls` claimed at 60-85% yield but live canary only supported `.xlsx`. Downgrade to metadata-only or defer to adapter issue.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
