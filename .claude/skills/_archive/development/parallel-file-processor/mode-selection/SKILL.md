---
name: parallel-file-processor-mode-selection
description: 'Sub-skill of parallel-file-processor: Mode Selection (+2).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Mode Selection (+2)

## Mode Selection


| Workload Type | Recommended Mode | Reason |
|---------------|------------------|--------|
| File I/O | `THREAD_POOL` | IO-bound, threads avoid GIL issues |
| Data parsing | `THREAD_POOL` | Pandas releases GIL during IO |
| CPU computation | `PROCESS_POOL` | Bypasses GIL for true parallelism |
| Network requests | `ASYNC` | Best for many concurrent connections |
| Simple operations | `SEQUENTIAL` | Overhead may exceed benefit |

## Worker Count


```python
import os

# IO-bound (reading files, network)
io_workers = os.cpu_count() * 2

# CPU-bound (heavy computation)
cpu_workers = os.cpu_count()

# Memory-constrained (large files)
memory_workers = max(2, os.cpu_count() // 2)
```

## Batch Size


- **Small files (<1MB):** Large batches (500-1000)
- **Medium files (1-100MB):** Medium batches (50-100)
- **Large files (>100MB):** Small batches (10-20) or one at a time
