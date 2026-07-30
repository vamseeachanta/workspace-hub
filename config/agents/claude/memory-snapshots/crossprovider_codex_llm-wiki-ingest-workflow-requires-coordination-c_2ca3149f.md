---
name: crossprovider codex llm-wiki-ingest-workflow-requires-coordination-c
description: llm-wiki ingest workflow requires coordination claim via claim.py before isolated publisher worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [llm-wiki, ingest, workflow, coordination, worktrees, parallelism]
---

Shared ingest loops must acquire/check a claim using `scripts/coordination/claim.py` before running `dispatch_corpus_ingest.py`. Workflow uses isolated publisher worktrees and restricts staged outputs strictly to `wikis/` and `docs/reports/`. Default is dry-run; canonical command: `uv run python scripts/ingest/dispatch_corpus_ingest.py --publisher <name> --max-docs-per-chunk N`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
