---
name: crossprovider codex csv-output-renderer-silently-drops-computed-modu
description: CSV output renderer silently drops computed module/data-directory status fields, contradicting documented contract
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, contracts, regression, output-validation, csv]
---

In worldenergydata `status --format csv`, `_run_status()` computes `module_loaded`, path, file count, size, and update time but the CSV renderer ignores all but provider-only fields. This contradicts CLI.md contract that `status` includes local data-directory status. Test accepts provider-only rows, allowing regression. Lesson: validate output contracts against documentation, not just syntactic parseability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
