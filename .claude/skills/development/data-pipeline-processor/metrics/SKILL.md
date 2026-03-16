---
name: data-pipeline-processor-metrics
description: 'Sub-skill of data-pipeline-processor: Metrics.'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Metrics

## Metrics


| Metric | Target | Description |
|--------|--------|-------------|
| Read Time | <1s per 100MB | Data loading speed |
| Validation Time | <500ms | Rule checking duration |
| Transform Time | Varies | Depends on operations |
| Export Time | <1s per 100MB | File writing speed |
| Memory Usage | <2x file size | Peak memory consumption |
