---
name: crossprovider codex fail-open-artifact-write-ordering
description: Fail-open artifact write ordering
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [safety-gate-ordering, build-pattern, llm-wiki-ingest]
---

Code that builds and writes output files must validate safety gates BEFORE writing, not after. Multiple batch reviews found unsafe content persisted on disk when guards ran post-write (manifest.jsonl, report.json, report.html written before _assert_repo_safe() check). Reorder guard-before-write.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
