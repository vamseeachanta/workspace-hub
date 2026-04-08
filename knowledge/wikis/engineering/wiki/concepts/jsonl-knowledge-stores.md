---
title: "JSONL Knowledge Stores"
tags: [jsonl, data-engineering, append-only, knowledge-base, portable]
sources: [career-learnings-seed]
added: 2026-04-08
last_updated: 2026-04-08
---

# JSONL Knowledge Stores

Using newline-delimited JSON (JSONL) as a lightweight, portable, append-only persistent data store.

## What is JSONL?

Each line is a self-contained, valid JSON object. No wrapping array, no commas between records:

```jsonl
{"id": "pipe-001", "od": 323.9, "wt": 12.7, "grade": "X65"}
{"id": "pipe-002", "od": 273.1, "wt": 9.3, "grade": "X52"}
```

| Property | Benefit |
|----------|---------|
| Line-per-record | Partial writes are safe -- only complete lines are parsed |
| Append-only | `>>` is the primary write operation; no file rewrite needed |
| Streamable | Process one record at a time; no need to load entire file |
| Git-friendly | Diffs show exactly which records changed |
| Portable | No database, no schema migration, no server |

## Writing Safely

### Never Overwrite -- Always Append

```bash
echo '{"id":"entry-42","text":"new finding"}' >> store.jsonl
```

Deduplication happens on read or during periodic index rebuilds, not at write time. This avoids corruption from concurrent writes or interrupted processes.

### Dedup by ID Before Writing

If you must avoid duplicates at write time, check within a lock:

```bash
exec 9>"${store}.lock"
flock -w 10 9
if ! grep -q '"id":"entry-42"' "$store"; then
  echo '{"id":"entry-42","text":"new finding"}' >> "$store"
fi
flock -u 9
```

See [Shell Scripting Patterns](shell-scripting-patterns.md) for details on flock and idempotency inside locks.

### Flock for Concurrent-Write Safety

Multiple agents or cron jobs appending to the same JSONL file must coordinate via `flock`. Without it, interleaved writes produce corrupted lines.

## Reading Safely

### Handle Malformed Lines

Wrap `json.loads` in try/except and skip bad lines with a warning:

```python
import json
from pathlib import Path

def read_store(path: Path) -> list[dict]:
    records = []
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"WARNING: skipping malformed line {lineno} in {path}")
    return records
```

This is essential because:
- A process may have been killed mid-write, leaving a truncated line
- Manual edits may introduce syntax errors
- Encoding issues can corrupt individual lines

### Dedup on Read

```python
def dedup_by_id(records: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for rec in records:
        seen[rec["id"]] = rec  # last-write-wins
    return list(seen.values())
```

## Index Files for Query Performance

For stores with hundreds or thousands of records, build an index file that maps IDs to byte offsets or summarizes key fields:

```
store.jsonl          # raw append-only data
store.jsonl.index    # derived index (JSON or JSONL)
```

### Staleness Detection

Check source `mtime` against index `mtime`:

```python
import os

def index_stale(store: Path, index: Path) -> bool:
    if not index.exists():
        return True
    return os.path.getmtime(store) > os.path.getmtime(index)
```

### Atomic Index Rebuild

Rebuild to a tmp file, then `mv` into place. Use flock to prevent concurrent rebuilds:

```bash
exec 9>"${index}.lock"
flock -w 30 9

tmp=$(mktemp "${index}.tmp.XXXXXX")
python3 build_index.py "$store" > "$tmp"
mv -- "$tmp" "$index"

flock -u 9
```

## JSONL vs Alternatives

| Format | Best for | Drawback |
|--------|----------|----------|
| JSONL | Append-heavy, multi-writer, streaming | No built-in query engine |
| SQLite | Complex queries, transactions | Write contention, not append-friendly |
| CSV | Tabular data, spreadsheet interchange | No nested data, quoting ambiguity |
| Parquet | Analytics, columnar queries | Binary, requires libraries |

JSONL is ideal when the primary operations are append and full-scan, the data has nested fields, and the environment cannot run a database server.

## Related Pages

- [Shell Scripting Patterns](shell-scripting-patterns.md) -- flock, atomic writes, and the patterns underlying safe JSONL operations
- [Python Type Safety](python-type-safety.md) -- typing json.loads results with TypedDict
- [Knowledge-to-Website Pipeline](knowledge-to-website-pipeline.md) -- JSONL as a knowledge source for publishing
