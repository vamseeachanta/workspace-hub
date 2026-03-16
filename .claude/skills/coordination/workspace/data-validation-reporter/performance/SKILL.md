---
name: data-validation-reporter-performance
description: 'Sub-skill of data-validation-reporter: Performance.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Performance

## Performance


**Benchmarks** (tested on 100,000 row dataset):
- Validation: ~2.5 seconds
- Report generation: ~1.2 seconds
- Total: ~3.7 seconds

**Memory usage**: ~150MB for 100k rows

**Scalability**:
- Tested up to 1M rows
- Linear scaling for validation
- Report generation optimized with sampling for large datasets
