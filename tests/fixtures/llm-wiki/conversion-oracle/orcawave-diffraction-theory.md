<!-- oracle_authored_by: claude-sonnet-4-6 -->
<!-- oracle_review_method: from-source -->
<!-- oracle_authored_at: 2026-04-25T00:00:00Z -->
<!-- oracle_second_reviewer: self-reviewed-with-24h-delay -->
<!-- oracle_reviewed_at: 2026-04-26T00:00:00Z -->
<!-- single_reviewer_timelag: true -->
<!-- source: https://www.orcina.com/webhelp/OrcaWave/Content/DiffractionTheory.htm -->

# Diffraction Theory

OrcaWave solves the linear diffraction and radiation problem using a boundary element method.

## Boundary Value Problem

The fluid domain satisfies the Laplace equation with boundary conditions on the body surface,
the free surface, and the seabed.

### Solution Components

- Incident wave potential
- Diffraction potential
- Radiation potentials (one per DOF)

## Panel Method

The body surface is discretised into panels. Each panel has a source distribution.

### Panel Requirements

| Panel type | Nodes | Integration |
|---|---|---|
| Quadrilateral | 4 | Gaussian |
| Triangular | 3 | Gaussian |

#### Mesh Quality

Panel aspect ratio should be less than 3:1 for accurate results.
