---
name: crossprovider codex per-artifact-class-sanitization-in-tests-prevent
description: Per-artifact-class sanitization in tests prevents generic 'safe output' false negatives
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [corpus-ingest, security]
---

When extraction writes to frontmatter, skip queues, logs, summaries, datasets, and verification queues, each artifact class needs explicit test checks. Generic 'outputs omit raw paths' tests are insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
