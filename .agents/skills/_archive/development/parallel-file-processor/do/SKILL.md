---
name: parallel-file-processor-do
description: 'Sub-skill of parallel-file-processor: Do (+1).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Do (+1)

## Do


1. Choose correct processing mode for workload type
2. Use progress callbacks for long operations
3. Batch large file sets to manage memory
4. Log individual failures for debugging
5. Consider retry logic for transient errors
6. Monitor memory usage with large DataFrames


## Don't


1. Use process pool for IO-bound tasks
2. Skip error handling in processor functions
3. Load all results into memory at once
4. Ignore batch result statistics
5. Use too many workers for memory-constrained tasks
