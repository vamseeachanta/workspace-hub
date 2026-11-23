---
name: diffraction-analysis-when-to-use-each-module
description: 'Sub-skill of diffraction-analysis: When to Use Each Module (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# When to Use Each Module (+1)

## When to Use Each Module


| Scenario | Recommended Module | Reason |
|----------|-------------------|--------|
| Parse AQWA .LIS files | `aqwa` or `bemrosetta` | Native parsing, no external dependencies |
| Run OrcaWave analysis | `orcawave` | Direct OrcaFlex API integration |
| Convert AQWA → OrcaFlex | `bemrosetta` | Purpose-built converter with validation |
| Compare AQWA vs OrcaWave | `diffraction` | Unified schema comparison framework |
| Handle QTF data | `bemrosetta` | QTF parser and OrcaFlex export |
| Convert mesh formats | `bemrosetta` | GDF/DAT/STL conversion |
| Store/retrieve coefficients | `hydrodynamics` | Coefficient database |

## Feature Matrix


| Feature | aqwa | orcawave | bemrosetta | diffraction |
|---------|------|----------|------------|-------------|
| Parse AQWA .LIS | ✅ | ❌ | ✅ | ✅ (via converter) |
| Parse OrcaWave | ❌ | ✅ | ❌ | ✅ (via converter) |
| RAO extraction | ✅ | ✅ | ✅ | ✅ |
| Added mass/damping | ✅ | ✅ | ✅ | ✅ |
| QTF (2nd order) | ❌ | ✅ | ✅ | ❌ |
| Export to OrcaFlex | ❌ | Native | ✅ | ✅ |
| Mesh conversion | ❌ | ❌ | ✅ | ❌ |
| Coefficient validation | ❌ | ❌ | ✅ | ✅ |
| Comparison framework | ❌ | ❌ | ❌ | ✅ |
