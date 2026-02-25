---
name: fitness-for-service
description: >
  Expert FFS engineer applying API 579-1/ASME FFS-1 methodology to corroded and damaged
  offshore equipment. Use for RSF calculations, MAWP re-rating, remaining life projection,
  UT grid inspection data, run-repair-replace decisions, and Level 1/2/3 assessment workflows.
version: 1.0.0
updated: 2026-02-19
category: asset-integrity
triggers:
  - fitness for service
  - FFS assessment
  - API 579
  - ASME FFS-1
  - remaining strength factor
  - RSF calculation
  - MAWP re-rating
  - metal loss assessment
  - corrosion damage
  - run repair replace
  - remaining life
  - wall thickness grid
  - UT thickness measurement
  - general metal loss
  - local metal loss
  - pitting assessment
  - inspection data
  - corrosion allowance
  - CTP critical thickness
related_skills:
  - engineering/marine-offshore/cathodic-protection
  - engineering/marine-offshore/risk-assessment
  - engineering/marine-offshore/structural-analysis
capabilities:
  - rsf-calculation
  - mawp-rereting
  - remaining-life-projection
  - ut-grid-ingestion
  - run-repair-replace-decision
  - level1-level2-assessment
requires: []
---

## When to Use

- Level 1 screening (conservative equations, minimal inspection data)
- Level 2 detailed assessment (refined analysis using thickness profiles)
- RSF and MAWP calculation from UT thickness data
- Remaining life projection with linear and power-law corrosion models
- Processing UT grid CSV data to CTP (Critical Thickness Profile) maps
- Run-repair-replace decision framework

## Assessment Levels (API 579-1/ASME FFS-1)

| Level | Approach | Input Required |
|-------|----------|----------------|
| Level 1 | Screening — conservative, tabulated equations | Nominal thickness, design pressure, corrosion rate |
| Level 2 | Detailed — refined with actual thickness profiles | UT grid measurements, material properties |
| Level 3 | Advanced — FEA/fracture mechanics | Full material data, specialist analysis |

## Core Calculations

### Remaining Strength Factor (RSF)

```python
from digitalmodel.asset_integrity.rsf_calculations import calculate_rsf, check_ffs_level1

# Level 1 screening — General Metal Loss
result = calculate_rsf(
    t_measured=0.280,    # measured wall thickness (inches)
    t_required=0.150,    # required minimum wall thickness (inches)
    t_nominal=0.375,     # original design wall thickness (inches)
)
print(f"RSF: {result['rsf']:.4f}")        # e.g. 0.7467
print(f"FFS: {result['ffs_acceptable']}")  # True if RSF >= RSF_allowable (0.90)
print(f"MAWP ratio: {result['mawp_ratio']:.4f}")

# Level 1 acceptability check
check = check_ffs_level1(
    t_measured=0.280,
    t_required=0.150,
    t_nominal=0.375,
    design_pressure_psi=1200.0,
    smys_psi=65000,
    outer_diameter_in=12.75,
)
print(f"Level 1 acceptable: {check['acceptable']}")
print(f"MAWP remaining: {check['mawp_psi']:.1f} psi")
```

### Remaining Life Projection

```python
from digitalmodel.asset_integrity.rsf_calculations import remaining_life

# Linear corrosion model (most common)
life = remaining_life(
    t_current=0.280,           # measured wall (inches)
    t_minimum=0.150,           # required wall (code minimum)
    corrosion_rate_in_per_yr=0.008,  # measured corrosion rate
    model="linear",
)
print(f"Remaining life: {life['remaining_years']:.1f} years")
print(f"Next inspection by: {life['inspection_date']}")

# Power-law model for accelerating corrosion
life_pw = remaining_life(
    t_current=0.280,
    t_minimum=0.150,
    corrosion_rate_in_per_yr=0.008,
    model="power_law",
    power_law_exponent=1.3,
)
```

### UT Grid — CTP Processing

```python
from digitalmodel.asset_integrity.rsf_calculations import process_ut_grid

# Read UT measurement grid from CSV
# CSV format: rows=axial positions, cols=circumferential positions, values=thickness (inches)
ctp = process_ut_grid(
    csv_path="inspection_data/UT_grid_node_123.csv",
    t_nominal=0.375,
    t_required=0.150,
)
print(f"Minimum measured thickness: {ctp['t_min']:.4f} in")
print(f"Average thickness: {ctp['t_avg']:.4f} in")
print(f"Metal loss fraction: {ctp['metal_loss_pct']:.1f}%")
print(f"CTP grid shape: {ctp['grid_shape']}")
print(f"Points below t_required: {ctp['critical_points']}")
```

## Run-Repair-Replace Decision Framework

| Decision | Condition | Action |
|----------|-----------|--------|
| **Run** | RSF >= 0.90 and t_min > t_required | Continue with monitoring plan |
| **Run (reduced MAWP)** | RSF < 0.90 but MAWP_remaining > 0 | Reduce operating pressure, re-inspect in <= remaining_life/2 |
| **Repair** | t_min < t_required, repair practical | Weld overlay, clamp, composite wrap |
| **Replace** | RSF -> 0 or repair impractical | Spool replacement, re-pipe |

## Standards Reference

| Standard | Scope |
|----------|-------|
| API 579-1 / ASME FFS-1 | Fitness-for-service (primary) |
| API 510 | Pressure vessel inspection |
| API 570 | Piping inspection codes |
| DNV-RP-G101 | Risk-based inspection, offshore topside |
| NACE SP0502 | Pipeline ECDA |

## Related Skills

- [cathodic-protection](../cathodic-protection/SKILL.md) — prevents corrosion; FFS assesses once it occurs
- [risk-assessment](../risk-assessment/SKILL.md) — probabilistic framework for inspection planning
- [structural-analysis](../structural-analysis/SKILL.md) — structural integrity checks
