---
name: crossprovider codex hard-coded-dates-in-multi-record-generators-bloc
description: Hard-coded dates in multi-record generators block incremental additions
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [generator-design, scaling, llm-wiki-completeness]
---

When a generator like private_index_completeness.py assumes all target issues share one CLI-level generated_date, adding a new target issue forces re-rendering all prior records with the new date or requires moving to per-record date derivation. Derive generated dates from record-specific metadata or artifact paths, not global CLI args.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
