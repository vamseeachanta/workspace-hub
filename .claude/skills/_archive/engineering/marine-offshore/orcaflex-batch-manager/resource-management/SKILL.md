---
name: orcaflex-batch-manager-resource-management
description: 'Sub-skill of orcaflex-batch-manager: Resource Management (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Resource Management (+2)

## Resource Management


1. **CPU headroom** - Keep 2 cores free for system
2. **Memory monitoring** - Reduce workers if >80% used
3. **Disk I/O** - Use SSD for results directory
4. **Network** - Minimize network storage for sim files


## Error Handling


1. **Continue on error** - Don't stop batch for single failure
2. **Retry logic** - Retry failed files with single worker
3. **Timeout** - Set reasonable per-file timeout
4. **Logging** - Log all failures with details


## Performance


1. **Sort by size** - Process large files first
2. **Chunk processing** - Break very large batches
3. **Checkpoint** - Save progress for resumability
4. **Off-hours** - Run large batches overnight
