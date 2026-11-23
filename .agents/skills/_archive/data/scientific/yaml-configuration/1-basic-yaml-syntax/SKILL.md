---
name: yaml-configuration-1-basic-yaml-syntax
description: 'Sub-skill of yaml-configuration: 1. Basic YAML Syntax (+1).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Basic YAML Syntax (+1)

## 1. Basic YAML Syntax


**Scalars:**
```yaml
# Strings
project_name: "FPSO Mooring Analysis"
description: Simple mooring system

# Numbers
water_depth: 1500        # Integer
wave_height: 8.5         # Float
scientific: 1.5e-3       # Scientific notation

# Booleans
include_current: true
dynamic_analysis: false

# Null values
optional_parameter: null
# or
optional_parameter: ~
```

**Lists:**
```yaml
# Inline list
mooring_lines: [1, 2, 3, 4, 5, 6]

# Block list
vessel_types:
  - FPSO
  - Semi-submersible
  - TLP
  - SPAR

# List of dictionaries
load_cases:
  - name: "Operating"
    Hs: 4.5
    Tp: 10.0
  - name: "Storm"
    Hs: 8.5
    Tp: 12.0
```

**Dictionaries:**
```yaml
# Nested dictionaries
vessel:
  name: "FPSO Vessel"
  dimensions:
    length: 320
    beam: 58
    draft: 22
  mass_properties:
    displacement: 150000
    lcg: 160
    vcg: 15
```


## 2. Advanced Features


**Anchors and Aliases (Reuse):**
```yaml
# Define anchor
default_material: &steel
  name: "Steel"
  density: 7850
  youngs_modulus: 200e9

# Reuse with alias
chain_material: *steel

mooring_line:
  material: *steel  # References same data

# Merge keys
base_config: &base
  version: 1.0
  author: "Engineering Team"

analysis_1:
  <<: *base  # Merge base_config
  name: "Analysis 1"
  parameters:
    duration: 3600

analysis_2:
  <<: *base  # Merge base_config
  name: "Analysis 2"
  parameters:
    duration: 7200
```

**Multi-line Strings:**
```yaml
# Preserve newlines (literal style)
description: |
  This is a multi-line string.
  Newlines are preserved.
  Use for comments or descriptions.

# Fold newlines (folded style)
notes: >
  This string will have
  newlines replaced with spaces,
  except for blank lines.

  This starts a new paragraph.
```

**Comments:**
```yaml
# This is a comment
project: "Mooring Analysis"  # Inline comment

# Comments for documentation
vessel:
  # Main dimensions
  length: 320  # meters
  beam: 58     # meters
```
