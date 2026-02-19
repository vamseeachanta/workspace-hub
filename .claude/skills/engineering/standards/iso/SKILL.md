---
name: iso
version: "1.0.0"
category: engineering
description: "ISO Standards Specialist"
capabilities: []
requires: []
see_also: []
---

# ISO Standards Specialist

> International Organization for Standardization (ISO) codes for general engineering, materials, and safety.

**Version:** 1.0.0
**Created:** 2026-01-12
**Category:** SME / Codes & Standards

## Overview

ISO standards provide the universal framework for quality, safety, and specific technical systems. In the context of this repository, we focus on ISO standards adopted by the oil & gas industry (often harmonized with API) and general engineering specs.

## Core Capabilities

### 1. Materials & Corrosion
- **ISO 15156**: Materials for use in H2S-containing environments (NACE MR0175). Critical for "Sour Service".
- **ISO 898**: Mechanical properties of fasteners.

### 2. Pipeline & Drilling
- **ISO 13628**: Design and operation of subsea production systems (parallels API 17 series).
- **ISO 19900 series**: Petroleum and natural gas industries – General requirements for offshore structures.

### 3. Quality & Safety
- **ISO 9001**: Quality Management Systems.
- **ISO 14001**: Environmental Management.

## When to Use

### Use This Skill When:
- Selecting materials for sour service (H2S).
- Working on international projects where API is not the governing code.
- Specifying fasteners and bolts.
- Establishing quality management protocols.

## Knowledge Areas

### 1. ISO vs. API
Many ISO standards are "identical" or "modified" adoptions of API standards (e.g., ISO 13628-4 = API 17D). However, regional annexes may apply.

### 2. Sour Service (ISO 15156)
The definitive guide for preventing Sulfide Stress Cracking (SSC). It classifies materials based on H2S partial pressure and pH.

## Code & Data Patterns

### Sour Service Region Check
```python
def check_nace_region(pH, pH2S_psi):
    """
    Determine severity region (0, 1, 2, 3) based on ISO 15156 / NACE MR0175.
    (Simplified logic for demonstration)
    """
    if pH2S_psi < 0.05:
        return "Region 0 (No specific requirements)"
    
    if pH > 3.5:
        return "Region 1 (Low Severity)"
    else:
        return "Region 3 (High Severity - Strict Material Controls)"
```

## Best Practices

- **Harmonization**: Check if an API equivalent exists (e.g., API 6A vs ISO 10423).
- **Traceability**: ISO standards emphasize material traceability and certification (Type 3.1, 3.2 certs).

## Resources
- **Source Files**: `/mnt/ace/O&G-Standards/ISO/`
