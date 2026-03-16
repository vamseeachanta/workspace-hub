---
name: orcaflex-monolithic-to-modular-significance-levels
description: 'Sub-skill of orcaflex-monolithic-to-modular: Significance Levels (+2).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Significance Levels (+2)

## Significance Levels


| Level | Meaning | Action |
|-------|---------|--------|
| `match` | Values identical (within tolerance) | None |
| `cosmetic` | < 0.01% numeric diff | Safe to ignore |
| `minor` | 0.01-1% numeric diff | Review if important |
| `significant` | > 1% numeric diff | Must investigate |
| `missing` | Present in mono, absent in mod | Fix extractor/builder |
| `extra` | Absent in mono, present in mod | Fix builder defaults |
| `type_mismatch` | Different types (bool vs string) | Fix type handling |


## Running Semantic Validation


```bash
# Single model
uv run python scripts/semantic_validate.py model.yml modular_dir/

# With HTML report
uv run python scripts/semantic_validate.py model.yml modular_dir/ --html report.html

# Batch mode
uv run python scripts/semantic_validate.py model.yml modular_dir/ --batch output_dir/
```


## Integrated in Benchmark


The benchmark pipeline (`scripts/benchmark_model_library.py`) runs semantic validation as a pre-statics gate:
```
.dat → YAML → extract → spec → generate modular → [SEMANTIC CHECK] → [statics] → compare
```
