---
name: crossprovider codex corpus-dispatcher-is-comprehensive-extend-rather
description: Corpus dispatcher is comprehensive; extend rather than rebuild
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [architecture, dispatch, llm-wiki, code-reuse]
---

dispatch_corpus_ingest.py (883 lines) handles publisher chunking, worktree isolation, single-PR dispatch, mechanical extraction, state tracking, and concurrent safety. When building orchestration/cockpit layers, extend this mature dispatcher rather than rewriting dispatch logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
