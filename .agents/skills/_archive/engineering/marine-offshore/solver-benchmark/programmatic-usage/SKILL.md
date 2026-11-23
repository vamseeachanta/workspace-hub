---
name: solver-benchmark-programmatic-usage
description: 'Sub-skill of solver-benchmark: Programmatic Usage.'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Programmatic Usage

## Programmatic Usage


```python
from pathlib import Path
from scripts.benchmark.run_3way_benchmark import run_benchmark

# Run benchmark
result = run_benchmark(
    spec_path=Path("specs/modules/benchmark/unit_box_spec.yml"),
    output_dir=Path("benchmark_output/unit_box"),
    solvers=["orcawave", "aqwa", "bemrosetta"],
    dry_run=False,
)

# Check results
print(f"Success: {result.success}")
for name, sr in result.solver_results.items():
    print(f"  {name}: {sr.status}")

if result.benchmark_result and result.benchmark_result.report:
    print(f"Consensus: {result.benchmark_result.report.overall_consensus}")
```
