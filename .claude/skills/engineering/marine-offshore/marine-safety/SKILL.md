# Marine Safety & Integrity Specialist

> Integrity management, life extension, and safety assessment for offshore assets.

**Version:** 1.0.0
**Created:** 2026-01-13
**Category:** SME / Safety & Integrity

## Overview

This skill covers the assessment of aging offshore assets, focusing on structural integrity, corrosion management, and life extension. It synthesizes knowledge from legacy projects like "Horn Mountain TTR VIV Analysis" and "Marlin TTR Life Extension".

## Core Capabilities

### 1. Life Extension Assessment (LEX)
- **Gap Analysis**: Comparing original design codes vs. current standards (API 2INT-MET).
- **Fatigue Re-analysis**: Using updated metocean data to calculate remaining fatigue life.
- **Risk-Based Inspection (RBI)**: Prioritizing inspections based on failure probability and consequence.

### 2. Corrosion Management
- **Corrosion Rate Modelling**: CO2/H2S corrosion prediction (Norsok M-506).
- **Wall Thickness Checks**: Evaluating hoop stress and collapse/burst pressure with degraded wall thickness.
- **Anode Retrofit**: Designing sacrificial anode sleds for life extension.

### 3. Fitness-For-Service (FFS)
- **API 579 / BS 7910**: Assessing defects (cracks, dents, corrosion) to determine if equipment is safe to operate.
- **VIV Assessment**: Vortex Induced Vibration fatigue analysis for risers and conductors.

## When to Use

### Use This Skill When:
- Evaluating an asset for operation beyond its original design life.
- Assessing the safety of a corroded pipeline or vessel.
- Planning inspection campaigns (RBI).
- Reviewing "Fitness for Service" reports.

### Do Not Use This Skill When:
- Designing a *new* asset (use Structural Analysis or DNV Standards).
- Calculating basic hydrostatics (use Marine Engineering).

## Knowledge Areas

### 1. Life Extension Workflow
1.  **Data Gathering**: Collect original design reports, inspection logs, and production history.
2.  **Condition Assessment**: Evaluate current physical state (corrosion, marine growth).
3.  **Re-Analysis**: Update models with current weight, metocean, and soil data.
4.  **Remediation**: Propose clamps, strengthening, or derating.

### 2. Defect Assessment
Cracks or metal loss are evaluated using "Failure Assessment Diagrams" (FAD) to determine if the combination of stress and defect size is critical.

## Code & Data Patterns

### Corrosion Derating Check
```python
def check_wall_thickness(nominal_wt, corrosion_rate, years, min_required_wt):
    """
    Calculate remaining wall thickness and check against minimum required.
    """
    loss = corrosion_rate * years
    current_wt = nominal_wt - loss
    
    if current_wt < min_required_wt:
        return False, f"FAILED: Current WT {current_wt:.2f}mm < Min {min_required_wt:.2f}mm"
    
    remaining_life = (current_wt - min_required_wt) / corrosion_rate
    return True, f"PASS: {remaining_life:.1f} years remaining"
```

## Best Practices

- **Conservatism**: When data is missing (e.g., actual corrosion rates), use conservative estimates from standards (e.g., Norsok M-506).
- **Trend Analysis**: Use historical inspection data (UT/ILI) to validate corrosion models.

## Resources
- **Legacy Projects**: `/mnt/ace/docs/disciplines/integrity_management/projects/`
    - `31519_fmog_marlin_ttr_life_extension`
    - `0185_ecs_ffs_engineering`
