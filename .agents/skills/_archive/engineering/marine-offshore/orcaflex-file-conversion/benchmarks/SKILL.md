---
name: orcaflex-file-conversion-benchmarks
description: 'Sub-skill of orcaflex-file-conversion: Benchmarks (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Benchmarks (+1)

## Benchmarks


- **Single file conversion**: 0.5-2 seconds per file
- **Batch processing (180 files)**: ~145 seconds with validation
- **Parallel processing (4 workers)**: ~3x faster than sequential
- **Memory usage**: ~200-500 MB per file during conversion

## Optimization Tips


1. Use parallel processing for > 10 files
2. Disable validation for trusted files
3. Process smaller files first (auto-sorted by size)
4. Limit max_workers based on available licenses
