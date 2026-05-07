---
title: "JSONL Knowledge Stores"
tags: [software, data-engineering, jsonl, append-only, indexing]
sources:
  - career-learnings
added: 2026-04-09
last_updated: 2026-04-09
---

# JSONL Knowledge Stores

JSONL (newline-delimited JSON) as a lightweight persistent data store for append-only,
queryable, portable knowledge bases — without requiring a database.

## Why JSONL

- Each line is valid JSON — partial writes are safe because only complete lines are parsed
- Append-only by default — no in-place mutation
- Portable across systems — plain text, no binary format
- Queryable with standard Unix tools (grep, jq) or Python json.loads

## Write Patterns

- Never overwrite JSONL — always append, then dedup on read or rebuild index
- Dedup by id field before writing to prevent duplicate entries
- Lock with flock for concurrent-write safety

## Index Strategy

- Build an index file (index.jsonl) for query performance
- Check source file mtimes against index mtime to detect staleness
- Index rebuild: atomic tmp+mv, flock to prevent concurrent rebuilds

## Error Handling

- Corrupt lines: wrap json.loads in try/except, skip malformed lines with warning
- Partial writes are safe — incomplete final line is discarded on read

## Design Patterns

- Never overwrite JSONL — always append, then dedup on read or rebuild index
- Corrupt lines: wrap json.loads in try/except, skip malformed lines with warning
- Index rebuild: atomic tmp+mv, flock to prevent concurrent rebuilds

## Cross-References

- **Related entity**: [[python-type-safety]] (typed Python scripts for JSONL processing)
- **Related entity**: [[shell-scripting-patterns]] (flock and atomic write patterns)
