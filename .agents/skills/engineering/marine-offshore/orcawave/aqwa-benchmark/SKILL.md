---
name: orcawave-aqwa-benchmark
description: Cross-validation specialist for comparing OrcaWave and AQWA diffraction
  analysis results. Provides statistical comparison, peak value validation, and automated
  benchmark reporting for hydrodynamic coefficient verification.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- AQWA OrcaWave comparison
- diffraction benchmark
- RAO validation
- hydrodynamic coefficient comparison
- cross-tool validation
- panel method benchmark
- added mass comparison
- damping comparison
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcawave Aqwa Benchmark

## When to Use

- Validating OrcaWave results against AQWA benchmarks
- Comparing RAO amplitudes and phases between tools
- Verifying added mass and damping matrices
- Running automated benchmark test suites
- Generating comparison reports for quality assurance
- Establishing confidence in diffraction analysis results
- Identifying discrepancies between panel method implementations

## Python API

### Basic Comparison

```python
from digitalmodel.diffraction.comparison_framework import (
    DiffractionComparator,
    PeakRAOComparator
)
from digitalmodel.diffraction.aqwa_converter import AQWAConverter
from digitalmodel.diffraction.orcawave_converter import OrcaWaveConverter

# Load AQWA results
aqwa_converter = AQWAConverter()

*See sub-skills for full details.*
### Peak-Focused Validation

```python
from digitalmodel.diffraction.comparison_framework import PeakRAOComparator

# Peak-focused comparison (recommended for validation)
peak_comparator = PeakRAOComparator(
    aqwa_results=aqwa_results,
    orcawave_results=orcawave_results,
    peak_threshold=0.10,  # 10% of peak magnitude
    tolerance=0.05  # 5% tolerance
)

*See sub-skills for full details.*
### Matrix Comparison

```python
from digitalmodel.diffraction.comparison_framework import MatrixComparator

# Compare added mass matrices
matrix_comp = MatrixComparator()

# Compare at specific frequency
freq = 0.1  # rad/s
am_comparison = matrix_comp.compare_added_mass(
    aqwa_matrix=aqwa_results['added_mass'][freq],

*See sub-skills for full details.*
### Statistical Analysis

```python
from digitalmodel.diffraction.comparison_framework import StatisticalAnalyzer

# Initialize analyzer
analyzer = StatisticalAnalyzer()

# Compute correlation metrics
correlation = analyzer.compute_correlation(
    aqwa_raos=aqwa_results['raos'],
    orcawave_raos=orcawave_results['raos']

*See sub-skills for full details.*

## Related Skills

- [orcawave-analysis](../orcawave-analysis/SKILL.md) - OrcaWave analysis execution
- [aqwa-analysis](../aqwa-analysis/SKILL.md) - AQWA analysis execution
- [hydrodynamics](../hydrodynamics/SKILL.md) - Coefficient management

## References

- Comparison Framework: `src/digitalmodel/modules/diffraction/comparison_framework.py`
- Benchmark Data: `docs/modules/orcawave/L01_aqwa_benchmark/`
- AQWA Converter: `src/digitalmodel/modules/diffraction/aqwa_converter.py`
- OrcaWave Converter: `src/digitalmodel/modules/diffraction/orcawave_converter.py`

---

**Version History**

- **1.0.0** (2026-01-17): Initial release with comparison framework, peak validation, and statistical analysis

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [Standard Tolerances (+1)](standard-tolerances/SKILL.md)
- [Benchmark Suite Configuration (+1)](benchmark-suite-configuration/SKILL.md)
- [CLI Usage](cli-usage/SKILL.md)
- [HTML Report Structure (+1)](html-report-structure/SKILL.md)
- [Standard Test Suite](standard-test-suite/SKILL.md)
- [Common Causes of Deviation (+1)](common-causes-of-deviation/SKILL.md)
- [Automated Validation in Pipeline](automated-validation-in-pipeline/SKILL.md)
- [Convention Differences (+3)](convention-differences/SKILL.md)
- [Single-Page HTML Report Structure (+3)](single-page-html-report-structure/SKILL.md)


## Documentation Reference

OrcaWave topics (`data/llm-wiki/orcawave/`):
- `Theory,First-orderequations.md` -- first-order panel method (OrcaWave side)
- `Results,Addedmassanddamping.md` -- AMD results for comparison
- `Results,DisplacementRAOs.md` -- RAO results for comparison
- `Theory,Coordinatesystems.md` -- coordinate conventions (key for cross-tool alignment)
- `Data,Validation.md` -- built-in validation checks

OrcaFlex topics (`data/llm-wiki/orcaflex/`):
- `Importinghydrodynamicdata,AQWA.md` -- AQWA import conventions
- `Importinghydrodynamicdata,OrcaWave.md` -- OrcaWave import conventions
- `Vesseltypes,CheckingRAOs.md` -- RAO quality checks
