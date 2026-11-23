# sectionproperties Evaluation

**Issue:** #1452
**Date:** 2026-03-31
**Version tested:** 3.10.2
**License:** MIT
**Repository:** https://github.com/robbievanleeuwen/section-properties

## Overview

[sectionproperties](https://sectionproperties.readthedocs.io) computes geometric and warping properties of arbitrary cross-sections using the finite element method. It supports AISC, Eurocode, and AS standards and provides a built-in library of standard sections (I-beams, channels, angles, hollow sections, etc.).

## Installation

```bash
# Added to digitalmodel/pyproject.toml
uv sync
```

**Install size:** ~10 MB (plus shapely and cytriangle dependencies).

## Evaluation Results

### Rectangular Section (200 x 400 mm)

| Property | Computed | Analytical | Error |
|----------|----------|------------|-------|
| A (mm^2) | 80,000 | 80,000 | 0.00% |
| Ixx (mm^4) | 1.067e9 | 1.067e9 | 0.00% |
| Iyy (mm^4) | 2.667e8 | 2.667e8 | 0.00% |
| Zxx plastic (mm^3) | 8.000e6 | 8.000e6 | 0.00% |
| Sxx elastic (mm^3) | 5.333e6 | 5.333e6 | 0.00% |

### AISC W14x90 I-Beam

| Property | Computed | AISC Manual | Error |
|----------|----------|-------------|-------|
| A (mm^2) | 17,390 | 17,097 | 1.71% |
| Ixx (mm^4) | 4.226e8 | 4.158e8 | 1.63% |
| Iyy (mm^4) | 1.496e8 | 1.507e8 | 0.69% |
| Zxx plastic (mm^3) | 2.612e6 | 2.573e6 | 1.51% |
| Sxx elastic (mm^3) | 2.374e6 | 2.343e6 | 1.32% |
| Cw (mm^6) | 4.211e12 | 4.297e12 | 2.00% |

The torsion constant J shows 12.8% deviation from AISC tables due to differences in fillet radius modeling (FEM vs simplified k-dimension). This is expected and documented in sectionproperties literature.

### CHS 24" OD x 1" WT (609.6 x 25.4 mm)

| Property | Computed | Analytical | Error |
|----------|----------|------------|-------|
| A (mm^2) | 46,542 | 46,617 | 0.16% |
| Ixx (mm^4) | 1.986e9 | 1.993e9 | 0.32% |
| J (mm^4) | 3.971e9 | 3.985e9 | 0.34% |

CHS symmetry verified: Ixx == Iyy within 0.001%.

## API Notes

The sectionproperties naming convention differs from AISC:

| sectionproperties | Returns | AISC Equivalent |
|-------------------|---------|-----------------|
| `get_s()` | Plastic section moduli (sxx, syy) | Z (plastic) |
| `get_z()` | Elastic section moduli (zxx+, zxx-, zyy+, zyy-) | S (elastic) |

This reversal is documented but can be confusing. The test suite includes explicit comments to prevent mix-ups.

## Test Coverage

15 integration tests covering:
- Rectangular section: area, Ixx, Iyy, elastic modulus, plastic modulus
- W14x90 I-beam: area, Ixx, Iyy, elastic modulus, plastic modulus
- CHS: area, Ixx, symmetry, torsion constant, elastic modulus

Test file: `digitalmodel/tests/test_sectionproperties_integration.py`

## Verdict

**RECOMMENDED** for production use. Accuracy is within 2% for geometric properties across all tested sections. The library is well-maintained (550+ stars, 40 contributors), MIT-licensed, and pip-installable with no heavy dependencies.

## Files

- `digitalmodel/pyproject.toml` — dependency added
- `digitalmodel/tests/test_sectionproperties_integration.py` — 15 integration tests
- `digitalmodel/scripts/integrations/sectionproperties_evaluation.py` — evaluation script
- `digitalmodel/scripts/integrations/sectionproperties_poc.py` — original POC
- `data/oss-engineering-catalog.yaml` — catalog entry updated
