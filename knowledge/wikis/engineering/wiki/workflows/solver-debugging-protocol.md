---
title: "Solver Debugging Protocol"
tags: [debugging, solvers, pre-flight, unit-traps, correlation]
sources:
  - dark-intelligence-extractions
  - career-learnings-seed
added: 2026-04-08
last_updated: 2026-04-08
---

# Solver Debugging Protocol

A systematic approach to debugging engineering solvers, developed from hard-won experience with OrcaFlex, AQWA, and cross-solver correlation failures. The core principle: **validate inputs BEFORE running solvers** — most solver bugs are input bugs.

## Phase 1: Pre-Flight Validation

Before submitting any solver run, verify:

| Check | What to Verify | Common Failure |
|-------|---------------|----------------|
| Frequency units | Hz vs rad/s | Wrong by factor of 2*pi |
| Frequency order | Ascending vs descending | Reversed arrays produce negative correlations |
| RAO units | rad/m vs deg/m | Wrong by factor of 57.3 |
| Array shape | (nheading, nfreq, 6) vs transposed | Silent wrong results |
| Element types | QPPL DIFF vs QPPL | No diffraction computed |
| Mesh closure | Watertight hull check | FATAL mesh errors in AQWA |
| Mass/inertia | Consistent units, correct COG | Non-physical responses |

## Phase 2: Unit Traps

The most common source of cross-solver disagreement is unit mismatch:

### Frequency Units

| Solver | Unit | Order |
|--------|------|-------|
| OrcaWave/OrcaFlex | Hz | Descending |
| AQWA | rad/s | Ascending (typically) |
| WAMIT | rad/s | Ascending |
| Nemoh | rad/s | Ascending |

**Conversion**: `omega (rad/s) = 2 * pi * f (Hz)`

### Rotational RAO Units

- OrcaFlex `.displacementRAOs`: rotational DOFs in **radians/m**
- Many comparison tools expect **deg/m**
- Conversion: `deg/m = rad/m * (180/pi)` or use `np.degrees()`

## Phase 3: Correlation Diagnostics

When comparing results from two solvers:

### Negative Correlations

Almost always caused by **frequency arrays in different order**. One solver outputs highest-frequency-first, the other lowest-frequency-first. Fix: sort both arrays to the same order before comparing.

### NaN Correlations

Caused by **zero standard deviation** in one or both arrays. Common scenario: yaw RAO at head seas (0 degrees) is identically zero for symmetric hulls. The correlation coefficient is undefined when one variable has zero variance.

**Fix**: Handle gracefully — skip the comparison, report as "N/A (zero response)", or add a tiny epsilon check before computing correlation.

### Poor Correlations (0.5 - 0.9)

Possible causes:
1. Array shape mismatch (transposed heading vs frequency axes)
2. Different heading conventions (going-to vs coming-from, or CW vs CCW)
3. Different phase conventions (cosine vs sine reference)
4. Mesh resolution differences between solvers

## Phase 4: AQWA-Specific Debugging

### FATAL Mesh Errors

- `OPTIONS GOON` does NOT override mesh FATAL errors
- Mesh FATALs require fixing the geometry: non-watertight hull, overlapping panels, degenerate elements
- Check panel normals — all must point outward consistently

### LIS Parser Issues

- **Normalize whitespace** before keyword matching: AQWA output contains inconsistent spacing (e.g., `"ADDED  MASS"` has double space)
- Use regex with `\s+` instead of literal space matching
- Verify you are reading the correct block — LIS files contain multiple result sections

## Phase 5: Cross-Solver Comparison Checklist

Before declaring results "don't match":

- [ ] Frequency arrays sorted to same order
- [ ] Frequency units converted (Hz <-> rad/s)
- [ ] Rotational RAO units converted (rad/m <-> deg/m)
- [ ] Array shapes match (nheading, nfreq, 6)
- [ ] Heading conventions aligned
- [ ] Phase conventions aligned
- [ ] Zero-response DOFs handled (NaN protection)
- [ ] Mesh resolution comparable between solvers
- [ ] Mass/inertia/COG identical in both models

## Cross-References

- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related entity**: [AQWA Solver](../entities/aqwa-solver.md)
- **Related entity**: [BEMRosetta Tool](../entities/bemrosetta-tool.md)
- **Related entity**: [Solver Queue](../entities/solver-queue.md)
