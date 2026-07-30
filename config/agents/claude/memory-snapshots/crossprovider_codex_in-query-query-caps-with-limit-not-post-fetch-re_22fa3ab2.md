---
name: crossprovider codex in-query-query-caps-with-limit-not-post-fetch-re
description: In-query query caps with LIMIT, not post-fetch rejection
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [query-safety, memory-safety, sql-patterns]
---

Enforcing result-size caps after materializing the full dataset via fetchall() defeats bounded-pilot safety and creates memory/availability risk. Use SQL LIMIT + overflow detection at the 26th row to stop immediately and detect oversized results without materializing the entire corpus.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
