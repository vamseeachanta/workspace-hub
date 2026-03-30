---
name: orcaflex-model-generator-3-way-benchmark
description: 'Sub-skill of orcaflex-model-generator: 3-Way Benchmark.'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 3-Way Benchmark

## 3-Way Benchmark


The benchmark validates three paths produce equivalent results:

| Path | Source | Pipeline |
|------|--------|----------|
| **A (monolithic)** | `.dat` file | Load directly in OrcFxAPI |
| **B (spec-driven)** | `.dat` → `.yml` → extract → spec → generate → load | Full round-trip |
| **C (library-direct)** | `spec.yml` → generate → load | From hand-written spec |

```bash
uv run python scripts/benchmark_model_library.py --library-only --three-way --skip-mesh
```

Results (2026-02-10): All 5 library models converge on all 3 paths with 0.00% tension difference.
