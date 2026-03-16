---
name: orcaflex-code-check
description: Verify OrcaFlex model results against industry standards (DNV, API, ISO).
  Perform capacity checks, safety factor verification, and compliance reporting for
  offshore structures.
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- code check
- standards compliance
- DNV check
- API check
- ISO check
- safety factor
- capacity check
- design verification
capabilities: []
requires: []
see_also:
- orcaflex-code-check-error-handling
tags: []
scripts_exempt: true
---

# Orcaflex Code Check

## Version Metadata

```yaml
version: 1.0.0
python_min_version: '3.10'
dependencies:
  orcaflex-modeling: '>=2.0.0,<3.0.0'
  structural-analysis: '>=1.0.0,<2.0.0'
orcaflex_version: '>=11.0'
compatibility:
  tested_python:
  - '3.10'
  - '3.11'
  - '3.12'
  - '3.13'
  os:
  - Windows
  - Linux
  - macOS
```

## Changelog

### [1.0.0] - 2026-01-17

**Added:**
- Initial release with standards compliance checking
- Mooring line capacity verification
- Safety factor calculation
- Multi-standard support (DNV, API, ISO)

## When to Use

- Verify mooring line tensions against MBL limits
- Check riser stress against allowable
- Validate safety factors per design codes
- Generate compliance reports for certification
- Design verification before fabrication
- Audit existing designs against current standards

## Supported Standards

### Mooring Systems

| Standard | Application | Key Checks |
|----------|-------------|------------|
| **API RP 2SK** | Stationkeeping | Safety factors, line capacity |
| **DNV-OS-E301** | Position mooring | Tension limits, fatigue |
| **ISO 19901-7** | Mooring systems | Capacity, redundancy |
### Risers

| Standard | Application | Key Checks |
|----------|-------------|------------|
| **API RP 2RD** | Riser design | Stress, fatigue |
| **DNV-OS-F201** | Dynamic risers | Stress, VIV |
| **API STD 2RD** | Design of risers | Combined loading |
### Pipelines

| Standard | Application | Key Checks |
|----------|-------------|------------|
| **DNV-OS-F101** | Submarine pipelines | Wall thickness, buckling |
| **API RP 1111** | Pipeline design | Pressure containment |

## Python API

### Mooring Safety Factor Check

```python
from digitalmodel.structural.structural_analysis.capacity import CapacityChecker

def check_mooring_safety_factors(
    max_tensions: dict,
    mbl_values: dict,
    standard: str = "API_RP_2SK"
) -> dict:
    """
    Check mooring line tensions against MBL limits.

*See sub-skills for full details.*
### Riser Stress Check

```python
from digitalmodel.structural.structural_analysis.capacity import CapacityChecker
import math

def check_riser_stress(
    max_tension: float,
    max_bend_moment: float,
    internal_pressure: float,
    external_pressure: float,
    od: float,

*See sub-skills for full details.*
### Standards Lookup

```python
from digitalmodel.infrastructure.common.standards_lookup import StandardsLookup

# Initialize lookup
lookup = StandardsLookup()

# Search for relevant standards
results = lookup.search("mooring design")

for standard in results:

*See sub-skills for full details.*
### Generate Compliance Report

```python
def generate_compliance_report(
    check_results: dict,
    output_path: str,
    project_info: dict
) -> str:
    """Generate HTML compliance report."""

    html_content = f"""
    <!DOCTYPE html>

*See sub-skills for full details.*

## Safety Factors Reference

### API RP 2SK (2015)

| Condition | Analysis | Safety Factor |
|-----------|----------|---------------|
| Intact | Quasi-static | 1.67 |
| Intact | Dynamic | 1.82 |
| Damaged | Quasi-static | 1.25 |
| Damaged | Dynamic | 1.43 |
### DNV-OS-E301

| Condition | Consequence Class 1 | Consequence Class 2 |
|-----------|---------------------|---------------------|
| ULS Intact | 2.20 | 2.50 |
| ULS Damaged | 1.50 | 1.65 |
| ALS | 1.00 | 1.10 |
### ISO 19901-7

| Condition | Category 1 | Category 2 |
|-----------|------------|------------|
| Intact | 1.67 | 2.00 |
| Damaged | 1.25 | 1.50 |

## Related Skills

- [orcaflex-post-processing](../orcaflex-post-processing/SKILL.md) - Extract results
- [orcaflex-extreme-analysis](../orcaflex-extreme-analysis/SKILL.md) - Find design loads
- [structural-analysis](../structural-analysis/SKILL.md) - Structural capacity checks
- [fatigue-analysis](../fatigue-analysis/SKILL.md) - Fatigue code checks

## References

- API RP 2SK: Design and Analysis of Stationkeeping Systems
- DNV-OS-E301: Position Mooring
- DNV-OS-F201: Dynamic Risers
- ISO 19901-7: Stationkeeping Systems for Floating Offshore Structures
- Source: `src/digitalmodel/infrastructure/common/standards_lookup.py`
- Source: `src/digitalmodel/modules/structural_analysis/capacity.py`

## Sub-Skills

- [Mooring Code Check (+1)](mooring-code-check/SKILL.md)
- [Before Code Check (+2)](before-code-check/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)
