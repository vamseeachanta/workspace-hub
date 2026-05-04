---
name: doc-extraction-naval-architecture-structural-scantling-tables
description: 'Sub-skill of doc-extraction-naval-architecture: Structural Scantling
  Tables.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Structural Scantling Tables

## Structural Scantling Tables


Minimum structural member dimensions from classification rules.

**Detection heuristics**:
- Keywords: "scantling", "plate thickness", "section modulus", "frame spacing",
  "shell plating", "deck plating", "stiffener", "web frame"
- Pattern: table with member type, location, and minimum dimensions
- Units: mm (thickness), cm³ (section modulus), mm (spacing)
- Context: classification society rules (ABS, DNV, LR, BV, ClassNK)

**Key extraction fields**:
```yaml
- content_type: tables
  domain: naval_architecture
  sub_type: scantling_table
  data:
    title: "Minimum shell plating thickness"
    columns:
      - {name: location, units: null}
      - {name: min_thickness, units: mm}
      - {name: material_grade, units: null}
      - {name: frame_spacing, units: mm}
    applicability:
      class_society: "DNV"
      rule_set: "Rules for Classification of Ships Part 3 Ch 1"
    source: "DNV Rules Pt.3 Ch.1 Sec.6"
```
