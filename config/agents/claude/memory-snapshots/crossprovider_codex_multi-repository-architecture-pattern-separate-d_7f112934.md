---
name: crossprovider codex multi-repository-architecture-pattern-separate-d
description: Multi-repository architecture pattern: separate data ingest, execution, knowledge, and frontend layers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, multi-repo, ownership-boundaries]
---

When features span multiple repositories, establish clear ownership boundaries rather than duplicating capability across repos. Pattern: public data/ingest layer (worldenergydata for Landman Project), private orchestration app (deckhand), shared knowledge content (llm-wiki), static frontend (aceengineer-website). This prevents coordination debt and enables independent evolution per layer.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
