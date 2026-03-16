---
name: orcaflex-batch-manager-parallel-execution
description: 'Sub-skill of orcaflex-batch-manager: Parallel Execution (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Parallel Execution (+1)

## Parallel Execution


| Feature | Description |
|---------|-------------|
| ThreadPoolExecutor | Parallel model processing |
| Adaptive scaling | Workers adjust based on CPU/memory |
| File-size optimization | Thread allocation by file complexity |
| Chunk processing | Memory-efficient large batch handling |

## Resource Management


| Resource | Management Strategy |
|----------|---------------------|
| CPU | Worker count = CPU cores - 2 (max 30) |
| Memory | Monitor usage, reduce workers if >80% |
| Disk I/O | Batch file reads, optimize writes |
| License | Respect OrcaFlex license limits |
