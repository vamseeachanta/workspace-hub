---
name: crossprovider codex plan-text-carries-the-same-public-private-leakag
description: Plan text carries the same public/private leakage risk as generated artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [public-private-boundary, leakage-control, content-scrubbing]
---

Absolute paths (`/mnt/local-analysis`), wiki identifiers, and private workbook references in plan files themselves are leakage if those files are public/committed. Don't rely only on generated-artifact scrubbing; scan and sanitize plan and review files before committing. Scope the `doc_key` and identifier leakage rules to both authored and generated content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
