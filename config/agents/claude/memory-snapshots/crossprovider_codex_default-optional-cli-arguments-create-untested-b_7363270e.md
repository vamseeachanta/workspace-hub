---
name: crossprovider codex default-optional-cli-arguments-create-untested-b
description: Default optional CLI arguments create untested behavior gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cli-design, testing-gaps, default-arguments]
---

Smoke tests that omit optional args (e.g., `cron-audit.py --json` without `--machine`) don't test behavior tied to that arg. cron-audit classifies machine-selected entries as `preserved_external` when `--machine` is omitted but `cataloged` when supplied. Fix: document the default value in smoke commands or explicitly require the arg for context-dependent operations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
