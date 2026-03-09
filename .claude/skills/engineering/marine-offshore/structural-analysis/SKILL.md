---
name: structural-analysis
version: "1.1.0"
category: engineering
description: >
  Expert structural analysis for marine and offshore structures. Use when
  performing ULS/ALS limit state checks, column buckling, beam deflection,
  tubular joint design, or stiffened panel analysis per DNV/API/ISO codes.
  Capabilities: section properties (circular tube, RHS, I-beam), combined
  loading stress checks, Euler and DNV column buckling, beam deflection
  formulae, tubular joint T/Y capacity (DNV-RP-C203), ULS interaction
  (linear + Eurocode), ALS dented pipe assessment, stiffened panel buckling.
tags:
  - structural
  - mechanics
  - dnv
  - buckling
  - uls
  - als
  - beam-theory
  - stress-analysis
created: 2026-01-06
updated: 2026-03-08
requires: []
see_also:
  - ../fatigue-analysis/SKILL.md
---

# Structural Analysis Skill

Expert structural analysis for marine and offshore structures — ULS/ALS
limit state checks, buckling, DNV/API standards, tubular members, stiffened
panels, combined loading.

See `references/standards.md` for: full calculation examples, design criteria
details, structural member tables, load case matrices, design check formulas,
material property tables, safety factor tables, design workflow skeleton, and
code compliance report template.

## When to Use

- Perform ULS (Ultimate Limit State) and ALS (Accidental Limit State) checks
- Analyze buckling of columns, beams, and stiffened panels
- Calculate section properties and stress distributions
- Apply DNV structural design standards
- Evaluate combined loading (axial + bending + torsion)
- Design tubular members and jacket structures
- Integrate fatigue analysis with structural checks

## Core Knowledge Areas

### 1. Section Properties

Key shapes: circular tube, rectangular hollow section (RHS), I-beam/H-beam.
All return `SectionProperties(area, Ix, Iy, J, Zx, Zy, rx, ry)`.
Full implementations: `references/standards.md §Section Properties`.

Circular tube shorthand:
- `A = π/4·(D²-d²)`, `I = π/64·(D⁴-d⁴)`, `r = √(I/A)`

### 2. Stress Analysis

Combined loading stresses (axial + bending + torsion + shear):
- Axial: `σ = N/A`
- Bending: `σ = M·y/I` (or `M/Z` at extreme fibre)
- Torsion: `τ = T·r/J`
- Von Mises: `σ_vm = √(σ²+3τ²)`

Principal stresses via Mohr's circle. Full code: `references/standards.md`.

### 3. Column Buckling

Euler critical load: `P_cr = π²EI/(KL)²`

DNV check (DNV-OS-C101 / DNV-RP-C201):
- Reduced slenderness: `λ̄ = (KL/r)·√(fy/E)/π`
- Buckling factor χ using European column curve 'a' (α=0.21 for welded tubes)
- Design resistance: `N_b_Rd = χ·A·fy/γ_M`
- Unity check: `N_Ed / N_b_Rd ≤ 1.0`

### 4. Beam Bending and Deflection

Simply supported: point at centre `δ = PL³/(48EI)`, UDL `5wL⁴/(384EI)`.
Cantilever: point at free end `δ = PL³/(3EI)`, UDL `wL⁴/(8EI)`.
Allowable: L/360 (general), L/180 (cantilever).

### 5. Tubular Joint Design (DNV-RP-C203)

Geometric parameters: `β=d/D`, `γ=D/(2T)`, `τ=t/T`.
Validity: `0.2≤β≤1.0`, `10≤γ≤50`, `θ≥30°`.
T/Y joint axial capacity: `N_cap = Qu·fy·T²/sin(θ)`.
Combined check: `(N/N_cap)^p + (M_ipb/M_ipb_cap)^p + ... ≤ 1`, p=2.
Full implementation: `references/standards.md §Tubular Joint`.

### 6. ULS and ALS Checks

ULS combined loading (DNV-OS-C101):
- Linear: `N/N_Rd + My/My_Rd + Mz/Mz_Rd ≤ 1.0`
- Eurocode: `(N/N_Rd)² + (My/My_Rd + Mz/Mz_Rd) ≤ 1.0`
- Use conservative max of both.

ALS dented pipe (DNV-RP-F110):
- `δ/D < 6%` acceptable; `6–20%` needs engineering assessment; `>20%` repair.
- Burst reduction: `P_burst_dented = f_dent · 2t·fy/D`.

### 7. Stiffened Panel Buckling

Plate critical stress: `σ_cr = k·π²E/(12(1-ν²))·(t/b)²`
Buckling coefficient k=4.0 for long plates (a/b≥1).
Column buckling of stiffener + effective plate width.
Overall UC = max(panel_UC, column_UC).

## Applicable Codes and Standards

See `references/standards.md §Standards List` for full titles and references.

**DNV:** OS-C101, RP-C201 (buckling), RP-C203 (fatigue/joints), RP-C205
(environmental), ST-0126 (wind turbine supports), OS-E301 (mooring).

**API:** RP 2A (fixed platforms), RP 2FPS (floating), RP 2SK (mooring),
Spec 2B (structural pipe).

**Other:** ISO 19902 (fixed steel offshore), Eurocode 3 (EN 1993), AISC 360.

## Software Tools

SACS (offshore jackets), ANSYS (FEA), STAAD.Pro, OrcaFlex (load export),
SESAM (DNV marine).
