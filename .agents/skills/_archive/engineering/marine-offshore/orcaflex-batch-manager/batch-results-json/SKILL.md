---
name: orcaflex-batch-manager-batch-results-json
description: 'Sub-skill of orcaflex-batch-manager: Batch Results JSON (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Batch Results JSON (+1)

## Batch Results JSON


```json
{
  "batch_id": "operability_20260117_143022",
  "start_time": "2026-01-17T14:30:22",
  "end_time": "2026-01-17T18:45:33",
  "total_files": 500,
  "successful": 495,
  "failed": 5,
  "success_rate": 99.0,
  "total_time_seconds": 15311,

*See sub-skills for full details.*

## Progress Log


```
2026-01-17 14:30:22 - Batch started: 500 files
2026-01-17 14:30:22 - Workers: 20 (adaptive)
2026-01-17 14:31:45 - Progress: 50/500 (10.0%) - Success: 50
2026-01-17 14:33:12 - Progress: 100/500 (20.0%) - Success: 100
2026-01-17 14:33:12 - Checkpoint saved
2026-01-17 14:35:40 - Workers adjusted: 20 -> 15 (memory 82%)
...
2026-01-17 18:45:33 - Batch complete: 495 successful, 5 failed
```
