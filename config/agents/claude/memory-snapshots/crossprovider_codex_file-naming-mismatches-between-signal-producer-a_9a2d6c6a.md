---
name: crossprovider codex file-naming-mismatches-between-signal-producer-a
description: File naming mismatches between signal producer and consumer cause silent zero-discovery
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [file-naming-conventions, data-pipeline, schema-contracts]
---

If signal writer outputs `${DATE}.jsonl` but reader searches `${DATE}-*.jsonl` with no fallback, discovery succeeds silently (find returns empty, grep finds zero signals). Document naming contracts and use OR-globs or explicit producer/consumer negotiation. Schema tests should verify both sides match.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
