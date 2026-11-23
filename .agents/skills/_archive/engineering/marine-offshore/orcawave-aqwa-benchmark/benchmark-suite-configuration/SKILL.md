---
name: orcawave-aqwa-benchmark-benchmark-suite-configuration
description: 'Sub-skill of orcawave-aqwa-benchmark: Benchmark Suite Configuration
  (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Benchmark Suite Configuration (+1)

## Benchmark Suite Configuration


```yaml
# configs/benchmark_suite.yml

benchmark:
  name: "FPSO Diffraction Validation"
  description: "OrcaWave vs AQWA comparison for FPSO vessel"

  reference:
    tool: "AQWA"
    version: "2024.R1"

*See sub-skills for full details.*

## Automated Validation Script


```yaml
# configs/validation_criteria.yml

validation:
  pass_criteria:
    # At least 90% of significant points within tolerance
    min_points_within_tolerance: 0.90

    # Maximum allowed deviation for any single point
    max_single_deviation: 0.15

*See sub-skills for full details.*
